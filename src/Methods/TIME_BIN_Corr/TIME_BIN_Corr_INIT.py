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
import os
import numpy as np
import pandas as pd
from numpy import log10,sqrt
import multipletau as mtau
import pickle
import time
import socket
import argparse
import tempfile
import gc
import ctypes
import multiprocessing as mp
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import wraps
from datetime import datetime
import inspect
import re
import include.INIT as inits
from include.fcsutils import load_fcs
logfile=os.path.join('Logs','log.txt')
bf = inits._basicF(logfile,None)
lprint = bf.lnprint
FCS = load_fcs(None,None)


def _attach_correlation_metadata(chunks, covariance, covariance_counts,
                                 lag_times):
    """Attach uncertainty metadata only to an available chunk table."""
    if chunks is None:
        return
    chunks.attrs['lag_covariance'] = np.asarray(covariance, dtype=float)
    chunks.attrs['lag_covariance_counts'] = np.asarray(
        covariance_counts, dtype=np.int64
    )
    chunks.attrs['lag_times'] = np.asarray(lag_times, dtype=float)


def _time_bin_executor(max_workers, start_methods=None):
    """Return an executor safe for the current platform and calling thread."""
    methods = (
        mp.get_all_start_methods()
        if start_methods is None else tuple(start_methods)
    )
    # Forking a process from the TCP server thread is unsafe for Numba/TBB and
    # may deadlock the application. Keep the faster process path for direct GUI
    # calls from the main thread; use threads for TCP calls and on Windows.
    is_main_thread = threading.current_thread() is threading.main_thread()
    if 'fork' in methods and is_main_thread:
        return (
            ProcessPoolExecutor(
                max_workers=max_workers,
                mp_context=mp.get_context('fork'),
            ),
            'processes',
        )
    return ThreadPoolExecutor(max_workers=max_workers), 'threads'

def natural_sort_key(value):
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r'(\d+)', str(value))]


def _correlate_time_bin_chunk_process(task):
    """Calculate the raw ACF and CCF curves for one time-binned data chunk."""
    (
        index,
        chunk_name,
        start,
        stop,
        channel_0_path,
        channel_1_path,
        delta_ms,
        nsub,
    ) = task
    started = time.perf_counter()
    channel_0 = np.load(channel_0_path, mmap_mode='r')[start:stop]
    result = {
        'index': index,
        'chunk_name': chunk_name,
        'chunk_length_1': delta_ms * max(0, stop - start - 1),
        'ACF_1': mtau.autocorrelate(
            channel_0,
            deltat=delta_ms,
            m=nsub,
            normalize=True,
        ),
    }
    if channel_1_path is not None:
        channel_1 = np.load(channel_1_path, mmap_mode='r')[start:stop]
        result.update(
            {
                'chunk_length_2': delta_ms * max(0, stop - start - 1),
                'ACF_2': mtau.autocorrelate(
                    channel_1,
                    deltat=delta_ms,
                    m=nsub,
                    normalize=True,
                ),
                'CCF_1': mtau.correlate(
                    channel_0,
                    channel_1,
                    deltat=delta_ms,
                    m=nsub,
                    normalize=True,
                ),
                'CCF_2': mtau.correlate(
                    channel_1,
                    channel_0,
                    deltat=delta_ms,
                    m=nsub,
                    normalize=True,
                ),
            }
        )
    result['process_id'] = os.getpid()
    result['duration'] = time.perf_counter() - started
    return result

class _TB_corr_init:
    def __init__(self,
                 size_ratio,
                 left_indent,
                 internal_indent,
                 right_indent,
                 bottom_indent,
                 top_indent,
                 group_spacer,
                 font_size,
                 last_directory,bf):
        '''General variables'''
        self.last_directory = last_directory
        self.bf = bf
        '''Layout variables'''
        self.size_ratio = size_ratio
        self.left_indent = int(left_indent*self.size_ratio['width'])
        self.internal_indent = int(internal_indent*self.size_ratio['width'])
        self.right_indent = int(right_indent*self.size_ratio['width'])
        self.bottom_indent = int(bottom_indent*self.size_ratio['width'])
        self.top_indent = int(top_indent*self.size_ratio['width'])
        self.group_spacer = int(group_spacer*self.size_ratio['width'])
        self.fnt_ratio = (self.size_ratio['width'] + self.size_ratio['height']) / 2
        self.font_size = int(np.round(font_size * self.fnt_ratio, 0))
        dpg.set_global_font_scale(self.fnt_ratio)
        self.file_window = {'name':'file_window',
                            'width':int(340*self.size_ratio['width']),
                            'height':dpg.get_viewport_height()-4*self.bottom_indent,
                            'pos':(self.left_indent,self.top_indent)
                            }
        self.TT_window = {'name':'TT_window',
                            'width':dpg.get_viewport_width()-self.left_indent-self.file_window['width']-self.internal_indent-self.right_indent,
                            'height':int(300*self.size_ratio['height']),
                            'pos':(self.file_window['pos'][0]+self.file_window['width']+self.internal_indent,
                                  self.top_indent)
                            }
        self.ACF_window = {'name':'ACF_window',
                            'width':dpg.get_viewport_width()-self.left_indent-self.file_window['width']-self.internal_indent-self.right_indent,
                            'height':self.file_window['height']-self.internal_indent-self.TT_window['height'],
                            'pos':(self.file_window['pos'][0]+self.file_window['width']+self.internal_indent,
                                  self.TT_window['pos'][1]+self.TT_window['height']+self.internal_indent)
                            }
        self.file_dialog_id_TB = {'name':'file_dialog_id_TB',
                               'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)
                              }
        self.file_dialog_save_correlated = {'name':'file_dialog_save_correlated',
                               'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)
                              }
        self.internal_width_left_panel = int(self.file_window['width']-self.internal_indent-self.group_spacer*3)
        self.file_box = {'name':'file_box',
                         'width':-1,
                         'num_items':10
                         }
        self.subplots = {'name':'subplots',
                         'rows':1,
                         'columns':1,
                         'row_ratios':[1.00],
                         'width':-1,
                         'height':-1
                         }
        self.FCS_subplots = {'name':'FCS_subplots',
                             'rows':1,
                             'columns':1,
                             'row_ratios':[1.00],
                             'width':-1,
                             'height':-1
                             }
        self.left_panel_tab_1 = {'name':'left_panel_tab_1',
                                 'width':-1}
        self.left_panel_tab_1_col_1 = {'name':'left_panel_tab_1_col_1',
                                       'width':self.internal_width_left_panel/2}
        self.left_panel_tab_1_col_2 = {'name':'left_panel_tab_1_col_2',
                                       'width':self.internal_width_left_panel/2}
        self.left_panel_drag_time_binning = {'name':'left_panel_drag_time_binning',
                                             'width':-1,
                                            'default_time_bin':np.round(1.0e-6,6)}
        self.left_panel_drag_subs = {'name':'left_panel_drag_subs',
                                     'width':-1,
                                     'default_value':100,
                                     'speed':2}
        self.left_panel_N_chunks = {'name':'left_panel_N_chunks',
                                    'width':-1,
                                    'default_value':30,
                                    'speed':1}
        self.Custom_chunks_check = {'name':'Custom_chunks_check',
                                    'default_value':False}
        
        self.Correlate_once_button ={'name':'Correlate_once_button','width':-1}
        self.Correlate_all_button ={'name':'Correlate_all_button','width':-1}
        self.left_panel_tau_min = {'name':'left_panel_tau_min',
                                   'width':-1,
                                   'default_value':1e-3,
                                   'speed':0.001}
        self.left_panel_tau_max = {'name':'left_panel_tau_max',
                                   'width':-1,
                                   'default_value':1e2,
                                   'speed':1}
        
        
class _TB_corr_common:
    def __init__(self,
                 INIT,
                 size_ratio,
                 group_spacer,
                 last_directory,
                 internal_width_left_panel,
                 left_panel_drag_time_binning,
                 basf,
                 menu,
                 globalITEMS
                 ):
        self.basf=basf
        self.method_init=INIT
        self.callback_listbox = self.timed(self.callback_listbox)
        self.correlate = self.timed(self.correlate)
        self.MAX_POINTS = 500_000
        self.menu=menu
        self.size_ratio = size_ratio
        self.IsTwoChannel = False
        self.group_spacer = group_spacer
        self.internal_width_left_panel = internal_width_left_panel
        self.last_directory = basf.recall_last_directory()
        self.output_path = self.last_directory
        self.globalITEMS = globalITEMS
        self.up_key = dpg.mvKey_Up
        self.down_key = dpg.mvKey_Down
        self.channels = ['_c0']
        self.directory = ''
        self.new_directory = ''
        self.files = ()
        self.anal_file = ''
        self.Mode = 'Auto'
        self.TT_subplots = self.method_init.subplots
        self.FCS_subplots = self.method_init.FCS_subplots
        self.TT_ydata_1 = np.empty(10)
        self.TT_xdata_1 = np.empty(10)
        self.TT_ydata_2 = np.empty(10)
        self.TT_xdata_2 = np.empty(10)
        self.TT_ydata_1_chunked = np.empty(10)
        self.TT_xdata_1_chunked = np.empty(10)
        self.TT_ydata_2_chunked = np.empty(10)
        self.TT_xdata_2_chunked = np.empty(10)
        self.shade_data_1=[np.empty(10),
                           np.empty(10),
                           np.empty(10)
                           ]
        self.shade_data_2=[np.empty(10),
                           np.empty(10),
                           np.empty(10)
                           ]
        self.left_panel_drag_time_binning = left_panel_drag_time_binning
        self.active_keys = [dpg.mvKey_Up,
                            dpg.mvKey_Down,
                           ]
        self.ACF_1 = pd.DataFrame()
        self.res_to_exp = {'filename':'',
                           'result_ACF_1':pd.DataFrame()}
        self.DialWinLis = []
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
    def timed(self, func):
        """Dekorator mający dostęp do self.basf"""
        enabled = self.basf.ENABLE_TIMING
        cwd = os.getcwd()
        tfile = os.path.join(cwd,self.basf.TIMING_FILE)
        @wraps(func)
        def wrapper(sender, app_data, *args, **kwargs):
            if not enabled:
                return func(sender, app_data, *args, **kwargs)
            start = time.perf_counter()
            result = func(sender, app_data, *args, **kwargs)
            duration = time.perf_counter() - start
            hostname = socket.gethostname()
            log_entry = (
                f"{datetime.now().isoformat()} | {hostname} | "
                f"{func.__qualname__} | file: {self.anal_file} | {duration:.6f}s\n"
            )
            with open(tfile, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[{hostname}] {func.__qualname__} took {duration:.4f}s")
            return result
        return wrapper    
        
    def define_file_menu_callbacks(self):
        dpg.configure_item('AC_menu_item',callback=self.callback_Open_TT_data)
        dpg.configure_item('Save_corr_item',callback=lambda: dpg.show_item('file_dialog_save_correlated'))
        dpg.configure_item('Forget_menu_item',callback=self.callback_Forget_PTU_data)
        dpg.configure_item('ForgetAll_menu_item',callback=self.callback_Forget_all_PTU_data)
    def remove_cor_files(self,file):
        filename = file+('_corr.dat')
        binary_filename = file+('_corr.corr')
        file_path_A1  =os.path.join(self.output_path,'AutoCorr_ch1',filename)
        file_path_A2  =os.path.join(self.output_path,'AutoCorr_ch2',filename)
        file_path_C1  =os.path.join(self.output_path,'CrossCorr_ch1',filename)
        file_path_C2  =os.path.join(self.output_path,'CrossCorr_ch2',filename)
        binary_paths = [
            os.path.join(self.output_path, folder, binary_filename)
            for folder in (
                'AutoCorr_ch1', 'AutoCorr_ch2',
                'CrossCorr_ch1', 'CrossCorr_ch2',
            )
        ]
        chnkpath = os.path.join(self.output_path,file+'.chnk')
        try:
            os.remove(file_path_A1)
        except:
            pass
        try:
            os.remove(file_path_A2)
        except:
            pass
        try:
            os.remove(file_path_C1)
        except:
            pass
        try:
            os.remove(file_path_C2)
        except:
            pass
        try:
            os.remove(chnkpath)
        except:
            pass
        for binary_path in binary_paths:
            try:
                os.remove(binary_path)
            except OSError:
                pass

    @staticmethod
    def _mean_count_rate(counts, bin_time):
        """Return the mean photon count rate in Hz for a binned trace."""
        counts = np.asarray(counts, dtype=float)
        if counts.size == 0 or bin_time <= 0:
            return 0.0
        return float(np.mean(counts) / bin_time)

    def _export_correlation_pair(
        self,
        directory,
        result,
        chunk_curves,
        covariance,
        covariance_counts,
        count_rate,
    ):
        """Export one correlation curve as human-readable DAT and binary CORR."""
        if result is None or chunk_curves is None:
            return None, None
        stem = self.anal_file + '_corr'
        dat_path = os.path.join(directory, stem + '.dat')
        corr_path = os.path.join(directory, stem + '.corr')

        result.to_csv(dat_path, sep='\t', index=False)
        correlation = result.copy()
        correlation.columns = (
            ['X', 'Y', 'Y_err']
            if len(correlation.columns) == 3 else ['X', 'Y']
        )
        chunks = chunk_curves.copy()
        _attach_correlation_metadata(
            chunks,
            covariance,
            covariance_counts,
            result['time'].to_numpy(dtype=float),
        )
        payload = {
            'Correlation': correlation,
            'CNTR': [float(count_rate)],
            'CorrelatedChunks': chunks,
            'LagCovariance': np.asarray(covariance, dtype=float),
            'LagCovarianceCounts': np.asarray(covariance_counts, dtype=np.int64),
            'LagTimes': result['time'].to_numpy(dtype=float),
        }
        with open(corr_path, 'wb') as output:
            pickle.dump(payload, output)
        return dat_path, corr_path
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
        
    def callback_Forget_PTU_data(self):
        if self.anal_file !='':
            file =self.anal_file +'.pck'
        if os.path.exists(os.path.join(self.last_directory,file)):
            os.remove(os.path.join(self.last_directory,file))
            self.remove_cor_files(self.anal_file)
            self.files[self.anal_file]['Meta']=None
            self.SaveSinglePickle(self.anal_file)
            self.load_data(self.anal_file)
        else:
            pass
    

    def callback_Forget_all_PTU_data(self):
        if self.anal_file !='':
            for file in self.files:
                path = os.path.join(self.last_directory,file)
                path =path + '.pck'
                if os.path.exists(path):
                    os.remove(path)
                    self.remove_cor_files(file)
                    self.files[file]['Meta']=None
                    self.SaveSinglePickle(self.anal_file)
                    self.load_data(self.anal_file)
                else:
                    pass
        else:
            pass
    
    def callback_Open_TT_data(self,sender,app_data):
        if sender == 'AC_menu_item':
            self.Mode = 'Auto'
        elif sender == 'CC_menu_item':
            self.Mode = 'Cross'
        else:
            pass
        dpg.show_item('file_dialog_id_TB')

    #########################################################################           
    #########################################################################           
    #########################################################################   
        
    def text_file_check(self, file):
        try:
            a = np.genfromtxt(file, delimiter=",", max_rows=5)
        except Exception:
            print(file, 'cos_sie_zjebalo')
            return False
        return a.ndim == 1

    #########################################################################           
    #########################################################################           
    #########################################################################   

        
    def add_chunks(self):
        nchunks = dpg.get_value('left_panel_N_chunks')
        xdata = self.TT_xdata_1
        chunk_nodes = np.linspace(0,len(xdata),nchunks+1).astype(int)
        self.chunks = {}
        for i in range(nchunks):
            ind_min = chunk_nodes[0+i]
            ind_max = chunk_nodes[1+i]
            mn, mx = xdata[ind_min:ind_max].min(),xdata[ind_min:ind_max].max()
            self.chunks['chunk_'+str(i)] = {'values':[mn,mx],
                                       'indices':[ind_min,ind_max]
                                      }
        existing_chunks_lines = dpg.get_aliases()
        existing_chunks_lines = [chL for chL in existing_chunks_lines if chL.startswith('Chunk_') and chL.endswith('_dragline')]
        for chL in existing_chunks_lines:
            dpg.delete_item(chL)
        for i in range(nchunks):
            if len(self.channels) ==1:
                dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
                                  tag="Chunk_1_"+str(i+1)+'_start_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][0],
                                  parent='plot_1',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                  )
                dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
                                  tag="Chunk_1_"+str(i+1)+'_stop_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][1],
                                  parent='plot_1',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                 )
                self.globalITEMS.windows.extend(["Chunk_1_"+str(i+1)+'_start_dragline',
                                                 "Chunk_1_"+str(i+1)+'_stop_dragline'])
            elif len(self.channels) ==2:
                dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
                                  tag="Chunk_1_"+str(i+1)+'_start_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][0],
                                  parent='plot_1',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                  )
                dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
                                  tag="Chunk_1_"+str(i+1)+'_stop_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][1],
                                  parent='plot_1',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                 )
                dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
                                  tag="Chunk_2_"+str(i+1)+'_start_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][0],
                                  parent='plot_2',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                  )
                dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
                                  tag="Chunk_2_"+str(i+1)+'_stop_dragline',
                                  color=[255, 0, 0, 255],
                                  default_value=self.chunks['chunk_'+str(i)]['values'][1],
                                  parent='plot_2',
                                  show=False,
                                  callback=self.on_drag_line_drag
                                 )
                self.globalITEMS.windows.extend(["Chunk_1_"+str(i+1)+'_start_dragline',
                                                 "Chunk_1_"+str(i+1)+'_stop_dragline',
                                                 "Chunk_2_"+str(i+1)+'_start_dragline',
                                                 "Chunk_2_"+str(i+1)+'_stop_dragline'])
                
        self.show_chunks_drag_lines('Custom_chunks_check',dpg.get_value('Custom_chunks_check'))
                
    #########################################################################           
    #########################################################################           
    #########################################################################   
    
    def show_chunks_drag_lines(self,sender,app_data):
        nchunks = dpg.get_value('left_panel_N_chunks')
        self.calculate_shade()
        if app_data:
            if len(self.channels) ==1:
                for i in range(nchunks):
                    dpg.show_item("Chunk_1_"+str(i+1)+'_start_dragline')
                    dpg.show_item("Chunk_1_"+str(i+1)+'_stop_dragline')
                    dpg.show_item('TT_shade_1')
            elif len(self.channels) ==2:
                for i in range(nchunks):
                    dpg.show_item("Chunk_1_"+str(i+1)+'_start_dragline')
                    dpg.show_item("Chunk_1_"+str(i+1)+'_stop_dragline')
                    dpg.show_item('TT_shade_1')
                    dpg.show_item("Chunk_2_"+str(i+1)+'_start_dragline')
                    dpg.show_item("Chunk_2_"+str(i+1)+'_stop_dragline')
                    dpg.show_item('TT_shade_2')
                
        else:
            if len(self.channels) ==1:
                for i in range(nchunks):
                    dpg.hide_item("Chunk_1_"+str(i+1)+'_start_dragline')
                    dpg.hide_item("Chunk_1_"+str(i+1)+'_stop_dragline') 
                    dpg.hide_item('TT_shade_1') 
            elif len(self.channels) ==2:
                for i in range(nchunks):
                    dpg.hide_item("Chunk_1_"+str(i+1)+'_start_dragline')
                    dpg.hide_item("Chunk_1_"+str(i+1)+'_stop_dragline') 
                    dpg.hide_item('TT_shade_1') 
                    dpg.hide_item("Chunk_2_"+str(i+1)+'_start_dragline')
                    dpg.hide_item("Chunk_2_"+str(i+1)+'_stop_dragline') 
                    dpg.hide_item('TT_shade_2')
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
        
        
    def callback_left_panel_drag_time_binning(self,sender,app_data):
        if not self.IsTwoChannel:
            if self.anal_file != '':
                value = self.round_data(app_data)
                self.TT_xdata_1 = np.arange(0, len(self.TT_ydata_1)*value, value,
                                            dtype=float)
                self.add_chunks()
                self.calculate_shade()
                self.plot_TT()
                
        if self.IsTwoChannel:
            if self.anal_file != '':
                value = self.round_data(app_data)
                self.TT_xdata_1 = np.arange(0, len(self.TT_ydata_1)*value, value,
                                            dtype=float)
                self.TT_xdata_2 = np.arange(0, len(self.TT_ydata_2)*value, value,
                                            dtype=float)
                self.add_chunks()
                self.calculate_shade()
                self.plot_TT()
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    def load_data(self,file):
        meta = self.files[file]
        keys = list(meta['Channels'].keys())
        keys.sort()
        value = self.round_data(dpg.get_value('left_panel_drag_time_binning'))
        if len(keys) ==1:
            ch = keys[0]
            self.channels = keys
            self.IsTwoChannel = False
            f = meta['Channels'][ch]
            file_path = os.path.join(self.last_directory,f)
            with open(file_path, "r") as f:
                self.TT_ydata_1 = np.fromstring(f.read(), sep="\n", dtype=np.int64)
            self.TT_xdata_1 = np.arange(0, len(self.TT_ydata_1)*value, value, dtype=float)
                
        elif len(keys) == 2:
            self.channels = keys
            self.IsTwoChannel = True
            for ch in keys:
                f =  meta['Channels'][ch]
                file_path = os.path.join(self.last_directory,f)
                if ch == '_c0':
                    with open(file_path, "r") as f:
                        self.TT_ydata_1 = np.fromstring(f.read(), sep="\n", dtype=np.int64)
                    self.TT_xdata_1 = np.arange(0, len(self.TT_ydata_1)*value, value, dtype=float)
                elif ch == '_c1':
                    with open(file_path, "r") as f:
                        self.TT_ydata_2 = np.fromstring(f.read(), sep="\n", dtype=np.int64)
                    self.TT_xdata_2 = np.arange(0, len(self.TT_ydata_2)*value, value, dtype=float)
        self.clean_FCS_plots()
        self.add_chunks()
        self.calculate_shade()
        self.plot_TT()
        self.callback_crossCorr_check('DUMMY',dpg.get_value('FCS_cross_check'))
        if meta['Meta'] !=None:
            loaded_correlation = False
            correlation_meta = meta['Meta'].get('Correlation', {})
            if not self.IsTwoChannel:
                correlation_paths = [correlation_meta.get('A_c0')]
                if all(path and os.path.isfile(path) for path in correlation_paths):
                    tmpdf = pd.read_csv(correlation_paths[0],sep='\t')
                    self.res_to_exp = {'filename':self.anal_file,
                                   'result_ACF_1':tmpdf}
                    loaded_correlation = True
            elif self.IsTwoChannel:
                correlation_paths = [
                    correlation_meta.get(key)
                    for key in ('A_c0', 'A_c1', 'C_c0', 'C_c1')
                ]
                if all(path and os.path.isfile(path) for path in correlation_paths):
                    tmpdf_A1 = pd.read_csv(correlation_paths[0],sep='\t')
                    tmpdf_A2 = pd.read_csv(correlation_paths[1],sep='\t')
                    tmpdf_C1 = pd.read_csv(correlation_paths[2],sep='\t')
                    tmpdf_C2 = pd.read_csv(correlation_paths[3],sep='\t')
                    self.res_to_exp = {'filename':self.anal_file,
                                   'result_ACF_1':tmpdf_A1,
                                   'result_ACF_2':tmpdf_A2,
                                   'result_CCF_1':tmpdf_C1,
                                   'result_CCF_2':tmpdf_C2}
                    loaded_correlation = True
            if not loaded_correlation:
                self.res_to_exp = {'filename': self.anal_file}
            time_bin = meta['Meta']['meta']['time_bin']
            dpg.set_value('left_panel_drag_time_binning',time_bin)
            Npoints = meta['Meta']['meta']['Npoints']
            dpg.set_value('left_panel_drag_subs',Npoints)
            Nchunks = meta['Meta']['meta']['Nchunks']
            dpg.set_value('left_panel_N_chunks',Nchunks)
            custom_chunks = meta['Meta']['meta']['custom_chunks']
            dpg.set_value('Custom_chunks_check',custom_chunks)
            self.chunks = meta['Meta']['meta']['chunks']
            tau_min = meta['Meta']['meta']['tau_min']
            dpg.set_value('left_panel_tau_min',tau_min)
            tau_max = meta['Meta']['meta']['tau_max']
            dpg.set_value('left_panel_tau_max',tau_max)
            if loaded_correlation:
                self.plot_ACF()
    #########################################################################           
    #########################################################################           
    #########################################################################   


    def load_TT_plots(self):
        with dpg.plot(no_title=True,tag='plot_1',show=True,parent = 'subplots'):
            self.TT_plt_x = dpg.add_plot_axis(dpg.mvXAxis, label="Time [s]", tag='TT_x_1',log_scale=False,show=True)
            self.TT_plt_y = dpg.plot_axis(dpg.mvYAxis, label="Counts",tag='TT_y_1',log_scale=False,show=True)
            with self.TT_plt_y:
                dpg.add_line_series([], [],tag='TT_plot_1',label='Timetrace Channel 1')
                dpg.add_shade_series(x = self.shade_data_1[0],
                                     y1 = self.shade_data_1[1],
                                     y2 = self.shade_data_1[2],
                                     tag='TT_shade_1'
                                     )
                dpg.bind_item_theme("TT_plot_1", "plot_green_theme")
                dpg.bind_item_theme("TT_shade_1", "plot_green_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast,show=True,tag='TT_CH1_leg')
        self.globalITEMS.windows.extend(['plot_1','TT_x_1','TT_y_1','TT_plot_1','TT_shade_1','TT_CH1_leg'])
        with dpg.plot(no_title=True,tag='plot_2',show=False,parent = 'subplots'):
            self.TT_plt_x_2 = dpg.add_plot_axis(dpg.mvXAxis, label="", tag='TT_x_2',log_scale=False,show=False)
            self.TT_plt_y_2 = dpg.plot_axis(dpg.mvYAxis, label="Counts",tag='TT_y_2',log_scale=False,show=False)
            with self.TT_plt_y_2:
                dpg.add_line_series([], [],tag='TT_plot_2',label='Timetrace Channel 2')
                dpg.add_shade_series(x = self.shade_data_2[0],
                                     y1 = self.shade_data_2[1],
                                     y2 = self.shade_data_2[2],
                                     tag='TT_shade_2'
                                     )
                dpg.bind_item_theme("TT_plot_2", "plot_green_theme")
                dpg.bind_item_theme("TT_shade_2", "plot_green_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast,show=True,tag='TT_CH2_leg')
        self.globalITEMS.windows.extend(['plot_2','TT_x_2','TT_y_2','TT_plot_2','TT_shade_2','TT_CH2_leg'])

    def callback_crossCorr_check(self,sender,app_data):
        dummy =  sender =='DUMMY'
        self.clean_FCS_plots()
        if not self.IsTwoChannel:
            dpg.hide_item('Cross_FCS_plot1')
            dpg.hide_item('Cross_FCS_plot1_shade')
            dpg.hide_item('Cross_FCS_plot2')
            dpg.hide_item('Cross_FCS_plot2_shade')
        elif self.IsTwoChannel:
            if app_data:
                dpg.show_item('Cross_FCS_plot1')
                dpg.show_item('Cross_FCS_plot1_shade')
                dpg.show_item('Cross_FCS_plot2')
                dpg.show_item('Cross_FCS_plot2_shade')
                dpg.configure_item('FCS_CH1_leg',location=dpg.mvPlot_Location_NorthEast)
                dpg.configure_item('FCS_CH2_leg',location=dpg.mvPlot_Location_NorthEast)
            else:
                dpg.hide_item('Cross_FCS_plot1')
                dpg.hide_item('Cross_FCS_plot1_shade')
                dpg.hide_item('Cross_FCS_plot2')
                dpg.hide_item('Cross_FCS_plot2_shade')
        required_results = {'result_ACF_1'}
        if self.IsTwoChannel:
            required_results.update(
                {'result_ACF_2', 'result_CCF_1', 'result_CCF_2'}
            )
        if not dummy and required_results.issubset(self.res_to_exp):
            self.plot_ACF()
        
    def load_FCS_plots(self):
        with dpg.plot(no_title=True,
                      tag='plot_fcs_1',
                      label='Channel 1',
                      show=True,
                      parent = 'FCS_subplots'):
            self.FCS_plt_x_1 = dpg.add_plot_axis(dpg.mvXAxis,
                                                 label="Lag time, \u03C4 [ms]",
                                                 tag='FCS_x_1',
                                                 log_scale=True)
            self.FCS_plt_y_1 = dpg.plot_axis(dpg.mvYAxis, 
                                             label="G(\u03C4)",
                                             tag='FCS_y_1',
                                             log_scale=False)
            with self.FCS_plt_y_1:
                dpg.add_shade_series(x=np.empty(10),y1=np.empty(10),y2=np.empty(10),tag='FCS_plot_shade_1')
                dpg.add_line_series(np.empty(10), np.empty(10),tag='FCS_plot_1',label='Autocorrelation Channel 1')
                dpg.bind_item_theme("FCS_plot_1", "plot_green_theme")
                dpg.bind_item_theme("FCS_plot_shade_1", "plot_green_theme")
                dpg.add_line_series([], [],tag='Cross_FCS_plot1',label='Crosscorrelation Channel 1 \u2192 2',show=False)
                dpg.add_shade_series(x=[],y1=[],y2=[],tag='Cross_FCS_plot1_shade',show=False)
                dpg.bind_item_theme("Cross_FCS_plot1", "plot_yellow_theme")
                dpg.bind_item_theme("Cross_FCS_plot1_shade", "plot_yellow_theme")
            dpg.set_axis_limits('FCS_x_1',0,1)
            dpg.set_axis_limits('FCS_y_1',0,1)
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast,show=True,tag='FCS_CH1_leg')
            self.globalITEMS.windows.extend(['plot_fcs_1',
                                             'FCS_x_1',
                                             'FCS_y_1',
                                             'FCS_plot_1',
                                             'FCS_plot_shade_1',
                                             'Cross_FCS_plot1',
                                             'Cross_FCS_plot1_shade',
                                            'FCS_CH1_leg'])
        with dpg.plot(no_title=True,
                      tag='plot_fcs_2',
                      label='Channel 2',
                      show=False,
                      parent = 'FCS_subplots'):
            self.FCS_plt_x_2 = dpg.add_plot_axis(dpg.mvXAxis,
                                                 label="Lag time, \u03C4 [ms]",
                                                 tag='FCS_x_2',
                                                 log_scale=True)
            self.FCS_plt_y_2 = dpg.plot_axis(dpg.mvYAxis, label="G(\u03C4)",tag='FCS_y_2',log_scale=False)
            with self.FCS_plt_y_2:
                dpg.add_shade_series(x=np.empty(10),y1=np.empty(10),y2=np.empty(10),tag='FCS_plot_shade_2')
                dpg.add_line_series(np.empty(10), np.empty(10),tag='FCS_plot_2',label='Autocorrelation Channel 2')
                dpg.bind_item_theme("FCS_plot_2", "plot_green_theme")
                dpg.bind_item_theme("FCS_plot_shade_2", "plot_green_theme")
                dpg.add_line_series([], [],tag='Cross_FCS_plot2',label='Crosscorrelation Channel 2 \u2192 1',show=False)
                dpg.add_shade_series(x=[],y1=[],y2=[],tag='Cross_FCS_plot2_shade',show=False)
                dpg.bind_item_theme("Cross_FCS_plot2", "plot_yellow_theme")
                dpg.bind_item_theme("Cross_FCS_plot2_shade", "plot_yellow_theme")
            dpg.set_axis_limits('FCS_x_2',0,1)
            dpg.set_axis_limits('FCS_y_2',0,1)
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast,show=True,tag='FCS_CH2_leg')
            self.globalITEMS.windows.extend(['plot_fcs_2',
                                             'FCS_x_2',
                                             'FCS_y_2',
                                             'FCS_plot_2',
                                             'FCS_plot_shade_2',
                                             'Cross_FCS_plot2',
                                             'Cross_FCS_plot2_shade',
                                            'FCS_CH2_leg'])
            
    def clean_FCS_plots(self):
        if not self.IsTwoChannel:
            self.FCS_subplots['columns'] = 1
            self.FCS_subplots['column_ratios'] = [1.00]
            dpg.configure_item('FCS_subplots',
                               columns = self.FCS_subplots['columns'],
                               column_ratios = self.FCS_subplots['column_ratios'])
            dpg.hide_item('plot_fcs_2')
            dpg.set_value('FCS_cross_check',False)
            dpg.hide_item('FCS_cross_check')
            dpg.set_value('FCS_plot_2',[np.empty(10), np.empty(10)])
            dpg.set_value('FCS_plot_shade_2',[np.empty(10), np.empty(10),np.empty(10)])
            dpg.set_axis_limits('FCS_x_2',0,1)
            dpg.set_axis_limits('FCS_y_2',0,1)
            dpg.hide_item('plot_fcs_2')
            dpg.set_value('FCS_plot_1',[np.empty(10), np.empty(10)])
            dpg.set_value('FCS_plot_shade_1',[np.empty(10), np.empty(10),np.empty(10)])
            dpg.set_axis_limits('FCS_x_1',0,1)
            dpg.set_axis_limits('FCS_y_1',0,1)

        if self.IsTwoChannel:

            self.FCS_subplots['columns'] = 2
            self.FCS_subplots['column_ratios'] = [0.5,0.5]
            dpg.configure_item('FCS_subplots',columns = self.FCS_subplots['columns'],column_ratios = self.FCS_subplots['column_ratios'])
            dpg.show_item('plot_fcs_2')
            dpg.show_item('FCS_cross_check')
            dpg.set_value('FCS_plot_2',[np.empty(10), np.empty(10)])
            dpg.set_value('FCS_plot_shade_2',[np.empty(10), np.empty(10),np.empty(10)])
            dpg.set_axis_limits('FCS_x_2',0,1)
            dpg.set_axis_limits('FCS_y_2',0,1)
            dpg.show_item('plot_fcs_2')
            dpg.set_value('FCS_plot_1',[np.empty(10), np.empty(10)])
            dpg.set_value('FCS_plot_shade_1',[np.empty(10), np.empty(10),np.empty(10)])
            dpg.set_axis_limits('FCS_x_1',0,1)
            dpg.set_axis_limits('FCS_y_1',0,1)
            
    #########################################################################           
    #########################################################################           
    #########################################################################   


    def downsample_mean_uniform(self,x, y,*, y_dtype=np.float32):
        """
        Downsample the timetrace to display only self.MAX_POINTS on the TT plot.
        """
        max_points =  self.MAX_POINTS
        x = np.asarray(x)
        y = np.asarray(y)
        n = x.size
        if n == 0:
            return np.ascontiguousarray(x), np.ascontiguousarray(y)
    
        if n <= max_points:
            return np.ascontiguousarray(x), np.ascontiguousarray(y.astype(y_dtype, copy=False))
        k = int((n + max_points - 1) // max_points)
        n2 = (n // k) * k 
        x2 = x[:n2].reshape(-1, k).mean(axis=1)
        y2 = y[:n2].astype(np.float64, copy=False).reshape(-1, k).mean(axis=1).astype(y_dtype)
        return np.ascontiguousarray(x2), np.ascontiguousarray(y2)
    
        
    def plot_TT(self):
        if not self.IsTwoChannel:
            self.TT_subplots['rows'] = 1
            self.TT_subplots['row_ratios'] = [1.00]
            dpg.configure_item('subplots',rows = self.TT_subplots['rows'],row_ratios = self.TT_subplots['row_ratios'])
            dpg.hide_item('plot_2')
            dpg.hide_item('TT_x_2')
            dpg.hide_item('TT_y_2')
            new_xdata_1, new_ydata_1 = self.downsample_mean_uniform(self.TT_xdata_1, self.TT_ydata_1)
            dpg.set_value('TT_plot_1', [new_xdata_1,new_ydata_1 ])
            dpg.configure_item('TT_shade_1',x = self.shade_data_1[0], y1= self.shade_data_1[1],y2 = self.shade_data_1[2])
            dpg.set_axis_limits('TT_x_1',self.TT_xdata_1.min(),self.TT_xdata_1.max())
            dpg.set_axis_limits('TT_y_1',new_ydata_1.min(),new_ydata_1.max())
        
        elif self.IsTwoChannel:
            self.TT_subplots['rows'] = 2
            self.TT_subplots['row_ratios'] = [0.50,0.50]
            dpg.configure_item('subplots',rows = self.TT_subplots['rows'],row_ratios = self.TT_subplots['row_ratios'])
            dpg.show_item('plot_2')
            dpg.show_item('TT_x_2')
            dpg.show_item('TT_y_2')
            new_xdata_1, new_ydata_1 = self.downsample_mean_uniform(self.TT_xdata_1, self.TT_ydata_1)
            new_xdata_2, new_ydata_2 = self.downsample_mean_uniform(self.TT_xdata_2, self.TT_ydata_2)
            dpg.set_value('TT_plot_1', [new_xdata_1, new_ydata_1 ])
            dpg.configure_item('TT_shade_1',x = self.shade_data_1[0], y1= self.shade_data_1[1],y2 = self.shade_data_1[2])
            dpg.set_axis_limits('TT_x_1',self.TT_xdata_1.min(),self.TT_xdata_1.max())
            dpg.set_axis_limits('TT_y_1',new_ydata_1.min(),new_ydata_1.max())
            dpg.set_value('TT_plot_2', [new_xdata_2, new_ydata_2 ])
            dpg.configure_item('TT_shade_2',x = self.shade_data_2[0], y1= self.shade_data_2[1],y2 = self.shade_data_2[2])
            dpg.set_axis_limits('TT_x_2',self.TT_xdata_2.min(),self.TT_xdata_2.max())
            dpg.set_axis_limits('TT_y_2',new_ydata_2.min(),new_ydata_2.max())
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
                    
    def plot_ACF(self):
        IfCrosscorrelate = dpg.get_value('FCS_cross_check')
        if not self.IsTwoChannel:
            xdata_1 = self.res_to_exp['result_ACF_1'].time
            ydata_1 = self.res_to_exp['result_ACF_1'].MEAN
            dpg.set_value('FCS_plot_1', [xdata_1.values,ydata_1.values ])
            if dpg.get_value('left_panel_N_chunks')>1:
                yerr_1 = self.res_to_exp['result_ACF_1'].SE
                dpg.configure_item('FCS_plot_shade_1', x =xdata_1.values,
                                   y1=(ydata_1+yerr_1).values,
                                  y2=(ydata_1-yerr_1).values)
                miny=np.min([ydata_1.min(),
                             (ydata_1+yerr_1).min(),
                             (ydata_1-yerr_1).min()])
                maxy=np.max([ydata_1.max(),
                             (yerr_1+ydata_1).max(),
                             (yerr_1-ydata_1).max()])
            else:
                miny=ydata_1.min()
                maxy=ydata_1.max()
                dpg.configure_item('FCS_plot_shade_1', x =np.empty(10),
                                   y1=np.empty(10),
                                  y2=np.empty(10))
            dpg.set_axis_limits('FCS_x_1',xdata_1.min(),xdata_1.max())
            dpg.set_axis_limits('FCS_y_1',miny,maxy)
            
        elif self.IsTwoChannel:
            Axdata_1 = self.res_to_exp['result_ACF_1'].time
            Aydata_1 = self.res_to_exp['result_ACF_1'].MEAN
            Axdata_2 = self.res_to_exp['result_ACF_2'].time
            Aydata_2 = self.res_to_exp['result_ACF_2'].MEAN
            Cxdata_1 = self.res_to_exp['result_CCF_1'].time
            Cydata_1 = self.res_to_exp['result_CCF_1'].MEAN
            Cxdata_2 = self.res_to_exp['result_CCF_2'].time
            Cydata_2 = self.res_to_exp['result_CCF_2'].MEAN
            dpg.set_value('FCS_plot_1', [Axdata_1.values,Aydata_1.values ])
            dpg.set_value('FCS_plot_2', [Axdata_2.values,Aydata_2.values ])
            dpg.set_value('Cross_FCS_plot1', [Cxdata_1.values,Cydata_1.values ])
            dpg.set_value('Cross_FCS_plot2', [Cxdata_2.values,Cydata_2.values ])
            if dpg.get_value('left_panel_N_chunks')>1:
                Ayerr_1 = self.res_to_exp['result_ACF_1'].SE
                Ayerr_2 = self.res_to_exp['result_ACF_2'].SE
                Cyerr_1 = self.res_to_exp['result_CCF_1'].SE
                Cyerr_2 = self.res_to_exp['result_CCF_2'].SE
                dpg.configure_item('FCS_plot_shade_1', x =Axdata_1.values,
                                   y1=(Aydata_1+Ayerr_1).values,
                                  y2=(Aydata_1-Ayerr_1).values)
                dpg.configure_item('FCS_plot_shade_2', x =Axdata_2.values,
                                   y1=(Aydata_2+Ayerr_2).values,
                                  y2=(Aydata_2-Ayerr_2).values)
                if IfCrosscorrelate:
                    miny_1=np.min([Aydata_1.min(),Cydata_1.min(),
                                 (Aydata_1+Ayerr_1).min(),
                                 (Aydata_1-Ayerr_1).min(),
                                 (Cydata_1+Cyerr_1).min(),
                                 (Cydata_1-Cyerr_1).min()])
                    maxy_1=np.max([Aydata_1.max(),Cydata_1.max(),
                                 (Aydata_1+Ayerr_1).max(),
                                 (Aydata_1-Ayerr_1).max(),
                                 (Cydata_1+Cyerr_1).max(),
                                 (Cydata_1-Cyerr_1).max()])
                    miny_2=np.min([Aydata_2.min(),Cydata_2.min(),
                                 (Aydata_2+Ayerr_2).min(),
                                 (Aydata_2-Ayerr_2).min(),
                                 (Cydata_2+Cyerr_2).min(),
                                 (Cydata_2-Cyerr_2).min()])
                    maxy_2=np.max([Aydata_2.max(),Cydata_2.max(),
                                 (Aydata_2+Ayerr_2).max(),
                                 (Aydata_2-Ayerr_2).max(),
                                 (Cydata_2+Cyerr_2).max(),
                                 (Cydata_2-Cyerr_2).max()])
                    dpg.configure_item('Cross_FCS_plot1_shade', x =Cxdata_1.values,
                                       y1=(Cydata_1+Cyerr_1).values,
                                      y2=(Cydata_1-Cyerr_1).values)
                    dpg.configure_item('Cross_FCS_plot2_shade', x =Cxdata_2.values,
                                       y1=(Cydata_2+Cyerr_2).values,
                                      y2=(Cydata_2-Cyerr_2).values)
                else:
                    miny_1=np.min([Aydata_1.min(),
                                 (Aydata_1+Ayerr_1).min(),
                                 (Aydata_1-Ayerr_1).min()])
                    maxy_1=np.max([Aydata_1.max(),
                                 (Aydata_1+Ayerr_1).max(),
                                 (Aydata_1-Ayerr_1).max()])
                    miny_2=np.min([Aydata_2.min(),
                                 (Aydata_2+Ayerr_2).min(),
                                 (Aydata_2-Ayerr_2).min()])
                    maxy_2=np.max([Aydata_2.max(),
                                 (Aydata_2+Ayerr_2).max(),
                                 (Aydata_2-Ayerr_2).max()])
                    dpg.configure_item('Cross_FCS_plot1_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('Cross_FCS_plot2_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
            else:
                if IfCrosscorrelate:
                    miny_1=np.min([Aydata_1.min(),Cydata_1.min()])
                    maxy_1=np.max([Aydata_1.max(),Cydata_1.max()])
                    miny_2=np.min([Aydata_2.min(),Cydata_2.min()])
                    maxy_2=np.max([Aydata_2.max(),Cydata_2.max()])
                    dpg.configure_item('FCS_plot_shade_1', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('FCS_plot_shade_2', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('Cross_FCS_plot1_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('Cross_FCS_plot2_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                elif not IfCrosscorrelate:
                    miny_1=Aydata_1.min()
                    maxy_1=Aydata_1.max()
                    miny_2=Aydata_2.min()
                    maxy_2=Aydata_2.max()
                    dpg.configure_item('FCS_plot_shade_1', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('FCS_plot_shade_2', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('Cross_FCS_plot1_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    dpg.configure_item('Cross_FCS_plot2_shade', x =np.empty(10),
                                       y1=np.empty(10),
                                      y2=np.empty(10))
                    
            dpg.set_axis_limits('FCS_x_1',Axdata_1.min(),Axdata_1.max())
            dpg.set_axis_limits('FCS_y_1',miny_1,maxy_1)
            dpg.set_axis_limits('FCS_x_2',Axdata_2.min(),Axdata_2.max())
            dpg.set_axis_limits('FCS_y_2',miny_2,maxy_2)
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
                    
    def round_data(self,value):
        exponent = int(np.round(np.ceil(log10(value))))
        if exponent <0:
            value = np.round(value,abs(exponent-1))
        return value

    def _correlate_single_chunk_worker(
        self,
        index,
        chunk_name,
        bintime,
        nsub,
        centers,
        edges,
    ):
        indices = self.chunks[chunk_name]['indices']
        start, stop = indices
        column = 'acf_' + chunk_name

        xdata_1 = self.TT_xdata_1[start:stop].astype(float)
        ydata_1 = self.TT_ydata_1[start:stop].astype(float)
        acf_1_raw = mtau.autocorrelate(
            ydata_1,
            deltat=1e3*bintime,
            m=nsub,
            normalize=True,
        )
        acf_1_taus = acf_1_raw[1:, 0]
        acf_1 = pd.DataFrame(
            FCS.rebin_tau_to_grid(acf_1_taus, centers, edges),
            columns=['lagtime'],
        )
        acf_1[column] = FCS.rebin_chunk_to_grid(
            acf_1_taus,
            acf_1_raw[1:, 1],
            centers,
            edges,
        )

        result = {
            'index': index,
            'chunk_name': chunk_name,
            'column': column,
            'chunk_length_1': 1e3*(xdata_1[-1]-xdata_1[0]),
            'ACF_1': acf_1,
        }

        if self.IsTwoChannel:
            xdata_2 = self.TT_xdata_2[start:stop].astype(float)
            ydata_2 = self.TT_ydata_2[start:stop].astype(float)

            acf_2_raw = mtau.autocorrelate(
                ydata_2,
                deltat=1e3*bintime,
                m=nsub,
                normalize=True,
            )
            ccf_1_raw = mtau.correlate(
                ydata_1,
                ydata_2,
                deltat=1e3*bintime,
                m=nsub,
                normalize=True,
            )
            ccf_2_raw = mtau.correlate(
                ydata_2,
                ydata_1,
                deltat=1e3*bintime,
                m=nsub,
                normalize=True,
            )

            for result_name, raw_result in (
                ('ACF_2', acf_2_raw),
                ('CCF_1', ccf_1_raw),
                ('CCF_2', ccf_2_raw),
            ):
                taus = raw_result[1:, 0]
                frame = pd.DataFrame(
                    FCS.rebin_tau_to_grid(taus, centers, edges),
                    columns=['lagtime'],
                )
                frame[column] = FCS.rebin_chunk_to_grid(
                    taus,
                    raw_result[1:, 1],
                    centers,
                    edges,
                )
                result[result_name] = frame

            result['chunk_length_2'] = 1e3*(xdata_2[-1]-xdata_2[0])

        return result

    def _convert_process_chunk_result(self, raw_result, centers, edges):
        column = 'acf_' + raw_result['chunk_name']
        result = {
            'index': raw_result['index'],
            'chunk_name': raw_result['chunk_name'],
            'column': column,
            'chunk_length_1': raw_result['chunk_length_1'],
        }
        for result_name in ('ACF_1', 'ACF_2', 'CCF_1', 'CCF_2'):
            if result_name not in raw_result:
                continue
            raw_curve = raw_result[result_name]
            taus = raw_curve[1:, 0]
            frame = pd.DataFrame(
                FCS.rebin_tau_to_grid(taus, centers, edges),
                columns=['lagtime'],
            )
            frame[column] = FCS.rebin_chunk_to_grid(
                taus,
                raw_curve[1:, 1],
                centers,
                edges,
            )
            result[result_name] = frame
        if 'chunk_length_2' in raw_result:
            result['chunk_length_2'] = raw_result['chunk_length_2']
        result['process_id'] = raw_result['process_id']
        result['duration'] = raw_result['duration']
        return result

    def _correlate_chunks_process(
        self,
        sender,
        label0,
        chnks,
        bintime,
        nsub,
        centers,
        edges,
    ):
        default_workers = min(12, os.cpu_count() or 1)
        workers = max(
            1,
            min(
                int(
                    os.environ.get(
                        'FCSIT_TIME_BIN_WORKERS',
                        str(default_workers),
                    )
                ),
                len(chnks),
            ),
        )
        started = time.perf_counter()
        completed = 0
        with tempfile.TemporaryDirectory(prefix='fcsit_time_bin_') as temporary:
            channel_0_path = os.path.join(temporary, 'channel_0.npy')
            channel_1_path = None
            dpg.set_item_label(sender, f"{label0} | preparing data")
            np.save(channel_0_path, self.TT_ydata_1, allow_pickle=False)
            if self.IsTwoChannel:
                channel_1_path = os.path.join(temporary, 'channel_1.npy')
                np.save(channel_1_path, self.TT_ydata_2, allow_pickle=False)

            tasks = []
            for index, chunk_name in enumerate(chnks):
                start, stop = self.chunks[chunk_name]['indices']
                tasks.append(
                    (
                        index,
                        chunk_name,
                        start,
                        stop,
                        channel_0_path,
                        channel_1_path,
                        1e3*bintime,
                        nsub,
                    )
                )
            raw_results = [None] * len(tasks)
            # Windows has no fork start method. There a thread pool avoids
            # re-importing the DearPyGui entry script through spawn.
            executor_context, executor_name = _time_bin_executor(workers)
            thread_variables = (
                'OMP_NUM_THREADS',
                'OPENBLAS_NUM_THREADS',
                'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS',
            )
            previous_thread_limits = {
                variable: os.environ.get(variable)
                for variable in thread_variables
            }
            try:
                for variable in thread_variables:
                    os.environ[variable] = '1'
                with executor_context as executor:
                    futures = [
                        executor.submit(_correlate_time_bin_chunk_process, task)
                        for task in tasks
                    ]
                    for future in as_completed(futures):
                        raw_result = future.result()
                        raw_results[raw_result['index']] = raw_result
                        completed += 1
                        dpg.set_item_label(
                            sender,
                            f"{label0} | chunks {completed}/{len(chnks)}",
                        )
            finally:
                for variable, previous_value in previous_thread_limits.items():
                    if previous_value is None:
                        os.environ.pop(variable, None)
                    else:
                        os.environ[variable] = previous_value

        results = [
            self._convert_process_chunk_result(raw_result, centers, edges)
            for raw_result in raw_results
        ]
        duration = time.perf_counter() - started
        chunk_times = ', '.join(
            f"{result['index'] + 1}:{result['duration']:.3f}s/pid{result['process_id']}"
            for result in results
        )
        print(
            f"Time-bin process correlation: {duration:.3f}s total, "
            f"{workers} {executor_name}; {chunk_times}"
        )
        return results

    def _correlate_impl(self,sender,app_data,progress_label=None):
        bintime = self.round_data(dpg.get_value('left_panel_drag_time_binning'))
        chnks = list(self.chunks.keys())
        npoints = dpg.get_value('left_panel_drag_subs')
        tau_min = self.round_data(dpg.get_value('left_panel_tau_min'))
        tau_max = dpg.get_value('left_panel_tau_max')
        decades = np.round(log10(tau_max)-log10(tau_min))
        nsub = int(np.floor(1*(npoints/decades)))
        centers, edges = FCS.make_log_grid_ms(tmin_ms=tau_min, tmax_ms=tau_max, points_per_decade=nsub)

        label0 = progress_label or dpg.get_item_label(sender)
        total_chunks = len(chnks)
        try:
            results = self._correlate_chunks_process(
                sender,
                label0,
                chnks,
                bintime,
                nsub,
                centers,
                edges,
            )
        except Exception as error:
            print(
                "Time-bin process correlation failed; falling back to "
                f"sequential mode: {error}"
            )
            results = [None] * len(chnks)
            for index, chnk in enumerate(chnks):
                result = self._correlate_single_chunk_worker(
                    index,
                    chnk,
                    bintime,
                    nsub,
                    centers,
                    edges,
                )
                results[result['index']] = result
                dpg.set_item_label(
                    sender,
                    f"{label0} | chunks {index + 1}/{total_chunks}",
                )
        
        if not self.IsTwoChannel:
            acf_columns = [result['column'] for result in results]
            chunk_lengths_sec_1 = [
                result['chunk_length_1'] for result in results
            ]
            for result in results:
                self.chunks[result['chunk_name']]['ACF'] = result['ACF_1']

            acf_frames = [self.chunks[chnk]['ACF'] for chnk in chnks]
            ACFFr = pd.concat(acf_frames,axis=1)
            if dpg.get_value('left_panel_N_chunks') > 1:
                t=ACFFr['lagtime'].mean(axis=1)
                ACFFr['time'] = t
            else:
                ACFFr['time'] = ACFFr['lagtime']
            auto_ch1 = FCS._compute_MEAN_STD(ACFFr, acf_columns,chunk_lengths_sec=chunk_lengths_sec_1)
            ACFFr['MEAN'], ACFFr['SE'] = auto_ch1[:2]
            self.res_to_exp['lag_covariance_ACF_1'] = auto_ch1[2]
            self.res_to_exp['filename']=self.anal_file
            if dpg.get_value('left_panel_N_chunks') > 1: 
                self.res_to_exp['result_ACF_1']=ACFFr[['time','MEAN','SE']]
            else:
                self.res_to_exp['result_ACF_1']=ACFFr[['time','MEAN']]
            Mainmeta = self.files[self.anal_file]['Meta']
            chunk_curves = ACFFr[['time'] + acf_columns].copy()
            count_rate = self._mean_count_rate(self.TT_ydata_1, bintime)
            file_path, corr_path = self._export_correlation_pair(
                os.path.join(self.output_path, 'AutoCorr_ch1'),
                self.res_to_exp['result_ACF_1'],
                chunk_curves,
                auto_ch1[2],
                auto_ch1[3],
                count_rate,
            )
            Mainmeta =  {'Correlation':{'A_c0':file_path,
                                        'A_c0_corr':corr_path},
                         'meta':{
                             'time_bin':dpg.get_value('left_panel_drag_time_binning'),
                             'Npoints':dpg.get_value('left_panel_drag_subs'),
                             'Nchunks':dpg.get_value('left_panel_N_chunks'),
                             'custom_chunks':dpg.get_value('Custom_chunks_check'),
                             'chunks':self.chunks,
                             'tau_min':dpg.get_value('left_panel_tau_min'),
                             'tau_max':dpg.get_value('left_panel_tau_max')
                             }
                     }
            self.files[self.anal_file]['Meta']=Mainmeta
            self.SaveSinglePickle(self.anal_file)
            self.plot_ACF()
            chnkpath = os.path.join(self.output_path,self.anal_file+'.chnk')
            with open(chnkpath, "wb") as p:
                pickle.dump(self.chunks, p)
        elif self.IsTwoChannel:
            chunk_columns = [result['column'] for result in results]
            chunk_lengths_sec_1 = [
                result['chunk_length_1'] for result in results
            ]
            chunk_lengths_sec_2 = [
                result['chunk_length_2'] for result in results
            ]
            for result in results:
                chunk = self.chunks[result['chunk_name']]
                chunk['ACF_1'] = result['ACF_1']
                chunk['ACF_2'] = result['ACF_2']
                chunk['CCF_1'] = result['CCF_1']
                chunk['CCF_2'] = result['CCF_2']
            acf_1_frames = [self.chunks[chnk]['ACF_1'] for chnk in chnks]
            acf_2_frames = [self.chunks[chnk]['ACF_2'] for chnk in chnks]
            ccf_1_frames = [self.chunks[chnk]['CCF_1'] for chnk in chnks]
            ccf_2_frames = [self.chunks[chnk]['CCF_2'] for chnk in chnks]
            ACFFr_1 = pd.concat(acf_1_frames,axis=1)
            ACFFr_2 = pd.concat(acf_2_frames,axis=1)
            CCFFr_1 = pd.concat(ccf_1_frames,axis=1)
            CCFFr_2 = pd.concat(ccf_2_frames,axis=1)
            if dpg.get_value('left_panel_N_chunks') > 1:
                t=ACFFr_1['lagtime'].mean(axis=1)
                ACFFr_1['time'] = t
                t=ACFFr_2['lagtime'].mean(axis=1)
                ACFFr_2['time'] = t
                t=CCFFr_1['lagtime'].mean(axis=1)
                CCFFr_1['time'] = t
                t=CCFFr_2['lagtime'].mean(axis=1)
                CCFFr_2['time'] = t
            else:
                ACFFr_1['time'] = ACFFr_1['lagtime']
                ACFFr_2['time'] = ACFFr_2['lagtime']
                CCFFr_1['time'] = CCFFr_1['lagtime']
                CCFFr_2['time'] = CCFFr_2['lagtime']
            auto_ch1 = FCS._compute_MEAN_STD(ACFFr_1, chunk_columns,chunk_lengths_sec=chunk_lengths_sec_1)
            auto_ch2 = FCS._compute_MEAN_STD(ACFFr_2, chunk_columns,chunk_lengths_sec=chunk_lengths_sec_2)
            cross_ch1 = FCS._compute_MEAN_STD(CCFFr_1, chunk_columns,chunk_lengths_sec=chunk_lengths_sec_1)
            cross_ch2 = FCS._compute_MEAN_STD(CCFFr_2, chunk_columns,chunk_lengths_sec=chunk_lengths_sec_2)
            ACFFr_1['MEAN'], ACFFr_1['SE'] = auto_ch1[:2]
            ACFFr_2['MEAN'], ACFFr_2['SE'] = auto_ch2[:2]
            CCFFr_1['MEAN'], CCFFr_1['SE'] = cross_ch1[:2]
            CCFFr_2['MEAN'], CCFFr_2['SE'] = cross_ch2[:2]
            self.res_to_exp['lag_covariance_ACF_1'] = auto_ch1[2]
            self.res_to_exp['lag_covariance_ACF_2'] = auto_ch2[2]
            self.res_to_exp['lag_covariance_CCF_1'] = cross_ch1[2]
            self.res_to_exp['lag_covariance_CCF_2'] = cross_ch2[2]
            self.res_to_exp['filename']=self.anal_file
            if dpg.get_value('left_panel_N_chunks') > 1: 
                self.res_to_exp['result_ACF_1']=ACFFr_1[['time','MEAN','SE']]
                self.res_to_exp['result_ACF_2']=ACFFr_2[['time','MEAN','SE']]
                self.res_to_exp['result_CCF_1']=CCFFr_1[['time','MEAN','SE']]
                self.res_to_exp['result_CCF_2']=CCFFr_2[['time','MEAN','SE']]
            else:
                self.res_to_exp['result_ACF_1']=ACFFr_1[['time','MEAN']]
                self.res_to_exp['result_ACF_2']=ACFFr_2[['time','MEAN']]
                self.res_to_exp['result_CCF_1']=CCFFr_1[['time','MEAN']]
                self.res_to_exp['result_CCF_2']=CCFFr_2[['time','MEAN']]
            Mainmeta = self.files[self.anal_file]['Meta']
            count_rate_1 = self._mean_count_rate(self.TT_ydata_1, bintime)
            count_rate_2 = self._mean_count_rate(self.TT_ydata_2, bintime)
            file_path_A1, corr_path_A1 = self._export_correlation_pair(
                os.path.join(self.output_path, 'AutoCorr_ch1'),
                self.res_to_exp['result_ACF_1'],
                ACFFr_1[['time'] + chunk_columns],
                auto_ch1[2],
                auto_ch1[3],
                count_rate_1,
            )
            file_path_A2, corr_path_A2 = self._export_correlation_pair(
                os.path.join(self.output_path, 'AutoCorr_ch2'),
                self.res_to_exp['result_ACF_2'],
                ACFFr_2[['time'] + chunk_columns],
                auto_ch2[2],
                auto_ch2[3],
                count_rate_2,
            )
            file_path_C1, corr_path_C1 = self._export_correlation_pair(
                os.path.join(self.output_path, 'CrossCorr_ch1'),
                self.res_to_exp['result_CCF_1'],
                CCFFr_1[['time'] + chunk_columns],
                cross_ch1[2],
                cross_ch1[3],
                count_rate_1,
            )
            file_path_C2, corr_path_C2 = self._export_correlation_pair(
                os.path.join(self.output_path, 'CrossCorr_ch2'),
                self.res_to_exp['result_CCF_2'],
                CCFFr_2[['time'] + chunk_columns],
                cross_ch2[2],
                cross_ch2[3],
                count_rate_2,
            )
            Mainmeta =  {'Correlation':{'A_c0':file_path_A1,
                                        'A_c1':file_path_A2,
                                        'C_c0':file_path_C1,
                                        'C_c1':file_path_C2,
                                        'A_c0_corr':corr_path_A1,
                                        'A_c1_corr':corr_path_A2,
                                        'C_c0_corr':corr_path_C1,
                                        'C_c1_corr':corr_path_C2,
                                       },
                     'meta':{
                         'time_bin':dpg.get_value('left_panel_drag_time_binning'),
                         'Npoints':dpg.get_value('left_panel_drag_subs'),
                         'Nchunks':dpg.get_value('left_panel_N_chunks'),
                         'custom_chunks':dpg.get_value('Custom_chunks_check'),
                         'chunks':self.chunks,
                         'tau_min':dpg.get_value('left_panel_tau_min'),
                         'tau_max':dpg.get_value('left_panel_tau_max')
                         }
                 }
            self.files[self.anal_file]['Meta']=Mainmeta
            self.SaveSinglePickle(self.anal_file)
            self.callback_crossCorr_check(
                'DUMMY',
                dpg.get_value('FCS_cross_check'),
            )
            self.plot_ACF()
            chnkpath = os.path.join(self.output_path,self.anal_file+'.chnk')
            with open(chnkpath, "wb") as p:
                pickle.dump(self.chunks, p)

        dpg.set_item_label(sender, label0)

    def correlate(self, sender, app_data, progress_label=None):
        old_button_label = dpg.get_item_label(sender)
        dpg.bind_item_theme(sender, "fit_button_theme_busy")
        try:
            effective_progress_label = (
                progress_label
                if progress_label is not None
                else "Correlating file 1/1"
            )
            return self._correlate_impl(
                sender,
                app_data,
                effective_progress_label,
            )
        finally:
            dpg.bind_item_theme(sender, "fit_button_theme")
            dpg.set_item_label(sender, old_button_label)

    def _release_loaded_measurement(self):
        """Release large arrays before loading the next independent file."""
        self.TT_xdata_1 = np.empty(0, dtype=float)
        self.TT_ydata_1 = np.empty(0, dtype=np.int64)
        self.TT_xdata_2 = np.empty(0, dtype=float)
        self.TT_ydata_2 = np.empty(0, dtype=np.int64)
        self.TT_xdata_1_chunked = np.empty(0, dtype=float)
        self.TT_ydata_1_chunked = np.empty(0, dtype=float)
        self.TT_xdata_2_chunked = np.empty(0, dtype=float)
        self.TT_ydata_2_chunked = np.empty(0, dtype=float)
        self.chunks = {}
        self.res_to_exp = {}
        gc.collect()
        try:
            malloc_trim = ctypes.CDLL(None).malloc_trim
            malloc_trim.argtypes = [ctypes.c_size_t]
            malloc_trim.restype = ctypes.c_int
            malloc_trim(0)
        except (AttributeError, OSError):
            pass

    def _archive_measurement_session(self, filename):
        """Move a completed session out of the input directory."""
        source = os.path.join(self.last_directory, filename + '.pck')
        destination_directory = os.path.dirname(self.output_path)
        destination = os.path.join(destination_directory, filename + '.pck')
        if os.path.isfile(source):
            os.replace(source, destination)
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    def correlate_all(self,sender,app_data):
        dpg.set_value('Custom_chunks_check',False)
        old_button_label = dpg.get_item_label('Correlate_all_button')
        dpg.bind_item_theme('Correlate_all_button', "fit_button_theme_busy")
        try:
            for i, file in enumerate(self.files):
                if i > 0:
                    self._release_loaded_measurement()
                fittin_label = f"Correlating file {i + 1}/{len(self.files)}"
                dpg.set_item_label('Correlate_all_button',fittin_label)
                dpg.set_value('file_box',file)
                if i > 0 or self.anal_file != file:
                    self.callback_listbox('file_box',file)
                self.correlate(
                    'Correlate_all_button',
                    None,
                    progress_label=fittin_label,
                )
                self._archive_measurement_session(file)
        finally:
            dpg.bind_item_theme('Correlate_all_button', "fit_button_theme")
            dpg.set_item_label('Correlate_all_button',old_button_label)
            
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    def CheckForPickle(self, path):
        return os.path.isfile(path)

        
    def ReadPickle(self,path):
        with open(path, "rb") as f:
            data = pickle.load(f)

        return data
        
    def SaveAllPickles(self):
        for f in self.files:
            pickle_path = os.path.join(self.last_directory,f+'.pck')
            with open(pickle_path, "wb") as p:
                pickle.dump(self.files[f], p)

    def SaveSinglePickle(self,file):
        pickle_path = os.path.join(self.last_directory,file+'.pck')
        with open(pickle_path, "wb") as p:
            pickle.dump(self.files[file], p)
        
            
    def UpdataMETA(self):
        for fil in list(self.files.keys()):
            pikle_path= os.path.join(self.last_directory,fil+'.pck')
            if self.CheckForPickle(pikle_path):
                self.files[fil] = self.ReadPickle(pikle_path)
    
    def callback_directory_select(self, sender, app_data):
        self.last_directory = app_data['current_path']
        fls = os.listdir(self.last_directory)
        fls = [f for f in fls if (f.endswith('.dat')) or (f.endswith('.csv')) or (f.endswith('.txt'))]
        fls = [f for f in fls if self.text_file_check(os.path.join(self.last_directory,f))]
        self.files = {}
        c0f = []
        c1f = []
        for f in fls:
            if '_c0' in f:
                chan = '_c0'
                c0f.append(f)
                self.files[f[:-4].replace(chan,'')] = {'Channels':{},
                                                       'Meta':None
                                                      }
            elif '_c1' in f:
                chan = '_c1'
                c1f.append(f)
                self.files[f[:-4].replace(chan,'')] = {'Channels':{},
                                                       'Meta':None
                                                      }
            else:
                chan = ''
                c0f.append(f)
                self.files[f[:-4].replace(chan,'')] = {'Channels':{},
                                                       'Meta':None
                                                      }
        for f in fls:
            if '_c0' in f:
                chan = '_c0'
                self.files[f[:-4].replace(chan,'')]['Channels'][chan] = f
            elif '_c1' in f:
                chan = '_c1'
                self.files[f[:-4].replace(chan,'')]['Channels'][chan] = f
            else:
                chan = ''
                self.files[f[:-4].replace(chan,'')]['Channels']['_c0'] = f

        self.files = dict(sorted(self.files.items(), key=lambda item: natural_sort_key(item[0])))
        if not self.files:
            self.anal_file = ''
            dpg.configure_item('file_box', items=(), default_value='')
            self.show_error('No supported time-binned data files were found in the selected directory.')
            return
        self.UpdataMETA()
        self.anal_file = list(self.files.keys())[0]
        dpg.configure_item('file_box', items=list(self.files.keys()),default_value = self.anal_file)
        self.load_data(self.anal_file)
        self.show_error('Use the same folder as the output directory for correlated data? ')
        self.basf.log_last_directory(self.last_directory)
        self.update_default_directory(self.last_directory)


        
    #########################################################################           
    #########################################################################           
    ######################################################################### 
    
    def show_error(self,error_text):
        try:
            dpg.add_window(pos=(400,150),
                           label='Error!',
                           tag='No_data_files',
                           no_move=True,
                           no_close=True,
                           no_title_bar=False,
                           no_resize=True,
                           show=True,
                           modal=False
                           )
            dpg.add_text(error_text,tag='no_files_error_text',
                     parent='No_data_files')
            with dpg.group(tag='no_files_error_text_butt_group',parent='No_data_files',horizontal=True,
                           horizontal_spacing=self.group_spacer
                  ):
                dpg.add_button(label='Yes',
                               parent='no_files_error_text_butt_group',
                               tag='yes_files_error_butt',
                               callback=self.callback_dialog_show_error_yes
                              )
            
                dpg.add_button(label='No',
                               parent='no_files_error_text_butt_group',
                               tag='no_files_error_butt',
                               callback=self.callback_dialog_show_error_no
                              )
            dpg.bind_item_theme('No_data_files', 'Error_window_theme')
        except:
            dpg.show_item('No_data_files')
            
    #########################################################################           
    #########################################################################           
    #########################################################################
                
    def callback_listbox(self,sender,app_data):
        self.anal_file = app_data
        self.load_data(self.anal_file)
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
                    
            
    def mount_TIME_BIN_Corr_handlers(self):
        dpg.add_key_press_handler(tag ='keyword_handler_TIME_BIN_Corr',
                                  callback=self.callback_TIME_BIN_Corr_Keyword_key,
                                  parent = 'handlers_registry')
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    
    def callback_TIME_BIN_Corr_Keyword_key(self,sender, app_data):
        dlgs = []
        for d in self.DialWinList:
            chck = dpg.is_item_shown(d)
            dlgs.append(chck)
        if not any(dlgs):
            if app_data in self.active_keys:
                self.all_items = dpg.get_aliases()
                if 'file_box' in self.all_items:
                    self.file_box_items = dpg.get_item_configuration('file_box')['items']
                    if len(self.file_box_items)!=0:
                        def_val = dpg.get_value('file_box')
                        index = self.file_box_items.index(def_val)
                        if app_data == self.up_key:
                            if index!=0:
                                index=index-1
                                dpg.set_value('file_box',self.file_box_items[index])
                                self.callback_listbox('file_box',self.file_box_items[index])
                            else:
                                pass
                        if app_data == self.down_key:
                            if index!=len(self.file_box_items)-1:
                                index=index+1
                                dpg.set_value('file_box',self.file_box_items[index])
                                self.callback_listbox('file_box',self.file_box_items[index])
                            else:
                                pass
                    
    def on_drag_line_drag(self,sender, sender_value, user_data):
        if user_data:  
            return None
        dpg.add_mouse_release_handler(button=0,
                                      callback=self.on_drag_line_release,
                                      user_data=sender,
                                      parent='handlers_registry')
        dpg.configure_item(sender, user_data=True)

    def on_drag_line_release(self,sender, sender_value, user_data):
        self.callback_chunk_drag_line(user_data,None,None)
        dpg.configure_item(user_data, user_data=False)
        dpg.delete_item(sender)    
    
    def callback_chunk_drag_line(self,sender,app_data,user_data):
        chunk_line = sender
        if isinstance(chunk_line, int):
            line_name = dpg.get_item_alias(chunk_line)
        elif isinstance(chunk_line, str):
            line_name = sender
            
        value = dpg.get_value(line_name)
        xdata1 = self.TT_xdata_1
        maxtime = xdata1.max()
        if len(self.channels) == 2:
            xdata2 = self.TT_xdata_2
            
        chunk_num = int(line_name.split('_')[2])-1
        chunk_line_end = line_name.split('_')[3]
        if not self.IsTwoChannel:
            if chunk_line_end == 'start':
                if value>dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'):
                    dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'))
                else:
                    if chunk_num !=0:
                        if value<dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'):
                            dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'))
                    else:
                        if value<0:
                            dpg.set_value(sender,0)
                        else:
                            pass
            elif chunk_line_end == 'stop':
                if value<dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'):
                    dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'))
                else:
                    if chunk_num+1 !=dpg.get_value('left_panel_N_chunks'):
                        if value>dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'):
                            dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'))
                    else:
                        if value>self.chunks['chunk_'+str(chunk_num)]['values'][1]:
                            dpg.set_value(sender,self.chunks['chunk_'+str(chunk_num)]['values'][1])
                        else:
                            pass
        elif self.IsTwoChannel:
            if chunk_line_end == 'start':
                if value>dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline') or value>dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_stop_dragline'):
                    dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'))
                    dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_stop_dragline'))
                else:
                    if chunk_num !=0:
                        if value<dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline') or value<dpg.get_value('Chunk_2_'+str(chunk_num)+'_stop_dragline'):
                            dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'))
                            dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num)+'_stop_dragline'))
                            value = dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline')
                    else:
                        if value<0:
                            dpg.set_value(sender,0)
                        else:
                            pass
            elif chunk_line_end == 'stop':
                if value<dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline') or  value<dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_start_dragline'):
                    dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'))
                    dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_start_dragline'))
                    value = dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline')
                else:
                    if chunk_num+1 !=dpg.get_value('left_panel_N_chunks'):
                        if value>dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline') or value>dpg.get_value('Chunk_2_'+str(chunk_num+2)+'_start_dragline'):
                            dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'))
                            dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+2)+'_start_dragline'))
                    else:
                        if value>maxtime:
                            dpg.set_value(sender,maxtime)
                        else:
                            pass
            value = dpg.get_value(line_name)
            if 'Chunk_1' in line_name:
                co_line_name = line_name.replace('Chunk_1','Chunk_2')
            elif 'Chunk_2' in line_name:
                co_line_name = line_name.replace('Chunk_2','Chunk_1')
            dpg.set_value(co_line_name,value)
        exponent = int(np.round((log10(dpg.get_value('left_panel_drag_time_binning')))))
        if exponent <0:
            ind =int(np.round(value/dpg.get_value('left_panel_drag_time_binning')))
            minval= dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline')
            maxval= dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline')
        if chunk_line_end == 'start':
            self.chunks['chunk_'+str(chunk_num)]['values'][0] = xdata1[ind]
            self.chunks['chunk_'+str(chunk_num)]['indices'][0] = ind
            self.chunks['chunk_'+str(chunk_num)]['values'][1] = maxval
            self.chunks['chunk_'+str(chunk_num)]['indices'][1] = int(np.round(maxval/dpg.get_value('left_panel_drag_time_binning')))
        elif chunk_line_end == 'stop':
            self.chunks['chunk_'+str(chunk_num)]['values'][1] = xdata1[ind]
            self.chunks['chunk_'+str(chunk_num)]['indices'][1] = ind
            self.chunks['chunk_'+str(chunk_num)]['values'][0] = maxval
            self.chunks['chunk_'+str(chunk_num)]['indices'][0] = int(np.round(minval/dpg.get_value('left_panel_drag_time_binning')))
        self.calculate_shade()
        self.plot_TT()
         
        
    def transfer_chunks_to_TT(self):
        self.TT_ydata_1_chunked = np.array([])
        self.TT_xdata_1_chunked = np.array([])
        for chunk in self.chunks.keys():
            xdata = self.TT_xdata_1
            ydata = self.TT_ydata_1
            irenage = self.chunks[chunk]['indices']
            chunked = self.TT_xdata_1_chunked
            chunked=np.append(chunked,xdata[irenage[0]:irenage[1]])
            self.TT_xdata_1_chunked = chunked
            chunked = self.TT_ydata_1_chunked
            chunked=np.append(chunked,ydata[irenage[0]:irenage[1]])
            self.TT_ydata_1_chunked = chunked
                
    def on_chunks_released(self,sender, app_data):
        value = dpg.get_value("left_panel_N_chunks")
        self.add_chunks()  
        self.calculate_shade()
        self.plot_TT()

    
    def calculate_shade(self):
        customchnk = dpg.get_value('Custom_chunks_check')
        meta = self.chunks
        keys =list(meta.keys() )
        ind = []
        y1 = []
        y2 = []
        rngmax=self.TT_ydata_1.max()
        xdt = self.TT_xdata_1
        shade_on = []
        for i,key in enumerate(keys):
            l = meta[key]['indices']
            shade_on.append(tuple(l))
        _shade_on1= np.zeros_like(xdt)
        for start, end in shade_on:
            _shade_on1[start:end] = rngmax
        segments_x = []
        segments_y1 = []
        segments_y2 = []
        current_value = _shade_on1[0]
        start_idx = 0
        for i in range(1, len(_shade_on1)):
            if _shade_on1[i] != current_value:
                end_idx = i - 1
                segments_x.extend([xdt[start_idx], xdt[end_idx]])
                segments_y1.extend([0, 0])
                segments_y2.extend([current_value, current_value])
                start_idx = i
                current_value = _shade_on1[i]
        end_idx = len(_shade_on1) - 1
        segments_x.extend([xdt[start_idx], xdt[end_idx]])
        segments_y1.extend([0, 0])
        segments_y2.extend([current_value, current_value])
        self.shade_data_1=[np.array(segments_x),
                           np.array(segments_y1),
                           np.array(segments_y2)
                           ]
        if self.IsTwoChannel:
            rngmax2=self.TT_ydata_2.max()
            self.shade_data_2=[np.array(segments_x),
                           np.array(segments_y1),
                           np.where(np.array(segments_y2)==rngmax,rngmax2,0)]


    def callback_dialog_show_error_yes(self,sender,app_data):
        self.callback_save_path(None,{'current_path':self.last_directory})
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('no_files_error_butt')
        dpg.delete_item('no_files_error_text_butt_group')
        dpg.delete_item('No_data_files')
        
    def callback_dialog_show_error_no(self,sender,app_data):
        dpg.configure_item('No_data_files',show=False)
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('no_files_error_butt')
        dpg.delete_item('no_files_error_text_butt_group')
        dpg.delete_item('No_data_files')
        dpg.show_item('file_dialog_save_correlated')
    
    def callback_save_path(self,sender,app_data):
        path = app_data['current_path']
        corrpath = os.path.join(path,'Correlation_curves')
        if os.path.exists(corrpath):
            pass
        else:
            os.mkdir(corrpath)
        auto_1_path = os.path.join(corrpath,'AutoCorr_ch1')
        auto_2_path = os.path.join(corrpath,'AutoCorr_ch2')
        cross_1_path = os.path.join(corrpath,'CrossCorr_ch1')
        cross_2_path = os.path.join(corrpath,'CrossCorr_ch2')
        if os.path.exists(auto_1_path):
            pass
        else:
            os.mkdir(auto_1_path)
        if os.path.exists(auto_2_path):
            pass
        else:
            os.mkdir(auto_2_path)
        if os.path.exists(cross_1_path):
            pass
        else:
            os.mkdir(cross_1_path)
        if os.path.exists(cross_2_path):
            pass
        else:
            os.mkdir(cross_2_path)
        # dpg.set_value('display_savepath_text',corrpath)
        # dpg.set_value('display_savepath_text_tooltip_text',dpg.get_value('display_savepath_text'))
        self.output_path = corrpath
        fb_items = dpg.get_item_configuration('file_box')['items']
        if len(fb_items) != 0:
            dpg.configure_item('Correlate_once_button',enabled=True)
            dpg.configure_item('Correlate_all_button',enabled=True)
            dpg.configure_item('Correlate_once_button',callback=self.correlate)
        else:
            pass
        
        
        
        
    def update_default_directory(self, last_directory):
        dpg.configure_item('file_dialog_id_TB', default_path=last_directory)
        dpg.configure_item('file_dialog_save_correlated', default_path=last_directory)
