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
from Methods.PTU_Corr.include.Third_party.readPTU_FLIM import PTUreader, PTUHeaderReader
from include.fcsutils import load_fcs
import pickle
import time
import include.INIT as inits
from include.INIT import _basicF as _bf
logfile=os.path.join('Logs','log.txt')
bf = inits._basicF(logfile,None)
lprint = bf.lnprint
import time
import socket
import argparse
from functools import wraps
from datetime import datetime
import inspect

class _PTU_Corr_init:
    lprint = _bf.lnprint
    def __init__(self,
                 size_ratio,
                 left_indent,
                 internal_indent,
                 right_indent,
                 bottom_indent,
                 top_indent,
                 group_spacer,
                 font_size,
                 last_directory):
        self.last_directory = last_directory
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
        
        self.Anal_window = {'name':'Anal_window',
                            'width':dpg.get_viewport_width()-self.left_indent-self.file_window['width']-self.internal_indent-self.right_indent,
                            'height':self.file_window['height']-self.internal_indent-self.TT_window['height'],
                            'pos':(self.file_window['pos'][0]+self.file_window['width']+self.internal_indent,
                                  self.TT_window['pos'][1]+self.TT_window['height']+self.internal_indent)
                            }
        
        self.file_dialog_id_PTU = {'name':'file_dialog_id_PTU',
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
        self.TT_subplots = {'name':'TT_subplots',
                         'rows':1,
                         'columns':1,
                         'row_ratios':[1.00],
                         'width':-1,
                         'height':-1
                        }
        self.Update_TCSPC_histogram ={'name':'Update_TCSPC_histogram',
                                      'width':int(200*self.size_ratio['width'])}
        self.TCSPC_subplots = {'name':'TCSPC_subplots',
                               'rows':1,
                               'columns':1,
                               'column_ratios':[1.00],
                               'width':-1,
                               'height':-1
                               }
        self.FCS_subplots = {'name':'FCS_subplots',
                             'rows':1,
                             'columns':1,
                             'column_ratios':[1.00],
                             'width':-1,
                             'height':-1
                             }
        
        
        self.left_panel_tab_1 = {'name':'left_panel_tab_1',
                                 'width':-1}
        self.left_panel_tab_1_col_1 = {'name':'left_panel_tab_1_col_1',
                                       'width':self.internal_width_left_panel/2}
        self.left_panel_tab_1_col_2 = {'name':'left_panel_tab_1_col_2',
                                       'width':self.internal_width_left_panel/2}

        self.left_panel_tab_2 = {'name':'left_panel_tab_2',
                                 'width':-1}
        self.left_panel_tab_2_col_1 = {'name':'left_panel_tab_2_col_1',
                                       'width':self.internal_width_left_panel/2}
        self.left_panel_tab_2_col_2 = {'name':'left_panel_tab_2_col_2',
                                       'width':self.internal_width_left_panel/2}
        
        self.left_panel_drag_time_binning = {'name':'left_panel_drag_time_binning',
                                             'width':-1,
                                             'default_time_bin':np.round(1.0e-3,3)}
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
        self.left_panel_tau_min = {'name':'left_panel_tau_min',
                                   'width':-1,
                                   'default_value':1e-3,
                                   'speed':0.001}
        self.left_panel_tau_max = {'name':'left_panel_tau_max',
                                   'width':-1,
                                   'default_value':1e2,
                                   'speed':1}
        self.TCSPC_dralines_init_values = {'TCSPC_L_dline_ch1':0.2,
                                           'TCSPC_U_dline_ch1':24.9,
                                           'TCSPC_L_dline_ch2':0.2,
                                           'TCSPC_U_dline_ch2':24.9,
                                           'TCSPC_PIE_L_dline_ch1':25.2,
                                           'TCSPC_PIE_U_dline_ch1':49.5,
                                           'TCSPC_PIE_L_dline_ch2':0.2,
                                           'TCSPC_PIE_U_dline_ch2':24.9,
                        }
        self.drag_line_thickness  = 2
        self.Calculate_filter_once_button ={'name':'Calculate_filter_once_button','width':-1}
        self.Calculate_filter_all_button ={'name':'Calculate_filter_all_button','width':-1}
        self.Calculate_correlation_once_button ={'name':'Calculate_correlation_once_button','width':-1}
        self.Calculate_correlation_all_button ={'name':'Calculate_correlation_all_button','width':-1}
        self.Export_correlation_curve_button ={'name':'Export_correlation_curve_button','width':-1}
        self.Export_all_correlation_curves_button ={'name':'Export_all_correlation_curves_button','width':-1}

        
class _PTU_Corr_common:
    def __init__(self,
                 INIT,
                 last_directory,
                 basf,
                 menu,
                 globalITEMS,
                 ):
        
        self.method_init=INIT
        self.basf=basf

        self.callback_listbox = self.timed(self.callback_listbox)
        self.callback_calc_fltr_one = self.timed(self.callback_calc_fltr_one)
        self.callback_calc_corr_one = self.timed(self.callback_calc_corr_one)
        
        self.menu=menu
        self.size_ratio = self.method_init.size_ratio 
        self.group_spacer = self.method_init.group_spacer
        self.internal_width_left_panel = self.method_init.internal_width_left_panel
        self.left_panel_drag_time_binning = self.method_init.left_panel_drag_time_binning
        self.last_directory = basf.recall_last_directory()
        self.output_path = self.last_directory
        self.channels = {'Channel_0':[]}
        self.globalITEMS = globalITEMS
        self.up_key = dpg.mvKey_Up
        self.down_key = dpg.mvKey_Down
        self.TT_subplots = self.method_init.TT_subplots
        self.TCSPC_subplots = self.method_init.TCSPC_subplots
        self.FCS_subplots = self.method_init.FCS_subplots
        self.TCSCP_draglines = self.method_init.TCSPC_dralines_init_values.copy()#TCSCP_draglines
        self.TCSCP_draglines_init = self.method_init.TCSPC_dralines_init_values.copy()#TCSCP_draglines.copy()
        self.drag_line_thickness = self.method_init.drag_line_thickness
        self.directory = ''
        self.new_directory = ''
        self.files = ()
        self.anal_file = ''
        self.active_keys = [dpg.mvKey_Up,
                            dpg.mvKey_Down,
                           ]
        self.TT_ydata_1 = np.empty(10)
        self.TT_xdata_1 = np.empty(10)
        self.TT_ydata_2 = np.empty(10)
        self.TT_xdata_2 = np.empty(10)
        self.shade_data_1=[np.empty(10),
                           np.empty(10),
                           np.empty(10)
                           ]
        self.shade_data_2=[np.empty(10),
                           np.empty(10),
                           np.empty(10)
                           ]
        self.TT_x_axis_limits_1 = ()
        self.TT_y_axis_limits_1 = ()
        self.TT_x_axis_limits_2 = ()
        self.TT_y_axis_limits_2 = ()
        self.TT_ydata_1_chunked = np.empty(10)
        self.TT_xdata_1_chunked = np.empty(10)
        self.TT_ydata_2_chunked = np.empty(10)
        self.TT_xdata_2_chunked = np.empty(10)
        self.active_tcspcs_ch1_L_inds = []
        self.active_tcspcs_ch1_U_inds = []
        self.active_tcspcs_ch2_L_inds = []
        self.active_tcspcs_ch2_U_inds = []
        self.inactive_tcspcs_ch1_L_inds = []
        self.inactive_tcspcs_ch1_U_inds = []
        self.inactive_tcspcs_ch2_L_inds = []
        self.inactive_tcspcs_ch2_U_inds = []
        self.CURVES = {}
        self.Filters = {}
        self.ww=450
        self.corr_export_all=None
        self.corr_export_ext = None
        self.META_data = {'TT info':{},
                          'TCSPC info':{'Filters':{}},
                          'FCS info':{}
                          }
        self.TT_draglines_positions = {}
        self.autoNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.autoNorm_ch_2 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.CrossNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.CrossNorm_ch_2  = pd.DataFrame(columns=['time','MEAN','SE'])
        self.DictOfChunks = {}
        self.DialWinLis = []
        self.status_label = ''
        self.status_label_0 = 'Calculating '
        self.status_label_N = ''

        self._chunk_draglines = []          # tagi dragline’ów, które stworzyliśmy
        self._bulk_updating_chunks = False  # blokada ciężkich aktualizacji w callbackach (opcjonalnie)
        
    #########################################################################           
    #########################################################################           
    #########################################################################   
    
    def timed(self, func):
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
                f"{func.__qualname__} | file: {self.anal_file} |{duration:.6f}s\n"
            )
            with open(tfile, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[{hostname}] {func.__qualname__} took {duration:.4f}s")
            return result

        return wrapper
        
    def define_file_menu_callbacks(self):
        dpg.configure_item('open_menu_item',callback=self.callback_Open_PTU_data)
        dpg.configure_item('Forget_menu_item',callback=self.callback_Forget_PTU_data)
        dpg.configure_item('ForgetAll_menu_item',callback=self.callback_Forget_all_PTU_data)
        dpg.configure_item('Save_corr_item',callback=lambda: dpg.show_item('file_dialog_save_correlated'))

    #########################################################################
    #########################################################################
    #########################################################################

    def on_drag_line_drag(self,sender, sender_value, user_data):
        if user_data:  
            return None
        dpg.add_mouse_release_handler(button=0, callback=self.on_drag_line_release, user_data=sender,parent='handlers_registry')
        dpg.configure_item(sender, user_data=True)

    def on_drag_line_release(self,sender, sender_value, user_data):
        self.callback_chunk_drag_line(user_data,None,None)
        dpg.configure_item(user_data, user_data=False)
        dpg.delete_item(sender)

    
    def callback_Forget_PTU_data(self):
        if self.anal_file !='':
            if os.path.exists(os.path.join(self.last_directory,self.anal_file)):
                file =self.anal_file.replace('.ptu','.pd1')
                if os.path.exists(os.path.join(self.last_directory,file)):
                    os.remove(os.path.join(self.last_directory,file))
                    self.load_data(os.path.join(self.last_directory,self.anal_file))
                else:
                    pass
            else:
                pass
    

    def callback_Forget_all_PTU_data(self):
        if self.anal_file !='':
            for file in self.files:
                path = os.path.join(self.last_directory,file)
                path =path.replace('.ptu','.pd1')
                if os.path.exists(path):
                    os.remove(path)
                else:
                    pass
        else:
            pass
        
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
        
        
    def callback_Open_PTU_data(self,sender,app_data):
        dpg.show_item('file_dialog_id_PTU')

    #########################################################################           
    #########################################################################           
    #########################################################################   

    def _after_chunks_changed(self):
        # jedna, wspólna ścieżka “commit”
        self.META_data['TT info'] = self.TT_snapshot()
        # if dpg.get_value('Custom_chunks_check'):
        self.calculate_shade()
        self.plot_TT()


    def _recompute_tcspc_for_all_chunks(self):
        # cache exact_time
        cache = getattr(self, "_tcspc_cache", None)
        if not cache:
            self._build_tcspc_time_cache()
            cache = self._tcspc_cache
    
        ph_ch = cache["channels"]
        nsel = len(self.channels)
    
        if nsel == 1:
            chan = ph_ch[0]
            exact = cache["exact_time"][chan]
            chn = 'ch1' if chan.endswith('_0') else ('ch2' if chan.endswith('_1') else 'ch1')
    
            for i in range(len(self.chunks)):
                ch = self.chunks.get(f"chunk_{i}")
                if ch is None:
                    continue
                t_start, t_stop = map(float, ch["values"])
                s, e = self._tcspc_indices_from_time(exact, t_start, t_stop)
                ch["tcspc"][chn][0] = s
                ch["tcspc"][chn][1] = e
    
        else:
            exact1 = cache["exact_time"][ph_ch[0]]
            exact2 = cache["exact_time"][ph_ch[1]]
    
            for i in range(len(self.chunks)):
                ch = self.chunks.get(f"chunk_{i}")
                if ch is None:
                    continue
                t_start, t_stop = map(float, ch["values"])
                s1, e1 = self._tcspc_indices_from_time(exact1, t_start, t_stop)
                s2, e2 = self._tcspc_indices_from_time(exact2, t_start, t_stop)
                ch["tcspc"]["ch1"][0] = s1
                ch["tcspc"]["ch1"][1] = e1
                ch["tcspc"]["ch2"][0] = s2
                ch["tcspc"]["ch2"][1] = e2
    
    def add_chunks(self, reset: bool = True):
        """
        Szybkie, deterministyczne tworzenie/przebudowa dragline’ów chunków.
    
        reset=True:
            - tworzy domyślne chunki (równe odcinki) i przebudowuje dragline’y
        reset=False:
            - próbuje użyć istniejących self.chunks['chunk_i']['values']
            - jeśli brak lub zła długość -> zachowuje się jak reset=True
    
        UWAGA: Ta funkcja NIE woła callbacków chunk dragline, NIE robi shade/plot.
        """
    
        nchunks = int(dpg.get_value('left_panel_N_chunks'))
        xdata = self.TT_xdata_1  # rosnące
    
        # --- init cache tagów (żeby nie używać dpg.get_aliases())
        if not hasattr(self, "_chunk_draglines"):
            self._chunk_draglines = []
    
        # --- 1) usuń stare dragline’y tylko z własnej listy (brak leaka)
        for tag in self._chunk_draglines:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        self._chunk_draglines.clear()
    
        # --- 2) usuń stare wpisy chunków z globalITEMS.windows (żeby nie rosło)
        if hasattr(self, "globalITEMS") and hasattr(self.globalITEMS, "windows"):
            self.globalITEMS.windows = [
                w for w in self.globalITEMS.windows
                if not (isinstance(w, str) and w.startswith("Chunk_") and w.endswith("_dragline"))
            ]
    
        # --- 3) kanały danych (do nazwy ch1/ch2 i struktury tcspc)
        photon_channels = [ch for ch in self.fcs_data.PHOTONS.keys() if ch.startswith("channel_")]
        photon_channels.sort()
        nsel = len(self.channels)  # 1 lub 2
    
        # --- 4) węzły TT (indeksy)
        nodes = np.linspace(0, len(xdata), nchunks + 1).astype(int)
    
        # --- 5) jeśli reset=False, ale chunks brak / zła długość -> wymuś reset
        if not reset:
            if (not hasattr(self, "chunks")) or (not isinstance(self.chunks, dict)) or (len(self.chunks) != nchunks):
                reset = True
    
        # --- 6) zbuduj domyślne chunki, jeśli reset
        if reset:
            self.chunks = {}
    
            # minimalnie: values+indices; tcspc możesz uzupełnić później w callbacku dragu
            if nsel == 1 and len(photon_channels) >= 1:
                ch0 = photon_channels[0]
                chn = 'ch1' if ch0.endswith('_0') else ('ch2' if ch0.endswith('_1') else 'ch1')
    
            for i in range(nchunks):
                a = int(nodes[i])
                b = int(nodes[i + 1]) - 1
                v0 = float(xdata[a])
                v1 = float(xdata[b])
    
                if nsel == 1:
                    self.chunks[f"chunk_{i}"] = {
                        "values": [v0, v1],
                        "indices": [a, b],
                        "tcspc": {chn: [0, 0]},   # placeholder, policzysz przy pierwszym dragu / osobno
                    }
                else:
                    self.chunks[f"chunk_{i}"] = {
                        "values": [v0, v1],
                        "indices": [a, b],
                        "tcspc": {"ch1": [0, 0], "ch2": [0, 0]},  # placeholder
                    }
    
        # --- 7) utwórz dragline’y na bazie self.chunks
        new_window_tags = []
    
        for i in range(nchunks):
            ch = self.chunks.get(f"chunk_{i}")
            if ch is None:
                # awaryjnie, gdy self.chunks jest niekompletne:
                a = int(nodes[i])
                b = int(nodes[i + 1]) - 1
                v0 = float(xdata[a])
                v1 = float(xdata[b])
            else:
                v0, v1 = ch["values"]
    
            # plot_1
            t1s = f"Chunk_1_{i+1}_start_dragline"
            t1e = f"Chunk_1_{i+1}_stop_dragline"
    
            dpg.add_drag_line(
                label=f"Chunk {i+1} start",
                tag=t1s,
                color=[255, 0, 0, 255],
                default_value=v0,
                parent="plot_1",
                show=False,
                callback=self.on_drag_line_drag,
            )
            dpg.add_drag_line(
                label=f"Chunk {i+1} stop",
                tag=t1e,
                color=[255, 0, 0, 255],
                default_value=v1,
                parent="plot_1",
                show=False,
                callback=self.on_drag_line_drag,
            )
    
            self._chunk_draglines.extend([t1s, t1e])
            new_window_tags.extend([t1s, t1e])
    
            # plot_2 jeśli 2 kanały
            if nsel == 2:
                t2s = f"Chunk_2_{i+1}_start_dragline"
                t2e = f"Chunk_2_{i+1}_stop_dragline"
    
                dpg.add_drag_line(
                    label=f"Chunk {i+1} start",
                    tag=t2s,
                    color=[255, 0, 0, 255],
                    default_value=v0,
                    parent="plot_2",
                    show=False,
                    callback=self.on_drag_line_drag,
                )
                dpg.add_drag_line(
                    label=f"Chunk {i+1} stop",
                    tag=t2e,
                    color=[255, 0, 0, 255],
                    default_value=v1,
                    parent="plot_2",
                    show=False,
                    callback=self.on_drag_line_drag,
                )
    
                self._chunk_draglines.extend([t2s, t2e])
                new_window_tags.extend([t2s, t2e])
    
        # --- 8) zapisz tagi w globalITEMS.windows (bez leaka, bo wcześniej czyściliśmy)
        if hasattr(self, "globalITEMS") and hasattr(self.globalITEMS, "windows"):
            self.globalITEMS.windows.extend(new_window_tags)
    
        # --- 9) show/hide (OK)
        self.show_chunks_drag_lines("Custom_chunks_check", dpg.get_value("Custom_chunks_check"),allow_reset=False)
        self._build_tcspc_time_cache()            # aktualny dataset
        self._recompute_tcspc_for_all_chunks()    # wypełnij tcspc od razu
    
    # def add_chunks(self):
    #     nchunks = int(dpg.get_value('left_panel_N_chunks'))
    #     xdata = self.TT_xdata_1
    
    #     chunk_nodes = np.linspace(0, len(xdata), nchunks + 1).astype(int)
    
    #     channels = [ch for ch in self.fcs_data.PHOTONS.keys() if ch.startswith('channel_')]
    #     nsel = len(self.channels)
    
    #     if nsel >= 1:
    #         chan = channels[0]
    #         chunk_TCSPC_CH1_nodes = np.linspace(
    #             0, len(self.fcs_data.PHOTONS[chan]['exact_time']), nchunks + 1
    #         ).astype(int)
    #     if nsel == 2:
    #         chan = channels[1]
    #         chunk_TCSPC_CH2_nodes = np.linspace(
    #             0, len(self.fcs_data.PHOTONS[chan]['exact_time']), nchunks + 1
    #         ).astype(int)
    
    #     self.chunks = {}
    #     if nsel == 1:
    #         chan = channels[0]
    #         chn = 'ch1' if chan.endswith('_0') else ('ch2' if chan.endswith('_1') else 'ch1')
    
    #     for i in range(nchunks):
    #         ind_min = chunk_nodes[i]
    #         ind_max = chunk_nodes[i + 1]
    #         stop_ix = ind_max - 1
    
    #         # xdata rosnące => min/max z brzegów (dokładnie to samo)
    #         mn = xdata[ind_min]
    #         mx = xdata[stop_ix]
    
    #         if nsel == 1:
    #             self.chunks[f'chunk_{i}'] = {
    #                 'values': [mn, mx],
    #                 'indices': [ind_min, stop_ix],
    #                 'tcspc': {chn: [chunk_TCSPC_CH1_nodes[i], chunk_TCSPC_CH1_nodes[i + 1] - 1]},
    #             }
    #         else:
    #             self.chunks[f'chunk_{i}'] = {
    #                 'values': [mn, mx],
    #                 'indices': [ind_min, stop_ix],
    #                 'tcspc': {
    #                     'ch1': [chunk_TCSPC_CH1_nodes[i], chunk_TCSPC_CH1_nodes[i + 1] - 1],
    #                     'ch2': [chunk_TCSPC_CH2_nodes[i], chunk_TCSPC_CH2_nodes[i + 1] - 1],
    #                 },
    #             }
    
    #     # --- szybkie kasowanie: nie skanuj aliasów
    #     if not hasattr(self, "_chunk_draglines"):
    #         self._chunk_draglines = []
    #     for tag in self._chunk_draglines:
    #         if dpg.does_item_exist(tag):
    #             dpg.delete_item(tag)
    #     self._chunk_draglines.clear()
    
    #     new_window_tags = []
    
    #     # --- tworzenie dragline; potem callback bez get_value
    #     for i in range(nchunks):
    #         v0, v1 = self.chunks[f'chunk_{i}']['values']
    
    #         t1s = f"Chunk_1_{i+1}_start_dragline"
    #         t1e = f"Chunk_1_{i+1}_stop_dragline"
    #         dpg.add_drag_line(label=f"Chunk {i+1} start", tag=t1s, color=[255, 0, 0, 255],
    #                           default_value=v0, parent='plot_1', show=False, callback=self.on_drag_line_drag)
    #         dpg.add_drag_line(label=f"Chunk {i+1} stop", tag=t1e, color=[255, 0, 0, 255],
    #                           default_value=v1, parent='plot_1', show=False, callback=self.on_drag_line_drag)
    
    #         self._chunk_draglines += [t1s, t1e]
    #         new_window_tags += [t1s, t1e]
    
    #         if nsel == 2:
    #             t2s = f"Chunk_2_{i+1}_start_dragline"
    #             t2e = f"Chunk_2_{i+1}_stop_dragline"
    #             dpg.add_drag_line(label=f"Chunk {i+1} start", tag=t2s, color=[255, 0, 0, 255],
    #                               default_value=v0, parent='plot_2', show=False, callback=self.on_drag_line_drag)
    #             dpg.add_drag_line(label=f"Chunk {i+1} stop", tag=t2e, color=[255, 0, 0, 255],
    #                               default_value=v1, parent='plot_2', show=False, callback=self.on_drag_line_drag)
    
    #             self._chunk_draglines += [t2s, t2e]
    #             new_window_tags += [t2s, t2e]
    #     self.globalITEMS.windows = [w for w in self.globalITEMS.windows if not (w.startswith("Chunk_") and w.endswith("_dragline"))]
    #     self.globalITEMS.windows.extend(new_window_tags)
    
    #     # init callback bez get_value
    #     for i in range(nchunks):
    #         v0, v1 = self.chunks[f'chunk_{i}']['values']
    #         self.callback_chunk_drag_line(f"Chunk_1_{i+1}_start_dragline", v0, None)
    #         self.callback_chunk_drag_line(f"Chunk_1_{i+1}_stop_dragline",  v1, None)
    
    #     self.show_chunks_drag_lines('Custom_chunks_check', dpg.get_value('Custom_chunks_check'))
    #     self.META_data['TT info'] = self.TT_snapshot()
    #     if dpg.get_value('Custom_chunks_check'):
    #         self.calculate_shade()
    #         self.plot_TT()
    #     self.META_data['TT info'] = self.TT_snapshot()
        
    # def add_chunks(self):
    #     nchunks = dpg.get_value('left_panel_N_chunks')
    #     xdata = self.TT_xdata_1
    #     chunk_nodes = np.linspace(0,len(xdata),nchunks+1).astype(int)
    #     channels = [ch for ch in self.fcs_data.PHOTONS.keys() if ch.startswith('channel_')]
    #     if len(self.channels) == 1:
    #         chan = channels[0]
    #         chunk_TCSPC_CH1_nodes = np.linspace(0,len(self.fcs_data.PHOTONS[chan]['exact_time']),nchunks+1).astype(int)
    #     if len(self.channels) == 2:
    #         chan = channels[0]
    #         chunk_TCSPC_CH1_nodes = np.linspace(0,len(self.fcs_data.PHOTONS[chan]['exact_time']),nchunks+1).astype(int)
    #         chan = channels[1]
    #         chunk_TCSPC_CH2_nodes = np.linspace(0,len(self.fcs_data.PHOTONS[chan]['exact_time']),nchunks+1).astype(int)
    #     self.chunks = {}
    #     for i in range(nchunks):
    #         if len(self.channels) ==1:
    #             chan = channels[0]
    #             if chan.endswith('_0'):
    #                 chn='ch1'
    #             elif chan.endswith('_1'):
    #                 chn='ch2'
    #             ind_min = chunk_nodes[0+i]
    #             ind_max = chunk_nodes[1+i]
    #             mn, mx = xdata[ind_min:ind_max-1].min(),xdata[ind_min:ind_max-1].max()
    #             self.chunks['chunk_'+str(i)] = {'values':[mn,mx],
    #                                        'indices':[ind_min,ind_max-1],
    #                                             'tcspc':{chn:[chunk_TCSPC_CH1_nodes[0+i],chunk_TCSPC_CH1_nodes[1+i]-1]}
    #                                       }
    #         elif len(self.channels) ==2:
    #             ind_min = chunk_nodes[0+i]
    #             ind_max = chunk_nodes[1+i]
    #             mn, mx = xdata[ind_min:ind_max-1].min(),xdata[ind_min:ind_max-1].max()
    #             self.chunks['chunk_'+str(i)] = {'values':[mn,mx],
    #                                        'indices':[chunk_nodes[0+i],ind_max-1],
    #                                             'tcspc':{'ch1':[chunk_TCSPC_CH1_nodes[0+i],chunk_TCSPC_CH1_nodes[1+i]-1],
    #                                                     'ch2':[chunk_TCSPC_CH2_nodes[0+i],chunk_TCSPC_CH2_nodes[1+i]-1]
    #                                                     }
    #                                       }
        
    #     existing_chunks_lines = dpg.get_aliases()
    #     existing_chunks_lines = [chL for chL in existing_chunks_lines if chL.startswith('Chunk_') and chL.endswith('_dragline')]
    #     for chL in existing_chunks_lines:
    #         dpg.delete_item(chL)
    #     for i in range(nchunks):
    #         if len(self.channels) == 1:
    #             value = self.chunks['chunk_'+str(i)]['values'][0]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
    #                               tag="Chunk_1_"+str(i+1)+'_start_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_1',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                               )
                
    #             value = self.chunks['chunk_'+str(i)]['values'][1]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
    #                               tag="Chunk_1_"+str(i+1)+'_stop_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_1',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                              )
    #             self.globalITEMS.windows.extend(["Chunk_1_"+str(i+1)+'_start_dragline',
    #                                              "Chunk_1_"+str(i+1)+'_stop_dragline'])
                
    #         elif len(self.channels) == 2:
    #             value = self.chunks['chunk_'+str(i)]['values'][0]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
    #                               tag="Chunk_1_"+str(i+1)+'_start_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_1',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                               )
                
    #             value = self.chunks['chunk_'+str(i)]['values'][1]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
    #                               tag="Chunk_1_"+str(i+1)+'_stop_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_1',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                              )
                
    #             value = self.chunks['chunk_'+str(i)]['values'][0]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' start',
    #                               tag="Chunk_2_"+str(i+1)+'_start_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_2',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                               )
                
    #             value = self.chunks['chunk_'+str(i)]['values'][1]
    #             dpg.add_drag_line(label="Chunk "+str(i+1)+' stop',
    #                               tag="Chunk_2_"+str(i+1)+'_stop_dragline',
    #                               color=[255, 0, 0, 255],
    #                               default_value = value,
    #                               parent='plot_2',
    #                               show=False,
    #                               callback=self.on_drag_line_drag
    #                              )
                
    #             self.globalITEMS.windows.extend(["Chunk_1_"+str(i+1)+'_start_dragline',
    #                                              "Chunk_1_"+str(i+1)+'_stop_dragline',
    #                                              "Chunk_2_"+str(i+1)+'_start_dragline',
    #                                              "Chunk_2_"+str(i+1)+'_stop_dragline'])
                
    #     for i in range(nchunks):
    #         value = dpg.get_value("Chunk_1_"+str(i+1)+'_start_dragline')
    #         self.callback_chunk_drag_line("Chunk_1_"+str(i+1)+'_start_dragline',value,None)
    #         value = dpg.get_value("Chunk_1_"+str(i+1)+'_stop_dragline')
    #         self.callback_chunk_drag_line("Chunk_1_"+str(i+1)+'_stop_dragline',value,None)
        
    #     self.show_chunks_drag_lines('Custom_chunks_check',dpg.get_value('Custom_chunks_check'))
    #     self.META_data['TT info']=self.TT_snapshot()
    #     if dpg.get_value('Custom_chunks_check'):
    #         self.calculate_shade()
    #         self.plot_TT()
    #     self.META_data['TT info']=self.TT_snapshot()
                    
    def on_chunks_released(self):
        value = dpg.get_value("left_panel_N_chunks")
        self.add_chunks(reset=True)   # albo reset=False
        self._after_chunks_changed()      

    def transfer_chunks_to_TT(self):
        if len(self.channels) == 1:
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
        elif len(self.channels) == 2:
            self.TT_ydata_1_chunked = np.array([])
            self.TT_xdata_1_chunked = np.array([])
            self.TT_ydata_2_chunked = np.array([])
            self.TT_xdata_2_chunked = np.array([])
            for chunk in self.chunks.keys():
                xdata1 = self.TT_xdata_1
                ydata1 = self.TT_ydata_1
                xdata2 = self.TT_xdata_2
                ydata2 = self.TT_ydata_2
                irenage = self.chunks[chunk]['indices']
                chunked1 = self.TT_xdata_1_chunked
                chunked2 = self.TT_xdata_2_chunked
                chunked1=np.append(chunked1,xdata1[irenage[0]:irenage[1]])
                chunked2=np.append(chunked2,xdata2[irenage[0]:irenage[1]])
                self.TT_xdata_1_chunked = chunked1
                self.TT_xdata_2_chunked = chunked2
                chunked1 = self.TT_ydata_1_chunked
                chunked1=np.append(chunked1,ydata1[irenage[0]:irenage[1]])
                self.TT_ydata_1_chunked = chunked1
                chunked2 = self.TT_ydata_2_chunked
                chunked2=np.append(chunked2,ydata2[irenage[0]:irenage[1]])
                self.TT_ydata_2_chunked = chunked2
                

    def transfer_chunks_to_TCSPC(self):
        if len(self.channels) == 1:
            self.TCSPC_CHUNKCED_indices_1 = np.array([])
            for chunk in self.chunks.keys():
                chan = list(self.channels)[0]
                if chan.endswith('_0'):
                    chn='ch1'
                elif  chan.endswith('_1'):
                    chn='ch2'
                irenage = self.chunks[chunk]['tcspc'][chn]
                self.TCSPC_CHUNKCED_indices_1 = np.concatenate((self.TCSPC_CHUNKCED_indices_1,np.arange(irenage[0],irenage[1],1)))
            self.fcs_data.decay_hist = self.fcs_data.calculate_decays(self.fcs_data.PHOTONS,[self.TCSPC_CHUNKCED_indices_1.astype(int)])
        elif len(self.channels) == 2:
            self.TCSPC_CHUNKCED_indices_1 = np.array([])
            self.TCSPC_CHUNKCED_indices_2 = np.array([])
            for chunk in self.chunks.keys():
                for chan in list(self.channels):
                    if chan.endswith('_0'):
                        chn='ch1'
                        irenage1 = self.chunks[chunk]['tcspc'][chn]
                    elif  chan.endswith('_1'):
                        chn='ch2'
                        irenage2 = self.chunks[chunk]['tcspc'][chn]
                self.TCSPC_CHUNKCED_indices_1 = np.concatenate((self.TCSPC_CHUNKCED_indices_1,
                                                                np.arange(irenage1[0],irenage1[1],1)))
                self.TCSPC_CHUNKCED_indices_2 = np.concatenate((self.TCSPC_CHUNKCED_indices_2,
                                                                np.arange(irenage2[0],irenage2[1],1)))
            self.fcs_data.decay_hist = self.fcs_data.calculate_decays(self.fcs_data.PHOTONS,[self.TCSPC_CHUNKCED_indices_1.astype(int),
                                                                                             self.TCSPC_CHUNKCED_indices_2.astype(int)])
                
    ########################################################################           
    ########################################################################           
    ########################################################################   
    
    def show_chunks_drag_lines(self, sender, app_data, user_data=None, *, allow_reset=True):
        """
        sender/app_data: jak w DPG callbacku
        allow_reset=False: używaj gdy wołasz z add_chunks(), żeby nie robić add_chunks() w środku (brak rekurencji)
        """
        show = bool(app_data)
        nchunks = int(dpg.get_value('left_panel_N_chunks'))
        nsel = len(self.channels)
    
        # OFF -> reset tylko jeśli wolno
        if (not show) and allow_reset:
            self.add_chunks(reset=True)
            # po add_chunks liczba dragline może się zmienić, więc pobierz ponownie
            nchunks = int(dpg.get_value('left_panel_N_chunks'))
        else:
            self.calculate_shade()
        self._after_chunks_changed()
        # show/hide
        for i in range(1, nchunks + 1):
            dpg.configure_item(f"Chunk_1_{i}_start_dragline", show=show)
            dpg.configure_item(f"Chunk_1_{i}_stop_dragline",  show=show)
            if nsel == 2:
                dpg.configure_item(f"Chunk_2_{i}_start_dragline", show=show)
                dpg.configure_item(f"Chunk_2_{i}_stop_dragline",  show=show)
    
        
    ########################################################################           
    ########################################################################           
    ########################################################################   
        
        
    def callback_left_panel_drag_time_binning(self,sender,app_data):
        if app_data>1e-1:
            app_data=1e-1
            dpg.set_value(sender,app_data)
        self.fcs_data.time_bin = self.round_data(app_data)
        self.fcs_data.timetrace = self.fcs_data.bin_time_data(self.fcs_data.PHOTONS,
                                                              self.fcs_data.time_bin,
                                                              self.fcs_data.occurence)
        self.fcs_data.count_rate = self.fcs_data.calculate_count_rate(self.fcs_data.PHOTONS,self.fcs_data.timetrace,self.fcs_data.time_bin)
        ylabel = self.stringer(dpg.get_value('left_panel_drag_time_binning'))
        dpg.configure_item('TT_y1',label=ylabel)
        dpg.configure_item('TT_y2',label=ylabel)
        if len(self.channels) == 1:
            self.TT_xdata_1=(self.fcs_data.timetrace[list(self.channels)[0]].time_interval*1e-9).values
            self.TT_ydata_1=(self.fcs_data.timetrace[list(self.channels)[0]].occurrences).values
        elif len(self.channels) == 2:
            self.TT_xdata_1=(self.fcs_data.timetrace[list(self.channels)[0]].time_interval*1e-9).values
            self.TT_ydata_1=(self.fcs_data.timetrace[list(self.channels)[0]].occurrences).values
            self.TT_xdata_2=(self.fcs_data.timetrace[list(self.channels)[1]].time_interval*1e-9).values
            self.TT_ydata_2=(self.fcs_data.timetrace[list(self.channels)[1]].occurrences).values
        
        self.add_chunks(reset=True)   # albo reset=False
        self._after_chunks_changed()
        if len(self.channels) == 1:
            BGLvL = (dpg.get_value('TCSPC_BG_dline_ch1'),None)
        elif len(self.channels) == 2:
            BGLvL = (dpg.get_value('TCSPC_BG_dline_ch1'),dpg.get_value('TCSPC_BG_dline_ch2'))
        self.plot_TCSPC(BGLvL)
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    def load_data(self,file):
        self.META_data = {'TT info':{},
                          'TCSPC info':{'Filters':{}},
                          'FCS info':{}
                         }
        time_bin = self.round_data(self.method_init.left_panel_drag_time_binning['default_time_bin'])
        # print(time_bin)
        dpg.set_value('left_panel_drag_time_binning',time_bin)
        dpg.set_value('left_panel_drag_subs',self.method_init.left_panel_drag_subs['default_value'])
        dpg.set_value('left_panel_N_chunks',self.method_init.left_panel_N_chunks['default_value'])
        dpg.set_value('Custom_chunks_check',self.method_init.Custom_chunks_check['default_value'])
        
        self.fcs_data = load_fcs(file,time_bin)
        self.channels = self.fcs_data.timetrace.keys()
        
        if len(self.channels) == 1:
            self.TCSCP_draglines['TCSPC_L_dline_ch1']=self.TCSCP_draglines_init['TCSPC_L_dline_ch1']
            self.TCSCP_draglines['TCSPC_U_dline_ch1']=self.TCSCP_draglines_init['TCSPC_U_dline_ch1']
            self.TCSCP_draglines['TCSPC_L_dline_ch2']=self.TCSCP_draglines_init['TCSPC_L_dline_ch2']
            self.TCSCP_draglines['TCSPC_U_dline_ch2']=self.TCSCP_draglines_init['TCSPC_U_dline_ch2']
            self.TT_xdata_1=(self.fcs_data.timetrace[list(self.channels)[0]].time_interval*1e-9).values.astype(float)
            self.TT_ydata_1=(self.fcs_data.timetrace[list(self.channels)[0]].occurrences).values.astype(float)
            self.shade_data_1=[self.TT_xdata_1,
                               np.zeros(len(self.TT_xdata_1)),
                               np.zeros(len(self.TT_xdata_1))
                               ]
            self.TCSPC_subplots['columns'] = 1
            self.TCSPC_subplots['column_ratios'] = [1.00]
            dpg.configure_item('TCSPC_subplots',columns = self.TCSPC_subplots['columns'],column_ratios = self.TCSPC_subplots['column_ratios'])
            dpg.hide_item('TCSPC_plt_ch_2')
            self.FCS_subplots['columns'] = 1
            self.FCS_subplots['column_ratios'] = [1.00]
            dpg.configure_item('FCS_subplots',columns = self.FCS_subplots['columns'],column_ratios = self.FCS_subplots['column_ratios'])
            dpg.hide_item('FCS_plt_ch_2')
            dpg.set_value('FCS_cross_check',False)
            dpg.hide_item('FCS_cross_check')
            dpg.set_value('TCSPC_L_dline_ch1',self.TCSCP_draglines['TCSPC_L_dline_ch1'])
            dpg.set_value('TCSPC_U_dline_ch1',self.TCSCP_draglines['TCSPC_U_dline_ch1'])
            
            
        elif len(self.channels) == 2:
            if self.fcs_data.PHOTONS['Mode'] == 'PIE':
                self.TCSCP_draglines['TCSPC_L_dline_ch1']=self.TCSCP_draglines_init['TCSPC_PIE_L_dline_ch1']
                self.TCSCP_draglines['TCSPC_U_dline_ch1']=self.TCSCP_draglines_init['TCSPC_PIE_U_dline_ch1']
                self.TCSCP_draglines['TCSPC_L_dline_ch2']=self.TCSCP_draglines_init['TCSPC_PIE_L_dline_ch2']
                self.TCSCP_draglines['TCSPC_U_dline_ch2']=self.TCSCP_draglines_init['TCSPC_PIE_U_dline_ch2']
            else:
                self.TCSCP_draglines['TCSPC_L_dline_ch1']=self.TCSCP_draglines_init['TCSPC_L_dline_ch1']
                self.TCSCP_draglines['TCSPC_U_dline_ch1']=self.TCSCP_draglines_init['TCSPC_U_dline_ch1']
                self.TCSCP_draglines['TCSPC_L_dline_ch2']=self.TCSCP_draglines_init['TCSPC_L_dline_ch2']
                self.TCSCP_draglines['TCSPC_U_dline_ch2']=self.TCSCP_draglines_init['TCSPC_U_dline_ch2']
            self.TT_xdata_1=(self.fcs_data.timetrace[list(self.channels)[0]].time_interval*1e-9).values.astype(float)
            self.TT_ydata_1=(self.fcs_data.timetrace[list(self.channels)[0]].occurrences).values.astype(float)
            self.TT_xdata_2=(self.fcs_data.timetrace[list(self.channels)[1]].time_interval*1e-9).values.astype(float)
            self.TT_ydata_2=(self.fcs_data.timetrace[list(self.channels)[1]].occurrences).values.astype(float)
            self.shade_data_2=[self.TT_xdata_2,
                               np.zeros(len(self.TT_xdata_2)),
                               np.zeros(len(self.TT_xdata_2))
                               ]
            self.TCSPC_subplots['columns'] = 2
            self.TCSPC_subplots['column_ratios'] = [0.5,0.5]
            dpg.configure_item('TCSPC_subplots',columns = self.TCSPC_subplots['columns'],column_ratios = self.TCSPC_subplots['column_ratios'])
            dpg.show_item('TCSPC_plt_ch_2')
            self.FCS_subplots['columns'] = 2
            self.FCS_subplots['column_ratios'] = [0.5,0.5]
            dpg.configure_item('FCS_subplots',columns = self.FCS_subplots['columns'],column_ratios = self.FCS_subplots['column_ratios'])
            dpg.show_item('FCS_plt_ch_2')
            dpg.show_item('FCS_cross_check')
            dpg.set_value('TCSPC_L_dline_ch1',self.TCSCP_draglines['TCSPC_L_dline_ch1'])
            dpg.set_value('TCSPC_U_dline_ch1',self.TCSCP_draglines['TCSPC_U_dline_ch1'])
            dpg.set_value('TCSPC_L_dline_ch2',self.TCSCP_draglines['TCSPC_L_dline_ch2'])
            dpg.set_value('TCSPC_U_dline_ch2',self.TCSCP_draglines['TCSPC_U_dline_ch2'])

        dpg.set_value('auto_FCS_plot1',([],[]))
        dpg.set_value('auto_FCS_plot2',([],[]))
        dpg.set_value('Cross_FCS_plot1',([],[]))
        dpg.set_value('Cross_FCS_plot2',([],[]))
        dpg.set_axis_limits('FCS_xaxis_chan1',0.001,1000)
        dpg.set_axis_limits('FCS_yaxis_chan1',0,1)  
        dpg.set_axis_limits('FCS_xaxis_chan2',0.001,1000)
        dpg.set_axis_limits('FCS_yaxis_chan2',0,1)  
        pkl = file.replace('.ptu','.pd1')
        
        if os.path.exists(pkl):
            self.read_PKL_DATA(pkl)
            if self.META_data['TCSPC info']['BG_lvl'] == (-1,-1):
                if len(self.channels) == 1:
                    BGLvL =(self.auto_bg_lvl('ch1'),None)
                    dpg.set_value('TCSPC_BG_dline_ch1',BGLvL[0])
                else:
                    BGLvL =(self.auto_bg_lvl('ch1'),self.auto_bg_lvl('ch2'))
                    dpg.set_value('TCSPC_BG_dline_ch1',BGLvL[0])
                    dpg.set_value('TCSPC_BG_dline_ch2',BGLvL[1])
            else:
                if len(self.channels) == 1:
                    BGLvL =(dpg.get_value('TCSPC_BG_dline_ch1'),dpg.get_value('TCSPC_BG_dline_ch2'))
                else:
                    BGLvL =(dpg.get_value('TCSPC_BG_dline_ch1'),dpg.get_value('TCSPC_BG_dline_ch2'))
            if 'Filters' in list(self.META_data['TCSPC info'].keys()):
                if len(self.META_data['TCSPC info']['Filters']) != 0:
                    self.Filters=self.META_data['TCSPC info']['Filters']
            else:
                pass
            
            chunks = self.META_data['TT info'].get('chunks')
            
            if isinstance(chunks, dict) and chunks:
                self.add_chunks(reset=False)   # albo reset=False
                self._after_chunks_changed()
            else:
                self.add_chunks(reset=True)   # albo reset=False
                self._after_chunks_changed()
        else:
            if len(self.channels) == 1:
                BGLvL =(self.auto_bg_lvl('ch1'),None)
                dpg.set_value('TCSPC_BG_dline_ch1',BGLvL[0])
            else:
                BGLvL =(self.auto_bg_lvl('ch1'),self.auto_bg_lvl('ch2'))
                dpg.set_value('TCSPC_BG_dline_ch1',BGLvL[0])
                dpg.set_value('TCSPC_BG_dline_ch2',BGLvL[1])
            self.add_chunks(reset=True)   # albo reset=False
            self._after_chunks_changed()
        self.callback_tcspc_timegate('TCSPC_timegate_check',dpg.get_value('TCSPC_timegate_check')) 
        self.plot_TCSPC(BGLvL)
        cntrt_1 = self.fcs_data.count_rate[list(self.channels)[0]]
        if cntrt_1[1]<1:
            dpg.configure_item('TT_plot1',label = 'Channel 0; '+ 'CNTR ='+ self.stringer_cntr([cntrt_1[0],None]))
        else:
            dpg.configure_item('TT_plot1',label = 'Channel 0; '+ 'CNTR ='+ self.stringer_cntr([cntrt_1[0],cntrt_1[1]])   )
        if len(self.channels)==2:
            cntrt_2 = self.fcs_data.count_rate[list(self.channels)[1]]    
            if cntrt_2[1]<1:
                dpg.configure_item('TT_plot2',label = 'Channel 1; '+ 'CNTR ='+ self.stringer_cntr([cntrt_2[0],None]))
            else:
                dpg.configure_item('TT_plot2',label = 'Channel 1; '+ 'CNTR ='+ self.stringer_cntr([cntrt_2[0],cntrt_2[1]])   )
        self.plot_FCS()
        self._PCKL_DATA()
            
        
    #########################################################################           
    #########################################################################           
    #########################################################################   


    def show_error_no_files_close_only(self,error_text):
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
            dpg.add_button(label='Close',
                           parent='No_data_files',
                           tag='no_files_error_butt',
                           callback=self.callback_no_files_dialog_close_only
                          )
            dpg.bind_item_theme('No_data_files', 'Error_window_theme')
        except:
            dpg.show_item('No_data_files')

    def callback_no_files_dialog_close_only(self,sender,app_data):
        dpg.configure_item('No_data_files',show=False)
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('no_files_error_butt')
        dpg.delete_item('No_data_files')
        if 'no_files_error_butt_yes' in dpg.get_aliases():
            dpg.delete_item('no_files_error_butt_yes')
        else:
            pass
    
    def stringer(self,num):
        value = 1/num
        val = int(np.round(value))
        if val>0 and val<100:
            text = '['+str(val)+'\u00D7Hz]'
        elif val>= 100 and val <=100000:
            text = '['+str(val/1000) +'\u00D7kHz]'
        elif val> 1e5 and val <=1e8:
            text = '['+str(val/1e6) +'\u00D7MHz]'
        elif val> 1e8 and val <=1e12:
            text = '['+str(val/1e9) +'\u00D7GHz]'
        elif val<=0:
            text = 'NULL!'
        else:
            text = 'inf!'
        return text
    
    def stringer_cntr(self,values):
        if values[1] ==None:
            val = int(np.round(values[0]))
            if val>0 and val<100:
                text = str(val)+' Hz'
            elif val>= 100 and val <=100000:
                text = str(np.round(val/1000,2)) +' kHz'
            elif val> 1e5 and val <=1e8:
                text = str(np.round(val/1e6,2)) +' MHz'
            elif val> 1e8 and val <=1e12:
                text = str(np.round(val/1e9,2)) +' GHz'
            elif val<=0:
                text = 'NULL!'
            else:
                text = 'inf!'
            return text
        else:
            val = int(np.round(values[0]))
            val1 = int(np.round(values[1]))
            if val>0 and val<100:
                text = str(val)+'\u00B1'+str(val1)+' Hz'
            elif val>= 100 and val <=100000:
                text = str(np.round(val/1000,2))+'\u00B1'+str(np.round(val1/1000,2)) +' kHz'
            elif val> 1e5 and val <=1e8:
                text = str(np.round(val/1e6,2)) +'\u00B1'+str(np.round(val1/1e6,2))+' MHz'
            elif val> 1e8 and val <=1e12:
                text = str(np.round(val/1e9,2)) +'\u00B1'+str(np.round(val1/1e9,2))+' GHz'
            elif val<=0:
                text = 'NULL!'
            else:
                text = 'inf!'
            return text
    
    def load_TT_plots(self):
        ylabel = self.stringer(dpg.get_value('left_panel_drag_time_binning'))
        with dpg.plot(no_title=True,tag='plot_1',show=True,parent = 'TT_subplots'):
            self.TT_plt_x1 = dpg.add_plot_axis(dpg.mvXAxis, label="Time [s]", tag='TT_x1',log_scale=False)
            self.TT_plt_y1 = dpg.plot_axis(dpg.mvYAxis, label=ylabel,tag='TT_y1',log_scale=False)
            with self.TT_plt_y1:
                dpg.add_line_series([], [],tag='TT_plot1',label='Channel 1')
                dpg.add_shade_series(x = self.shade_data_1[0],
                                     y1 = self.shade_data_1[1],
                                     y2 = self.shade_data_1[2],
                                     tag='TT_shade1'
                                    )
                dpg.bind_item_theme("TT_plot1", "plot_green_theme")
                dpg.bind_item_theme("TT_shade1", "plot_green_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast)
        self.globalITEMS.windows.extend(['plot_1','TT_x1','TT_y1','TT_plot1','TT_shade1'])        
        with dpg.plot(no_title=True,tag='plot_2',show=False,parent = 'TT_subplots'):
            self.TT_plt_x2 = dpg.add_plot_axis(dpg.mvXAxis, label="Time [s]", tag='TT_x2',log_scale=False)
            self.TT_plt_y2 = dpg.plot_axis(dpg.mvYAxis, label=ylabel,tag='TT_y2',log_scale=False)
            with self.TT_plt_y2:
                dpg.add_line_series([], [],tag='TT_plot2',label='Channel 2')
                dpg.bind_item_theme("TT_plot2", "plot_green_theme")
                dpg.add_shade_series(x = self.shade_data_2[0],
                                     y1 = self.shade_data_2[1],
                                     y2 = self.shade_data_2[2],
                                     tag='TT_shade2'
                                    )
                dpg.bind_item_theme("TT_shade2", "plot_green_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast)
        self.globalITEMS.windows.extend(['plot_2','TT_x2','TT_y2','TT_plot2','TT_shade2'])
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################
    
    def check_TCSPC_filtering_options(self):
        if dpg.get_value('TCSPC_timegate_check'):
            if not 'TCSPC_L_dline_ch1' in  self.globalITEMS.windows and 'TCSPC_U_dline_ch1' in  self.globalITEMS.windows:
                self.TCSPC_1_LDG =  dpg.add_drag_line(label="Lower limit",
                                                      tag='TCSPC_L_dline_ch1' ,
                                                      color=[255, 100, 0, 255],
                                                      default_value=self.TCSCP_draglines['TCSPC_L_dline_ch1'],
                                                      callback=self.callback_TCSPC_dragline,
                                                      show = True,
                                                      thickness = self.drag_line_thickness,
                                                      parent = 'TCSPC_plt_ch_1'
                                                      )
                self.TCSPC_1_UDG =  dpg.add_drag_line(label="Upper limit",
                                                      tag='TCSPC_U_dline_ch1',
                                                      color=[255, 0, 100, 255],
                                                      default_value=self.TCSCP_draglines['TCSPC_U_dline_ch1'],
                                                      callback=self.callback_TCSPC_dragline,
                                                      show = True,
                                                      thickness = self.drag_line_thickness,
                                                      parent = 'TCSPC_plt_ch_1'
                                                      )
                self.globalITEMS.windows.extend(['TCSPC_L_dline_ch1',
                                                 'TCSPC_U_dline_ch1',])
        if dpg.get_value('TCSPC_BG_correction_check'):
            if not 'TCSPC_BG_dline_ch1' in self.globalITEMS.windows:
                self.TCSPC_1_BG =  dpg.add_drag_line(label="Background level",
                                                     tag='TCSPC_BG_dline_ch1',
                                                     color=[255, 0, 0, 255],
                                                     default_value=-1,
                                                     vertical = False,
                                                     callback=self.subtract_tcspc,
                                                     show = True,
                                                     thickness = self.drag_line_thickness,
                                                     parent = 'TCSPC_plt_ch_1'
                                                     )
                self.globalITEMS.windows.extend(['TCSPC_BG_dline_ch1'])
        
    def load_FCS_plots(self):
        with dpg.plot(no_title=False,label='Channel 1',
                      query=False,
                      no_menus=True,
                      tag='FCS_plt_ch_1',
                      show=True,
                      parent = 'FCS_subplots'):
            self.FCS_1_x = dpg.add_plot_axis(dpg.mvXAxis,
                                             label="Lag time [ms]",
                                             tag="FCS_xaxis_chan1",
                                             log_scale=True)
            self.FCS_1_y = dpg.plot_axis(dpg.mvYAxis,
                                           label="G(\u03C4)",
                                           tag="FCS_yaxis_chan1",
                                           log_scale=False)
            with self.FCS_1_y:
                dpg.add_line_series([], [],tag='auto_FCS_plot1',label='Autocorrelation Channel 1')
                dpg.add_shade_series(x=[],y1=[],y2=[],tag='auto_FCS_plot1_shade')
                dpg.add_line_series([], [],tag='Cross_FCS_plot1',label='Crosscorrelation Channel 1 \u2192 2',show=False)
                dpg.add_shade_series(x=[],y1=[],y2=[],tag='Cross_FCS_plot1_shade',show=False)
                dpg.bind_item_theme("auto_FCS_plot1", "plot_green_theme")
                dpg.bind_item_theme("Cross_FCS_plot1", "plot_yellow_theme")
                dpg.bind_item_theme("auto_FCS_plot1_shade", "plot_green_theme")
                dpg.bind_item_theme("Cross_FCS_plot1_shade", "plot_yellow_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast,show=False,tag='FCS_CH1_leg')
        self.globalITEMS.windows.extend(['FCS_plt_ch_1',
                                         'FCS_xaxis_chan1',
                                         'FCS_yaxis_chan1',
                                         'auto_FCS_plot1',
                                         'Cross_FCS_plot1',
                                         'auto_FCS_plot1_shade',
                                         'Cross_FCS_plot1_shade',
                                         'FCS_CH1_leg'
                                         ])
        
        with dpg.plot(no_title=False,
                      label='Channel 2',
                      query=False,
                      no_menus=True,
                      tag='FCS_plt_ch_2',
                      show=False,
                      parent = 'FCS_subplots'):
            self.FCS_2_x = dpg.add_plot_axis(dpg.mvXAxis,
                                             label="Lag time [ms]",
                                             tag="FCS_xaxis_chan2",
                                             log_scale=True)
            self.FCS_2_y = dpg.plot_axis(dpg.mvYAxis,
                                         label="G(\u03C4)",
                                         tag="FCS_yaxis_chan2",
                                         log_scale=False)
            with self.FCS_2_y:
                dpg.add_line_series([], [],tag='auto_FCS_plot2',label='Autocorrelation Channel 2')
                dpg.add_shade_series(x=np.empty(10),y1=np.empty(10),y2=np.empty(10),tag='auto_FCS_plot2_shade')
                dpg.add_line_series([], [],tag='Cross_FCS_plot2',label='Crosscorrelation Channel 2 \u2192 1',show=False)
                dpg.add_shade_series(x=np.empty(10),y1=np.empty(10),y2=np.empty(10),tag='Cross_FCS_plot2_shade',show=False)
                dpg.bind_item_theme("auto_FCS_plot2", "plot_green_theme")
                dpg.bind_item_theme("Cross_FCS_plot2", "plot_yellow_theme")
                dpg.bind_item_theme("auto_FCS_plot2_shade", "plot_green_theme")
                dpg.bind_item_theme("Cross_FCS_plot2_shade", "plot_yellow_theme")
            dpg.add_plot_legend(show=False,tag='FCS_CH2_leg')     
        self.globalITEMS.windows.extend(['FCS_plt_ch_2',
                                         'FCS_subplots',
                                         'FCS_xaxis_chan2',
                                         'FCS_yaxis_chan2',
                                         'auto_FCS_plot2',
                                         'Cross_FCS_plot2',
                                         'auto_FCS_plot2_shade',
                                         'Cross_FCS_plot2_shade',
                                         'FCS_CH2_leg'
                                        ])
        
    def load_TCSPC_plots(self):
        with dpg.plot(no_title=False,
                      label='Channel 1',
                      query=False,
                      no_menus=True,
                      tag='TCSPC_plt_ch_1',
                      show=True,
                      parent = 'TCSPC_subplots'):
            self.TCSPC_1_x = dpg.add_plot_axis(dpg.mvXAxis, label="Time [ns]", tag="TCSPC_xaxis_chan1",log_scale=False)
            self.TCSPC_1_y = dpg.plot_axis(dpg.mvYAxis, label="Intensity", tag="TCSPC_yaxis_chan1",log_scale=True)
            with self.TCSPC_1_y:
                dpg.add_line_series([], [],tag='TCSPC_plot1',label='Channel 1')
                dpg.bind_item_theme("TCSPC_plot1", "plot_green_theme")
                dpg.add_line_series([], [],tag='TCSPC_sub_plot1',label='Subtracted background 1')
                dpg.bind_item_theme("TCSPC_sub_plot1", "plot_yellow_theme")
                dpg.add_line_series([], [],tag='TCSPC_plot1_L_inactive',label='')
                dpg.bind_item_theme("TCSPC_plot1_L_inactive", "plot_green_inactive_theme")
                dpg.add_line_series([], [],tag='TCSPC_plot1_U_inactive',label='')
                dpg.bind_item_theme("TCSPC_plot1_U_inactive", "plot_green_inactive_theme")
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast)
            self.TCSPC_1_LDG =  dpg.add_drag_line(label="Lower limit",
                                                  tag='TCSPC_L_dline_ch1',
                                                  color=[255, 100, 0, 255],
                                                  default_value=self.TCSCP_draglines['TCSPC_L_dline_ch1'],
                                                  callback=self.callback_TCSPC_dragline,
                                                  show = False,
                                                  thickness = self.drag_line_thickness
                                                  )
            self.TCSPC_1_UDG =  dpg.add_drag_line(label="Upper limit",
                                                  tag='TCSPC_U_dline_ch1',
                                                  color=[255, 0, 100, 255],
                                                  default_value=self.TCSCP_draglines['TCSPC_U_dline_ch1'],
                                                  callback=self.callback_TCSPC_dragline,
                                                  show = False,
                                                  thickness = self.drag_line_thickness
                                                  )
            self.TCSPC_1_BG =  dpg.add_drag_line(label="Background level",
                                                 tag='TCSPC_BG_dline_ch1',
                                                 color=[255, 0, 0, 255],
                                                 default_value=-1,
                                                 vertical = False,
                                                 callback=self.subtract_tcspc,
                                                 show = False,
                                                 thickness = self.drag_line_thickness
                                                 )
            
        self.globalITEMS.windows.extend(['TCSPC_plt_ch_1',
                                         'TCSPC_xaxis_chan1',
                                         'TCSPC_yaxis_chan1',
                                         'TCSPC_plot1',
                                         'TCSPC_plot1_L_inactive',
                                         'TCSPC_plot1_U_inactive',
                                         'TCSPC_L_dline_ch1',
                                         'TCSPC_U_dline_ch1',
                                         'TCSPC_BG_dline_ch1'
                                         ])
        with dpg.plot(no_title=False,
                      label='Channel 2',
                      query=False,
                      no_menus=True,
                      tag='TCSPC_plt_ch_2',
                      show=False,
                      parent = 'TCSPC_subplots'):
            self.TCSPC_2_x = dpg.add_plot_axis(dpg.mvXAxis, label="Time [ns]", tag="TCSPC_xaxis_chan2",log_scale=False)
            self.TCSPC_2_y = dpg.plot_axis(dpg.mvYAxis, label="Intensity", tag="TCSPC_yaxis_chan2",log_scale=True)
            with self.TCSPC_2_y:
                dpg.add_line_series([], [],tag='TCSPC_plot2',label='Channel 2')
                dpg.bind_item_theme("TCSPC_plot2", "plot_green_theme")
                dpg.add_line_series([], [],tag='TCSPC_sub_plot2',label='Subtracted background 2')
                dpg.bind_item_theme("TCSPC_sub_plot2", "plot_yellow_theme")
                dpg.add_line_series([], [],tag='TCSPC_plot2_L_inactive',label='')
                dpg.bind_item_theme("TCSPC_plot2_L_inactive", "plot_green_inactive_theme")
                dpg.add_line_series([], [],tag='TCSPC_plot2_U_inactive',label='')
                dpg.bind_item_theme("TCSPC_plot2_U_inactive", "plot_green_inactive_theme")
            self.TCSPC_2_LDG =  dpg.add_drag_line(label="Lower limit",
                                                  tag='TCSPC_L_dline_ch2',
                                                  color=[255, 100, 0, 255],
                                                  default_value=self.TCSCP_draglines['TCSPC_L_dline_ch2'],
                                                  callback=self.callback_TCSPC_dragline,
                                                  show = True,
                                                  thickness = self.drag_line_thickness
                                                  )
            self.TCSPC_2_UDG =  dpg.add_drag_line(label="Upper limit",
                                                  tag='TCSPC_U_dline_ch2',
                                                  color=[255, 0, 100, 255],
                                                  default_value=self.TCSCP_draglines['TCSPC_U_dline_ch2'],
                                                  callback=self.callback_TCSPC_dragline,
                                                  show = True,
                                                  thickness = self.drag_line_thickness
                                                  )
            self.TCSPC_2_BG =  dpg.add_drag_line(label="Background level",
                                                 tag='TCSPC_BG_dline_ch2',
                                                 color=[255, 0, 0, 255],
                                                 default_value=-1,
                                                 vertical = False,
                                                 callback=self.subtract_tcspc,
                                                 show = False,
                                                 thickness = self.drag_line_thickness
                                                 )
            dpg.add_plot_legend(location=dpg.mvPlot_Location_NorthEast)
        self.globalITEMS.windows.extend(['TCSPC_plt_ch_2',
                                         'TCSPC_xaxis_chan2',
                                         'TCSPC_yaxis_chan2',
                                         'TCSPC_plot2',
                                         'TCSPC_plot2_L_inactive',
                                         'TCSPC_plot2_U_inactive',
                                         'TCSPC_L_dline_ch2',
                                         'TCSPC_U_dline_ch2',
                                         'TCSPC_BG_dline_ch2'])
            
        
        
    def plot_TT(self):
        if len(self.channels) == 1:
            self.TT_subplots['rows'] = 1
            self.TT_subplots['row_ratios'] = [1.00]
            dpg.configure_item('TT_subplots',rows = self.TT_subplots['rows'],row_ratios = self.TT_subplots['row_ratios'])
            dpg.hide_item('plot_2')
            tt_plot_data_X_1 = self.TT_xdata_1
            tt_plot_data_Y_1 = self.TT_ydata_1
            dpg.set_value('TT_plot1',[tt_plot_data_X_1,tt_plot_data_Y_1])
            self.TT_x_axis_limits_1 = [self.TT_xdata_1.min(),self.TT_xdata_1.max()]
            self.TT_y_axis_limits_1 = [self.TT_ydata_1.min(),self.TT_ydata_1.max()]
            dpg.configure_item('TT_shade1',x = self.shade_data_1[0], y1= self.shade_data_1[1],y2 = self.shade_data_1[2])
            dpg.set_axis_limits('TT_x1',self.TT_x_axis_limits_1[0],self.TT_x_axis_limits_1[1])
            dpg.set_axis_limits('TT_y1',self.TT_y_axis_limits_1[0],self.TT_y_axis_limits_1[1])
            
        elif len(self.channels) == 2:
            self.TT_subplots['rows'] = 2
            self.TT_subplots['row_ratios'] = [0.50,0.50]
            dpg.configure_item('TT_subplots',rows = self.TT_subplots['rows'],row_ratios = self.TT_subplots['row_ratios'])
            dpg.show_item('plot_2')
            tt_plot_data_X_1 = self.TT_xdata_1
            tt_plot_data_Y_1 = self.TT_ydata_1
            tt_plot_data_X_2 = self.TT_xdata_2
            tt_plot_data_Y_2 = self.TT_ydata_2
            dpg.set_value('TT_plot1',[tt_plot_data_X_1,tt_plot_data_Y_1])
            dpg.set_value('TT_plot2',[tt_plot_data_X_2,tt_plot_data_Y_2])
            self.TT_x_axis_limits_1 = [self.TT_xdata_1.min(),self.TT_xdata_1.max()]
            self.TT_y_axis_limits_1 = [self.TT_ydata_1.min(),self.TT_ydata_1.max()]
            dpg.set_axis_limits('TT_x1',self.TT_x_axis_limits_1[0],self.TT_x_axis_limits_1[1])
            dpg.set_axis_limits('TT_y1',self.TT_y_axis_limits_1[0],self.TT_y_axis_limits_1[1])
            self.TT_x_axis_limits_2 = [self.TT_xdata_2.min(),self.TT_xdata_2.max()]
            self.TT_y_axis_limits_2 = [self.TT_ydata_2.min(),self.TT_ydata_2.max()]
            dpg.set_axis_limits('TT_x2',self.TT_x_axis_limits_2[0],self.TT_x_axis_limits_2[1])
            dpg.set_axis_limits('TT_y2',self.TT_y_axis_limits_2[0],self.TT_y_axis_limits_2[1])
            dpg.configure_item('TT_shade1',x = self.shade_data_1[0], y1= self.shade_data_1[1],y2 = self.shade_data_1[2])
            dpg.configure_item('TT_shade2',x = self.shade_data_2[0], y1= self.shade_data_2[1],y2 = self.shade_data_2[2])
        
    def plot_TCSPC(self,bglvl):   
        is_bg = dpg.get_value('TCSPC_BG_correction_check')
        if len(self.channels) == 1:
            xdata_1=(self.fcs_data.decay_hist[list(self.channels)[0]].decay_time).values
            ydata_1=(self.fcs_data.decay_hist[list(self.channels)[0]].counts).values
            dpg.set_axis_limits('TCSPC_xaxis_chan1',xdata_1.min(),xdata_1.max())
            dpg.set_axis_limits('TCSPC_yaxis_chan1',ydata_1.min(),ydata_1.max())
            self.callback_TCSPC_dragline('TCSPC_L_dline_ch1',None)
            self.callback_TCSPC_dragline('TCSPC_U_dline_ch1',None)
            if is_bg:
                dpg.show_item('TCSPC_BG_dline_ch1')
                dpg.set_value('TCSPC_BG_dline_ch1',bglvl[0])
                self.subtract_tcspc('TCSPC_BG_dline_ch1',None)
            else:
                dpg.hide_item('TCSPC_BG_dline_ch1')
        elif len(self.channels) == 2:
            xdata_1=(self.fcs_data.decay_hist[list(self.channels)[0]].decay_time).values
            ydata_1=(self.fcs_data.decay_hist[list(self.channels)[0]].counts).values
            xdata_2=(self.fcs_data.decay_hist[list(self.channels)[1]].decay_time).values
            ydata_2=(self.fcs_data.decay_hist[list(self.channels)[1]].counts).values
            dpg.set_axis_limits('TCSPC_xaxis_chan1',xdata_1.min(),xdata_1.max())
            dpg.set_axis_limits('TCSPC_yaxis_chan1',ydata_1.min(),ydata_1.max())
            dpg.set_axis_limits('TCSPC_xaxis_chan2',xdata_2.min(),xdata_2.max())
            dpg.set_axis_limits('TCSPC_yaxis_chan2',ydata_2.min(),ydata_2.max())
            if dpg.get_value('TCSPC_timegate_check'):
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch1',None)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch1',None)
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch2',None)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch2',None)
            if is_bg:
                dpg.show_item('TCSPC_BG_dline_ch1')
                dpg.show_item('TCSPC_BG_dline_ch2')
                dpg.set_value('TCSPC_BG_dline_ch1',bglvl[0])
                dpg.set_value('TCSPC_BG_dline_ch2',bglvl[1])
                self.subtract_tcspc('TCSPC_BG_dline_ch1',None)
                self.subtract_tcspc('TCSPC_BG_dline_ch2',None)
            else:
                dpg.hide_item('TCSPC_BG_dline_ch1')
                dpg.hide_item('TCSPC_BG_dline_ch2')
            

    #########################################################################           
    #########################################################################           
    #########################################################################   
    #########################################################################           
    #########################################################################           
    #########################################################################   
                    
    def round_data(self,value):
        exponent = int(np.round(np.ceil(log10(value))))
        if exponent <0:
            value = np.round(value,abs(exponent-1))
        return value
    
     
    #########################################################################           
    #########################################################################           
    #########################################################################   

    
    def callback_directory_select(self, sender, app_data):
        self.last_directory = app_data['current_path']
        fls = os.listdir(self.last_directory)
        fls = [f for f in fls if (f.endswith('.ptu'))]
        fls = [f for f in fls if self.test_read(os.path.join(self.last_directory,f))]
        self.files=fls
        if len(self.files)>0:
            self.anal_file = self.files[0]
            dpg.configure_item('file_box', items=self.files,default_value = self.anal_file)
            file = os.path.join(self.last_directory,self.anal_file)
            self.load_data(file)
            self.mnt_bttns_TCSPC()
            try:
                self.umnt_bttns_FCS()
            except:
                pass
            dpg.configure_item('file_dialog_id_PTU',default_path=self.last_directory)
            dpg.configure_item('file_dialog_save_correlated',default_path=self.last_directory)
            dpg.configure_item('Anal_window_Correlation_tab', user_data=False)
            dpg.configure_item('Anal_window_TCSPC_tab', user_data=True)
            self.basf.log_last_directory(self.last_directory)
            self.update_default_directory(self.last_directory)
        else:
            self.show_error('Empty folder, or no .ptu files found.')
    
    #########################################################################           
    #########################################################################           
    ######################################################################### 
    
        
    # def test_read(self,file):
        
    #     ptu_file  = PTUreader(file, print_header_data = False)
    #     submode = ptu_file.head["Measurement_SubMode"]
    #     cond = (submode == 1) or (submode == 0)
    #     return cond

    def test_read(self, file):
        submode = PTUHeaderReader.read_tag_fast(file, "Measurement_SubMode")
        return submode in (0, 1)
    
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
                dpg.add_button(label='OK',
                               parent='no_files_error_text_butt_group',
                               tag='ok_files_error_butt',
                               callback=self.callback_dialog_show_error_ok
                              )
            
            dpg.bind_item_theme('No_data_files', 'Error_window_theme')
        except:
            dpg.show_item('No_data_files')
            
            
    def callback_dialog_show_error_ok(self,sender,app_data):
        dpg.configure_item('No_data_files',show=False)
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('ok_files_error_butt')
        dpg.delete_item('no_files_error_text_butt_group')
        dpg.delete_item('No_data_files')
            
            
    #########################################################################           
    #########################################################################           
    #########################################################################
                
    def callback_listbox(self,sender,app_data):
        self.anal_file = app_data
        file = os.path.join(self.last_directory,self.anal_file)
        self.load_data(file)
        try:
            self.umnt_bttns_TCSPC()
        except:
            pass
        try:
            self.umnt_bttns_FCS()
        except:
            pass
        try:
            self.mnt_bttns_TCSPC()
        except:
            pass
        
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
                    
            
    def mount_PTU_Corr_handlers(self):
        dpg.add_key_press_handler(tag ='keyword_handler_PTU_Corr',callback=self.callback_PTU_Corr_Keyword_key,parent = 'handlers_registry')
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    
    def callback_PTU_Corr_Keyword_key(self,sender, app_data):
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
                    
        


    def is_sorted_numpy(self,arr):
        return np.all(arr[:-1] <= arr[1:])

    def find_all_occurrences(self,sorted_arr, x):
        left_index = np.searchsorted(sorted_arr, x, side='left')
        right_index = np.searchsorted(sorted_arr, x, side='right')
        if left_index == right_index:
            return np.array([])
        return np.arange(left_index, right_index)

    def _ensure_tcspc_index_cache(self, binw: float, photon_channels):
        cache = getattr(self, "_tcspc_cache", None)
        if cache is not None and cache.get("binw") == binw and cache.get("photon_channels") == tuple(photon_channels):
            return
    
        by_chan = {}
        for chan in photon_channels:
            t = np.asarray(self.fcs_data.PHOTONS[chan]["exact_time"], dtype=float)
            by_chan[chan] = np.rint(t / binw).astype(np.int64)
    
        self._tcspc_cache = {
            "binw": binw,
            "photon_channels": tuple(photon_channels),
            "by_chan": by_chan,
        }
    
    def _tcspc_span_for_target(self, idx_array: np.ndarray, target: int):
        left = int(np.searchsorted(idx_array, target, side="left"))
        right = int(np.searchsorted(idx_array, target, side="right") - 1)
        if left <= right:
            return left, right
        start_candidate = min(left, len(idx_array) - 1)   # >=
        end_candidate = max(left - 1, 0)                  # <=
        return start_candidate, end_candidate

        
    def _get_photon_channels(self):
        """Zwraca listę kanałów 'channel_*' w stałej kolejności."""
        chans = [ch for ch in self.fcs_data.PHOTONS.keys() if ch.startswith("channel_")]
        chans.sort()
        return chans
    
    def _build_tcspc_time_cache(self):
        ph_ch = [ch for ch in self.fcs_data.PHOTONS if ch.startswith("channel_")]
        ph_ch.sort()
        self._tcspc_cache = {
            "channels": tuple(ph_ch),
            "exact_time": {
                ch: np.asarray(self.fcs_data.PHOTONS[ch]["exact_time"], dtype=float)
                for ch in ph_ch
            },
        }

    
    def _tcspc_indices_from_time(self, exact_time, t_start, t_stop):
            i_start = int(np.searchsorted(exact_time, t_start, side="left"))
            i_stop  = int(np.searchsorted(exact_time, t_stop, side="right") - 1)
        
            n = len(exact_time)
            if n == 0:
                return 0, 0
            if i_start < 0: i_start = 0
            if i_start >= n: i_start = n - 1
            if i_stop < 0: i_stop = 0
            if i_stop >= n: i_stop = n - 1
            if i_stop < i_start:
                i_stop = i_start
            return i_start, i_stop

    def callback_chunk_drag_line(self, sender, app_data, user_data):
        # --- alias + tryb (bulk vs real drag)
        if isinstance(sender, int):
            line_name = dpg.get_item_alias(sender)
            fake_sender = False
            dpg.configure_item('Update_TCSPC_histogram', enabled=True)
        else:
            line_name = sender
            fake_sender = True
    
        # --- value: preferuj app_data
        value = app_data if app_data is not None else dpg.get_value(line_name)
    
        binw = float(dpg.get_value('left_panel_drag_time_binning'))
        nchunks = int(dpg.get_value('left_panel_N_chunks'))
    
        xdata1 = self.TT_xdata_1
        maxtime = float(xdata1[-1])  # xdata rosnące
    
        # realne kanały w danych
        photon_channels = self._get_photon_channels()
        nsel = len(self.channels)  # zostawiamy Twoją logikę wyboru 1/2
        # ale zabezpiecz się:
        if nsel == 2 and len(photon_channels) < 2:
            nsel = 1
    
        # parsowanie nazwy
        parts = line_name.split('_')
        chunk_num = int(parts[2]) - 1
        chunk_line_end = parts[3]
    
        t_start_1 = f"Chunk_1_{chunk_num+1}_start_dragline"
        t_stop_1  = f"Chunk_1_{chunk_num+1}_stop_dragline"
    
        # --- clamp (Twoja logika; ograniczona liczba get_value)
        if nsel == 1:
            if chunk_line_end == 'start':
                stop_val = float(dpg.get_value(t_stop_1))
                if value >= stop_val:
                    dpg.set_value(sender, stop_val)
                    value = stop_val
                else:
                    if chunk_num != 0:
                        prev_stop = float(dpg.get_value(f"Chunk_1_{chunk_num}_stop_dragline"))
                        if value < prev_stop:
                            dpg.set_value(sender, prev_stop)
                            value = prev_stop
                    else:
                        if value < 0:
                            dpg.set_value(sender, 0.0)
                            value = 0.0
    
            else:  # stop
                start_val = float(dpg.get_value(t_start_1))
                if value < start_val:
                    dpg.set_value(sender, start_val)
                    value = start_val
                else:
                    if (chunk_num + 1) != nchunks:
                        nxt_start_tag = f"Chunk_1_{chunk_num+2}_start_dragline"
                        if dpg.does_item_exist(nxt_start_tag):
                            nxt_start = float(dpg.get_value(nxt_start_tag))
                            if value > nxt_start:
                                dpg.set_value(sender, nxt_start)
                                value = nxt_start
                    else:
                        orig_max = float(self.chunks[f'chunk_{chunk_num}']['values'][1])
                        if value > orig_max:
                            dpg.set_value(sender, orig_max)
                            value = orig_max
    
        else:  # nsel == 2
            t_start_2 = f"Chunk_2_{chunk_num+1}_start_dragline"
            t_stop_2  = f"Chunk_2_{chunk_num+1}_stop_dragline"
    
            if chunk_line_end == 'start':
                stop1 = float(dpg.get_value(t_stop_1))
                stop2 = float(dpg.get_value(t_stop_2))
                stop_val = min(stop1, stop2)
                if value > stop_val:
                    dpg.set_value(sender, stop_val)
                    value = stop_val
                else:
                    if chunk_num != 0:
                        prev_stop1 = float(dpg.get_value(f"Chunk_1_{chunk_num}_stop_dragline"))
                        prev_stop2 = float(dpg.get_value(f"Chunk_2_{chunk_num}_stop_dragline"))
                        prev_stop = max(prev_stop1, prev_stop2)
                        if value < prev_stop:
                            dpg.set_value(sender, prev_stop)
                            value = prev_stop
                    else:
                        if value < 0:
                            dpg.set_value(sender, 0.0)
                            value = 0.0
    
            else:  # stop
                start1 = float(dpg.get_value(t_start_1))
                start2 = float(dpg.get_value(t_start_2))
                start_val = max(start1, start2)
                if value < start_val:
                    dpg.set_value(sender, start_val)
                    value = start_val
                else:
                    if (chunk_num + 1) != nchunks:
                        nxt_tag1 = f"Chunk_1_{chunk_num+2}_start_dragline"
                        nxt_tag2 = f"Chunk_2_{chunk_num+2}_start_dragline"
                        if dpg.does_item_exist(nxt_tag1) and dpg.does_item_exist(nxt_tag2):
                            nxt = min(float(dpg.get_value(nxt_tag1)), float(dpg.get_value(nxt_tag2)))
                            if value > nxt:
                                dpg.set_value(sender, nxt)
                                value = nxt
                    else:
                        if value > maxtime:
                            dpg.set_value(sender, maxtime)
                            value = maxtime
    
            # sync
            if 'Chunk_1' in line_name:
                co_line = line_name.replace('Chunk_1', 'Chunk_2')
            else:
                co_line = line_name.replace('Chunk_2', 'Chunk_1')
            dpg.set_value(co_line, value)
    
        # --- indeks TT
        ind = int(np.rint(value / binw))
        if ind < 0:
            ind = 0
        elif ind >= len(xdata1):
            ind = len(xdata1) - 1
    
        # start/stop z Chunk_1
        minval = float(dpg.get_value(t_start_1))
        maxval = float(dpg.get_value(t_stop_1))
        minvind = int(np.rint(minval / binw))
        maxvind = int(np.rint(maxval / binw))
        
        ch = self.chunks[f'chunk_{chunk_num}']
        
        # --- aktualizacja values/indices (jak u Ciebie)
        if chunk_line_end == 'start':
            ch['values'][0] = float(xdata1[ind])
            ch['indices'][0] = ind
            ch['values'][1] = maxval
            ch['indices'][1] = maxvind
        else:  # stop
            ch['values'][1] = float(xdata1[ind])
            ch['indices'][1] = ind
            ch['values'][0] = minval
            ch['indices'][0] = minvind
        
        # --- NOWE: TCSPC przez exact_time + searchsorted
        cache = getattr(self, "_tcspc_cache", None)
        if not cache:
            self._build_tcspc_time_cache()
            cache = self._tcspc_cache
        
        ph_ch = cache["channels"]
        t_start = float(minval)
        t_stop  = float(maxval)
        
        if nsel == 1:
            chan = ph_ch[0]
            exact = cache["exact_time"][chan]
            tcspc_s, tcspc_e = self._tcspc_indices_from_time(exact, t_start, t_stop)
            chn = 'ch1' if chan.endswith('_0') else ('ch2' if chan.endswith('_1') else 'ch1')
            ch['tcspc'][chn][0] = tcspc_s
            ch['tcspc'][chn][1] = tcspc_e
        
        else:
            exact1 = cache["exact_time"][ph_ch[0]]
            exact2 = cache["exact_time"][ph_ch[1]]
        
            s1, e1 = self._tcspc_indices_from_time(exact1, t_start, t_stop)
            s2, e2 = self._tcspc_indices_from_time(exact2, t_start, t_stop)
            ch['tcspc']['ch1'][0] = s1
            ch['tcspc']['ch1'][1] = e1
            ch['tcspc']['ch2'][0] = s2
            ch['tcspc']['ch2'][1] = e2
        # meta + ciężkie rzeczy tylko przy realnym dragu
        self.META_data['TT info'] = self.TT_snapshot()
        if not fake_sender:
            self.calculate_shade()
            self.plot_TT()


    
    # def callback_chunk_drag_line(self,sender,app_data,user_data):
    #     chunk_line = sender
    #     if isinstance(chunk_line, int):
    #         line_name = dpg.get_item_alias(chunk_line)
    #         fake_sender = False
    #         dpg.configure_item('Update_TCSPC_histogram', enabled=True)
    #     elif isinstance(chunk_line, str):
    #         line_name = sender
    #         fake_sender = True
            
    #     value = dpg.get_value(line_name)
    #     xdata1 = self.TT_xdata_1
    #     maxtime = xdata1.max()
    #     if len(self.channels) == 2:
    #         xdata2 = self.TT_xdata_2
    #     else:
    #         pass
    #     chunk_num = int(line_name.split('_')[2])-1
    #     chunk_line_end = line_name.split('_')[3]
    #     if len(self.channels) == 1:
    #         if chunk_line_end == 'start':
    #             if value>=dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'):
    #                 dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'))
    #             else:
    #                 if chunk_num !=0:
    #                     if value<dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'):
    #                         dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'))
    #                         value = dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline')
    #                 else:
    #                     if value<0:
    #                         dpg.set_value(sender,0)
    #                     else:
    #                         pass
    #         elif chunk_line_end == 'stop':
    #             if value<dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'):
    #                 dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'))
    #             else:
    #                 if chunk_num+1 !=dpg.get_value('left_panel_N_chunks'):
    #                     try:
    #                         if value>dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'):
    #                             dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'))
    #                             value = dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline')
    #                     except:
    #                         pass
    #                 else:
    #                     if value>self.chunks['chunk_'+str(chunk_num)]['values'][1]:
    #                         dpg.set_value(sender,self.chunks['chunk_'+str(chunk_num)]['values'][1])
    #                     else:
    #                         pass
    #     elif len(self.channels) == 2:
    #         if chunk_line_end == 'start':
    #             if value>dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline') or value>dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_stop_dragline'):
    #                 dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline'))
    #                 dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_stop_dragline'))
    #             else:
    #                 if chunk_num !=0:
    #                     if value<dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline') or value<dpg.get_value('Chunk_2_'+str(chunk_num)+'_stop_dragline'):
    #                         dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline'))
    #                         dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num)+'_stop_dragline'))
    #                         value = dpg.get_value('Chunk_1_'+str(chunk_num)+'_stop_dragline')
    #                 else:
    #                     if value<0:
    #                         dpg.set_value(sender,0)
    #                     else:
    #                         pass
    #         elif chunk_line_end == 'stop':
    #             if value<dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline') or  value<dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_start_dragline'):
    #                 dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline'))
    #                 dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+1)+'_start_dragline'))
    #                 value = dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline')
    #             else:
    #                 if chunk_num+1 !=dpg.get_value('left_panel_N_chunks'):
    #                     if value>dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline') or value>dpg.get_value('Chunk_2_'+str(chunk_num+2)+'_start_dragline'):
    #                         dpg.set_value(sender,dpg.get_value('Chunk_1_'+str(chunk_num+2)+'_start_dragline'))
    #                         dpg.set_value(sender,dpg.get_value('Chunk_2_'+str(chunk_num+2)+'_start_dragline'))
    #                 else:
    #                     if value>maxtime:
    #                         dpg.set_value(sender,maxtime)
    #                     else:
    #                         pass
    #         value = dpg.get_value(line_name)
                
    #         if 'Chunk_1' in line_name:
    #             co_line_name = line_name.replace('Chunk_1','Chunk_2')
            
    #         elif 'Chunk_2' in line_name:
    #             co_line_name = line_name.replace('Chunk_2','Chunk_1')
    #         dpg.set_value(co_line_name,value)                            
    #     ind =int(np.round(value/dpg.get_value('left_panel_drag_time_binning')))
    #     minval= dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_start_dragline')
    #     maxval= dpg.get_value('Chunk_1_'+str(chunk_num+1)+'_stop_dragline')   


    #     if chunk_line_end == 'start':
    #         self.chunks['chunk_'+str(chunk_num)]['values'][0] = xdata1[ind]
    #         self.chunks['chunk_'+str(chunk_num)]['indices'][0] = ind
    #         self.chunks['chunk_'+str(chunk_num)]['values'][1] = maxval
    #         self.chunks['chunk_'+str(chunk_num)]['indices'][1] = int(np.round(maxval/dpg.get_value('left_panel_drag_time_binning')))
    #         if len(self.channels) == 1:
    #             chan  = list(self.channels)[0]
    #             ind_array1= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             if ind in ind_array1:
    #                 tcspcind1_s = self.find_all_occurrences(ind_array1,ind)[0]
    #             else:
    #                 tcspcind1_s = self.find_closest(ind_array1,ind,False)
    #             maxvind = int(np.round(maxval/dpg.get_value('left_panel_drag_time_binning')))
    #             if maxvind in ind_array1:
    #                 tcspcind1_e = self.find_all_occurrences(ind_array1,maxvind)[-1]
    #             else: 
    #                 tcspcind1_e = self.find_closest(ind_array1,maxvind,True)
    #             chan = list(self.channels)[0]
    #             if chan.endswith('_0'):
    #                 chn = 'ch1'
    #             elif chan.endswith('_1'):
    #                 chn = 'ch2'
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc'][chn][0] = tcspcind1_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc'][chn][1] = tcspcind1_e
            
    #         if len(self.channels) == 2:
    #             chan  = list(self.channels)[0]
    #             ind_array1= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             chan  = list(self.channels)[1]
    #             ind_array2= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             if ind in ind_array1:
    #                 tcspcind1_s = self.find_all_occurrences(ind_array1,ind)[0]
    #             else:
    #                 tcspcind1_s = self.find_closest(ind_array1,ind,False)
    #             maxvind = int(np.round(maxval/dpg.get_value('left_panel_drag_time_binning')))
    #             if maxvind in ind_array1:
    #                 tcspcind1_e = self.find_all_occurrences(ind_array1,maxvind)[-1]
    #             else: 
    #                 tcspcind1_e = self.find_closest(ind_array1,maxvind,True)
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch1'][0] = tcspcind1_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch1'][1] = tcspcind1_e
    #             if ind in ind_array2:
    #                 tcspcind2_s = self.find_all_occurrences(ind_array2,ind)[0]
    #             else:
    #                 tcspcind2_s = self.find_closest(ind_array2,ind,False)
    #             if maxvind in ind_array2:
    #                 tcspcind2_e = self.find_all_occurrences(ind_array2,maxvind)[-1]
    #             else: 
    #                 tcspcind2_e = self.find_closest(ind_array2,maxvind,True)
               
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch2'][0] = tcspcind2_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch2'][1] = tcspcind2_e

        
    #     elif chunk_line_end == 'stop':
    #         if ind >np.argmax(xdata1):
    #             self.chunks['chunk_'+str(chunk_num)]['values'][1] = xdata1[np.argmax(xdata1)]
    #         else:
    #             self.chunks['chunk_'+str(chunk_num)]['values'][1] = xdata1[ind]
    #         self.chunks['chunk_'+str(chunk_num)]['indices'][1] = ind
    #         self.chunks['chunk_'+str(chunk_num)]['values'][0] = minval
    #         self.chunks['chunk_'+str(chunk_num)]['indices'][0] = int(np.round(minval/dpg.get_value('left_panel_drag_time_binning')))
    #         minvind = int(np.round(minval/dpg.get_value('left_panel_drag_time_binning')))
    #         if len(self.channels) == 1:
    #             chan  = list(self.channels)[0]
    #             ind_array1= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             if minvind in ind_array1:
    #                 # tcspcind1_s = np.where(ind_array1==minvind)[0][0]
    #                 tcspcind1_s = self.find_all_occurrences(ind_array1,minvind)[0]
    #             else:
    #                 tcspcind1_s = self.find_closest(ind_array1,minvind,False)
    #             if ind in ind_array1: 
    #                 tcspcind1_e = self.find_all_occurrences(ind_array1,ind)[-1]
    #             else:
    #                 tcspcind1_e =self.find_closest(ind_array1,ind,True)
    #             chan = list(self.channels)[0]
    #             if chan.endswith('_0'):
    #                 chn = 'ch1'
    #             elif chan.endswith('_1'):
    #                 chn = 'ch2'
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc'][chn][0] = tcspcind1_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc'][chn][1] = tcspcind1_e
    #         if len(self.channels) == 2:
    #             chan  = list(self.channels)[0]    
    #             ind_array1= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             chan  = list(self.channels)[1]
    #             ind_array2= np.round(self.fcs_data.PHOTONS[chan]['exact_time']/dpg.get_value('left_panel_drag_time_binning')).astype(int)
    #             if minvind in ind_array1:
    #                 tcspcind1_s = self.find_all_occurrences(ind_array1,minvind)[0]
    #             else:
    #                 tcspcind1_s = self.find_closest(ind_array1,minvind,False)
    #             if ind in ind_array1: 
    #                 tcspcind1_e = self.find_all_occurrences(ind_array1,ind)[-1]
    #             else:
    #                 tcspcind1_e =self.find_closest(ind_array1,ind,True)
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch1'][0] = tcspcind1_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch1'][1] = tcspcind1_e
    #             if minvind in ind_array2:
    #                 tcspcind2_s = self.find_all_occurrences(ind_array2,minvind)[0]
    #             else:
    #                 tcspcind2_s = self.find_closest(ind_array2,minvind,False)
    #             if ind in ind_array2: 
    #                 tcspcind2_e = self.find_all_occurrences(ind_array2,ind)[-1]
    #             else:
    #                 tcspcind2_e = self.find_closest(ind_array2,ind,True)
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch2'][0] = tcspcind2_s
    #             self.chunks['chunk_'+str(chunk_num)]['tcspc']['ch2'][1] = tcspcind2_e

    #     self.META_data['TT info']=self.TT_snapshot()

    #     if not fake_sender:
    #         self.calculate_shade()
    #         self.plot_TT()
            
        
    def calculate_shade(self):
        customchnk = dpg.get_value('Custom_chunks_check')
        if customchnk:
            meta = self.META_data['TT info']['chunks']
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
            if len(self.channels) == 2:
                rngmax2=self.TT_ydata_2.max()
                self.shade_data_2=[np.array(segments_x),
                               np.array(segments_y1),
                               np.where(np.array(segments_y2)==rngmax,rngmax2,0)]

        else:
            self.shade_data_1=[self.TT_xdata_1,
                               np.zeros(len(self.TT_xdata_1)),
                               np.zeros(len(self.TT_xdata_1))
                               ]
            if len(self.channels) == 2:
                self.shade_data_2=[self.TT_xdata_2,
                               np.zeros(len(self.TT_xdata_2)),
                               np.zeros(len(self.TT_xdata_2))
                               ]

    
    def call_back_update_TCSPC(self):
        self.transfer_chunks_to_TCSPC()
        self.META_data['TCSPC info']=self.TCSPC_snapshot()
        if len(self.channels) == 1:
            BGLvL = (dpg.get_value('TCSPC_BG_dline_ch1'),None)
        elif len(self.channels) == 2:
            BGLvL = (dpg.get_value('TCSPC_BG_dline_ch1'),dpg.get_value('TCSPC_BG_dline_ch2'))
        self.plot_TCSPC(BGLvL)
        dpg.configure_item('Update_TCSPC_histogram', enabled=False)
        
    def callback_tcspc_timegate(self,sender,app_data):
        if app_data:
            min1 = self.TCSCP_draglines['TCSPC_L_dline_ch1']
            max1 = self.TCSCP_draglines['TCSPC_U_dline_ch1']
            dpg.show_item('TCSPC_L_dline_ch1')
            dpg.set_value('TCSPC_L_dline_ch1',min1)
            self.callback_TCSPC_dragline('TCSPC_L_dline_ch1',min1)
            dpg.show_item('TCSPC_U_dline_ch1')
            dpg.set_value('TCSPC_U_dline_ch1',max1)
            self.callback_TCSPC_dragline('TCSPC_U_dline_ch1',max1)
            if len(self.channels) == 2: 
                min2 = self.TCSCP_draglines['TCSPC_L_dline_ch2']
                max2 = self.TCSCP_draglines['TCSPC_U_dline_ch2']
                dpg.show_item('TCSPC_L_dline_ch2')
                dpg.set_value('TCSPC_L_dline_ch2',min2)
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch2',min2)
                dpg.show_item('TCSPC_U_dline_ch2')
                dpg.set_value('TCSPC_U_dline_ch2',max2)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch2',min2)
        else:
            if len(self.channels) == 1: 
                chan = list(self.channels)[0]
                min1 = self.fcs_data.decay_hist[chan].decay_time.min()
                max1 = self.fcs_data.decay_hist[chan].decay_time.max()
                dpg.set_value('TCSPC_L_dline_ch1',min1)
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch1',min1)
                dpg.hide_item('TCSPC_L_dline_ch1')
                dpg.set_value('TCSPC_U_dline_ch1',max1)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch1',max1)
                dpg.hide_item('TCSPC_U_dline_ch1')
            if len(self.channels) == 2: 
                min1 = self.fcs_data.decay_hist['channel_0'].decay_time.min()
                max1 = self.fcs_data.decay_hist['channel_0'].decay_time.max()
                min2 = self.fcs_data.decay_hist['channel_1'].decay_time.min()
                max2 = self.fcs_data.decay_hist['channel_1'].decay_time.max()
                dpg.set_value('TCSPC_L_dline_ch1',min1)
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch1',min1)
                dpg.hide_item('TCSPC_L_dline_ch1')
                dpg.set_value('TCSPC_U_dline_ch1',max1)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch1',max1)
                dpg.hide_item('TCSPC_U_dline_ch1')
                dpg.set_value('TCSPC_L_dline_ch2',min2)
                self.callback_TCSPC_dragline('TCSPC_L_dline_ch2',min2)
                dpg.hide_item('TCSPC_L_dline_ch2')
                dpg.set_value('TCSPC_U_dline_ch2',max2)
                self.callback_TCSPC_dragline('TCSPC_U_dline_ch2',min2)
                dpg.hide_item('TCSPC_U_dline_ch2')
                                             
        
    def callback_tcspc_BG(self,sender,app_data):
        if app_data:
            dpg.show_item('TCSPC_BG_dline_ch1')
            dpg.show_item('TCSPC_BG_dline_ch2')
            self.subtract_tcspc('TCSPC_BG_dline_ch1',None)
            if len(self.channels) == 2: 
                self.subtract_tcspc('TCSPC_BG_dline_ch2',None)
        else:
            dpg.set_value('TCSPC_sub_plot1',([],[]))
            dpg.set_value('TCSPC_sub_plot2',([],[]))
            dpg.hide_item('TCSPC_BG_dline_ch1')
            dpg.hide_item('TCSPC_BG_dline_ch2')
        
    def callback_TCSPC_dragline(self,sender,app_data):
        if isinstance(sender, int):
            line_name = dpg.get_item_alias(sender)
        elif isinstance(sender, str):
            line_name = sender
        value = dpg.get_value(line_name)
        is_bg =dpg.get_value('TCSPC_BG_correction_check')
        if line_name == 'TCSPC_L_dline_ch1':
            xdata = (self.fcs_data.decay_hist[list(self.channels)[0]].decay_time).values
            Uvalue=dpg.get_value('TCSPC_U_dline_ch1')
            self.active_tcspcs_ch1_U_inds = np.where(xdata<=Uvalue)[0]
            self.active_tcspcs_ch1_L_inds = np.where(xdata>=value)[0]
            self.inactive_tcspcs_ch1_L_inds = np.where(xdata<value)[0]
            inds = np.intersect1d(self.active_tcspcs_ch1_L_inds,self.active_tcspcs_ch1_U_inds).astype(int)
            newxdata = xdata[inds]
            inctxdata = xdata[self.inactive_tcspcs_ch1_L_inds]
            ydata = (self.fcs_data.decay_hist[list(self.channels)[0]].counts).values
            newydata = ydata[inds]
            inctydata = ydata[self.inactive_tcspcs_ch1_L_inds]
            df = pd.DataFrame(newxdata,columns=['decay_time'])
            df['counts']=newydata
            self.fcs_data.active_decay_hist[list(self.channels)[0]] = df
            indf = pd.DataFrame(inctxdata,columns=['decay_time'])
            indf['counts']=inctydata
            self.fcs_data.inactive_decay_hist_L[list(self.channels)[0]] = indf
            dpg.set_value('TCSPC_plot1',(newxdata,newydata.astype(float)))
            dpg.set_value('TCSPC_plot1_L_inactive',(inctxdata,inctydata.astype(float)))
            if is_bg:
                self.subtract_tcspc('TCSPC_BG_dline_ch1',None)
            else:
                pass

        elif line_name == 'TCSPC_U_dline_ch1':
            xdata = (self.fcs_data.decay_hist[list(self.channels)[0]].decay_time).values
            Lvalue=dpg.get_value('TCSPC_L_dline_ch1')
            self.active_tcspcs_ch1_L_inds = np.where(xdata>=Lvalue)[0]
            self.active_tcspcs_ch1_U_inds = np.where(xdata<=value)[0]
            self.inactive_tcspcs_ch1_U_inds = np.where(xdata>value)[0]
            inds = np.intersect1d(self.active_tcspcs_ch1_L_inds,self.active_tcspcs_ch1_U_inds).astype(int)
            newxdata = xdata[inds]
            inctxdata = xdata[self.inactive_tcspcs_ch1_U_inds]
            ydata = (self.fcs_data.decay_hist[list(self.channels)[0]].counts).values
            newydata = ydata[inds]
            inctydata = ydata[self.inactive_tcspcs_ch1_U_inds]
            df = pd.DataFrame(newxdata,columns=['decay_time'])
            df['counts']=newydata
            self.fcs_data.active_decay_hist[list(self.channels)[0]] = df
            indf = pd.DataFrame(inctxdata,columns=['decay_time'])
            indf['counts']=inctydata
            self.fcs_data.inactive_decay_hist_U[list(self.channels)[0]] = indf
            dpg.set_value('TCSPC_plot1',[newxdata,newydata.astype(float)])
            dpg.set_value('TCSPC_plot1_U_inactive',[inctxdata,inctydata.astype(float)])
            if is_bg:
                self.subtract_tcspc('TCSPC_BG_dline_ch1',None)
            else:
                pass
        elif line_name == 'TCSPC_L_dline_ch2':
            xdata = (self.fcs_data.decay_hist[list(self.channels)[1]].decay_time).values
            Uvalue=dpg.get_value('TCSPC_U_dline_ch2')
            self.active_tcspcs_ch2_U_inds = np.where(xdata<=Uvalue)[0]
            self.active_tcspcs_ch2_L_inds = np.where(xdata>=value)[0]
            self.inactive_tcspcs_ch2_L_inds = np.where(xdata<value)[0]
            inds = np.intersect1d(self.active_tcspcs_ch2_L_inds,self.active_tcspcs_ch2_U_inds).astype(int)
            newxdata = xdata[inds]
            inctxdata = xdata[self.inactive_tcspcs_ch2_L_inds]
            ydata = (self.fcs_data.decay_hist[list(self.channels)[1]].counts).values
            newydata = ydata[inds]
            inctydata = ydata[self.inactive_tcspcs_ch2_L_inds]
            df = pd.DataFrame(newxdata,columns=['decay_time'])
            df['counts']=newydata
            self.fcs_data.active_decay_hist[list(self.channels)[1]] = df
            indf = pd.DataFrame(inctxdata,columns=['decay_time'])
            indf['counts']=inctydata
            self.fcs_data.inactive_decay_hist_L[list(self.channels)[1]] = indf
            dpg.set_value('TCSPC_plot2',(newxdata,newydata.astype(float)))
            dpg.set_value('TCSPC_plot2_L_inactive',(inctxdata,inctydata.astype(float)))
            if is_bg:
                self.subtract_tcspc('TCSPC_BG_dline_ch2',None)
            else:
                pass
            
        elif line_name == 'TCSPC_U_dline_ch2':
            xdata = (self.fcs_data.decay_hist[list(self.channels)[1]].decay_time).values
            Lvalue=dpg.get_value('TCSPC_L_dline_ch2')
            self.active_tcspcs_ch2_L_inds = np.where(xdata>=Lvalue)[0]
            self.active_tcspcs_ch2_U_inds = np.where(xdata<=value)[0]
            self.inactive_tcspcs_ch2_U_inds = np.where(xdata>value)[0]
            inds = np.intersect1d(self.active_tcspcs_ch2_L_inds,self.active_tcspcs_ch2_U_inds).astype(int)
            newxdata = xdata[inds]
            inctxdata = xdata[self.inactive_tcspcs_ch2_U_inds]
            ydata = (self.fcs_data.decay_hist[list(self.channels)[1]].counts).values
            newydata = ydata[inds]
            inctydata = ydata[self.inactive_tcspcs_ch2_U_inds]
            df = pd.DataFrame(newxdata,columns=['decay_time'])
            df['counts']=newydata
            self.fcs_data.active_decay_hist[list(self.channels)[1]] = df
            indf = pd.DataFrame(inctxdata,columns=['decay_time'])
            indf['counts']=inctydata
            self.fcs_data.inactive_decay_hist_U[list(self.channels)[1]] = indf
            dpg.set_value('TCSPC_plot2',[newxdata,newydata.astype(float)])
            dpg.set_value('TCSPC_plot2_U_inactive',[inctxdata,inctydata.astype(float)])
            if is_bg:
                self.subtract_tcspc('TCSPC_BG_dline_ch2',None)
            else:
                pass

    def subtract_tcspc(self,sender,app_data):
        if isinstance(sender, int):
            line_name = dpg.get_item_alias(sender)
        elif isinstance(sender, str):
            line_name = sender
        value = dpg.get_value(line_name)
        if line_name == 'TCSPC_BG_dline_ch1':
            xdata1 = self.fcs_data.decay_hist[list(self.channels)[0]].copy().decay_time
            ydata1 = self.fcs_data.decay_hist[list(self.channels)[0]].copy().counts
            sub_data1 = ydata1-value
            self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].decay_time = xdata1
            self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].counts = sub_data1
            inds = np.intersect1d(self.active_tcspcs_ch1_L_inds,self.active_tcspcs_ch1_U_inds).astype(int)
            xdata1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].decay_time.values[inds]
            ydata1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].counts.values[inds]
            dpg.set_value('TCSPC_sub_plot1',(xdata1,ydata1))
        elif line_name == 'TCSPC_BG_dline_ch2':
            xdata2 = self.fcs_data.decay_hist[list(self.channels)[1]].copy().decay_time
            ydata2 = self.fcs_data.decay_hist[list(self.channels)[1]].copy().counts
            sub_data2 = ydata2-value
            self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].decay_time = xdata2
            self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].counts = sub_data2
            inds = np.intersect1d(self.active_tcspcs_ch2_L_inds,self.active_tcspcs_ch2_U_inds).astype(int)
            xdata2 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].decay_time.values[inds]
            ydata2 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].counts.values[inds]
            dpg.set_value('TCSPC_sub_plot2',(xdata2,ydata2))
    
    
    def find_closest(self,array,value,upper):
        idx = np.searchsorted(array, value)
        if idx == 0:
            closest_value = array[0]
        elif idx >= len(array)-1:
            closest_value = array[-1]
        elif idx!= 0 and idx < len(array)-1:  
            before = array[idx - 1]
            after = array[idx]
            if abs(value - before) <= abs(value - after):
                closest_value = before
            else:
                closest_value = after

        index1 = self.find_all_occurrences(array,closest_value)
        if len(index1)>1:
            if upper:
                index1 = index1[-1]
            elif not upper:
                index1 = index1[0]
        elif len(index1) == 1:
            index1=index1[0]
        return index1
    
    def adjust_curves(self,imported_data, original_time_data):
        original_time_data.columns = ['time']
        imported_data = pd.concat([imported_data, original_time_data], ignore_index=True)
        imported_data = imported_data.sort_values(by='time').reset_index(drop=True)
        imported_data = imported_data.interpolate(method='cubicspline')
        joined_df = imported_data[imported_data['time'].isin(original_time_data['time'])].copy()
        joined_df['dif'] = joined_df['time'].diff()
        joined_df = joined_df.dropna().reset_index(drop=True)
        joined_df.loc[0, 'dif'] = -1
        joined_df = joined_df[joined_df['dif'] != 0].reset_index(drop=True)
        return joined_df
    
    
    def Calculate_TCSPC_filters(self,butt):
        is_gated = dpg.get_value('TCSPC_timegate_check')
        is_bg = dpg.get_value('TCSPC_BG_correction_check')
        if not is_gated and not is_bg:
            if len(self.channels) == 1:
                chan = list(self.channels)[0]
                raw_ch1 = self.fcs_data.decay_hist[list(self.channels)[0]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                self.CURVES[chan]=raw_ch1.ydata
                self.Filters[chan]={'Data':np.ones(len(self.CURVES[chan]))}
                rawx=raw_ch1.time.values
                self.Filters[chan]['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
            elif len(self.channels) == 2:
                raw_ch1 = self.fcs_data.decay_hist[list(self.channels)[0]].copy()
                raw_ch2 = self.fcs_data.decay_hist[list(self.channels)[1]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch2.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch2['ydata'] = raw_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                raw_ch2['ydata'] = raw_ch2.ydata/raw_ch2.ydata.sum()
                self.CURVES['channel_0']=raw_ch1.ydata
                self.CURVES['channel_1']=raw_ch2.ydata
                self.Filters['channel_0']={'Data':np.ones(len(self.CURVES['channel_0']))}
                self.Filters['channel_1']={'Data':np.ones(len(self.CURVES['channel_1']))}
                rawx=raw_ch1.time.values
                self.Filters['channel_0']['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
                rawx=raw_ch2.time.values
                self.Filters['channel_1']['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
        elif is_gated and not is_bg :
            if len(self.channels) == 1:
                chan = list(self.channels)[0]
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                self.CURVES[chan]={'Data':raw_ch1.ydata}
                self.Filters[chan]={'Data':np.ones(len(self.CURVES[chan]['Data']))}
                rawx=raw_ch1.time.values
                self.Filters[chan]['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
            elif len(self.channels) == 2:
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch2 = self.fcs_data.active_decay_hist[list(self.channels)[1]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch2.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch2['ydata'] = raw_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                raw_ch2['ydata'] = raw_ch2.ydata/raw_ch2.ydata.sum()
                self.CURVES['channel_0']={'Data':raw_ch1.ydata}
                self.CURVES['channel_1']={'Data':raw_ch2.ydata}
                self.Filters['channel_0']={'Data':np.ones(len(self.CURVES['channel_0']['Data']))}
                self.Filters['channel_1']={'Data':np.ones(len(self.CURVES['channel_1']['Data']))}
                rawx=raw_ch1.time.values
                self.Filters['channel_0']['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
                rawx=raw_ch2.time.values
                self.Filters['channel_1']['tcscp']=(rawx/self.fcs_data.tau_resolution).astype(int)
                
        elif not is_gated and is_bg:
            if len(self.channels) == 1:
                chan = list(self.channels)[0]
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                sub_ch1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].copy()
                sub_ch1.columns = ['time','ydata']
                sub_ch1['ydata'] = sub_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch1['ydata'] = sub_ch1.ydata/sub_ch1.ydata.sum()
                adjusted1 = self.adjust_curves(sub_ch1, pd.Series(raw_ch1.time).to_frame().copy())
                self.CURVES[chan]={'Data':adjusted1.ydata}
                afterpulse = 1/np.unique(adjusted1.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES[chan]['Data']])
                self.CURVES[chan]['BG']=afterpulse
                rawy=raw_ch1.ydata.values
                rawx=raw_ch1.time.values
                self.status_label = self.status_label_0+'channel 1 '+self.status_label_N
                self._set_butt_label(butt)
                self.Filters[chan]=self.fcs_data.calculate_stat_filter(self.CURVES[chan],rawy,rawx)
            elif len(self.channels) == 2:
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch2 = self.fcs_data.active_decay_hist[list(self.channels)[1]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch2.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch2['ydata'] = raw_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                raw_ch2['ydata'] = raw_ch2.ydata/raw_ch2.ydata.sum()
                sub_ch1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].copy()
                sub_ch1.columns = ['time','ydata']
                sub_ch1['ydata'] = sub_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch1['ydata'] = sub_ch1.ydata/sub_ch1.ydata.sum()
                adjusted1 = self.adjust_curves(sub_ch1, pd.Series(raw_ch1.time).to_frame().copy())
                self.CURVES['channel_0']={'Data':adjusted1.ydata}
                afterpulse = 1/np.unique(adjusted1.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES['channel_0']['Data']])
                self.CURVES['channel_0']['BG']=afterpulse
                rawy=raw_ch1.ydata.values
                rawx=raw_ch1.time.values
                self.status_label = self.status_label_0+'channel 1 '+self.status_label_N
                self._set_butt_label('Calculate_filter_once_button')
                self.Filters['channel_0']=self.fcs_data.calculate_stat_filter(self.CURVES['channel_0'],rawy,rawx)
                sub_ch2 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].copy()
                sub_ch2.columns = ['time','ydata']
                sub_ch2['ydata'] = sub_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch2['ydata'] = sub_ch2.ydata/sub_ch2.ydata.sum()
                adjusted2 = self.adjust_curves(sub_ch2, pd.Series(raw_ch2.time).to_frame().copy())
                self.CURVES['channel_1']={'Data':adjusted2.ydata}
                afterpulse = 1/np.unique(adjusted2.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES['channel_1']['Data']])
                self.CURVES['channel_1']['BG']=afterpulse
                rawy=raw_ch2.ydata.values
                rawx=raw_ch2.time.values
                self.status_label = self.status_label_0+'channel 2 '+self.status_label_N
                self._set_butt_label(butt)
                self.Filters['channel_1']=self.fcs_data.calculate_stat_filter(self.CURVES['channel_1'],rawy,rawx)
                
        elif is_gated and is_bg:
            if len(self.channels) == 1:
                chan = list(self.channels)[0]
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                sub_ch1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].copy()
                sub_ch1.columns = ['time','ydata']
                sub_ch1['ydata'] = sub_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch1['ydata'] = sub_ch1.ydata/sub_ch1.ydata.sum()
                adjusted1 = self.adjust_curves(sub_ch1, pd.Series(raw_ch1.time).to_frame().copy())
                self.CURVES[chan]={'Data':adjusted1.ydata}
                afterpulse = 1/np.unique(adjusted1.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES[chan]['Data']])
                self.CURVES[chan]['BG']=afterpulse
                rawy=raw_ch1.ydata.values
                rawx=raw_ch1.time.values
                self.status_label = self.status_label_0+'channel 1 '+self.status_label_N
                self._set_butt_label(butt)
                self.Filters[chan]=self.fcs_data.calculate_stat_filter(self.CURVES[chan],rawy,rawx)
            elif len(self.channels) == 2:
                raw_ch1 = self.fcs_data.active_decay_hist[list(self.channels)[0]].copy()
                raw_ch2 = self.fcs_data.active_decay_hist[list(self.channels)[1]].copy()
                raw_ch1.columns = ['time','ydata']
                raw_ch2.columns = ['time','ydata']
                raw_ch1['ydata'] = raw_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch2['ydata'] = raw_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                raw_ch1['ydata'] = raw_ch1.ydata/raw_ch1.ydata.sum()
                raw_ch2['ydata'] = raw_ch2.ydata/raw_ch2.ydata.sum()
                sub_ch1 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[0]].copy()
                sub_ch1.columns = ['time','ydata']
                sub_ch1['ydata'] = sub_ch1['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch1['ydata'] = sub_ch1.ydata/sub_ch1.ydata.sum()
                adjusted1 = self.adjust_curves(sub_ch1, pd.Series(raw_ch1.time).to_frame().copy())
                self.CURVES['channel_0']={'Data':adjusted1.ydata}
                afterpulse = 1/np.unique(adjusted1.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES['channel_0']['Data']])
                self.CURVES['channel_0']['BG']=afterpulse
                rawy=raw_ch1.ydata.values
                rawx=raw_ch1.time.values
                self.status_label = self.status_label_0+'channel 1 '+self.status_label_N
                self._set_butt_label(butt)
                self.Filters['channel_0']=self.fcs_data.calculate_stat_filter(self.CURVES['channel_0'],rawy,rawx)
                sub_ch2 = self.fcs_data.active_decay_hist_subtracted[list(self.channels)[1]].copy()
                sub_ch2.columns = ['time','ydata']
                sub_ch2['ydata'] = sub_ch2['ydata'].apply(lambda x: 0 if x < 0 else x)
                sub_ch2['ydata'] = sub_ch2.ydata/sub_ch2.ydata.sum()
                adjusted2 = self.adjust_curves(sub_ch2, pd.Series(raw_ch2.time).to_frame().copy())
                self.CURVES['channel_1']={'Data':adjusted2.ydata}
                afterpulse = 1/np.unique(adjusted2.time.values).size
                afterpulse = np.array([afterpulse for i in self.CURVES['channel_1']['Data']])
                self.CURVES['channel_1']['BG']=afterpulse
                rawy=raw_ch2.ydata.values
                rawx=raw_ch2.time.values
                self.status_label = self.status_label_0+'channel 2 '+self.status_label_N
                self._set_butt_label(butt)
                self.Filters['channel_1']=self.fcs_data.calculate_stat_filter(self.CURVES['channel_1'],rawy,rawx)
    
    def TCSPC_filtering(self,butt):
        self.autoNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.autoNorm_ch_2 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.CrossNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
        self.CrossNorm_ch_2  = pd.DataFrame(columns=['time','MEAN','SE'])
        self.Calculate_TCSPC_filters(butt)
        self.META_data['TCSPC info']=self.TCSPC_snapshot()
        
        
    def Correlating(self,sender):
        is_Two_channel = len(self.channels) == 2
        bintime = self.round_data(dpg.get_value('left_panel_drag_time_binning'))
        npoints = dpg.get_value('left_panel_drag_subs')
        tau_min = self.round_data(dpg.get_value('left_panel_tau_min'))
        tau_max = dpg.get_value('left_panel_tau_max')
        decades = max(1.0, (np.log10(tau_max) - np.log10(tau_min)))
        nsub = int(np.floor(npoints / decades))
        nsub = max(1, nsub)
        chunks = list(self.META_data['TT info']['chunks'].keys())
        self.autoNorm_ch_1,self.autoNorm_ch_2,self.CrossNorm_ch_1,self.CrossNorm_ch_2,self.DictOfChunks =self.fcs_data._CORRELATE(chunks,nsub,npoints,tau_min,tau_max,self.META_data,sender)

            
    def callback_crossCorr_check(self,sender,app_data):
        is_Two_channel = len(self.channels) == 2
        if app_data:
            dpg.show_item('FCS_CH1_leg')
            dpg.show_item('Cross_FCS_plot1')
            dpg.show_item('Cross_FCS_plot1_shade')
            dpg.hide_item('Cross_FCS_plot2_shade')
            if is_Two_channel:
                dpg.show_item('FCS_CH2_leg')
                dpg.show_item('Cross_FCS_plot2')
                dpg.show_item('Cross_FCS_plot2_shade')
                dpg.configure_item('FCS_CH1_leg',location=dpg.mvPlot_Location_NorthEast)
                dpg.configure_item('FCS_CH2_leg',location=dpg.mvPlot_Location_NorthEast)
        else:
            dpg.hide_item('FCS_CH1_leg')
            dpg.hide_item('Cross_FCS_plot1')
            dpg.hide_item('Cross_FCS_plot1_shade')
            dpg.hide_item('Cross_FCS_plot2_shade')
            if is_Two_channel:
                dpg.hide_item('FCS_CH2_leg')
                dpg.hide_item('Cross_FCS_plot2')
                dpg.hide_item('Cross_FCS_plot2_shade')
            
            

    def plot_FCS(self):
        is_Two_channel = len(self.channels) == 2
        is_chan_1 = list(self.channels)[0].endswith('_0')
        is_chan_2 = list(self.channels)[0].endswith('_1')
        if not is_Two_channel:
            if is_chan_1:
                is_len_non_0 = len(self.autoNorm_ch_1)!=0
                if is_len_non_0:
                    xAdata_1 = self.autoNorm_ch_1.time.values
                    yAdata_1 = self.autoNorm_ch_1.MEAN.values
                    yerrAdata_1 = [yAdata_1-self.autoNorm_ch_1.SE.values,yAdata_1+self.autoNorm_ch_1.SE.values]
                    dpg.set_axis_limits('FCS_xaxis_chan1',xAdata_1.min(),xAdata_1.max())
                    dpg.set_axis_limits('FCS_yaxis_chan1',yerrAdata_1[0].min(),yerrAdata_1[1].max())
                else:
                    xAdata_1 = np.empty(10)
                    yAdata_1 = np.empty(10)
                    yerrAdata_1 = [np.empty(10),np.empty(10)]
            elif is_chan_2:
                is_len_non_0 = len(self.autoNorm_ch_2)!=0
                if is_len_non_0:
                    xAdata_1 = self.autoNorm_ch_2.time.values
                    yAdata_1 = self.autoNorm_ch_2.MEAN.values
                    yerrAdata_1 = [yAdata_1-self.autoNorm_ch_2.SE.values,yAdata_1+self.autoNorm_ch_2.SE.values]
                    dpg.set_axis_limits('FCS_xaxis_chan1',xAdata_1.min(),xAdata_1.max())
                    dpg.set_axis_limits('FCS_yaxis_chan1',yerrAdata_1[0].min(),yerrAdata_1[1].max())
                else:
                    xAdata_1 = np.empty(10)
                    yAdata_1 = np.empty(10)
                    yerrAdata_1 = [np.empty(10),np.empty(10)]
                    dpg.set_axis_limits('FCS_xaxis_chan1',0.001,1000)
                    dpg.set_axis_limits('FCS_yaxis_chan1',0,1)
            else:
                pass
            dpg.set_value('auto_FCS_plot1',[xAdata_1,yAdata_1])
            dpg.set_value('auto_FCS_plot1_shade',[xAdata_1,yerrAdata_1[0],yerrAdata_1[1]])
            dpg.set_value('FCS_cross_check',False)
            self.callback_crossCorr_check('FCS_cross_check',dpg.get_value('FCS_cross_check'))
        else:
            dpg.show_item('FCS_cross_check')
            is_len_1_non_0 = len(self.autoNorm_ch_1)!=0
            if is_len_1_non_0:
                xAdata_1 = self.autoNorm_ch_1.time.values
                yAdata_1 = self.autoNorm_ch_1.MEAN.values
                yerrAdata_1 = [yAdata_1-self.autoNorm_ch_1.SE.values,yAdata_1+self.autoNorm_ch_1.SE.values]
                xCdata_1 = self.CrossNorm_ch_1.time.values
                yCdata_1 = self.CrossNorm_ch_1.MEAN.values
                yerrCdata_1 = [yCdata_1-self.CrossNorm_ch_1.SE.values,yCdata_1+self.CrossNorm_ch_1.SE.values]
                dpg.set_axis_limits('FCS_xaxis_chan1',xAdata_1.min(),xAdata_1.max())
                dpg.set_axis_limits('FCS_yaxis_chan1',
                                    min(yerrAdata_1[0].min(),yerrCdata_1[0].min()),
                                    max(yerrAdata_1[1].max(),yerrCdata_1[1].max())
                                   )
            else:
                xAdata_1 = np.empty(10)
                yAdata_1 = np.empty(10)
                yerrAdata_1 = [np.empty(10),np.empty(10)]
                xCdata_1 = np.empty(10)
                yCdata_1 = np.empty(10)
                yerrCdata_1 = [np.empty(10),np.empty(10)]
                
            is_len_2_non_0 = len(self.autoNorm_ch_2)!=0
            if is_len_2_non_0:
                xAdata_2 = self.autoNorm_ch_2.time.values
                yAdata_2 = self.autoNorm_ch_2.MEAN.values
                yerrAdata_2 = [yAdata_2-self.autoNorm_ch_2.SE.values,yAdata_2+self.autoNorm_ch_2.SE.values]
                xCdata_2 = self.CrossNorm_ch_2.time.values
                yCdata_2 = self.CrossNorm_ch_2.MEAN.values
                yerrCdata_2 = [yCdata_2-self.CrossNorm_ch_2.SE.values,yCdata_2+self.CrossNorm_ch_2.SE.values]
                dpg.set_axis_limits('FCS_xaxis_chan2',xAdata_2.min(),xAdata_2.max())
                dpg.set_axis_limits('FCS_yaxis_chan2',
                                    min(yerrAdata_2[0].min(),yerrCdata_2[0].min()),
                                    max(yerrAdata_2[1].max(),yerrCdata_2[1].max())
                                   )
            else:
                xAdata_2 = np.empty(10)
                yAdata_2 = np.empty(10)
                yerrAdata_2 = [np.empty(10),np.empty(10)]
                xCdata_2 = np.empty(10)
                yCdata_2 = np.empty(10)
                yerrCdata_2 = [np.empty(10),np.empty(10)]
                dpg.set_axis_limits('FCS_xaxis_chan2',0.001,1000)
                dpg.set_axis_limits('FCS_yaxis_chan2',0,1)

            dpg.set_value('auto_FCS_plot1',[xAdata_1,yAdata_1])
            dpg.set_value('auto_FCS_plot1_shade',[xAdata_1,yerrAdata_1[0],yerrAdata_1[1]])
            dpg.set_value('auto_FCS_plot2',[xAdata_2,yAdata_2])
            dpg.set_value('auto_FCS_plot2_shade',[xAdata_2,yerrAdata_2[0],yerrAdata_2[1]])
            dpg.set_value('Cross_FCS_plot1',[xCdata_1,yCdata_1])
            dpg.set_value('Cross_FCS_plot1_shade',[xCdata_1,yerrCdata_1[0],yerrCdata_1[1]])
            dpg.set_value('Cross_FCS_plot2',[xCdata_2,yCdata_2])
            dpg.set_value('Cross_FCS_plot2_shade',[xCdata_2,yerrCdata_2[0],yerrCdata_2[1]])
            dpg.set_value('FCS_cross_check',True)
            self.callback_crossCorr_check('FCS_cross_check',dpg.get_value('FCS_cross_check'))
            
    
    def mnt_bttns_TCSPC(self):
        dpg.configure_item('Calculate_filter_once_button',enabled=True)
        dpg.configure_item('Calculate_filter_all_button',enabled=True)
    
    
    def umnt_bttns_TCSPC(self):
        dpg.configure_item('Calculate_filter_once_button',enabled=False)
        dpg.configure_item('Calculate_filter_all_button',enabled=False)


    def mnt_bttns_FCS(self):
        dpg.configure_item('Calculate_correlation_once_button',enabled=True)
        dpg.configure_item('Calculate_correlation_all_button',enabled=True)
        dpg.configure_item('Export_correlation_curve_button',enabled=True)
        dpg.configure_item('Export_all_correlation_curves_button',enabled=True)
        dpg.configure_item('Export_correlation_curve_binary_button',enabled=True)
        dpg.configure_item('Export_all_correlation_curves_binary_button',enabled=True)
    
    def umnt_bttns_FCS(self):
        dpg.configure_item('Calculate_correlation_once_button',enabled=False)
        dpg.configure_item('Calculate_correlation_all_button',enabled=False)
        dpg.configure_item('Export_correlation_curve_button',enabled=False)
        dpg.configure_item('Export_all_correlation_curves_button',enabled=False)
        dpg.configure_item('Export_correlation_curve_binary_button',enabled=False)
        dpg.configure_item('Export_all_correlation_curves_binary_button',enabled=False)

    
    def tab_callback(self,sender, app_data, user_data):
        tab = dpg.get_item_alias(app_data)
        if tab =='Anal_window_TCSPC_tab':
            self.umnt_bttns_FCS()
            self.mnt_bttns_TCSPC()
        elif tab == 'Anal_window_Correlation_tab':
            self.umnt_bttns_TCSPC()
            self.mnt_bttns_FCS()
            

    def callback_calc_fltr_all(self,sender,app_data):
        filterscheck={'TG':dpg.get_value('TCSPC_timegate_check'),
                     'BG':dpg.get_value('TCSPC_BG_correction_check'),
                     'Nsubs':dpg.get_value('left_panel_drag_subs'),
                     'Nchunks':dpg.get_value('left_panel_N_chunks')}
        old_button_label = dpg.get_item_label('Calculate_filter_all_button')
        dpg.bind_item_theme('Calculate_filter_all_button', "fit_button_theme_busy")
        for i,file in enumerate(self.files):
            self.status_label_N = ' File '+str(i+1)+'/'+str(len(self.files))
            self.status_label = self.status_label_0+self.status_label_N
            self._set_butt_label('Calculate_filter_all_button')
            self.anal_file=file
            dpg.set_value('file_box',self.anal_file)
            self.callback_listbox('file_box',self.anal_file)
            dpg.set_value('TCSPC_timegate_check',filterscheck['TG'])
            self.callback_tcspc_timegate('TCSPC_timegate_check',dpg.get_value('TCSPC_timegate_check')) 
            dpg.set_value('TCSPC_BG_correction_check',filterscheck['BG'])
            self.callback_tcspc_BG('TCSPC_BG_correction_check',dpg.get_value('TCSPC_BG_correction_check'))
            dpg.set_value('left_panel_drag_subs',filterscheck['Nsubs'])
            dpg.set_value('left_panel_N_chunks',filterscheck['Nchunks'])
            # self.add_chunks(reset=True)   # albo reset=False
            # self._after_chunks_changed()
            self.TCSPC_filtering('Calculate_filter_all_button')
            self._PCKL_DATA()
        dpg.bind_item_theme('Calculate_filter_all_button', "fit_button_theme")
        dpg.set_item_label('Calculate_filter_all_button',old_button_label)

    def _set_butt_label(self,butt):
        dpg.set_item_label(butt,self.status_label)


            
    def callback_calc_fltr_one(self,sender,app_data):
        old_button_label = dpg.get_item_label('Calculate_filter_once_button')
        dpg.bind_item_theme('Calculate_filter_once_button', "fit_button_theme_busy")
        self.TCSPC_filtering('Calculate_filter_once_button')
        self._PCKL_DATA()
        dpg.bind_item_theme('Calculate_filter_once_button', "fit_button_theme")
        dpg.set_item_label('Calculate_filter_once_button',old_button_label)
            

    def callback_calc_corr_one(self,sender,app_data):
        if self.check_if_filters_exists():
            old_button_label = dpg.get_item_label('Calculate_correlation_once_button')
            dpg.bind_item_theme('Calculate_correlation_once_button', "fit_button_theme_busy")
            self.status_label = 'Correlating'
            self._set_butt_label('Calculate_correlation_once_button')
            self.Correlating(sender)
            self.plot_FCS()
            self._PCKL_DATA()
            dpg.bind_item_theme('Calculate_correlation_once_button', "fit_button_theme")
            dpg.set_item_label('Calculate_correlation_once_button',old_button_label)
            
        else:
            self.show_error('Please calculate TCSPC filters first!')


    def callback_calc_corr_all(self,sender,app_data):
        filterscheck={'Nsubs':dpg.get_value('left_panel_drag_subs'),
                     'Nchunks':dpg.get_value('left_panel_N_chunks')}
        inc_f=self.check_if_all_filters_exists()
        if len(inc_f) == 0:
            old_button_label = dpg.get_item_label('Calculate_correlation_all_button')
            dpg.bind_item_theme('Calculate_correlation_all_button', "fit_button_theme_busy")
            for i,file in enumerate(self.files):
                self.status_label_N = ' file '+str(i+1)+'/'+str(len(self.files))
                self.status_label = 'Correlating '+self.status_label_N
                self._set_butt_label('Calculate_correlation_all_button')
                self.anal_file=file
                dpg.set_value('file_box',self.anal_file)
                self.callback_listbox('file_box',self.anal_file)
                try: 
                    self.umnt_bttns_TCSPC()
                    self.mnt_bttns_FCS()
                except:
                    pass
                dpg.set_value('left_panel_drag_subs',filterscheck['Nsubs'])
                dpg.set_value('left_panel_N_chunks',filterscheck['Nchunks'])
                # self.add_chunks(reset=True)   # albo reset=False
                # self._after_chunks_changed()
                self.Correlating(sender)
                self.plot_FCS()
                self._PCKL_DATA()
            dpg.bind_item_theme('Calculate_correlation_all_button', "fit_button_theme")
            dpg.set_item_label('Calculate_correlation_all_button',old_button_label)
        else:
            self.show_error('Please calculate TCSPC filters first for the following files: \n'+"\n".join(inc_f))
    
    def mount_status_modal(self):
        aliases = dpg.get_aliases()
        with dpg.window(tag='load_ind_win',
                        width=self.ww,
                        height=250,
                        menubar=False,
                        autosize=False,
                        no_resize=True,
                        no_title_bar=True,
                        no_move=True,
                        no_background=True,
                        modal=True,
                        show=True):
            dpg.add_button(tag='loading_title',width=self.ww,label='Processing file:')
            dpg.bind_item_theme('loading_title', 'transparent_theme')
            dpg.add_button(tag='loading_butt',width=self.ww,label='')
            dpg.bind_item_theme('loading_butt', 'transparent_theme')
            dpg.add_button(tag='loading_status_text',width=self.ww,label='Status:')
            dpg.bind_item_theme('loading_status_text', 'transparent_theme')
            dpg.add_button(tag='loading_status',width=self.ww,label='')
            dpg.bind_item_theme('loading_status', 'transparent_theme')
            dpg.add_button(tag='loading_cnt_butt',width=self.ww,label='')
            dpg.bind_item_theme('loading_cnt_butt', 'transparent_theme')
        win_width = dpg.get_item_configuration('load_ind_win')['width']
        win_height = dpg.get_item_configuration('load_ind_win')['height']
        VP_w = dpg.get_viewport_width()
        VP_h = dpg.get_viewport_height()
        posit = (int(VP_w/2-win_width/2),int(VP_h/2-win_height/2))
        dpg.configure_item('load_ind_win',pos=posit)
        
        
    def unmount_status_modal(self):
        dpg.configure_item('load_ind_win',show=False)
        dpg.delete_item('loading_butt')
        dpg.delete_item('loading_status_text')
        dpg.delete_item('loading_status')
        dpg.delete_item('loading_cnt_butt')
        dpg.delete_item('loading_title')
        dpg.delete_item('load_ind_win')

            
    def auto_bg_lvl(self,ch):
        if self.fcs_data.PHOTONS['Mode'] != 'PIE':
            if ch == 'ch1':
                df = self.fcs_data.decay_hist[list(self.channels)[0]].copy()
                bgrng = df.where(df.decay_time>23.5).dropna()
                bgrng = bgrng.where(bgrng.decay_time<24.5).dropna()
                bg = bgrng.counts.mean()
            elif ch =='ch2':
                df = self.fcs_data.decay_hist[list(self.channels)[1]].copy()
                bgrng = df.where(df.decay_time>23.5).dropna()
                bgrng = bgrng.where(bgrng.decay_time<24.5).dropna()
                bg = bgrng.counts.mean()
        else:
            if ch == 'ch1':
                df = self.fcs_data.decay_hist[list(self.channels)[0]].copy()
                bgrng = df.where(df.decay_time>48.5).dropna()
                bgrng = bgrng.where(bgrng.decay_time<49.5).dropna()
                bg = bgrng.counts.mean()
            elif ch =='ch2':
                df = self.fcs_data.decay_hist[list(self.channels)[1]].copy()
                bgrng = df.where(df.decay_time>23.5).dropna()
                bgrng = bgrng.where(bgrng.decay_time<24.5).dropna()
                bg = bgrng.counts.mean()
        return bg

    def TT_snapshot(self):
        tbin = self.round_data(dpg.get_value('left_panel_drag_time_binning'))
        nsubs = dpg.get_value('left_panel_drag_subs')
        nchunks = dpg.get_value('left_panel_N_chunks')
        custom_chunk = dpg.get_value('Custom_chunks_check')
        chunks = self.chunks
        self.fcs_data.count_rate = self.fcs_data.calculate_count_rate(self.fcs_data.PHOTONS,self.fcs_data.timetrace,self.fcs_data.time_bin)
        output ={'Time_bin':tbin,
                 'Nsubs':nsubs,
                 'nchunks':nchunks,
                 'custom_chunk':custom_chunk,
                 'chunks':chunks,
                 'chunk_rates':self.fcs_data.count_rate
                }
        return output 


    def TCSPC_snapshot(self):
        tgate = dpg.get_value('TCSPC_timegate_check')
        tcspcBG_chk = dpg.get_value('TCSPC_BG_correction_check')
        dlines={'TCSPC_L_dline_ch1':dpg.get_value('TCSPC_L_dline_ch1'),
                'TCSPC_U_dline_ch1':dpg.get_value('TCSPC_U_dline_ch1'),
                'TCSPC_L_dline_ch2':dpg.get_value('TCSPC_L_dline_ch2'),
                'TCSPC_U_dline_ch2':dpg.get_value('TCSPC_U_dline_ch2'),
               }
        inact_decay = (self.fcs_data.inactive_decay_hist_L,self.fcs_data.inactive_decay_hist_U)
        act_decay = self.fcs_data.active_decay_hist
        BG_lvl = (dpg.get_value('TCSPC_BG_dline_ch1'),dpg.get_value('TCSPC_BG_dline_ch2'))
        subtracted = self.fcs_data.active_decay_hist_subtracted
        if self.META_data['TCSPC info']['Filters']==self.Filters:
            Filters = self.META_data['TCSPC info']['Filters']
        else:
            Filters = self.Filters
        output ={'tgate':tgate,
                 'tcspcBG_chk':tcspcBG_chk,
                 'dlines':dlines,                 
                 'inact_decay':inact_decay,
                 'act_decay':act_decay,
                 'BG_lvl':BG_lvl,
                 'subtracted':subtracted,
                 'Filters':Filters
                }
        return output 

    def FCS_snapshot(self):
        output ={'AutoCorr_1':self.autoNorm_ch_1,
                 'AutoCorr_2':self.autoNorm_ch_2,
                 'CrossCorr_12':self.CrossNorm_ch_1,
                 'CrossCorr_21':self.CrossNorm_ch_2
                }
        return output
        
    
        

    
    def _PCKL_DATA(self):
        self.META_data['TT info']=self.TT_snapshot()
        self.META_data['TCSPC info']=self.TCSPC_snapshot()
        self.META_data['FCS info']=self.FCS_snapshot()
        file=self.anal_file.replace('.ptu','.pd1')
        path = self.last_directory
        pkl_path = os.path.join(path,file)
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.META_data, f)
        chnk_file=self.anal_file.replace('.ptu','.chnk')
        path = self.last_directory
        chnk_path = os.path.join(path,chnk_file)
    def _apply_chunks_to_gui_fast(self):
        nsel = len(self.channels)
        # iteruj deterministycznie po chunk_0..chunk_{n-1}
        nchunks = int(dpg.get_value('left_panel_N_chunks'))
        for i in range(nchunks):
            ch = self.chunks.get(f"chunk_{i}")
            if ch is None:
                continue
            v0, v1 = ch["values"]
            dpg.set_value(f"Chunk_1_{i+1}_start_dragline", v0)
            dpg.set_value(f"Chunk_1_{i+1}_stop_dragline",  v1)
            if nsel == 2:
                dpg.set_value(f"Chunk_2_{i+1}_start_dragline", v0)
                dpg.set_value(f"Chunk_2_{i+1}_stop_dragline",  v1)

                
    def read_PKL_DATA(self,path):
    
        with open(path, 'rb') as file:
            pkl = pickle.load(file)
    
        self.META_data = pkl
    
        tt = pkl.get('TT info', {})
        tbin         = tt.get('Time_bin')
        nsubs        = tt.get('Nsubs')
        nchunks_pkl  = tt.get('nchunks')
        custom_chunk = tt.get('custom_chunk')
        chunks_pkl   = tt.get('chunks', {})
    
        if tbin is not None:
            dpg.set_value('left_panel_drag_time_binning', tbin)
        if nsubs is not None:
            dpg.set_value('left_panel_drag_subs', nsubs)
        if nchunks_pkl is not None:
            dpg.set_value('left_panel_N_chunks', int(nchunks_pkl))
        if custom_chunk is not None:
            dpg.set_value('Custom_chunks_check', bool(custom_chunk))
    
    
        self.chunks = chunks_pkl if isinstance(chunks_pkl, dict) else dict(chunks_pkl)
        self.add_chunks(reset=False)
    
        self._apply_chunks_to_gui_fast()
    
    
        self.META_data['TT info'] = self.TT_snapshot()
        if dpg.get_value('Custom_chunks_check'):
            self.calculate_shade()
            self.plot_TT()
    
    
        tc = pkl.get('TCSPC info', {})
        tgate = tc.get('tgate')
        tcspcBG_chk = tc.get('tcspcBG_chk')
        dlines = tc.get('dlines', {})
        BG_lvl = tc.get('BG_lvl', [0, 0])
    
        if tgate is not None:
            dpg.set_value('TCSPC_timegate_check', bool(tgate))
            self.callback_tcspc_timegate('TCSPC_timegate_check', bool(tgate))
    
        if tcspcBG_chk is not None:
            dpg.set_value('TCSPC_BG_correction_check', bool(tcspcBG_chk))
            self.callback_tcspc_BG('TCSPC_BG_correction_check', bool(tcspcBG_chk))
    
        if 'TCSPC_L_dline_ch1' in dlines: dpg.set_value('TCSPC_L_dline_ch1', dlines['TCSPC_L_dline_ch1'])
        if 'TCSPC_U_dline_ch1' in dlines: dpg.set_value('TCSPC_U_dline_ch1', dlines['TCSPC_U_dline_ch1'])
        if 'TCSPC_L_dline_ch2' in dlines: dpg.set_value('TCSPC_L_dline_ch2', dlines['TCSPC_L_dline_ch2'])
        if 'TCSPC_U_dline_ch2' in dlines: dpg.set_value('TCSPC_U_dline_ch2', dlines['TCSPC_U_dline_ch2'])
    
        if isinstance(BG_lvl, (list, tuple)) and len(BG_lvl) >= 2:
            dpg.set_value('TCSPC_BG_dline_ch1', BG_lvl[0])
            dpg.set_value('TCSPC_BG_dline_ch2', BG_lvl[1])
    
    
        fcs = pkl.get('FCS info', {})
        try:
            self.autoNorm_ch_1 = fcs.get('AutoCorr_1', pd.DataFrame(columns=['time','MEAN','SE']))
        except Exception:
            self.autoNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
    
        try:
            self.autoNorm_ch_2 = fcs.get('AutoCorr_2', pd.DataFrame(columns=['time','MEAN','SE']))
        except Exception:
            self.autoNorm_ch_2 = pd.DataFrame(columns=['time','MEAN','SE'])
    
        try:
            self.CrossNorm_ch_1 = fcs.get('CrossCorr_12', pd.DataFrame(columns=['time','MEAN','SE']))
        except Exception:
            self.CrossNorm_ch_1 = pd.DataFrame(columns=['time','MEAN','SE'])
    
        try:
            self.CrossNorm_ch_2 = fcs.get('CrossCorr_21', pd.DataFrame(columns=['time','MEAN','SE']))
        except Exception:
            self.CrossNorm_ch_2 = pd.DataFrame(columns=['time','MEAN','SE'])
    
        try:
            self.META_data['FCS info'] = self.FCS_snapshot()
        except Exception:
            pass
    
    

    def check_if_filters_exists(self):
        if len(self.META_data['TCSPC info']['Filters'])>0:
            return True
        else:
            return False
            

    def check_if_all_filters_exists(self):
        incorrect_files=[]
        for file in self.files:
            path = os.path.join(self.last_directory,file)
            path = path.replace('.ptu','.pd1')
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    pkl = pickle.load(f)
                    
                if len(pkl['TCSPC info']['Filters'])>0:
                    pass
                else:
                    incorrect_files.append(file)
            else:
                incorrect_files.append(file)
        return incorrect_files


    def check_if_all_Correlations_exists(self):
        incorrect_files=[]
        for file in self.files:
            path = os.path.join(self.last_directory,file)
            path = path.replace('.ptu','.pd1')
            with open(path, 'rb') as f:
                pkl = pickle.load(f)
            if len(pkl['FCS info']['AutoCorr_1'])>0 or len(pkl['FCS info']['AutoCorr_2'])>0:
                pass
            else:
                incorrect_files.append(file)
        return incorrect_files


    def callback_Export_correlation_curve_button(self,sender,app_data):
        if sender == 'Export_correlation_curve_button':
            if len(self.META_data['FCS info']['AutoCorr_1']) == 0:
                self.show_error('No correlation data yet. Please correlate data')
            else:
                dpg.show_item('file_dialog_save_correlated')
                self.corr_export_all='single'
                self.corr_export_ext = '.dat'
        else:
            inc_f=self.check_if_all_Correlations_exists()
            if len(inc_f) == 0:
                dpg.show_item('file_dialog_save_correlated')
                self.corr_export_all='all'
                self.corr_export_ext = '.dat'
            else:
                self.show_error('Please first calculate correlation curves for the following files: \n'+"\n".join(inc_f))

    
    def callback_Export_correlation_curve_binary_button(self,sender,app_data):
        if sender == 'Export_correlation_curve_binary_button':
            if len(self.META_data['FCS info']['AutoCorr_1']) == 0 and len(self.META_data['FCS info']['AutoCorr_2']) == 0:
                self.show_error('No correlation data yet. Please correlate data')
            else:
                dpg.show_item('file_dialog_save_correlated')
                self.corr_export_all='single'
                self.corr_export_ext = '.corr'
        else:
            inc_f=self.check_if_all_Correlations_exists()
            if len(inc_f) == 0:
                dpg.show_item('file_dialog_save_correlated')
                self.corr_export_all='all'
                self.corr_export_ext = '.corr'
            else:
                self.show_error('Please first calculate correlation curves for the following files: \n'+"\n".join(inc_f))

    
    def callback_export_correlation(self,sender,app_data):
        path_to_save = app_data['current_path']
        auto_1_path = os.path.join(path_to_save,'AutoCorr_ch1')
        auto_2_path = os.path.join(path_to_save,'AutoCorr_ch2')
        cross_1_path = os.path.join(path_to_save,'CrossCorr_ch1')
        cross_2_path = os.path.join(path_to_save,'CrossCorr_ch2')
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
        if self.corr_export_ext == '.dat':
            if self.corr_export_all=='single':
                is_cross = dpg.get_value('FCS_cross_check')
                file = self.anal_file.replace('.ptu','.dat')
                if len(self.channels) == 1:
                    chan = list(self.channels)[0]
                    if chan.endswith('_0'):
                        pathA1 = os.path.join(auto_1_path,file)
                        data=self.autoNorm_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathA1,index=False,sep='\t')
                    elif chan.endswith('_1'):
                        pathA2 = os.path.join(auto_2_path,file)
                        data=self.autoNorm_ch_2
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathA2,index=False,sep='\t')
                elif len(self.channels) == 2:
                    pathA1 = os.path.join(auto_1_path,file)
                    data=self.autoNorm_ch_1
                    data.columns=['X','Y','Y_err']
                    if np.all(data.Y_err == 0):
                        data.drop('Y_err',axis=1,inplace=True)
                    data.to_csv(pathA1,index=False,sep='\t')
                    pathA2 = os.path.join(auto_2_path,file)
                    data=self.autoNorm_ch_2
                    data.columns=['X','Y','Y_err']
                    if np.all(data.Y_err == 0):
                        data.drop('Y_err',axis=1,inplace=True)
                    data.to_csv(pathA2,index=False,sep='\t')
                    if is_cross:
                        pathC1 = os.path.join(cross_1_path,file)
                        data=self.CrossNorm_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathC1,index=False,sep='\t')
                        pathC2 = os.path.join(cross_2_path,file)
                        data=self.CrossNorm_ch_2
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathC2,index=False,sep='\t')
                    else:
                        pass
                
            elif self.corr_export_all=='all':
                for file in self.files:
                    pkl_path = os.path.join(self.last_directory,file)
                    pkl_path = pkl_path.replace('.ptu','.pd1')
                    expfile = file.replace('.ptu','.dat')
                    with open(pkl_path, 'rb') as f:
                        pkl = pickle.load(f)
                    auto_ch_1 = pkl['FCS info']['AutoCorr_1']
                    auto_ch_2 = pkl['FCS info']['AutoCorr_2']
                    Cross_ch_1 = pkl['FCS info']['CrossCorr_12']
                    Cross_ch_2 = pkl['FCS info']['CrossCorr_21']
                    is_cross = len(Cross_ch_1) >0 and len(Cross_ch_2)>0
                    if len(pkl['TCSPC info']['Filters']) == 1:
                        chan = list(pkl['TCSPC info']['Filters'].keys())[0]
                        if chan.endswith('_0'):
                            pathA1 = os.path.join(auto_1_path,expfile)
                            data=auto_ch_1
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            data.to_csv(pathA1,index=False,sep='\t')
                        elif chan.endswith('_1'):
                            pathA2 = os.path.join(auto_2_path,expfile)
                            data=auto_ch_2
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            data.to_csv(pathA2,index=False,sep='\t')
                    elif len(pkl['TCSPC info']['Filters']) == 2:
                        pathA1 = os.path.join(auto_1_path,expfile)
                        data=auto_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathA1,index=False,sep='\t')
                        pathA2 = os.path.join(auto_2_path,expfile)
                        data=auto_ch_2
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        data.to_csv(pathA2,index=False,sep='\t')
                        if is_cross:
                            pathC1 = os.path.join(cross_1_path,expfile)
                            data=Cross_ch_1
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            data.to_csv(pathC1,index=False,sep='\t')
                            pathC2 = os.path.join(cross_2_path,expfile)
                            data=Cross_ch_2
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            data.to_csv(pathC2,index=False,sep='\t')
            else:
                pass
            self.corr_export_all=None
        elif self.corr_export_ext == '.corr':
            if self.corr_export_all=='single':
                is_cross = dpg.get_value('FCS_cross_check')
                file = self.anal_file.replace('.ptu','.corr')
                if len(self.channels) == 1:
                    chan = list(self.channels)[0]
                    if chan.endswith('_0'):
                        pathA1 = os.path.join(auto_1_path,file)
                        data=self.autoNorm_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        DATA={'Correlation':data,
                              'CNTR':self.META_data['TT info']['chunk_rates'][chan],
                              'CorrelatedChunks':self.DictOfChunks['Channel_0']['ACF_1']
                             }
                        with open(pathA1, 'wb') as f:
                            pickle.dump(DATA, f)
                    elif chan.endswith('_1'):
                        pathA2 = os.path.join(auto_2_path,file)
                        data=self.autoNorm_ch_2
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        DATA={'Correlation':data,
                              'CNTR':self.META_data['TT info']['chunk_rates'][chan],
                              'CorrelatedChunks':self.DictOfChunks['Channel_1']['ACF_2']}
                        with open(pathA2, 'wb') as f:
                            pickle.dump(DATA, f)
                elif len(self.channels) == 2:
                    pathA1 = os.path.join(auto_1_path,file)
                    data=self.autoNorm_ch_1
                    data.columns=['X','Y','Y_err']
                    if np.all(data.Y_err == 0):
                        data.drop('Y_err',axis=1,inplace=True)
                    DATA={'Correlation':data,
                          'CNTR':self.META_data['TT info']['chunk_rates']['channel_0'],
                          'CorrelatedChunks':self.DictOfChunks['Channel_0']['ACF_1']}
                    with open(pathA1, 'wb') as f:
                        pickle.dump(DATA, f)
                    pathA2 = os.path.join(auto_2_path,file)
                    data=self.autoNorm_ch_2
                    data.columns=['X','Y','Y_err']
                    if np.all(data.Y_err == 0):
                        data.drop('Y_err',axis=1,inplace=True)
                    DATA={'Correlation':data,
                          'CNTR':self.META_data['TT info']['chunk_rates']['channel_1'],
                          'CorrelatedChunks':self.DictOfChunks['Channel_1']['ACF_2']}
                    with open(pathA2, 'wb') as f:
                        pickle.dump(DATA, f)
                    if is_cross:
                        pathC1 = os.path.join(cross_1_path,file)
                        data=self.CrossNorm_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        DATA={'Correlation':data,
                              'CNTR':self.META_data['TT info']['chunk_rates']['channel_0'],
                              'CorrelatedChunks':self.DictOfChunks['Channel_0']['CCF_1']}
                        with open(pathC1, 'wb') as f:
                            pickle.dump(DATA, f)
                        if is_cross:
                            pathC2 = os.path.join(cross_2_path,file)
                            data=self.CrossNorm_ch_2
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            DATA={'Correlation':data,
                                  'CNTR':self.META_data['TT info']['chunk_rates']['channel_1'],
                                  'CorrelatedChunks':self.DictOfChunks['Channel_1']['CCF_2']}
                            with open(pathC2, 'wb') as f:
                                pickle.dump(DATA, f)
                    else:
                        pass
                
            elif self.corr_export_all=='all':
                for file in self.files:
                    pkl_path = os.path.join(self.last_directory,file)
                    pkl_path = pkl_path.replace('.ptu','.pd1')
                    expfile = file.replace('.ptu','.corr')
                    with open(pkl_path, 'rb') as f:
                        pkl = pickle.load(f)
                    auto_ch_1 = pkl['FCS info']['AutoCorr_1']
                    auto_ch_2 = pkl['FCS info']['AutoCorr_2']
                    Cross_ch_1 = pkl['FCS info']['CrossCorr_12']
                    Cross_ch_2 = pkl['FCS info']['CrossCorr_21']
                    CNTR=pkl['TT info']['chunk_rates']
                    is_cross = len(Cross_ch_1) >0 and len(Cross_ch_2)>0
                    if len(pkl['TCSPC info']['Filters']) == 1:
                        chan = list(pkl['TCSPC info']['Filters'].keys())[0]
                        if chan.endswith('_0'):
                            pathA1 = os.path.join(auto_1_path,expfile)
                            data=auto_ch_1
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            DATA={'Correlation':data,
                                  'CNTR':pkl['TT info']['chunk_rates'][chan],
                                  'CorrelatedChunks':self.DictOfChunks['Channel_0']['ACF_1']
                                 }
                            with open(pathA1, 'wb') as f:
                                pickle.dump(DATA, f)
                        elif chan.endswith('_1'):
                            pathA2 = os.path.join(auto_2_path,expfile)
                            data=auto_ch_2
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            DATA={'Correlation':data,
                                  'CNTR':pkl['TT info']['chunk_rates'][chan],
                                  'CorrelatedChunks':self.DictOfChunks['Channel_1']['ACF_2']
                                 }
                            with open(pathA2, 'wb') as f:
                                pickle.dump(DATA, f)
                    elif len(pkl['TCSPC info']['Filters']) == 2:
                        pathA1 = os.path.join(auto_1_path,expfile)
                        data=auto_ch_1
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        DATA={'Correlation':data,
                              'CNTR':pkl['TT info']['chunk_rates']['channel_0'],
                              'CorrelatedChunks':self.DictOfChunks['Channel_0']['ACF_1']
                              }
                        with open(pathA1, 'wb') as f:
                            pickle.dump(DATA, f)
                        pathA2 = os.path.join(auto_2_path,expfile)
                        data=auto_ch_2
                        data.columns=['X','Y','Y_err']
                        if np.all(data.Y_err == 0):
                            data.drop('Y_err',axis=1,inplace=True)
                        DATA={'Correlation':data,
                              'CNTR':pkl['TT info']['chunk_rates']['channel_1'],
                              'CorrelatedChunks':self.DictOfChunks['Channel_1']['ACF_2']
                              }
                        with open(pathA2, 'wb') as f:
                            pickle.dump(DATA, f)
                        if is_cross:
                            pathC1 = os.path.join(cross_1_path,expfile)
                            data=Cross_ch_1
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            DATA={'Correlation':data,
                                  'CNTR':pkl['TT info']['chunk_rates']['channel_0'],
                                  'CorrelatedChunks':self.DictOfChunks['Channel_0']['CCF_1']
                                 }
                            with open(pathC1, 'wb') as f:
                                pickle.dump(DATA, f)
                            pathC2 = os.path.join(cross_2_path,expfile)
                            data=Cross_ch_2
                            data.columns=['X','Y','Y_err']
                            if np.all(data.Y_err == 0):
                                data.drop('Y_err',axis=1,inplace=True)
                            DATA={'Correlation':data,
                                  'CNTR':pkl['TT info']['chunk_rates']['channel_1'],
                                  'CorrelatedChunks':self.DictOfChunks['Channel_1']['CCF_2']
                                 }
                            with open(pathC2, 'wb') as f:
                                pickle.dump(DATA, f)
            else:
                pass
            self.corr_export_all=None
        dpg.configure_item('file_dialog_id_PTU',default_path=self.last_directory)
        dpg.configure_item('file_dialog_save_correlated',default_path=self.last_directory)
        self.basf.log_last_directory(self.last_directory)    
        self.update_default_directory(self.last_directory)
            

    def calculate_chunk_rate(self):
        channels = list(self.fcs_data.timetrace.keys())
        chhunk_rates = {}
        chhunk_rates ={ch:() for ch in channels}
        if 'chunks' in self.META_data['TT info'].keys():
            for ch in channels:
                chunks = list(self.META_data['TT info']['chunks'].keys())
                if len(chunks)==1:
                    for chunk in chunks:
                        ind=self.META_data['TT info']['chunks'][chunk]['indices']
                        Time = self.fcs_data.timetrace[ch].time_interval.values[ind[0]:ind[1]]
                        occur = self.fcs_data.timetrace[ch].occurrences.values[ind[0]:ind[1]]
                        df = self.fcs_data.timetrace[ch][ind[0]:ind[1]]
                        
                        cntr = self.fcs_data.calculate_chunk_count_rate(df)
                elif len(chunks)>1:
                    CHNK = []
                    for chunk in chunks:
                        ind=self.META_data['TT info']['chunks'][chunk]['indices']
                        Time = self.fcs_data.timetrace[ch].time_interval.values[ind[0]:ind[1]]
                        occur = self.fcs_data.timetrace[ch].occurrences.values[ind[0]:ind[1]]
                        df = self.fcs_data.timetrace[ch][ind[0]:ind[1]]
                        cntr = self.fcs_data.calculate_chunk_count_rate(df)
                        CHNK.append(cntr[0])
                        print(df.head())
                    cntr = (np.mean(CHNK),np.std(CHNK,ddof=1))
                chhunk_rates[ch]=cntr
        else:
            pass
        return chhunk_rates
            

    def update_default_directory(self, last_directory):
        dpg.configure_item('file_dialog_id_PTU', default_path=last_directory)
        dpg.configure_item('file_dialog_save_correlated', default_path=last_directory)