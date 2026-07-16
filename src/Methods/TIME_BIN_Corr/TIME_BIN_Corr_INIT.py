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
from functools import wraps
from datetime import datetime
import inspect
import include.INIT as inits
from include.fcsutils import load_fcs
logfile=os.path.join('Logs','log.txt')
bf = inits._basicF(logfile,None)
lprint = bf.lnprint
FCS = load_fcs(None,None)
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
        file_path_A1  =os.path.join(self.output_path,'AutoCorr_ch1',filename)
        file_path_A2  =os.path.join(self.output_path,'AutoCorr_ch2',filename)
        file_path_C1  =os.path.join(self.output_path,'CrossCorr_ch1',filename)
        file_path_C2  =os.path.join(self.output_path,'CrossCorr_ch1',filename)
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
            if not self.IsTwoChannel:
                tmpdf = pd.read_csv(meta['Meta']['Correlation']['A_c0'],sep='\t')
                self.res_to_exp = {'filename':self.anal_file,
                               'result_ACF_1':tmpdf}
            elif self.IsTwoChannel:
                tmpdf_A1 = pd.read_csv(meta['Meta']['Correlation']['A_c0'],sep='\t')
                tmpdf_A2 = pd.read_csv(meta['Meta']['Correlation']['A_c1'],sep='\t')
                tmpdf_C1 = pd.read_csv(meta['Meta']['Correlation']['C_c0'],sep='\t')
                tmpdf_C2 = pd.read_csv(meta['Meta']['Correlation']['C_c1'],sep='\t')
                self.res_to_exp = {'filename':self.anal_file,
                               'result_ACF_1':tmpdf_A1,
                               'result_ACF_2':tmpdf_A2,
                               'result_CCF_1':tmpdf_C1,
                               'result_CCF_2':tmpdf_C2}
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
        if not dummy:
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

    def correlate(self,sender,app_data):
        bintime = self.round_data(dpg.get_value('left_panel_drag_time_binning'))
        chnks = self.chunks.keys()
        npoints = dpg.get_value('left_panel_drag_subs')
        tau_min = self.round_data(dpg.get_value('left_panel_tau_min'))
        tau_max = dpg.get_value('left_panel_tau_max')
        decades = np.round(log10(tau_max)-log10(tau_min))
        nsub = int(np.floor(1*(npoints/decades)))
        centers, edges = FCS.make_log_grid_ms(tmin_ms=tau_min, tmax_ms=tau_max, points_per_decade=nsub)
        
        if not self.IsTwoChannel:
            acf_columns = []
            chunk_lengths_sec_1 = []
            for chnk in chnks:
                indices = self.chunks[chnk]['indices']
                xdata = self.TT_xdata_1[indices[0]:indices[1]].astype(float)
                ydata = self.TT_ydata_1[indices[0]:indices[1]].astype(float)
                column = 'acf_'+chnk
                acf_columns.append(column)
                self.ACF_1 = pd.DataFrame(mtau.autocorrelate(ydata,
                                                             deltat=1e3*bintime,
                                                             m=nsub,
                                                             normalize=True),
                                                             columns = ['lagtime',
                                                                        column])
                chunk_lengths_sec_1.append(1e3*(xdata[-1]-xdata[0]))
                taus = self.ACF_1.lagtime.values[1:]
                ACF = self.ACF_1[column].values[1:]
                self.ACF_1 = pd.DataFrame(FCS.rebin_tau_to_grid(taus,centers, edges),columns = ['lagtime'])
                self.ACF_1[column] = FCS.rebin_chunk_to_grid(taus,ACF, centers, edges)
                self.chunks[chnk]['ACF'] = self.ACF_1.copy()

            acf_frames = [self.chunks[chnk]['ACF'] for chnk in chnks]
            ACFFr = pd.concat(acf_frames,axis=1)
            if dpg.get_value('left_panel_N_chunks') > 1:
                t=ACFFr['lagtime'].mean(axis=1)
                ACFFr['time'] = t
            else:
                ACFFr['time'] = ACFFr['lagtime']
            auto_ch1 = FCS._compute_MEAN_STD(ACFFr, acf_columns,chunk_lengths_sec=chunk_lengths_sec_1)
            ACFFr['MEAN'],ACFFr['SE']  = auto_ch1
            self.res_to_exp['filename']=self.anal_file
            if dpg.get_value('left_panel_N_chunks') > 1: 
                self.res_to_exp['result_ACF_1']=ACFFr[['time','MEAN','SE']]
            else:
                self.res_to_exp['result_ACF_1']=ACFFr[['time','MEAN']]
            Mainmeta = self.files[self.anal_file]['Meta']
            filename = self.anal_file+('_corr.dat')
            file_path  =os.path.join(self.output_path,'AutoCorr_ch1',filename)
            Mainmeta =  {'Correlation':{'A_c0':file_path},
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
            self.res_to_exp['result_ACF_1'].to_csv(file_path,sep='\t',index=False)
            chnkpath = os.path.join(self.output_path,self.anal_file+'.chnk')
            with open(chnkpath, "wb") as p:
                pickle.dump(self.chunks, p)
        elif self.IsTwoChannel:
            chunk_columns = []
            chunk_lengths_sec_1 = []
            chunk_lengths_sec_2 = []
            for chnk in chnks:
                indices = self.chunks[chnk]['indices']
                xdata_1 = self.TT_xdata_1[indices[0]:indices[1]].astype(float)
                xdata_2 = self.TT_xdata_2[indices[0]:indices[1]].astype(float)
                ydata_1 = self.TT_ydata_1[indices[0]:indices[1]].astype(float)
                ydata_2 = self.TT_ydata_2[indices[0]:indices[1]].astype(float)
                column = 'acf_'+chnk
                chunk_columns.append(column)
                self.ACF_1 = pd.DataFrame(mtau.autocorrelate(ydata_1,
                                                             deltat=1e3*bintime,
                                                             m=nsub,
                                                             normalize=True),
                                                             columns = ['lagtime',column])
                self.ACF_2 = pd.DataFrame(mtau.autocorrelate(ydata_2,
                                                             deltat=1e3*bintime,
                                                             m=nsub,
                                                             normalize=True),
                                                             columns = ['lagtime',column])
                self.CCF_1 = pd.DataFrame(mtau.correlate(ydata_1,ydata_2,
                                                             deltat=1e3*bintime,
                                                             m=nsub,
                                                             normalize=True),
                                                             columns = ['lagtime',column])
                self.CCF_2 = pd.DataFrame(mtau.correlate(ydata_2,ydata_1,
                                                             deltat=1e3*bintime,
                                                             m=nsub,
                                                             normalize=True),
                                                             columns = ['lagtime',column])
                chunk_lengths_sec_1.append(1e3*(xdata_1[-1]-xdata_1[0]))
                chunk_lengths_sec_2.append(1e3*(xdata_2[-1]-xdata_2[0]))
                Ataus_1 = self.ACF_1.lagtime.values[1:]
                Ataus_2 = self.ACF_2.lagtime.values[1:]
                Ctaus_1 = self.CCF_1.lagtime.values[1:]
                Ctaus_2 = self.CCF_2.lagtime.values[1:]
                ACF_1 = self.ACF_1[column].values[1:]
                ACF_2 = self.ACF_2[column].values[1:]
                CCF_1 = self.CCF_1[column].values[1:]
                CCF_2 = self.CCF_2[column].values[1:]
                self.ACF_1 = pd.DataFrame(FCS.rebin_tau_to_grid(Ataus_1,centers, edges),columns = ['lagtime'])
                self.ACF_2 = pd.DataFrame(FCS.rebin_tau_to_grid(Ataus_2,centers, edges),columns = ['lagtime'])
                self.CCF_1 = pd.DataFrame(FCS.rebin_tau_to_grid(Ctaus_1,centers, edges),columns = ['lagtime'])
                self.CCF_2 = pd.DataFrame(FCS.rebin_tau_to_grid(Ctaus_2,centers, edges),columns = ['lagtime'])
                self.ACF_1[column] = FCS.rebin_chunk_to_grid(Ataus_1,ACF_1, centers, edges)
                self.ACF_2[column] = FCS.rebin_chunk_to_grid(Ataus_2,ACF_2, centers, edges)
                self.CCF_1[column] = FCS.rebin_chunk_to_grid(Ctaus_1,CCF_1, centers, edges)
                self.CCF_2[column] = FCS.rebin_chunk_to_grid(Ctaus_2,CCF_2, centers, edges)
                self.chunks[chnk]['ACF_1'] = self.ACF_1.copy()
                self.chunks[chnk]['ACF_2'] = self.ACF_2.copy()
                self.chunks[chnk]['CCF_1'] = self.CCF_1.copy()
                self.chunks[chnk]['CCF_2'] = self.CCF_2.copy()
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
            ACFFr_1['MEAN'],ACFFr_1['SE'] = auto_ch1
            ACFFr_2['MEAN'],ACFFr_2['SE'] = auto_ch2
            CCFFr_1['MEAN'],CCFFr_1['SE'] = cross_ch1
            CCFFr_2['MEAN'],CCFFr_2['SE'] = cross_ch2
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
            filename = self.anal_file+('_corr.dat')
            file_path_A1  =os.path.join(self.output_path,'AutoCorr_ch1',filename)
            file_path_A2  =os.path.join(self.output_path,'AutoCorr_ch2',filename)
            file_path_C1  =os.path.join(self.output_path,'CrossCorr_ch1',filename)
            file_path_C2  =os.path.join(self.output_path,'CrossCorr_ch1',filename)
            Mainmeta =  {'Correlation':{'A_c0':file_path_A1,
                                        'A_c1':file_path_A2,
                                        'C_c0':file_path_C1,
                                        'C_c1':file_path_C2,
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
            self.plot_ACF()
            self.res_to_exp['result_ACF_1'].to_csv(file_path_A1,sep='\t',index=False)
            self.res_to_exp['result_ACF_2'].to_csv(file_path_A2,sep='\t',index=False)
            self.res_to_exp['result_CCF_1'].to_csv(file_path_C1,sep='\t',index=False)
            self.res_to_exp['result_CCF_2'].to_csv(file_path_C2,sep='\t',index=False)
            chnkpath = os.path.join(self.output_path,self.anal_file+'.chnk')
            with open(chnkpath, "wb") as p:
                pickle.dump(self.chunks, p)
    
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    def correlate_all(self,sender,app_data):
        dpg.set_value('Custom_chunks_check',False)
        old_button_label = dpg.get_item_label('Correlate_all_button')
        dpg.bind_item_theme('Correlate_all_button', "fit_button_theme_busy")
        for i, file in enumerate(self.files):
            fittin_label = 'Correlating file '+str(i+1)+' of '+str(len(self.files))
            dpg.set_item_label('Correlate_all_button',fittin_label)
            dpg.set_value('file_box',file)
            self.callback_listbox('file_box',file)
            self.correlate('Correlate_once_button',None)
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