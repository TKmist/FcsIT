"""
Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)

This file is part of the FcsIT repository.

This file is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later version.

This file is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this file. If not, see <https://www.gnu.org/licenses/>.
"""
import dearpygui.dearpygui as dpg
import numpy as np
from numpy import log10, sqrt, exp, log, pi
import os
import pandas as pd
import datetime
from lmfit import Model
from numpy.linalg import inv, det,cond,pinv
import matplotlib.pyplot as plt
from functools import wraps
from pathlib import Path
try:
    from phconvert.pqreader import load_pt3, load_ptu
except ImportError:
    load_pt3 = None
    load_ptu = None
from Methods.PTU_Corr.include.correlation_methods import tttr2xfcs
import time
import socket


from numba import njit, prange

from concurrent.futures import ThreadPoolExecutor, as_completed


@njit(cache=True)
def _fcs_build_block_idx_numba(M, n_bootstrap, block_size, seed):
    np.random.seed(seed)

    n_blocks = (M + block_size - 1) // block_size
    out = np.empty((n_bootstrap, M), dtype=np.int64)

    for b in range(n_bootstrap):
        pos = 0
        for _ in range(n_blocks):
            start = np.random.randint(0, M)
            for k in range(block_size):
                if pos < M:
                    out[b, pos] = (start + k) % M
                    pos += 1

    return out


@njit(cache=True)
def _fcs_nanmean_1d_numba(arr):
    s = 0.0
    c = 0

    for i in range(arr.shape[0]):
        v = arr[i]
        if not np.isnan(v):
            s += v
            c += 1

    if c == 0:
        return np.nan

    return s / c


@njit(cache=True)
def _fcs_nanstd_sample_1d_numba(arr, mean):
    c = 0
    s2 = 0.0

    for i in range(arr.shape[0]):
        v = arr[i]
        if not np.isnan(v):
            d = v - mean
            s2 += d * d
            c += 1

    if c == 0:
        return np.nan

    if c == 1:
        return 0.0

    return np.sqrt(s2 / (c - 1))


@njit(parallel=True, cache=True)
def _fcs_compute_mean_std_kernel_numba(X, Ki_eps, block_idx):
    Tn, M = X.shape
    B, M2 = block_idx.shape

    boot_mean_avg = np.empty(Tn, dtype=np.float64)
    std_boot = np.empty(Tn, dtype=np.float64)
    bootstrap_curves = np.empty((B, Tn), dtype=np.float64)

    for i in prange(Tn):
        any_positive_weight = False

        for m in range(M):
            if Ki_eps[i, m] > 0.0:
                any_positive_weight = True
                break

        if not any_positive_weight:
            boot_mean_avg[i] = np.nan
            std_boot[i] = np.nan
            bootstrap_curves[:, i] = np.nan
            continue

        boot_means = np.empty(B, dtype=np.float64)

        for b in range(B):
            wsum = 0.0
            num = 0.0
            usum = 0.0
            ucnt = 0

            for j in range(M2):
                k = block_idx[b, j]
                v = X[i, k]

                if not np.isnan(v):
                    usum += v
                    ucnt += 1

                    w = Ki_eps[i, k]
                    if w > 0.0:
                        num += v * w
                        wsum += w

            if wsum > 0.0:
                boot_means[b] = num / wsum
            elif ucnt > 0:
                boot_means[b] = usum / ucnt
            else:
                boot_means[b] = np.nan

            bootstrap_curves[b, i] = boot_means[b]

        mu = _fcs_nanmean_1d_numba(boot_means)
        sd = _fcs_nanstd_sample_1d_numba(boot_means, mu)

        boot_mean_avg[i] = mu
        std_boot[i] = sd

    return boot_mean_avg, std_boot, bootstrap_curves


def _bootstrap_covariance(bootstrap_curves):
    """Return PSD lag covariance and pairwise effective replicate counts."""
    curves = np.asarray(bootstrap_curves, dtype=float)
    n_lags = curves.shape[1]
    if curves.shape[0] < 2:
        return (
            np.zeros((n_lags, n_lags), dtype=float),
            np.zeros((n_lags, n_lags), dtype=np.int64),
        )
    if np.all(np.isfinite(curves)):
        covariance = np.atleast_2d(np.cov(curves, rowvar=False, ddof=1))
        counts = np.full(covariance.shape, curves.shape[0], dtype=np.int64)
        return covariance, counts

    covariance = np.zeros((n_lags, n_lags), dtype=float)
    counts = np.zeros((n_lags, n_lags), dtype=np.int64)
    for left in range(n_lags):
        for right in range(left, n_lags):
            valid = np.isfinite(curves[:, left]) & np.isfinite(curves[:, right])
            counts[left, right] = np.count_nonzero(valid)
            counts[right, left] = counts[left, right]
            value = 0.0
            if np.count_nonzero(valid) > 1:
                value = np.cov(
                    curves[valid, left], curves[valid, right], ddof=1
                )[0, 1]
            covariance[left, right] = value
            covariance[right, left] = value

    # Pairwise deletion can produce an indefinite matrix. Project its
    # correlation form onto the PSD cone and restore the original variances.
    variance = np.clip(np.diag(covariance), 0.0, None)
    scale = np.sqrt(variance)
    positive = scale > 0.0
    correlation = np.eye(n_lags, dtype=float)
    denominator = scale[:, None] * scale[None, :]
    np.divide(
        covariance, denominator, out=correlation,
        where=(denominator > 0.0),
    )
    correlation = np.clip(0.5 * (correlation + correlation.T), -1.0, 1.0)
    eigenvalues, eigenvectors = np.linalg.eigh(correlation)
    correlation = (eigenvectors * np.clip(eigenvalues, 0.0, None)) @ eigenvectors.T
    normalization = np.sqrt(np.clip(np.diag(correlation), 1e-15, None))
    correlation /= normalization[:, None] * normalization[None, :]
    covariance = correlation * denominator
    covariance[~positive, :] = 0.0
    covariance[:, ~positive] = 0.0
    np.fill_diagonal(covariance, variance)
    return covariance, counts


def _attach_lag_covariance(frame, bootstrap_result, lag_times):
    """Attach lag uncertainty metadata when a correlation curve exists."""
    if frame is None:
        return
    frame.attrs['lag_covariance'] = bootstrap_result[2]
    frame.attrs['lag_covariance_counts'] = bootstrap_result[3]
    frame.attrs['lag_times'] = np.asarray(lag_times, dtype=float)


class load_fcs:
    def __init__(self,file,time_bin):
        
        self.file = file
        self.TTTR_Mode = None
        self.mode = ''
        self.time_bin = time_bin #[s]
        self.timetrace = {}
        self.count_rate = {} #[Hz]
        self.decay_hist = {}
        self.active_decay_hist = {}
        self.inactive_decay_hist = {}
        self.active_decay_hist_subtracted = {}
        
        # self.calculate_stat_filter = self.timed(self.calculate_stat_filter)
        # self.weight_filtering_chunk = self.timed(self.weight_filtering_chunk)
        # self.prepare_for_corr = self.timed(self.prepare_for_corr)
        # self.make_log_grid_ms = self.timed(self.make_log_grid_ms)
        # self.rebin_tau_to_grid = self.timed(self.rebin_tau_to_grid)
        # self.rebin_chunk_to_grid = self.timed(self.rebin_chunk_to_grid)
        # self.rebin_to_grid = self.timed(self.rebin_to_grid)
        # self.correlate_chunk = self.timed(self.correlate_chunk)
        # self._compute_MEAN_STD = self.timed(self._compute_MEAN_STD)
        # self._CORRELATE = self.timed(self._CORRELATE)
        if file == None and time_bin == None:
            pass

        else:
            self.calculate_photons = self.timed(self.calculate_photons)
            self.Photons_occurence = self.timed(self.Photons_occurence)
            self.bin_time_data = self.timed(self.bin_time_data)
            self.calculate_count_rate = self.timed(self.calculate_count_rate)
            self.calculate_decays = self.timed(self.calculate_decays)

            
            self.PHOTONS, self.tau_resolution = self.calculate_photons()
            self.occurence = self.Photons_occurence(self.PHOTONS)
            self.timetrace = self.bin_time_data(self.PHOTONS,self.time_bin,self.occurence)
            self.count_rate = self.calculate_count_rate(self.PHOTONS,self.timetrace,self.time_bin)
            self.decay_hist =  self.calculate_decays(self.PHOTONS,[])
            self.active_decay_hist =self.decay_hist.copy()
            self.inactive_decay_hist_L=self.decay_hist.copy()
            self.inactive_decay_hist_U=self.decay_hist.copy()
            self.active_decay_hist_subtracted={k:pd.DataFrame(columns=['decay_time','counts']) for k in self.active_decay_hist.keys()}
    

    def timed(self, func):
        enabled = False#True#self.basf.ENABLE_TIMING
        # cwd = os.getcwd()
        # tfile = os.path.join(cwd,self.basf.TIMING_FILE)
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled:
                return func(*args, **kwargs)
    
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            hostname = socket.gethostname()
    
            print(f"[{hostname}] {func.__qualname__} took {duration:.4f}s")
            return result

        return wrapper
    
    def calculate_photons(self):
        PHOTS = {}
        self.fcs_data = self.load_data(self.file)
        PHOTS, TAU_RES = self.extract_photons(self.fcs_data)
        return PHOTS, TAU_RES

    @staticmethod
    def _unpack_phconvert_result(result):
        """Normalize return values from supported phconvert versions."""
        if len(result) == 5:
            timestamps, detectors, nanotimes, metadata, marker_ids = result
        elif len(result) == 4:
            timestamps, detectors, nanotimes, metadata = result
            marker_ids = np.empty(0, dtype=np.uint8)
        else:
            raise ValueError(
                f"Unexpected phconvert result containing {len(result)} values."
            )
        return timestamps, detectors, nanotimes, metadata, marker_ids

    def load_data(self, file):
        """Load PicoQuant PTU or PT3 TTTR events with phconvert."""
        if load_ptu is None or load_pt3 is None:
            raise RuntimeError(
                "PTU/PT3 support requires phconvert. Install it from the "
                "FcsIT dependency update dialog and restart FcsIT."
            )
        suffix = Path(file).suffix.lower()
        if suffix == '.ptu':
            result = load_ptu(file, return_marker=True, ovcfunc='base')
        elif suffix == '.pt3':
            result = load_pt3(file)
        else:
            raise ValueError(
                f"Unsupported file type {suffix!r}; expected .ptu or .pt3."
            )

        timestamps, detectors, nanotimes, metadata, marker_ids = \
            self._unpack_phconvert_result(result)
        timestamps = np.asarray(timestamps, dtype=np.uint64)
        detectors = np.asarray(detectors)
        marker_ids = np.asarray(marker_ids)

        photon_mask = ~np.isin(detectors, marker_ids)
        if suffix == '.pt3':
            photon_mask &= detectors != 15
        timestamps = timestamps[photon_mask]
        detectors = detectors[photon_mask]

        if nanotimes is None:
            nanotimes = np.zeros(timestamps.size, dtype=np.uint16)
            tau_resolution = 0.0
            mode = 'CW'
        else:
            nanotimes = np.asarray(nanotimes, dtype=np.uint16)[photon_mask]
            tau_resolution = float(
                np.asarray(metadata['nanotimes_unit']).reshape(-1)[0]
            )
            mode = 'Standard'

        detector_ids = np.unique(detectors)
        normalized_detectors = np.empty(detectors.shape, dtype=np.uint8)
        for normalized_id, detector_id in enumerate(detector_ids):
            normalized_detectors[detectors == detector_id] = normalized_id

        global_resolution = float(
            np.asarray(metadata['timestamps_unit']).reshape(-1)[0]
        )
        repetition_rate = metadata.get(
            'laser_repetition_rate', 1.0 / global_resolution
        )
        sync_rate = int(round(float(np.asarray(repetition_rate).reshape(-1)[0])))
        special = np.zeros(timestamps.size, dtype=np.uint8)
        header_variables = [
            tau_resolution, global_resolution, 0, sync_rate, mode
        ]
        self.TTTR_Mode = mode
        return (
            timestamps, nanotimes, normalized_detectors, special,
            header_variables,
        )
        
        
        
    def extract_photons(self,FCSDATA):
        # print(FCSDATA)
        subMode = int(FCSDATA[4][2])
        tau_resolution = FCSDATA[4][0]*1e9 # //ns
        GlobalResolution = FCSDATA[4][1]
        sync_Rate = int(FCSDATA[4][3])
        mode = FCSDATA[4][4]
        channels = np.unique(FCSDATA[2])
        Photons ={}
        for chan in channels:
            indices = np.asarray(FCSDATA[2]==chan)
            SYNC = np.delete(FCSDATA[0],(~indices).nonzero())
            TCSPC = np.delete(FCSDATA[1],(~indices).nonzero())
            SPECIAL = np.delete(FCSDATA[3],(~indices).nonzero())
            marker_indices = np.asarray(SPECIAL!=0)
            SYNC = np.delete(SYNC,(marker_indices).nonzero())
            TCSPC = np.delete(TCSPC,(marker_indices).nonzero())
            SPECIAL = np.delete(SPECIAL,(marker_indices).nonzero())
            if np.unique(SPECIAL).size==0:
                continue
            else:
                Photons['channel_'+str(chan)] = {'sync':SYNC,
                                                 'tcspc':TCSPC,
                                                 'exact_time':SYNC/sync_Rate+TCSPC*tau_resolution*1e-9
                                                 }
                Photons['tau_resolution'] = tau_resolution
                Photons['sync_Rate'] = sync_Rate
                Photons['GlobalResolution'] = GlobalResolution
                Photons['Mode'] = mode
        return Photons,tau_resolution
    
    def Photons_occurence(self, PHOTS):
        channels = [ch for ch in PHOTS.keys() if ch.startswith('channel_')]
        occur = {}
    
        global_resolution = PHOTS['GlobalResolution']
    
        for ch in channels:
            time = PHOTS[ch]['sync'].astype(np.float64) * global_resolution * 1e9
    
            occur[ch] = {
                'time': time,
                'number': np.ones(time.size),
                'weights': np.ones(time.size),
                'mx': int(np.ceil(time.max()))
            }
    
        return occur


    def bin_time_data(self, PHOTS, tb, OCCUR):
        channels = [ch for ch in PHOTS.keys() if ch.startswith('channel_')]
        trace = {}
        delta_t_ns = int(round(tb * 1e9))
        for ch in channels:
            # print(OCCUR[ch]['time'])
            t_ns = np.floor(OCCUR[ch]['time'] + 0.5).astype(np.int64)
            offset = t_ns.min()
            bins_idx = (t_ns - offset) // delta_t_ns
            
            counts = np.bincount(bins_idx, minlength=bins_idx.max() + 1)
            time_axis = (offset + np.arange(counts.size, dtype=np.int64) * delta_t_ns).astype(np.float64)
            trace[ch] = pd.DataFrame({
                'time_interval': time_axis,
                'occurrences': counts
            })
            # print(trace[ch])
            # print('offset',offset)
            # print('bins_idx',bins_idx)
            # print('counts',counts)
        return trace

            
    def calculate_count_rate(self, PHOTS, TT, tb, drop_leading_zeros=False):
        channels = [ch for ch in PHOTS.keys() if ch.startswith('channel_')]
        cntr = {}
    
        dt_ns = int(round(tb * 1e9))
        dt_s = dt_ns * 1e-9
    
        for ch in channels:
            counts = TT[ch]['occurrences'].to_numpy().astype(np.float64)
    
            if counts.size == 0 or counts.sum() == 0:
                cntr[ch] = [0.0, 0.0]
                continue
    
            if drop_leading_zeros:
                first_nonzero = np.argmax(counts > 0)
                counts = counts[first_nonzero:]
    
            total_counts = counts.sum()
            total_time_s = counts.size * dt_s
    
            if total_time_s <= 0:
                cntr[ch] = [0.0, 0.0]
                continue
    
            r_hat = total_counts / total_time_s
            se_r = np.sqrt(total_counts) / total_time_s
    
            cntr[ch] = [float(r_hat), float(se_r)]
    
        return cntr




    def calculate_chunk_count_rate(self,DF):
        def lin_fit(x,slope):
            return slope*x
        fit_model = Model(lin_fit)
        df=DF.copy()
        df.reset_index(drop=True,inplace=True)
        xdata = df.time_interval.values*1e-9
        xdata=xdata-xdata[0]
        ydata = df.occurrences.cumsum().values
        fit_results = fit_model.fit(ydata,x=xdata,slope=1)
        params = fit_results.params
        cntr=[params['slope'].value,params['slope'].stderr]
        return cntr
    

    def calculate_decays(self, PHOTS, time_indices=None):
        
        channels = [ch for ch in PHOTS.keys() if ch.startswith('channel_')]
        decays = {}
        if self.TTTR_Mode != 'CW':
            tau_res = self.tau_resolution
            def _select_idx(j, ch):
                if time_indices is None:
                    return None
                if isinstance(time_indices, (list, tuple)) and len(time_indices) == 0:
                    return None
                if isinstance(time_indices, dict):
                    return time_indices.get(ch, None)
                if isinstance(time_indices, (list, tuple)):
                    return time_indices[j] if j < len(time_indices) else None
                return None
    
            for j, ch in enumerate(channels):
                tc_all = PHOTS[ch]['tcspc']
                idx = _select_idx(j, ch)
                tc = tc_all[idx] if idx is not None else tc_all
                if tc.size == 0:
                    decays[ch] = pd.DataFrame({'decay_time': np.array([], dtype=float),
                                               'counts': np.array([], dtype=int)})
                    continue
    
                m = int(tc.max()) + 1
                hist = np.bincount(tc, minlength=m)
                nz = np.nonzero(hist)[0]
                counts = hist[nz]
                decay_time = nz * tau_res 
                decays[ch] = pd.DataFrame({'decay_time': decay_time, 'counts': counts})

        return decays

    
    # def calculate_stat_filter(self,Pure_components_dict,raw_signal,rawx):
    #     pure_components = []
    #     for c in Pure_components_dict.keys():
    #         pure_components.append(Pure_components_dict[c])
    #     M = np.concatenate(pure_components).reshape((len(pure_components),
    #                                                  len(pure_components[-1]))).T
    #     I = raw_signal
    #     diagI=np.diag(I)
    #     try:
    #         DET = det(diagI)
    #     except:
    #         DET = 0
    #     if np.isclose(DET, 0.0, atol=1e-12) or np.isinf(DET):
    #         invdiag = pinv(diagI)
    #     else:
    #         invdiag = inv(diagI)

    #     A = np.dot(np.dot(M.T,invdiag),M)
    #     if  np.isclose(det(A), 0.0, atol=1e-12):
    #         F = np.dot(pinv(A), np.dot(M.T, invdiag))
    #     else:
    #         F = np.dot(inv(A), np.dot(M.T, invdiag))

    #     FILTERS_dict = {}
    #     for i,c in enumerate(Pure_components_dict.keys()):
    #         FILTERS_dict[c]=F[i]
    #     FILTERS_dict1 = {}  
    #     for F_name in FILTERS_dict.keys():
    #         F = FILTERS_dict[F_name]
    #         F = F/np.max(F)
    #         FILTERS_dict1[F_name] = F
    #     FILTERS_dict1['tcscp']=(rawx/self.tau_resolution).astype(int)
    #     return FILTERS_dict1


    def calculate_stat_filter(self, Pure_components_dict, raw_signal, rawx, atol=1e-12):
        keys = list(Pure_components_dict.keys())
    
        # M: (N, K) — kolumny to p^{(k)} (TCSPC patterns)
        comps = np.asarray([Pure_components_dict[k] for k in keys], dtype=float)  # (K, N)
        M = comps.T  # (N, K)
    
        # I: (N,)
        I = np.asarray(raw_signal, dtype=float)
    
        # diag(I)^{-1} jako wektor (dokładnie równoważne inv/pinv dla diagonali)
        invI = np.zeros_like(I)
        good = np.isfinite(I) & (np.abs(I) > atol)
        invI[good] = 1.0 / I[good]   # dla zer zostaje 0 -> jak pinv(diag(I))
    
        # A = M^T diag(I)^{-1} M
        MW  = M * invI[:, None]      # diag(I)^{-1} M
        A   = M.T @ MW
    
        # F = A^{-1} M^T diag(I)^{-1}
        RHS = MW.T                   # = M^T diag(I)^{-1}
    
        # solve jest matematycznie równoważne inv(A)@RHS (w arytmetyce dokładnej)
        try:
            F = np.linalg.solve(A, RHS)
        except np.linalg.LinAlgError:
            F = np.linalg.pinv(A) @ RHS
    
        out = {k: F[i] for i, k in enumerate(keys)}
        out["tcscp"] = (np.asarray(rawx) / self.tau_resolution).astype(np.int64)
        return out

    def weight_filtering_chunk(self,chnk,meta):

        sig_f={'t':{},
               'w':{}}
        channels = [k for k in self.PHOTONS.keys() if k.startswith('channel_')]

        is_cw = self.PHOTONS['Mode'] == 'CW'
        
        for ch in channels:
            if ch=='channel_0':
                chn = 'ch1'
            elif ch=='channel_1':
                chn = 'ch2'
            # chkrng  = meta['TT info']['chunks'][chnk]['tcspc'][chn]
            # if is_cw:
            #     chkrng = meta['TT info']['chunks'][chnk]['photon'][chn]
            # else:
            chkrng = meta['TT info']['chunks'][chnk]['tcspc'][chn]
            chunk_ind = np.arange(chkrng[0],chkrng[1])
            sig_f['t'][ch] = ((self.PHOTONS[ch]['sync'][chunk_ind]*self.PHOTONS['GlobalResolution'])*1e9)
            # sig_f['t'][ch] = ((self.PHOTONS[ch]['sync'][chunk_ind]/self.PHOTONS['sync_Rate'])*10**(9))
            sig_f['w'][ch] = np.ones(sig_f['t'][ch].size)
            if not is_cw:
                tscpc = self.PHOTONS[ch]['tcspc'][chunk_ind]
        
                filters = meta.get('TCSPC info', {}).get('Filters', {}).get(ch, {})
                tcspc_filter = filters.get('tcscp', [])
                filter_data = filters.get('Data', [])
        
                for i, tch in enumerate(tcspc_filter):
                    findex = np.where(tscpc == tch)[0]
                    sig_f['w'][ch][findex] = filter_data[i]
        return sig_f

    def prepare_for_corr(self, sig_f):
        channels = [k for k in self.PHOTONS.keys() if k.startswith('channel_')]
        if len(channels) == 1:
            t_ch_0 = sig_f['t'][channels[0]]
            t_ch_1 = np.array([])
            num_ch_0 = np.ones(t_ch_0.size)
            num_ch_1 = np.array([])
            w_ch_0 = sig_f['w'][channels[0]]
            w_ch_1 = np.array([])
        else:  
            t_ch_0 = sig_f['t'][channels[0]]
            t_ch_1 = sig_f['t'][channels[1]]
            num_ch_0 = np.ones(t_ch_0.size)
            num_ch_1 = np.zeros(t_ch_1.size)
            w_ch_0 = sig_f['w'][channels[0]]
            w_ch_1 = sig_f['w'][channels[1]]
    
        time = np.hstack((t_ch_0, t_ch_1))
        idx = np.argsort(time, kind="stable")   # stabilne sortowanie
        time = time[idx]
        num = np.hstack((num_ch_0, num_ch_1))[idx]
        wgh = np.hstack((w_ch_0, w_ch_1))[idx]
        num = np.hstack((num.reshape(-1, 1), np.zeros(len(num)).reshape(-1, 1)))
        num[:, 1] = (~num[:, 0].astype(bool)).astype(int)
        num[:, 0] = num[:, 0] * wgh
        num[:, 1] = num[:, 1] * wgh
        return time, num


    def make_log_grid_ms(self,tmin_ms, tmax_ms, points_per_decade=8):
        tmin = float(tmin_ms); tmax = float(tmax_ms)
        n = int(np.ceil(points_per_decade * (np.log10(tmax) - np.log10(tmin))))
        n = max(n, 2)
        centers = np.logspace(np.log10(tmin), np.log10(tmax), n)
        edges = np.sqrt(centers[:-1] * centers[1:])
        edges = np.concatenate([[centers[0]/np.sqrt(10)], edges, [centers[-1]*np.sqrt(10)]])
        return centers, edges
    
    def rebin_tau_to_grid(self,tau,centers_ms, edges_ms):
        idx = np.digitize(tau, edges_ms) - 1
        out_tau = []
        for b in range(len(centers_ms)):
            m = (idx == b)
            if not np.any(m):
                continue
            out_tau.append(centers_ms[b])
        return np.array(out_tau)
    
    def rebin_chunk_to_grid(self,tau,G, centers_ms, edges_ms):
        idx = np.digitize(tau, edges_ms) - 1
        out_G = []
        for b in range(len(centers_ms)):
            m = (idx == b)
            if not np.any(m):
                continue
            Gw = np.mean(G[m])
            out_G.append(Gw)
        return np.array(out_G)

    
    def rebin_to_grid(self,df, centers_ms, edges_ms):
        tau = df['time'].to_numpy()
        G   = df['MEAN'].to_numpy()
        SD  = df['STD'].to_numpy()
        eps = np.nanmedian(SD[SD>0]) if np.any(SD>0) else 1.0
        SD  = np.where(SD>0, SD, eps)
        idx = np.digitize(tau, edges_ms) - 1  
        out_tau, out_G, out_SD = [], [], []
        for b in range(len(centers_ms)):
            m = (idx == b)
            if not np.any(m):
                continue
            w = 1.0 / (SD[m]**2)
            Gw = np.average(G[m], weights=w)
            sd_comb = 1.0 / np.sqrt(np.sum(w)) 
            out_tau.append(centers_ms[b])
            out_G.append(Gw)
            out_SD.append(sd_comb)
        DF = pd.DataFrame({'time': np.array(out_tau),
                             'MEAN': np.array(out_G),
                             'STD':  np.array(out_SD)})
        DF['STD'] = DF['STD'].rolling(window=3, center=True).mean()
        DF.dropna(inplace=True)
        return DF

    
    def correlate_chunk(self, t, num, nsub, npoints, tau_min, tau_max):
        autocorr, autotime = tttr2xfcs(t, num, 0, npoints, nsub, tau_min, tau_max)
        # autocorr, autotime = tttr2xfcs_numba(t, num, 0, npoints, nsub, tau_min, tau_max)

        # auto_old, tau_old = tttr2xfcs(t, num, 0, npoints, nsub, tau_min, tau_max)
        # auto_new, tau_new = tttr2xfcs_numba(t, num, 0, npoints, nsub, tau_min, tau_max)
        
        # print('allclose',np.allclose(tau_old, tau_new, rtol=1e-12, atol=1e-12))
        # print(np.nanmax(np.abs(auto_old - auto_new)))
        # print(np.nanmax(np.abs(auto_old - auto_new) / (np.abs(auto_old) + 1e-12)))

        
        T = float(np.max(t) - np.min(t))      # dokładny czas, bez ceil/floor
        count0 = float(np.sum(num[:, 0]))
        count1 = float(np.sum(num[:, 1]))
        autoNorm = np.zeros_like(autocorr, dtype=float)
        if count0 > 0:
            autoNorm[:, 0, 0] = (autocorr[:, 0, 0] * T) / (count0 * count0) - 1.0
        if count1 > 0:
            autoNorm[:, 1, 1] = (autocorr[:, 1, 1] * T) / (count1 * count1) - 1.0
        if (count0 > 0) and (count1 > 0):
            autoNorm[:, 0, 1] = (autocorr[:, 0, 1] * T) / (count0 * count1) - 1.0
            autoNorm[:, 1, 0] = (autocorr[:, 1, 0] * T) / (count1 * count0) - 1.0
        tau = np.asarray(autotime, dtype=float)   # już 1D i w sekundach po poprawce w tttr2xfcs
        return tau, autoNorm



    def _compute_MEAN_STD(self, df, cols, tau_col='time',
                          n_bootstrap=5001, block_size=3,
                          random_state=None,
                          chunk_lengths_sec=None,
                          bin_width_col=None):
        rng = np.random.default_rng(random_state)
        M = len(cols)
        if M == 0:
            nan_series = pd.Series(np.nan, index=df.index, name='MEAN')
            return nan_series, nan_series.rename('SE'), np.empty((0, 0)), np.empty((0, 0), dtype=int)
        if M == 1:
            mean_series = df[cols[0]].rename('MEAN')
            std_series  = pd.Series(0.0, index=df.index, name='SE')
            covariance = np.zeros((len(df), len(df)), dtype=float)
            return mean_series, std_series, covariance, np.ones_like(covariance, dtype=int)
        X   = df[cols].to_numpy(float)   
        tau = df[tau_col].to_numpy(float)
        Tn  = len(tau)
        if bin_width_col is not None:
            dtaus = df[bin_width_col].to_numpy(float)
        else:
            dtaus = np.empty(Tn, float)
            if Tn == 1:
                dtaus[:] = max(tau[0], 1e-12)
            else:
                dtaus[1:-1] = 0.5 * (tau[2:] - tau[:-2])
                dtaus[0]    = tau[1] - tau[0]
                dtaus[-1]   = tau[-1] - tau[-2]
            dtaus = np.clip(dtaus, 1e-12, None)
        if chunk_lengths_sec is None:
            tau_max = float(np.nanmax(tau))
            T_i = np.full(M, 2.0 * tau_max, dtype=float)
        else:
            T_i = np.asarray(chunk_lengths_sec, dtype=float)
        T_grid  = np.broadcast_to(T_i, (Tn, M))
        Ki = np.floor((T_grid - tau[:, None]) / dtaus[:, None])
        Ki = np.where(Ki > 0, Ki, 0.0)
        Ki_eps = np.where(Ki > 0, Ki, 0.0)
        n_blocks = int(np.ceil(M / block_size))
        start_idx = rng.integers(0, M, size=(n_bootstrap, n_blocks))
        offs = np.arange(block_size)[None, None, :]
        block_idx = (start_idx[..., None] + offs).reshape(n_bootstrap, -1) % M
        block_idx = block_idx[:, :M]   
        B = n_bootstrap
        std_boot = np.empty(Tn, float)
        boot_mean_avg = np.empty(Tn, float)
        bootstrap_curves = np.full((B, Tn), np.nan, dtype=float)
        for i in range(Tn):
            if np.all(Ki_eps[i, :] <= 0):
                boot_mean_avg[i] = np.nan
                std_boot[i] = np.nan
                continue
            
            vals = np.take_along_axis(
                X[i, :][None, :].repeat(B, 0), 
                block_idx,
                axis=1
            ) 
    
            wts = np.take_along_axis(
                Ki_eps[i, :][None, :].repeat(B, 0),
                block_idx,
                axis=1
            )  

            if np.all(Ki_eps[i, :] <= 0):
                boot_mean_avg[i] = np.nan
                std_boot[i] = np.nan
                continue
            finite0 = np.isfinite(vals)
            wts_eff  = np.where(finite0, wts, 0.0)
            vals_eff = np.where(finite0, vals, 0.0)    
            Wsum = wts_eff.sum(axis=1)               
            num  = (vals_eff * wts_eff).sum(axis=1)  
            boot_mean = np.full(B, np.nan, dtype=float)
            pos = (Wsum > 0)
            boot_mean[pos] = num[pos] / Wsum[pos]
            if np.any(~pos):
                vals_sub = vals[~pos]
                fin_sub  = np.isfinite(vals_sub)
                sum_u = np.where(fin_sub, vals_sub, 0.0).sum(axis=1)
                cnt_u = fin_sub.sum(axis=1).astype(float)
                out = np.full_like(cnt_u, np.nan, dtype=float)
                np.divide(sum_u, cnt_u, out=out, where=(cnt_u > 0))
                boot_mean[~pos] = out
    
            bm = boot_mean[np.isfinite(boot_mean)]
            if bm.size == 0:
                boot_mean_avg[i] = np.nan
                std_boot[i] = np.nan
            elif bm.size == 1:
                boot_mean_avg[i] = bm[0]
                std_boot[i] = 0.0
            else:
                boot_mean_avg[i] = bm.mean()
                std_boot[i] = bm.std(ddof=1)
            bootstrap_curves[:, i] = boot_mean
    
        finite = np.isfinite(std_boot)
        if not np.all(finite):
            med = np.nanmedian(std_boot[finite]) if np.any(finite) else 0.0
            std_boot = np.where(finite, std_boot, med)
    
        mean_series = pd.Series(boot_mean_avg, index=df.index, name='MEAN')
        std_series  = pd.Series(std_boot,      index=df.index, name='SE')
    
        covariance, valid_counts = _bootstrap_covariance(bootstrap_curves)
        return mean_series, std_series, covariance, valid_counts


    def _CORRELATE(self,chunks,nsub,npoints,tau_min,tau_max,meta,sender):
        t_total = time.perf_counter()
        t_filter = 0.0
        t_prepare = 0.0
        t_tttr = 0.0
        t_rebin = 0.0
        t_mean = 0.0
        t_df = 0.0
        DictOfChunks = {}
        # _AUTOTIME = []
        # _AUTONORM = []
        # _ChunkLength = []
        t0 = time.perf_counter()
        centers, edges = self.make_log_grid_ms(tmin_ms=tau_min, tmax_ms=tau_max, points_per_decade=nsub)
        window=0.3*nsub
        t_df += time.perf_counter() - t0

        label0 = dpg.get_item_label(sender) if sender is not None else "Correlation"

        max_workers = min(len(chunks), os.cpu_count() or 1)
        results = [None] * len(chunks)
        t_parallel_wait0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [
                ex.submit(
                    self._correlate_single_chunk_worker,
                    i,
                    chnk,
                    meta,
                    nsub,
                    npoints,
                    tau_min,
                    tau_max,
                )
                for i, chnk in enumerate(chunks)
            ]
        
            total_chunks = len(futures)
        
            for done, fut in enumerate(as_completed(futures), start=1):
                i, autotime, autoNorm, chunklength,tf, tp, tt = fut.result()
                results[i] = (autotime, autoNorm, chunklength)
                t_filter += tf
                t_prepare += tp
                t_tttr += tt
                if sender is not None:
                    dpg.set_item_label(
                        sender,
                        f"{label0} | calculated {done}/{total_chunks} chunks"
                    )
        t_parallel_wall = time.perf_counter() - t_parallel_wait0
        _AUTOTIME = [r[0] for r in results]
        _AUTONORM = [r[1] for r in results]
        _ChunkLength = [r[2] for r in results]

        
        t0 = time.perf_counter()
        min_len = min(len(t) for t in _AUTOTIME)
        _AUTOTIME = [t[:min_len] for t in _AUTOTIME]
        _AUTONORM = [a[:min_len] for a in _AUTONORM]
        rebinedTime = self.rebin_tau_to_grid( _AUTOTIME[0], centers, edges)
        autoNorm_ch_1 = pd.DataFrame(rebinedTime,columns=['time'])
        autoNorm_ch_2 = pd.DataFrame(rebinedTime,columns=['time'])
        CrossNorm_ch_1 = pd.DataFrame(rebinedTime,columns=['time'])
        CrossNorm_ch_2 = pd.DataFrame(rebinedTime,columns=['time'])
        t_df += time.perf_counter() - t0
        t0 = time.perf_counter()
        # chan = list(meta['TCSPC info']['Filters'].keys())[0]
        for i,chunk in enumerate(_AUTONORM):
            # if chan.endswith('_0'):
                
            autoNorm_ch_1['ACF_chunk_'+str(i)]=self.rebin_chunk_to_grid(_AUTOTIME[0],chunk[:,0,0], centers, edges)
            autoNorm_ch_2['ACF_chunk_'+str(i)]=self.rebin_chunk_to_grid(_AUTOTIME[0],chunk[:,1,1], centers, edges)
            CrossNorm_ch_1['CCF_chunk_'+str(i)]=self.rebin_chunk_to_grid(_AUTOTIME[0],chunk[:,0,1], centers, edges)
            CrossNorm_ch_2['CCF_chunk_'+str(i)]=self.rebin_chunk_to_grid(_AUTOTIME[0],chunk[:,1,0], centers, edges)
        t_rebin += time.perf_counter() - t0
        t0 = time.perf_counter()
        ChunkedCorrelationCurves_channel_1 = [autoNorm_ch_1,CrossNorm_ch_1]
        ChunkedCorrelationCurves_channel_2 = [autoNorm_ch_2,CrossNorm_ch_2]
        for i,correlation_curves in enumerate(ChunkedCorrelationCurves_channel_1):
            curves_df = correlation_curves.copy()
            curves_df=curves_df.where(curves_df!=0).dropna()
            if len(curves_df)==0:
                ChunkedCorrelationCurves_channel_1[i]=None
        for i,correlation_curves in enumerate(ChunkedCorrelationCurves_channel_2):
            curves_df = correlation_curves.copy()
            curves_df=curves_df.where(curves_df!=0).dropna()
            if len(curves_df)==0:
                ChunkedCorrelationCurves_channel_2[i]=None
            
        DictOfChunks['Channel_0'] = {'ACF_1':ChunkedCorrelationCurves_channel_1[0],
                                             'CCF_1':ChunkedCorrelationCurves_channel_1[1]
                                             }
        DictOfChunks['Channel_1'] = {'ACF_2':ChunkedCorrelationCurves_channel_2[0],
                                             'CCF_2':ChunkedCorrelationCurves_channel_2[1]
                                             }
        t0 = time.perf_counter()
        cols_ch_1 = [col for col in autoNorm_ch_1.columns if col.startswith('ACF_chunk_')]
        cols_ch_2 = [col for col in autoNorm_ch_2.columns if col.startswith('ACF_chunk_')]
        ccols_ch_1 = [col for col in CrossNorm_ch_1.columns if col.startswith('CCF_chunk_')]
        ccols_ch_2 = [col for col in CrossNorm_ch_2.columns if col.startswith('CCF_chunk_')]
        if len(cols_ch_1) ==1:
            autoNorm_ch_1['MEAN'] = autoNorm_ch_1[[col for col in autoNorm_ch_1.columns if col.startswith('ACF_chunk_')][0]]
            CrossNorm_ch_1['MEAN']=CrossNorm_ch_1[[col for col in CrossNorm_ch_1.columns if col.startswith('CCF_chunk_')][0]]
        else:
            # auto_ch1 = self._compute_MEAN_STD(autoNorm_ch_1, cols_ch_1,chunk_lengths_sec=_ChunkLength)
            # Cross_ch1 =  self._compute_MEAN_STD(CrossNorm_ch_1, ccols_ch_1,chunk_lengths_sec=_ChunkLength)
            auto_ch1 = self._compute_MEAN_STD_numba(autoNorm_ch_1, cols_ch_1,chunk_lengths_sec=_ChunkLength)
            Cross_ch1 =  self._compute_MEAN_STD_numba(CrossNorm_ch_1, ccols_ch_1,chunk_lengths_sec=_ChunkLength)
            # print(auto_ch1[0].head(),auto_ch1[1].head())
            # print(auto_ch1_[0].head(),auto_ch1_[1].head())
            autoNorm_ch_1['MEAN'] = auto_ch1[0]
            autoNorm_ch_1['SE'] = auto_ch1[1]
            CrossNorm_ch_1['MEAN'] = Cross_ch1[0]
            CrossNorm_ch_1['SE'] = Cross_ch1[1]
            DictOfChunks['Channel_0']['ACF_1_covariance'] = auto_ch1[2]
            DictOfChunks['Channel_0']['CCF_1_covariance'] = Cross_ch1[2]
            _attach_lag_covariance(
                DictOfChunks['Channel_0']['ACF_1'], auto_ch1,
                autoNorm_ch_1['time'].to_numpy(),
            )
            _attach_lag_covariance(
                DictOfChunks['Channel_0']['CCF_1'], Cross_ch1,
                CrossNorm_ch_1['time'].to_numpy(),
            )
        if len(cols_ch_2) ==1:
            autoNorm_ch_2['MEAN'] = autoNorm_ch_2[[col for col in autoNorm_ch_2.columns if col.startswith('ACF_chunk_')][0]]
            CrossNorm_ch_2['MEAN']=CrossNorm_ch_2[[col for col in CrossNorm_ch_2.columns if col.startswith('CCF_chunk_')][0]]
        else:
            # auto_ch2 = self._compute_MEAN_STD(autoNorm_ch_2, cols_ch_2,chunk_lengths_sec=_ChunkLength)
            # Cross_ch2 =  self._compute_MEAN_STD(CrossNorm_ch_2, ccols_ch_2,chunk_lengths_sec=_ChunkLength)
            auto_ch2 = self._compute_MEAN_STD_numba(autoNorm_ch_2, cols_ch_2,chunk_lengths_sec=_ChunkLength)
            Cross_ch2 =  self._compute_MEAN_STD_numba(CrossNorm_ch_2, ccols_ch_2,chunk_lengths_sec=_ChunkLength)
            autoNorm_ch_2['MEAN'] = auto_ch2[0]
            autoNorm_ch_2['SE'] = auto_ch2[1]
            CrossNorm_ch_2['MEAN'] = Cross_ch2[0]
            CrossNorm_ch_2['SE'] = Cross_ch2[1]
            DictOfChunks['Channel_1']['ACF_2_covariance'] = auto_ch2[2]
            DictOfChunks['Channel_1']['CCF_2_covariance'] = Cross_ch2[2]
            _attach_lag_covariance(
                DictOfChunks['Channel_1']['ACF_2'], auto_ch2,
                autoNorm_ch_2['time'].to_numpy(),
            )
            _attach_lag_covariance(
                DictOfChunks['Channel_1']['CCF_2'], Cross_ch2,
                CrossNorm_ch_2['time'].to_numpy(),
            )
        t_mean += time.perf_counter() - t0
        autoNorm_ch_1 = autoNorm_ch_1[['time','MEAN','SE']]
        autoNorm_ch_2 = autoNorm_ch_2[['time','MEAN','SE']]
        CrossNorm_ch_1 = CrossNorm_ch_1[['time','MEAN','SE']]
        CrossNorm_ch_2 = CrossNorm_ch_2[['time','MEAN','SE']]

        return autoNorm_ch_1,autoNorm_ch_2,CrossNorm_ch_1,CrossNorm_ch_2,DictOfChunks

    
    ############################################################################################
    ######## NUMBA bootstrap                                                          ##########
    ############################################################################################


    def _compute_MEAN_STD_numba(
        self,
        df,
        cols,
        tau_col='time',
        n_bootstrap=5001,
        block_size=3,
        random_state=None,
        chunk_lengths_sec=None,
        bin_width_col=None,
    ):
        M = len(cols)
    
        if M == 0:
            nan_series = pd.Series(np.nan, index=df.index, name='MEAN')
            return nan_series, nan_series.rename('SE'), np.empty((0, 0)), np.empty((0, 0), dtype=int)
    
        if M == 1:
            mean_series = df[cols[0]].rename('MEAN')
            std_series = pd.Series(0.0, index=df.index, name='SE')
            covariance = np.zeros((len(df), len(df)), dtype=float)
            return mean_series, std_series, covariance, np.ones_like(covariance, dtype=int)
    
        X = df[cols].to_numpy(dtype=np.float64)
        tau = df[tau_col].to_numpy(dtype=np.float64)
        Tn = tau.shape[0]
    
        if bin_width_col is not None:
            dtaus = df[bin_width_col].to_numpy(dtype=np.float64)
        else:
            dtaus = np.empty(Tn, dtype=np.float64)
    
            if Tn == 1:
                dtaus[0] = max(tau[0], 1e-12)
            else:
                dtaus[1:-1] = 0.5 * (tau[2:] - tau[:-2])
                dtaus[0] = tau[1] - tau[0]
                dtaus[-1] = tau[-1] - tau[-2]
    
            dtaus = np.clip(dtaus, 1e-12, None)
    
        if chunk_lengths_sec is None:
            tau_max = float(np.nanmax(tau))
            T_i = np.full(M, 2.0 * tau_max, dtype=np.float64)
        else:
            T_i = np.asarray(chunk_lengths_sec, dtype=np.float64)
    
            if T_i.shape[0] != M:
                raise ValueError(
                    f"chunk_lengths_sec has length {T_i.shape[0]}, "
                    f"but {M} chunk columns were provided."
                )
    
        Ki = np.floor((T_i[None, :] - tau[:, None]) / dtaus[:, None])
        Ki_eps = np.where(Ki > 0.0, Ki, 0.0).astype(np.float64, copy=False)
    
        seed = 0 if random_state is None else int(random_state)
    
        block_idx = _fcs_build_block_idx_numba(
            M,
            int(n_bootstrap),
            int(block_size),
            seed,
        )
    
        boot_mean_avg, std_boot, bootstrap_curves = _fcs_compute_mean_std_kernel_numba(
            X,
            Ki_eps,
            block_idx,
        )
    
        finite = np.isfinite(std_boot)
        if not np.all(finite):
            med = np.nanmedian(std_boot[finite]) if np.any(finite) else 0.0
            std_boot = np.where(finite, std_boot, med)
    
        mean_series = pd.Series(boot_mean_avg, index=df.index, name='MEAN')
        std_series = pd.Series(std_boot, index=df.index, name='SE')
    
        covariance, valid_counts = _bootstrap_covariance(bootstrap_curves)
        return mean_series, std_series, covariance, valid_counts




    def _correlate_single_chunk_worker(
        self,
        i,
        chnk,
        meta,
        nsub,
        npoints,
        tau_min,
        tau_max,
    ):
        t0 = time.perf_counter()
        sg = self.weight_filtering_chunk(chnk, meta)
        time_arr, num = self.prepare_for_corr(sg)
        t_filter = time.perf_counter() - t0

        t0 = time.perf_counter()
        chunklength = (time_arr[-1] - time_arr[0]) / 1_000_000.0
        t_prepare = time.perf_counter() - t0

        t0 = time.perf_counter()
        autotime, autoNorm = self.correlate_chunk(
            time_arr,
            num,
            nsub,
            npoints,
            tau_min,
            tau_max,
        )

        

        
        t_tttr = time.perf_counter() - t0
        return i, autotime, autoNorm, chunklength, t_filter, t_prepare, t_tttr
