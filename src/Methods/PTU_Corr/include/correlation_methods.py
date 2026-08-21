import numpy as np
"""
This file is a modified version of the source code originally written by
Dominic Waithe as a part of the FCS Bulk Correlation Software project.

Original source:
https://github.com/dwaithe/FCS_point_correlator/blob/master/focuspoint/correlation_methods/correlation_methods.py

Original work:
Copyright (C) 2015 Dominic Waithe

Modifications and this derived version:
Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)

This file is derived from work originally licensed under the GNU General
Public License, either version 2 of the License, or (at your option) any
later version, by Dominic Waithe.

This modified version is distributed under the terms of the GNU General
Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This file is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this file.  If not, see <https://www.gnu.org/licenses/>.

Modifications related to the original implementation of the tttr2xfcs function:

- This file contains only a modified version of the tttr2xfcs function.
  Other functions from the original file were intentionally omitted due to 
  the replacement of the original Cython-based components with a pure
  NumPy approach.
- The tttr2xfcs function interface is extended by adding tau_min and
  tau_max parameters, explicitly limiting the computed correlation lag
  time window.
- The dependency on the Cython-based fib4.dividAndConquer routine is
  replaced with lag-pair matching logic based on a pure NumPy
  implementation using np.searchsorted.
- The handling of correlation lag times is changed so that autotime is
  stored directly in milliseconds rather than raw time ticks, with a
  final conversion.
- The finite-size normalisation is reworked to operate in milliseconds,
  applied in a vectorised form, and a safety threshold is introduced to
  avoid numerical divergence as tau approaches the total measurement
  duration.
- An explicit maximum-lag cutoff is added, relative to the total
  acquisition time, to discard long-lag correlation points with poor
  finite-size behaviour.

The overall correlation algorithm, data flow, and scientific intent of
the original tttr2xfcs implementation are preserved.
"""



def tttr2xfcs (y,num,NcascStart,NcascEnd, Nsub,tau_min,tau_max):

    
    """autocorr, autotime = tttr2xfcs(t, num, 0, npoints, nsub, tau_min, tau_max)
    
    This is the modification of the function provided by Dominic Waithe (the source code available at     https://github.com/dwaithe/FCS_point_correlator/blob/master/focuspoint/correlation_methods/correlation_methods.py)
    For details of modification, see the header of this file. 
    The overall correlation algorithm, data flow, and scientific intent of the original tttr2xfcs function are preserved.
    
    The original comment by Dominic Waithe:
     Translation into Python of:
     Fast calculation of fluorescence correlation data with asynchronous time-correlated single-photon counting.
     Michael Wahl, Ingo Gregor, Matthias Patting, Jorg Enderlein
     This algorithm is most appropriate to use with time-tag data, whereby the photons are recorded individually as they arrive.
     The arrival times are correlated rather than binned intensities (though some binning is performed at later cycles).
     for intensity data which is recorded at regular intervals use a high-peforming correlation such as multipletau:
     (https://github.com/FCS-analysis/multipletau_)
     or a basic numpy version which can be found amongst others here:
     https://github.com/dwaithe/generalMacros/blob/master/diffusion%20simulations%20/Correlate%20Comparison.ipynb
    
    
    --- Current inputs --- 
    

    y:
        1D array of photon arrival times (time tags). This implementation
        assumes that the time unit of y is nanoseconds (ns). Internally the
        algorithm rounds values to integer ticks and performs multi-tau
        rebinning.

    num:
        2D array of photon counts/indicators per time tag and per channel,
        shape (len(y), n_channels). In the first stage this is typically a
        boolean/0-1 indicator array (a '1' represents a photon at the
        corresponding time tag for a given channel). During processing the
        values are rebinned into per-bin photon counts.

    NcascStart:
        Cascade level at which correlation computation starts (allows skipping
        initial cascade levels for speed).

    NcascEnd:
        Total number of cascade levels to compute (multi-tau logarithmic ranges).

    Nsub:
        Number of sub-levels (linear lag steps) per cascade level.

    tau_min:
        Minimum correlation lag time to include, in milliseconds (ms).
        Lags smaller than tau_min are computed but skipped in the output.

    tau_max:
        Maximum correlation lag time to include, in milliseconds (ms).
        Lags larger than tau_max are skipped in the output.

    
    
    --- Current outputs ---
    

    auto:
        3D array containing the un-normalised auto- and cross-correlation
        functions for all computed lag times.
        The array has shape (n_lags, n_channels, n_channels), where:

            auto[:, 0, 0]  – autocorrelation of channel 0
            auto[:, 1, 1]  – autocorrelation of channel 1
            auto[:, 1, 0]  – cross-correlation (channel 1 vs channel 0)
            auto[:, 0, 1]  – cross-correlation (channel 0 vs channel 1)

        A finite-size correction is applied internally as a function of lag
        time relative to the total acquisition duration.

    autotime:
        1D array of correlation lag times corresponding to the first dimension
        of auto. Lag times are expressed in milliseconds (ms).

        The returned lag range is constrained by the user-specified tau_min
        and tau_max parameters and additionally truncated by an internal
        maximum-lag cutoff relative to the total acquisition time.
  
    """
    dt = np.max(y) - np.min(y)
    y = np.round(y[:], 0)
    autotime = np.zeros(((NcascEnd+1)*(Nsub+1), 1))
    auto = np.zeros(((NcascEnd+1)*(Nsub+1), num.shape[1], num.shape[1]),
                    dtype=np.float64)
    shift = 0.0
    delta = 1.0
    for j in range(NcascEnd):
        y, k1 = np.unique(y, return_index=True)
        k1shape = k1.shape[0]
        cs = np.cumsum(num, axis=0).T
        diffArr1 = np.zeros((k1shape+1))
        diffArr2 = np.zeros((k1shape+1))
        diffArr1[1:] = cs[0, k1]
        diffArr2[1:] = cs[1, k1]
        num = np.zeros((y.shape[0], 2))
        num[:, 0] = np.diff(diffArr1)
        num[:, 1] = np.diff(diffArr2)
        for k in range(Nsub):
            shift += delta   
            tau_ms = shift / 1_000_000.0   
            lag = int(np.round(shift/delta))
            if tau_ms > tau_max:
                continue
            if tau_ms < tau_min:
                continue
            if j >= NcascStart:
                y_shifted = y + lag
                idx2 = np.searchsorted(y, y_shifted, side='left')
                valid = (idx2 < len(y))
                idx2 = idx2[valid]
                y_shifted = y_shifted[valid]
                i1 = np.nonzero(valid)[0]
                mask = (y[idx2] == y_shifted)
                i2 = idx2[mask]
                i1 = i1[mask]
                if i1.size and i2.size:
                    jin = np.dot((num[i1, :]).T, num[i2, :]) / delta
                    auto[k + j*Nsub, :, :] = jin

            autotime[k + j*Nsub] = tau_ms
        y = np.ceil(0.5 * y)
        delta *= 2.0
    tau = autotime.flatten()  # w ms
    scale = np.ones_like(tau, dtype=float)
    dt_ms = dt / 1_000_000.0
    mask = tau < 0.95 * dt_ms
    scale[mask] = dt_ms / (dt_ms - tau[mask])
    auto *= scale[:, None, None]
    max_lag_allowed = 0.2 * dt_ms
    valid_idx = (tau > 0) & (tau < max_lag_allowed)
    autotime = autotime[valid_idx]
    auto = auto[valid_idx]
    autotime = autotime.flatten()
    idauto = np.where(autotime != 0)[0]
    autotime = autotime[idauto]
    auto = auto[idauto, :, :]

    return auto, autotime

