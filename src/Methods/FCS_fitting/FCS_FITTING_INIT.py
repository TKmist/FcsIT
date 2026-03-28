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
import json
import pandas as pd
import numpy as np
from numpy import log10, sqrt, exp, log, pi
import time
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from matplotlib.transforms import Bbox
import matplotlib.pyplot as plt
from scipy.stats import chi2
from sympy.parsing.sympy_parser import parse_expr
from sympy import latex
from io import BytesIO
from PIL import Image
from lmfit import Model, Parameters, Minimizer
from colorama import  Fore, Style
import colorama 
colorama.init()

import ast
import pickle
import include.INIT as inits

import time
import socket
import argparse
from functools import wraps
from datetime import datetime
import inspect

from include.INIT import _basicF as _bf

logfile=os.path.join('Logs','log.txt')

###############################################################################
###############################################################################
''' Inits'''
###############################################################################
###############################################################################


class _FCS_Fitting_init:
    
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
        '''General variables'''
        self.last_directory = last_directory
       
        
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
        self.Settings_window = {'width':600,
                              'height':550,
                              'pos':(300,200)
                                }
        self.Setts_save_defaults = 150
        self.Setts_cancel = 150

        dpg.set_global_font_scale(self.fnt_ratio)
        
        self.file_window = {'name':'file_window',
                            'width':int(340*self.size_ratio['width']),
                            'height':dpg.get_viewport_height()-4*self.bottom_indent,
                            'pos':(self.left_indent,self.top_indent)
                            }
        self.comm_window = {'name':'comm_window',
                            'width':int(350*self.size_ratio['width']),
                            'height':int(100*self.size_ratio['height']),
                            'pos':(self.file_window['pos'][0]+self.file_window['width']+self.internal_indent,
                                   self.file_window['height']-int(100*self.size_ratio['height'])+self.top_indent)
                            }
        self.comm_box = {'name':'comm_box',
                         'width':-1,
                         'num_items':int(4*self.size_ratio['height']),
                         'items': []
                        }
        self.Model_selection_panel = {'name':'Model_selection_panel',
                            'width':int(350*self.size_ratio['width']),
                            'height':self.file_window['height']-self.comm_window['height']-self.internal_indent,
                            'pos':(self.file_window['pos'][0]+self.file_window['width']+self.internal_indent,self.file_window['pos'][1])
                            }
        
        
        self.Add_model_window = {'name':'Add_model_window',
                            'width':int(1230*self.size_ratio['width']),
                            'height':int(900*self.size_ratio['height']),
                            'pos':(2*self.left_indent,2*self.top_indent)
                            }
        self.plot_win = {'name':'plot_win',
                            'width':dpg.get_viewport_width()-self.file_window['width']-self.internal_indent-self.Model_selection_panel['width']-self.internal_indent-2*self.right_indent,
                            'height':self.file_window['height'],
                            'pos':(self.Model_selection_panel['pos'][0]+self.Model_selection_panel['width']+self.internal_indent,
                                   self.Model_selection_panel['pos'][1])
                            }
        
        self.file_dialog_id1 = {'name':'file_dialog_id1',
                               'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)
                              }
        self.multi_file_dialog_id = {'name':'multi_file_dialog_id',
                                     'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)}
        
        self.file_dialog_plot_all = {'name':'file_dialog_plot_all',
                                     'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)}
        
        self.file_dialog_export = {'name':'file_dialog_export',
                                   'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)}
        
        self.internal_width_left_panel = int(self.file_window['width']-self.internal_indent-self.group_spacer*3)
        
        self.internal_width_middle_panel = int(self.Model_selection_panel['width']-self.internal_indent-self.group_spacer*3)
        
        self.internal_width_right_panel = int(self.plot_win['width']-2*self.internal_indent+3*self.group_spacer)
        
        self.internal_height_right_panel = int(self.plot_win['height']-2*self.internal_indent-self.group_spacer)

        self.file_box = {'name':'file_box',
                         'width':-1,
                         'num_items':10
                        }
        self.Add_model_button = {'name':'Add_model_button',
                         'width':int(107*self.size_ratio['width'])
                        }
        self.model_choose = {'name':'model_choose',
                         'width':int(self.internal_width_middle_panel-self.Add_model_button['width'])
                        }
        
        self.CNTR ={'name':'CNTR',
            'width':-1}
        self.BRIGHT ={'name':'BRIGHT',
            'width':-1}
        self.Xunits = {'name':'Xunits',
                         'width':int(165*self.size_ratio['width'])
                        }
        self.Yunits = {'name':'Yunits',
                         'width':int(165*self.size_ratio['width'])
                        }
        self.df_min = {'name':'df_min',
                         'width':int(165*self.size_ratio['width'])
                        }
        self.df_max = {'name':'df_max',
                         'width':int(165*self.size_ratio['width'])
                        }
        self.Reset_range = {'name':'Reset_range',
                         'width':int(165*self.size_ratio['width'])
                        }
        
        self.subplots = {'name':'subplots',
                         'width': self.internal_width_right_panel,
                         'height': self.internal_height_right_panel-4*self.internal_indent-self.group_spacer*2}
        
        self.image_1 = { 
                         'width':int(1224*self.size_ratio['width']),
                             'height':int(200*self.size_ratio['height'])}

        self.DialWinList = []
    
    
    
    
    
    def load_default_settings(self):
        path = os.path.join('Methods','FCS_fitting','res','JSON_files','Default_settings.json')

        with open(path) as json_settings:
            OPTIONS = json.load(json_settings)

        for item in OPTIONS.keys():
            dpg.set_value(item,OPTIONS[item])
    def callback_save_as_def(self,sender,app_data):
        items = ['Sett_export_each',
                 'Sett_export_to_excel',
                 'Sett_export_plot_as_png',
                 'Sett_export_to_csv',
                 'Sett_export_plot_as_csv',
                 'Sett_export_to_pickle',
                 'Sett_export_plot_as_pickle',
                 'Sett_export_stats',
                 'Sett_export_plot_loglog',
                 'Sett_export_stats_to_csv',
                 'Sett_export_stats_to_xlsx',
                 'Sett_export_stats_to_pickle',
                 'Sett_preserve_time',
                 'Sett_preserve_units',
                 'default_quick_export_filename',
                 'default_quick_stst_filename']

        options = {}
        for item in items:
            
            options[item]=dpg.get_value(item)

        
        path = os.path.join('Methods','FCS_fitting','res','JSON_files','Default_settings.json')
        with open(path, 'w') as f:
            json.dump(options, f, indent=4, sort_keys=False)
        dpg.configure_item(sender,enabled=False)   
    def callback_settings_data_stats(self,sender,app_data):   
        items = ['Sett_export_stats_to_csv','Sett_export_stats_to_xlsx',]
        dpg.configure_item('Setts_save_defaults',enabled=True)
        if app_data:
            for item in items:
                dpg.configure_item(item, enabled = True)
        else:
            for item in items:

                dpg.configure_item(item, enabled = False)
    def callback_settings_data_export_each(self,sender,app_data): 
        items = ['Sett_export_to_excel','Sett_export_to_csv','Sett_export_to_pickle']
        dpg.configure_item('Setts_save_defaults',enabled=True)
        if app_data:
            for item in items:
                dpg.configure_item(item, enabled = True)
        else:
            for item in items:
                dpg.configure_item(item, enabled = False)
    
                                 
###############################################################################
###############################################################################
''' Variables'''
###############################################################################
###############################################################################

class _FCS_Fitting_vars_funct:
    # lprint = _bf.lnprint
    def __init__(self,
                 size_ratio,
                 group_spacer,
                 image_width1,
                 image_height1,
                last_directory,
                 internal_width_left_panel,
                 internal_width_middle_panel,
                basf):
        
        self.basf=basf

        #####################################
        #### Decorate callback functions ####
        #####################################
        
        self.callback_fit_all_button = self.timed(self.callback_fit_all_button)

        #####################################
        #####################################
        #####################################
        
        self.size_ratio = size_ratio 
        
        self.group_spacer = group_spacer
        
        self.image_width1 = image_width1
        self.image_height1 = image_height1
        self.internal_width_left_panel = internal_width_left_panel
        self.internal_width_middle_panel = internal_width_middle_panel
        self.last_directory = self.basf.recall_last_directory()
        self.dpg_image1 = []
        self.variable_drag_float ={'name':'variable_drag_float',
            'width':-1}
        self.variable_slider_float = {'name':'variable_slider_float',
            'width':-1}
        self.Fit_button = {'name':'Fit_button',
            'width':-1}
        self.Fit_all_button = {'name':'Fit_all_button',
            'width':-1}
        self.vars_input_float = {'name':'vars_input_float',
            'width':320* self.size_ratio['width']}
        self.keep_results_butt = {'name':'keep_results_butt',
                         'width':-1
                                 }
        self.show_res_win = {'name':'show_res_win',
                         'width':int(1500*self.size_ratio['width']),
                             'height': int(200*self.size_ratio['height']),
                             'pos':(8,150)
                            }
        self.show_results_butt = {'name':'show_results_butt',
                         'width':-1
                                 }
        self.save_single_butt = {'name':'save_single_butt',
                         'width':int(320*self.size_ratio['width'])}
        self.save_results_butt = {'name':'save_results_butt',
                         'width':-1       
                                 }
        self.plot_all_results_butt = {'name':'plot_all_results_butt',
                         'width':-1             
                                     }
        self.close_button_results = {'name':'close_button_results',
                         'width':int(100*self.size_ratio['width'])}
        self.remove_button_results = {'name':'remove_button_results',
                         'width':int(100*self.size_ratio['width'])}
        self.image_id1 = { 'name':'image_id1'
                         }
        self.Add_model_window = {'name':'Add_model_window',
                         'width':int(1230*self.size_ratio['width']),
                                  'height': int(900*self.size_ratio['height']),
                                  'pos': (int(100*self.size_ratio['width']),
                                          int(20*self.size_ratio['height']))}
        self.Close_Add_model_button = {'name':'Close_Add_model_button',
                         'width':int(150*self.size_ratio['width'])}
        self.Save_model_button = {'name':'Save_model_button',
                         'width':int(150*self.size_ratio['width'])}
        self.model_input_name = {'name':'model_input_name',
                         'width':self.image_width1}
        self.model_input_describe = {'name':'model_input_describe',
                         'width':self.image_width1}
        self.model_input_text1 = {'name':'model_input_text1',
                         'width':self.image_width1}
        self.model_input_variables = {'name':'model_input_variables',
                         'width':self.image_width1}
        self.directory = ''
        self.new_directory = ''
        self.files = ()
        self.anal_file =''
        self.time_range = (None,None)
        self.math_expr = ['arccos','arccosh','arcsin','arcsinh','arctan','arctan2',
            'arctanh','cos','cosh','exp','exp2','expm1','log','log10','log1p',
            'log2','mod','sign','sin','sinh','sqrt','square','tan','tanh',
            'pi','isfinite']
        self.pre_defined_FCS_models = os.path.join('Methods','FCS_fitting','res',
                                                   'JSON_files',
                                                   'Pre-defined_FCS_functions.json')
        self.user_defined_FCS_models = os.path.join('Methods','FCS_fitting','res',
                                                    'JSON_files',
                                                    'User_functions.json')
        self.VAR_RELATED_GROUPS=[]
        self.VAR_RELATED_ITEMS=[]
        self.VARIABLES_RANGE={}   
        self.FIXED_VARIABLES={}
        self.JSONDATA = {}
        self.EXPRESSION = ''
        self.REACTON_FUNCTIONS = {'Reaction - Fast':'FIT_fast_reaction',
                                  'Reaction - Slow': 'FIT_slow_reaction',
                                  'Reaction - Intermediate':'FIT_initermediate_reaction'}
        self.FUNCTION_NAME = ''
        self.VARIABLES = {}
        self.DESCRIPTION = ''
        self.UJSONDATA = {}
        self.RESTAB_RELATED_ITEMS=[]
        self.RES_DF = None
        '''Model variables'''
        self.variable_range_delimiter=100
        self.Models =[]
        self.init_model = ''
        self.res_dict= {}
        self.reserr_dict = {}
        self.workspace_iso = {}
        self.workspace_iso_path = ''
        self.FCS_data_type = '3C'
        self.df = pd.DataFrame()
        self.df_copy = self.df.copy()
        self.chisqr = None
        self.redchi = None
        self.pvalue = None
        self.row_number_count = 0
        self.res_add = []
        self.err_messages = {}
        '''Handler variables'''
        self.all_items = None
        self.file_box_items = []
        self.up_key = dpg.mvKey_Up
        self.down_key = dpg.mvKey_Down
        self.w_key = dpg.mvKey_W
        self.s_key = dpg.mvKey_S
        self.d_key = dpg.mvKey_D
        self.return_key = dpg.mvKey_Return
        self.ctrl_key = dpg.mvKey_Control
        self.LAlt_key = dpg.mvKey_Alt
        self.Del = dpg.mvKey_Delete
        self.esc = dpg.mvKey_Escape
        self.x_key = dpg.mvKey_X
        self.active_keys = [dpg.mvKey_Up,
                            dpg.mvKey_Down,
                            dpg.mvKey_W,
                            dpg.mvKey_S,
                            dpg.mvKey_D,
                            dpg.mvKey_Return,
                            dpg.mvKey_Control,
                            dpg.mvKey_Alt,
                            dpg.mvKey_Delete,
                            dpg.mvKey_X,
                            dpg.mvKey_Escape]
        
        self.fit_all_state = None
        
    # ###############################################################################
    # ###############################################################################
    ''' Functions'''
    # ###############################################################################
    # ###############################################################################
        
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

    def load_json(self):
    
        '''Function that loads JSON file containing fitting function details 
        Define global variables
        Check the selected technique. TECHNIQE0 corresponds to the default technique (FCS).'''
        with open(self.pre_defined_FCS_models) as json_FCS_functions_file:
            self.JSONDATA = json.load(json_FCS_functions_file)['Functions']
        try:
            with open(self.user_defined_FCS_models) as json_user_functions_file:
                    self.UJSONDATA = json.load(json_user_functions_file)['Functions'] 
                    self.JSONDATA.update(self.UJSONDATA)
        except:
            pass

        self.Models=list(self.JSONDATA.keys())
        self.init_model=self.Models[0]
        '''load expression variables and description for models stored in a given JSON file'''
        self.FUNCTION_NAME = self.init_model
        self.EXPRESSION = self.JSONDATA[self.init_model]['Function_expression']
        self.VARIABLES = self.JSONDATA[self.init_model]['Variables']
        self.DESCRIPTION = self.JSONDATA[self.init_model]['Function_description'] 
        self.VARIABLES_RANGE = self.JSONDATA[self.init_model]['Initial-range']    
        self.FIXED_VARIABLES = self.JSONDATA[self.init_model]['Fixed Variables']
        dpg.configure_item('model_choose', items=self.Models)
        dpg.set_value('model_choose',self.init_model)
    
    def define_RES_DF(self):
        res_columns=['file']
        res_columns.extend([v for v in self.VARIABLES.keys()])
        res_columns.extend(['B','B_err'])
        res_columns.extend(['chi_sqr','Red.chi_sqr'])
        res_columns.extend(['p-value'])
        self.RES_DF = pd.DataFrame(columns=res_columns)    
        
    def auto_fit_fontsize(self,text, width, height, fig=None, ax=None):
        '''Auto-decrease the fontsize of a text object.
        Args:
            text (matplotlib.text.Text)
            width (float): allowed width in data coordinates
            height (float): allowed height in data coordinates
        '''
        fig = fig or plt.gcf()
        ax = ax or plt.gca()
        renderer = FigureCanvas(fig).get_renderer()
        bbox_text = text.get_window_extent(renderer=renderer)
        bbox_text = Bbox(ax.transData.inverted().transform(bbox_text))
        fits_width = bbox_text.width*0.85 < width if width else True
        fits_height = bbox_text.height < height if height else True
        if not all((fits_width, fits_height)):
            text.set_fontsize(text.get_fontsize()-2)
            auto_fit_fontsize(text, width, height, fig, ax)
            
            
    def count_curves(self,f):
        '''Function counts the number of data curves included in the input file. Output depends on the user declared number of columns per data curve (2 columns for X,Y data and 3 columns for X,Y,Y_err data).'''
        cnt,DF = self.count_skiprows(f)
        if (len(DF.columns))%3==0:
            cols = 3
            COLS = len(DF.columns)
            return int(COLS/cols)
        else:
            return -1
        
    def diff_coeff(self,omega,tau):
        ''' Calclulates diffusion coefficient based on the omega and diffusion time.'''
        D = omega**2/(4*pi*1e-3*tau)
        return D
    
    def evaluate(self,expression,names):
        """Evaluate a math expression."""
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in names.keys():
                raise NameError(f"The use of '{name}' is not allowed")
        VArs={"__builtins__": {}}
        return eval(code,VArs , names)
    
    def fit_function(self,DF,pars):
        '''Fit the model function'''
        my_model = Model(self.my_universal_function)   #create expression based on the selected model.

        xdata=DF.X.values
        ydata=DF.Y.values
        
        xdata=[n for n in DF.X.values]
        ydata=[n for n in DF.Y.values]
        if self.FCS_data_type=='bin':
            DF.to_pickle('bin.pickle')
            if dpg.get_value('FITing_checkbox'):
                ydata_err=[ 1/n for n in DF.Y_err.values]
                results = my_model.fit(ydata, pars, x=xdata, weights=ydata_err,scale_covar=True)
            else:
                results = my_model.fit(ydata, pars, x=xdata)
        if self.FCS_data_type=='3C':
            DF.to_pickle('3C.pickle')
            if dpg.get_value('FITing_checkbox'):
                ydata_err=[ 1/n for n in DF.Y_err.values]
                results = my_model.fit(ydata, pars, x=xdata, weights=ydata_err,scale_covar=True)
            else:
                results = my_model.fit(ydata, pars, x=xdata)
        elif self.FCS_data_type == '2C':
            results = my_model.fit(ydata, pars, x=xdata)
        else:
            pass
        return results


    def evaluate_expr(self,x,**kwargs):
        '''universal function returning the python readable expression used for fitting and plotting.'''
        x=np.array(x)
        '''Define allowed names for evaluate function.'''
        allowed_names = {
                k: v for k, v in np.__dict__.items() if k in self.math_expr
            }
        variables=kwargs.keys()
        '''Add model variables to varaibles allowed for evaulation of the expression.'''
        allowed_names['x']= x 
        for vr in variables:
            allowed_names[vr]= kwargs[vr] 
        return self.evaluate(self.EXPRESSION,allowed_names) # return expression

    def evaluate_reaction_model(self,x,fname):
        x=np.array(x)/1e3
        function = self.REACTON_FUNCTIONS[fname]
        return function
        
    
    def my_universal_function(self,x,**kwargs):
        if self.FUNCTION_NAME not in list(self.REACTON_FUNCTIONS.keys()):
            return self.evaluate_expr(x,**kwargs)
        else:
            values = self.evaluate_reaction_model(x,self.FUNCTION_NAME)
            
    def count_skiprows(self,f):
        '''Count how many rows need to be skiped during loading the data file. The rows that do not contain numerical values (headers and other strings) will be omited.'''
        stop = False
        cnt=0
        while stop == False:
            testdf = pd.read_csv(f,
                         sep='[:,|\t]',
                         skiprows=cnt,
                         header=0,
                 encoding = 'latin1',
                         engine='python')
            cond_1 = not(np.any(testdf.head(1).apply(lambda col: col.map(lambda x: isinstance(x, (int, float)))).values))
            if cond_1:
                cnt=cnt+1
            else:
                stop=True
        return cnt,testdf

    def unmount_variables(self):
        '''Unmount items (sliders and range inputs) related to the variables defined in a given model.'''
        for alias in self.VAR_RELATED_ITEMS:
            dpg.delete_item(alias)
        self.VAR_RELATED_ITEMS=[]
        VGroups_ends = ['group0','group1','group']
        for group in VGroups_ends: 
            for alias in [al for al in self.VAR_RELATED_GROUPS if al.endswith(group)]:
                dpg.delete_item(alias)
        self.VAR_RELATED_GROUPS=[]
        dpg.delete_item('sep_mid_2')
        dpg.delete_item('Fit_button')
        dpg.delete_item('Fit_button')
        dpg.delete_item('FIT_checkbox')
        dpg.delete_item('FITting_group')
        dpg.delete_item('Fit_all_button_toolitp_text')
        dpg.delete_item('Fit_all_button_toolitp')
        dpg.delete_item('Fit_all_button')
        
    def unmount_tables(self):
        '''Unmount the tables containing the fitting results.'''
        starts = ['results_','row_','column_'] 
        for st in starts: 
            for alias in [al for al in self.RESTAB_RELATED_ITEMS if al.startswith(st)]:
                dpg.delete_item(alias)
        self.RESTAB_RELATED_ITEMS=[]
        try:
            dpg.delete_item('results_pval_name_mean')
        except:
            pass
        try:
            dpg.delete_item('results_pval_value_mean')
        except:
            pass
        try:
            dpg.delete_item('results_pval_error_mean')
        except:
            pass
        try:
            dpg.delete_item('results_chisqr_name_mean')
        except:
            pass
        try:
            dpg.delete_item('results_chisqr_value_mean')
        except:
            pass
        try:
            dpg.delete_item('results_chisqr_error_mean')
        except:
            pass
        try:
            dpg.delete_item('results_bright_name_mean')
        except:
            pass
        try:
            dpg.delete_item('results_bright_value_mean')
        except:
            pass
        try:
            dpg.delete_item('results_bright_error_mean')
        except:
            pass
        try:
            dpg.delete_item('table_results')
        except:
            pass
        try:
            dpg.delete_item('remove_button_results')
        except:
            pass
        try: 
            dpg.delete_item('close_button_results')
        except:
            pass
        try:
            dpg.delete_item('group_close_results_table')
        except:
            pass
        try:
            dpg.delete_item('table_results_show')
        except:
            pass
        try:
            dpg.delete_item('show_res_win')
        except:
            pass
        try:
            dpg.delete_item('table_results_mean')
        except:
            pass
        try:
            dpg.delete_item('keep_results_butt')
        except:
            pass
        try:
            dpg.delete_item('show_results_butt')
        except:
            pass
        try:
            dpg.delete_item('save_results_butt')
        except:
            pass
        try:
            dpg.delete_item('plot_all_results_butt')
        except:
            pass
        try:
            dpg.delete_item('save_single_butt')
        except:
            pass
        try:
            dpg.delete_item('group_keep_res')
        except:
            pass
        try:
            dpg.delete_item('group_keep_res_tab')
        except:
            pass
        try:
            dpg.delete_item('sep_left_3')
        except:
            pass
        try:
            dpg.delete_item('group_keep_res_mean')
        except:
            pass
        try:
            dpg.delete_item('sep_left_4')
        except:
            pass
        try:
            dpg.delete_item('group_results')
        except:
            pass

    def mount_variables(self):
        '''Mount item corresponding to the variables for a given model and show the fit button.'''
        for v in self.VARIABLES:
            Vgroup1 = 'VARIABLES_'+v+'_group1'
            self.VAR_RELATED_GROUPS.extend([Vgroup1])
            with dpg.group(tag=Vgroup1,parent='Model_selection_panel'
                  ):
                Vgroup0 = 'VARIABLES_'+v+'_group0'
                col00 = 'VARIABLES_'+v+'_group0_col0'
                col01 = 'VARIABLES_'+v+'_group0_col1'
                row0 = 'VARIABLES_'+v+'_group0_row0'
                self.VAR_RELATED_GROUPS.extend([Vgroup0,col00,col01,row0])
                with dpg.table(header_row=False,tag=Vgroup0,width=-1,borders_innerH=False, 
                               borders_outerH=False, borders_innerV=False, borders_outerV=False,
                               no_pad_innerX=False,no_pad_outerX=True,no_host_extendX=True,
                               no_clip=True, policy=dpg.mvTable_SizingStretchSame):
                    dpg.add_table_column(tag=col00,width=self.internal_width_middle_panel/2)
                    dpg.add_table_column(tag=col01,width=self.internal_width_middle_panel/2)
                    with dpg.table_row(tag=row0):
                        var_item = 'VARIABLES_'+v+'_min'
                        self.VAR_RELATED_ITEMS.extend([var_item])
                        dpg.add_drag_float(label='',
                                           width= self.variable_drag_float['width'],
                                           tag=var_item,
                                           show=True,
                                           default_value=self.VARIABLES_RANGE[v][0],
                                           speed=self.VARIABLES_RANGE[v][0]/self.variable_range_delimiter,
                                           callback=self.callback_range_min,
                                           no_input=False,
                                           format=v+' (min) = %g'
                                          )
                        with dpg.tooltip(var_item):
                            dpg.add_text("Define lowest value of "+v+", also bottom constrain while fitting. Drag to change. Double click or Ctrl + Click to input the value directly.")
                        var_item = 'VARIABLES_'+v+'_max'
                        self.VAR_RELATED_ITEMS.extend([var_item])
                        dpg.add_drag_float(label='',
                                           width=self.variable_drag_float['width'],
                                           tag=var_item,
                                           show=True,
                                           default_value=self.VARIABLES_RANGE[v][1],
                                           speed=self.VARIABLES_RANGE[v][1]/self.variable_range_delimiter,
                                           callback=self.callback_range_max,
                                           no_input=False,
                                           format=v+' (max) = %g'
                                          )
                        with dpg.tooltip(var_item):
                            dpg.add_text("Define highest value of "+v+", also top constrain while fitting. Drag to change. Double click or Ctrl + Click to input the value directly.")
                    
                Vgroup = 'VARIABLES_'+v+'_group'
                self.VAR_RELATED_GROUPS.extend([Vgroup])
                with dpg.group(tag=Vgroup,parent='Model_selection_panel',horizontal=True,
                           horizontal_spacing=self.group_spacer*4
                      ):
                    var_item = 'VARIABLES_'+v+'_check'
                    self.VAR_RELATED_ITEMS.extend([var_item])
                    dpg.add_checkbox(label="", tag=var_item,default_value = ast.literal_eval(self.FIXED_VARIABLES[v]))
                    with dpg.tooltip(var_item):
                        dpg.add_text("Check for fixing durig fit.")


                    var_item = 'VARIABLES_'+v+'_slider'
                    self.VAR_RELATED_ITEMS.extend([var_item])
                    dpg.add_slider_float(label='',
                                         width = self.variable_slider_float['width'],
                                         tag = var_item,
                                         show=True,
                                         no_input=False,
                                         default_value=self.VARIABLES[v],
                                         min_value=dpg.get_value('VARIABLES_'+v+'_min'),
                                         max_value=dpg.get_value('VARIABLES_'+v+'_max'),
                                         callback=self.callback_slider,
                                         format=v+' = %g'
                                        )

                    with dpg.tooltip(var_item):
                        dpg.add_text("Slide to change the initial value of "+v+" for fitting. Double click or Ctrl + Click to input the value directly.")
                        
        dpg.add_separator(tag ='sep_mid_2',parent='Model_selection_panel',show=True)
        with dpg.group(tag='FITting_group',
                       parent='Model_selection_panel',
                           horizontal=True,
                           horizontal_spacing=self.group_spacer
                       ):
            if self.FCS_data_type == '2C':
                dpg.configure_item('FITing_checkbox',default_value = False,
                                 enabled=False,
                                 show=True)
            else:
                dpg.configure_item('FITing_checkbox',default_value = True,
                                 enabled=True,
                                 show=True)
            dpg.add_button(label='FIT',
                           width =self.Fit_button['width'],
                           show=True,
                           tag='Fit_button',
                           parent='FITting_group',
                           callback=self.callback_fit_button
                           )
            with dpg.tooltip('Fit_button'):
                dpg.add_text("Press to fit the data. (Ctrl+Enter)")
            dpg.bind_item_theme('Fit_button', 'fit_button_theme')
        dpg.add_button(label='FIT and keep ALL',
                       width =self.Fit_all_button['width'],
                       show=True,
                       tag='Fit_all_button',
                       parent='Model_selection_panel',
                       callback=self.callback_fit_all_button
                       )
        with dpg.tooltip('Fit_all_button',tag='Fit_all_button_toolitp'):
            dpg.add_text("Press to fit ALL data.",tag='Fit_all_button_toolitp_text')
        dpg.bind_item_theme('Fit_all_button', 'fit_button_theme')  
        Variable_groups = [item for item in dpg.get_aliases() if item.startswith('VARIABLES_') and item.endswith('_group')] 
        Variable_groups.extend(['sep_mid_1',
                                'sep_mid_2',
                                'Fit_button',
                                'Fit_all_button',
                                'Fit_all_button_toolitp',
                               'Fit_all_button_toolitp_text'])
        if len(dpg.get_item_configuration('file_box')['items'])!=0:
            for item in Variable_groups:
                dpg.configure_item(item,show=True)
        else:
            for item in Variable_groups:
                dpg.configure_item(item,show=False)


    def workspace_test(self,f):
        if f in self.workspace_iso['FILES']:
            if len(self.workspace_iso['FILES'][f]) !=0:
                Current_model = dpg.get_value('model_choose')
                if Current_model != self.workspace_iso['Model']:
                    dpg.configure_item('model_choose',default_value = self.workspace_iso['Model'])
                    self.callback_models('model_choose',self.workspace_iso['Model'])
                else:
                    pass
                tau_min = self.workspace_iso['FILES'][f]['tau_min']
                dpg.set_value('df_min',tau_min)
                self.callback_df_range('df_min',tau_min)
                tau_max = self.workspace_iso['FILES'][f]['tau_max']
                dpg.set_value('df_max',tau_max)
                self.callback_df_range('df_max',tau_max)
                Time_units = self.workspace_iso['FILES'][f]['Time_units']
                dpg.set_value('Xunits',Time_units)
                self.callback_Xunits('Xunits',Time_units)
                G0_units = self.workspace_iso['FILES'][f]['G0_units']
                dpg.set_value('Yunits',G0_units)
                self.callback_Xunits('Yunits',G0_units)
                Weights_checkbox = self.workspace_iso['FILES'][f]['Weights_checkbox']
                dpg.set_value('FITing_checkbox',Weights_checkbox)
                RES_add = self.workspace_iso['FILES'][f]['RES_ADD']
                dpg.set_value('chi_sqr','\u03C7\u00B2 = '+ str(self.basf.zeros_chi(RES_add['chi_sqr']))+ '   ||   Reduced \u03C7\u00B2 = '+ str(self.basf.zeros(RES_add['Red.chi_sqr']))+ '   || p-value = '+str(self.basf.zeros(RES_add['p-value'])))
                for v  in self.VARIABLES:
                    field = v+'_min'
                    var_item = 'VARIABLES_'+field
                    field_value = self.workspace_iso['FILES'][f][field]
                    dpg.set_value(var_item,field_value)
                    self.callback_range_min(var_item,field_value)
                    field = v+'_max'
                    var_item = 'VARIABLES_'+field
                    field_value = self.workspace_iso['FILES'][f][field]
                    dpg.set_value(var_item,field_value)
                    self.callback_range_max(var_item,field_value)
                    field = v+'_check'
                    var_item = 'VARIABLES_'+field
                    field_value = self.workspace_iso['FILES'][f][field]
                    dpg.set_value(var_item,field_value)
                    field = v+'_slider'
                    var_item = 'VARIABLES_'+field
                    field_value = RES_add[v]
                    dpg.set_value(var_item,field_value)
                    self.callback_slider(var_item,field_value)
                    dpg.set_value('results_'+v+'_name',v)
                    dpg.set_value('results_'+v+'_value',self.basf.zeros(field_value))
                    if not dpg.get_value('VARIABLES_'+v+"_check"):
                        dpg.set_value('results_'+v+'_error',self.basf.zeros(RES_add[v+'_err']))
                    else:
                        dpg.set_value('results_'+v+'_error','Fixed')

            else:
                pass
        else:
            pass
    

    
    def callback_listbox(self,sender,app_data):
        '''Reloads and replots the data upon selwction of the datafile.'''
        self.anal_file=app_data
        self.load_data(self.new_directory,self.anal_file)
        self.plot_scater(self.df,'callback_listbox')
        
        
    #######################################################
    def callback_models(self,sender, app_data):
        '''Changes the variables control panel and replots upon change of the model.'''
        self.unmount_variables()
        self.unmount_tables()
        self.FUNCTION_NAME = app_data
        data = self.JSONDATA[self.FUNCTION_NAME]
        self.VARIABLES_RANGE=self.JSONDATA[self.FUNCTION_NAME]['Initial-range']
        self.FIXED_VARIABLES=self.JSONDATA[self.FUNCTION_NAME]['Fixed Variables']
        self.EXPRESSION=data['Function_expression']
        variables_dict = data['Variables']
        self.VARIABLES=list(variables_dict.keys())
        '''Define variables'''
        self.VARIABLES = data['Variables']
        self.VARIABLES_RANGE=data['Initial-range']
        self.mount_tables()
        self.mount_variables()
        self.define_RES_DF()
        self.plot_scater(self.df,'callback_models')

    def callback_save_variables_to_json(self,sender,app_data):
        '''Saves the newely defined model to JSON file.'''
        expr=parse_expr(dpg.get_value('model_input_text1')).free_symbols
        expr=sorted(set([str(v) for v in expr]))
        try: 
            expr.remove('x')
        except:
            pass
        model_input_variables=tt1=dpg.get_value('model_input_variables').replace(" ",'').split(',')
        model_input_variables=model_input_variables
        if expr == sorted(set(model_input_variables)):
            variables={}
            fixed_variables={}
            variables_range={}
            for v in model_input_variables:
                variables[v]=dpg.get_value('vars_input_'+v+'_def')
                fixed_variables[v]=str(dpg.get_value('New_fixed_VARIABLES_'+v+"_check"))
                variables_range[v]=[dpg.get_value('vars_input_'+v+'_min'),
                                    dpg.get_value('vars_input_'+v+'_max')
                                   ]

            function = dpg.get_value('model_input_text1')
            name = 'User-defined - '+dpg.get_value('model_input_name')
            description = 'User-defined function: '+dpg.get_value('model_input_describe')
            js_entry = {name:{'Function_description':description,
                              'Function_expression':function,
                              'Variables':variables,
                              'Fixed Variables':fixed_variables,
                              'Initial-range':variables_range
                             }
                       }

            user_file=self.user_defined_FCS_models
            try:
                with open(user_file) as f:
                    data = json.load(f)
                    data['Functions'].update(js_entry)
            except:
                data={'Functions':js_entry}

            with open(user_file, 'w') as f:
                json.dump(data, f, indent=4, sort_keys=False)
            self.load_json()
            dpg.configure_item('model_choose',items=self.Models)
            try:
                dpg.configure_item('Add_model_window', show=False)
                self.callback_close_new_model_window(None,None)
            except:
                pass
        else:
            pass
        

    def callback_close_new_model_window(self,sender,app_data):
        '''Closes the new model window.'''
        dpg.configure_item('Add_model_window', show=False)
        for item in reversed(self.add_window_items):
            print(item)
            dpg.delete_item(item)
        self.add_window_items = []
    def callback_show_new_model_window(self,sender,app_data):
        self.add_window_items = ['Add_model_window']
        with dpg.window(label='Add model',
                        tag="Add_model_window",
                        width=self.Add_model_window['width'],
                        height=self.Add_model_window['height'],
                        pos=self.Add_model_window['pos'],
                        no_move=False,
                        no_collapse=True,
                        no_title_bar=True,
                        no_resize=True,
                        show=True,
                        modal=False,
                        on_close =self.callback_close_new_model_window
                        ):
            with dpg.group(tag='var_def_group_1',
                           horizontal=True,
                           horizontal_spacing=self.group_spacer,
                           parent = 'Add_model_window'
                           ):
                dpg.add_button(label="Close",
                               tag='Close_Add_model_button',
                               width = self.Close_Add_model_button['width'],
                               callback=self.callback_close_new_model_window
                              )
                dpg.add_button(label="Save model",
                               tag='Save_model_button',
                               width = self.Save_model_button['width'],
                               show=False,
                               callback=self.callback_save_variables_to_json
                              )
                dpg.bind_item_theme('Close_Add_model_button', 'fit_button_theme') 
                dpg.bind_item_theme('Save_model_button', 'fit_button_theme') 
                self.add_window_items.extend(['Close_Add_model_button','Save_model_button'])
            dpg.add_input_text(label="",
                               default_value="Enter the name of the model.",
                               tag='model_input_name',
                               on_enter=True,
                               enabled=True,
                               width=self.model_input_name['width'],
                               parent = 'Add_model_window'
                              )
            dpg.add_input_text(label="",
                               default_value="Enter the model description.",
                               tag='model_input_describe',
                               on_enter=True,
                               enabled=True,
                               multiline=True,
                               width=self.model_input_describe['width'],
                               parent = 'Add_model_window'
                              )
            dpg.add_text('Input the function. Avoid using a single capital N letter as varibale. Use x character for independent variable.',
                         parent = 'Add_model_window',
                         tag='add_model_text_1')
            self.add_window_items.extend(['model_input_name','model_input_describe','add_model_text_1'])
            dpg_image1 = []
            for i in range(0, self.image_height1):
                for j in range(0, self.image_width1):
                    dpg_image1.append(80/255)
                    dpg_image1.append(80/255)
                    dpg_image1.append(80/255)
                    dpg_image1.append(255/255)

            dpg.add_input_text(label="",
                               default_value="",
                               tag='model_input_text1',
                               on_enter=False,
                               enabled=True,
                               multiline=True,
                               callback=self.callback_stringtest1,
                               width=self.model_input_text1['width'],parent = 'Add_model_window')
            self.add_window_items.extend(['model_input_text1',])
            if dpg.does_item_exist("texture_reg1"):
                pass
            else:
                dpg.add_texture_registry(show=False, tag='texture_reg1')
                self.add_window_items.extend(['texture_reg1'])

            if dpg.does_item_exist(self.image_id1['name']):
                dpg.add_dynamic_texture(self.image_width1,
                                        self.image_height1,
                                        default_value=dpg_image1,
                                        tag=self.image_id1['name'],
                                        parent = 'texture_reg1'
                                       )
                dpg.add_image(self.image_id1['name'],
                                  width = self.image_width1,
                                  height = self.image_height1,
                                  uv_min=(0, 0),
                                  uv_max=(1, 1),
                                  tag='draw_image_', parent = 'Add_model_window',show=True)
                self.add_window_items.extend([self.image_id1['name'],'draw_image_'])
            else:
                dpg.add_dynamic_texture(self.image_width1,
                                        self.image_height1,
                                        default_value=dpg_image1,
                                        tag=self.image_id1['name'],
                                        parent = 'texture_reg1'
                                       )
                dpg.add_image(self.image_id1['name'],
                                  width = self.image_width1,
                                  height = self.image_height1,
                                  uv_min=(0, 0),
                                  uv_max=(1, 1),
                                  tag='draw_image_', parent = 'Add_model_window',show=True)
                self.add_window_items.extend([self.image_id1['name'],'draw_image_'])

            dpg.add_text('List all variables, without x variable. Use coma to separate the symbols. Avoid doubles. Confirm with ENTER.',
                         tag='List_all_variables_text',
                         parent = 'Add_model_window')
            self.add_window_items.extend(['List_all_variables_text'])
            dpg.add_input_text(label="",
                               default_value="",
                               tag='model_input_variables',
                               on_enter=True,
                               enabled=True,
                               callback=self.callback_new_var_string,
                               width=self.model_input_variables['width'],
                               parent = 'Add_model_window'
                              )
            dpg.add_group(tag='vars_group', show=False,parent = 'Add_model_window')
            dpg.add_text('Enter the minimal, the default, and the maximal values of variables. Press "Save" to finish.',
                         tag='vars_min_def_max',
                         parent='vars_group')
            self.add_window_items.extend(['vars_group','model_input_variables','vars_min_def_max'])


    def callback_stringtest1(self,sender,app_data):
        '''Renders the expression into the image in the add-model window.'''
        try: 
            latextexpression=latex(parse_expr(app_data))
            variables = parse_expr(app_data).free_symbols
            px = 1/plt.rcParams['figure.dpi']
            fig=Figure(figsize=(self.image_width1*px, self.image_height1*px),facecolor='#505050')
            ax = fig.add_subplot()
            text = ax.text(0.5, 0.9,
                           r'$G\left(x\right)='+latextexpression+'$',
                           va='top',
                           ha='center',
                           fontsize=25,color='White'
                           )
            ax.axis('off')
            self.auto_fit_fontsize(text, 1, None, fig=fig, ax=ax)
            b = BytesIO()
            FigureCanvas(fig).print_png(b)
            b.seek(0)
            image = Image.open(b)
            self.dpg_image1 = []
            for i in range(0, image.height):
                for j in range(0, image.width):
                    pixel = image.getpixel((j, i))
                    self.dpg_image1.append(pixel[0]/255)
                    self.dpg_image1.append(pixel[1]/255)
                    self.dpg_image1.append(pixel[2]/255)
                    self.dpg_image1.append(255/255)
            
            dpg.set_value(self.image_id1['name'], self.dpg_image1)
            try:
                dpg.configure_item('model_input_variables',enabled=True)
            except:
                pass
            try:
                for alias in dpg.get_aliases():
                    if alias.startswith('vars_input_'):
                        dpg.delete_item(alias)
                    if alias.startswith('New_fixed_VARIABLES_'):
                        dpg.delete_item(alias)
                for alias in dpg.get_aliases():
                    if alias.startswith('vars_') & alias.endswith('_group0'):
                        dpg.delete_item(alias)
                dpg.configure_item('Save_model_button',show=False)
            except:
                pass

        except:
            pass

    def callback_new_var_string(self,sender,app_data):
        '''Checks if the variables given by the user are in agreement with the variables extracted from the expression. enables input of the initial values and ranges of defined variables.'''
        expr=parse_expr(dpg.get_value('model_input_text1')).free_symbols
        expr=sorted(set([str(v) for v in expr]))
        user_defined_variables=app_data.replace(" ",'').split(',')
        try: 
            expr.remove('x')
        except:
            pass
        if expr==sorted(set(user_defined_variables)):
            dpg.configure_item(sender,enabled=False)
            dpg.configure_item('vars_group',show=True)
            for v in user_defined_variables:
                with dpg.group(tag='vars_'+v+'_group0',parent='vars_group',horizontal=True,
                   horizontal_spacing=15):
                    dpg.add_input_float(label='',
                                       width=self.vars_input_float['width'],
                                       tag='vars_input_'+v+'_min',
                                        format=v+' (min) = %g'
                                      )
                    dpg.add_input_float(label='',
                                        width=self.vars_input_float['width'],
                                        tag='vars_input_'+v+'_def',
                                        format=v+' = %g'
                                       )
                    dpg.add_input_float(label='',
                                        width=self.vars_input_float['width'],
                                        tag='vars_input_'+v+'_max',
                                        format=v+' (max) = %g'
                                       )
                    dpg.add_checkbox(label="Fixed", parent='vars_'+v+'_group0', tag='New_fixed_VARIABLES_'+v+"_check")
                    with dpg.tooltip('New_fixed_VARIABLES_'+v+"_check",tag='New_fixed_VARIABLES_'+v+"_check_tooltip"):
                            dpg.add_text("Check for fixing durig fit.",tag='New_fixed_VARIABLES_'+v+"_check_tooltip_text")
                    dpg.configure_item('Save_model_button',show=True)
                    self.add_window_items.extend(['vars_'+v+'_group0',
                                                  'vars_input_'+v+'_min',
                                                 'vars_input_'+v+'_def',
                                                  'vars_input_'+v+'_max',
                                                  'vars_'+v+'_group0',
                                                  'New_fixed_VARIABLES_'+v+"_check",
                                                  'New_fixed_VARIABLES_'+v+"_check_tooltip",
                                                  'New_fixed_VARIABLES_'+v+"_check_tooltip_text"
                                                 ])
        else:
            try:
                dpg.add_window(pos=(400,150),
                               tag='var_err',
                               show=True,
                               modal=True
                              )
                dpg.add_text('Given variables do no match the variables provided in the equation above.',
                             parent='var_err')

                dpg.add_button(label='Close',
                               parent='var_err',
                               callback=lambda:dpg.configure_item('var_err',show=False)
                              )
                dpg.bind_item_theme('var_err', 'Error_window_theme')
            except:
                dpg.configure_item('var_err',show=True)
                
    def callback_range_min(self,sender,app_data):
        '''Changes the minimal limit for the slider related to the given variable.'''
        variable=sender.replace('VARIABLES_', '').replace('_min', '')
        self.VARIABLES_RANGE[variable][0]=app_data
        dpg.configure_item('VARIABLES_'+variable+'_slider', min_value=app_data)
        dec = self.basf.decimal_rounds_lim(app_data*10)
        if app_data>1e3:
            form = variable+' (min) = %.'+str(3)+'e'
        else:
            if dec == 0:
                form = variable+' (min) = %.'+str(dec)+'f'
            else:
                form = variable+' (min) = %.'+str(dec)+'g'
        dpg.configure_item(sender,speed=abs(app_data/100.))
        dpg.configure_item(sender,format=form)

    def callback_range_max(self,sender,app_data):
        '''Changes the maximal limit for the slider related to the given variable.'''
        variable=sender.replace('VARIABLES_', '').replace('_max', '')
        self.VARIABLES_RANGE[variable][1]=app_data
        dpg.configure_item('VARIABLES_'+variable+'_slider', max_value=app_data)  
        dec = self.basf.decimal_rounds_lim(app_data*10)
        if app_data>1e3:
            form = variable+' (max) = %.'+str(3)+'e'
        else:
            if dec == 0:
                form = variable+' (max) = %.'+str(dec)+'f'
            else:
                form = variable+' (max) = %.'+str(dec)+'g'
        dpg.configure_item(sender,speed=abs(app_data/100.))
        dpg.configure_item(sender,format=form)

    def callback_slider(self,sender,app_data):
        '''Changes the value of the variable and replots.'''
        variable=sender.replace('VARIABLES_', '').replace('_slider', '')
        self.VARIABLES[variable]=app_data
        dec = self.basf.decimal_rounds_lim(app_data*10)
        if app_data>1e3:
            form = variable+' = %.'+str(3)+'e'
        else:
            if dec <= 1:
                form = variable+' = %.'+str(dec)+'f'
            else:
                form = variable+' = %.'+str(dec)+'g'
        dpg.configure_item(sender,format=form)
        self.callback_calculate_mol_bright('CNTR',dpg.get_value('CNTR'))
        self.plot_scater(self.df,'callback_slider')
    
    def gof_pvalue_from_result(self,result):
        """
        p-value jakości dopasowania (goodness-of-fit) na bazie χ².
        Zakłada poprawne wagi: weights = 1/sigma.
        """
        chi2_obs = result.chisqr      # suma [(y - yhat)/sigma]^2
        dof      = result.nfree       # N - k
        p_gof = 1 - chi2.cdf(chi2_obs, dof)  # P(Χ²_ν ≥ χ²_obs)
        return chi2_obs, dof, p_gof

    def update_error_list(self,file):
        message = 'Check file: ' + file
        self.err_messages[file] = message
        
        dpg.configure_item('comm_box', items=[self.err_messages[v] for v in list(self.err_messages.keys())])

    def callback_comm_box(self,sender,app_data):
        file = app_data.replace('Check file: ','')
        dpg.configure_item('file_box',default_value = file)
        self.callback_listbox('file_box',file)
        
    def checkIfFitCorrected(self,file):
        keys = self.err_messages.keys()
        if file in keys:
            del self.err_messages[file]
            dpg.configure_item('comm_box', items=[self.err_messages[v] for v in list(self.err_messages.keys())])

    def clear_error_list(self):
        self.err_messages = {}
        dpg.configure_item('comm_box', items=list(self.err_messages.keys()))

    def callback_fit_button(self,sender,app_data):
        ''' Fits the data with the function provided by the model of choice.'''
        params = Parameters()
        for v in self.VARIABLES:
            if dpg.get_value('VARIABLES_'+v+'_min')!=dpg.get_value('VARIABLES_'+v+'_max'):
                params.add(v,
                           value=dpg.get_value('VARIABLES_'+v+'_slider'),
                           vary=not dpg.get_value('VARIABLES_'+v+"_check"),
                           min=dpg.get_value('VARIABLES_'+v+'_min'),
                           max=dpg.get_value('VARIABLES_'+v+'_max')
                          )
            else:
                params.add(v,
                           value=dpg.get_value('VARIABLES_'+v+'_slider'),
                           vary=not dpg.get_value('VARIABLES_'+v+"_check")
                          )
        fit_output = self.fit_function(self.df,params)
        chi2_obs, dof, p_gof = self.gof_pvalue_from_result(fit_output)
        self.res_dict={v:float(fit_output.best_values[v]) for v in self.VARIABLES}
        self.reserr_dict={v+'_err':fit_output.params[v].stderr for v in self.VARIABLES}
        if any([self.reserr_dict[v+'_err'] is None for v in self.VARIABLES] ):
            self.reserr_dict={v+'_err':float(0.0) for v in self.VARIABLES}
            self.update_error_list(self.anal_file)    
        else:
            self.reserr_dict={v+'_err':float(fit_output.params[v].stderr) for v in self.VARIABLES}
            if not all([self.reserr_dict[v+'_err'] is None for v in self.VARIABLES] ):
                
                self.checkIfFitCorrected(self.anal_file)
                
 
        for v in self.VARIABLES:
            if self.reserr_dict[v+'_err'] is None:
                try:
                    dpg.add_window(pos=(400,150),
                               tag='FIT_err',
                               show=True,
                               modal=True
                              )
                    dpg.add_text('Fit failed. Try to redefine input parameters.',
                                 parent='FIT_err')
                    dpg.add_button(label='Close',
                                   parent='FIT_err',
                                   callback=lambda:dpg.configure_item('FIT_err',show=False)
                                  )
                    dpg.bind_item_theme('FIT_err', 'Error_window_theme')
                    break
                except:
                    dpg.configure_item('FIT_err',show=True)
                    break

            self.VARIABLES[v]=self.res_dict[v]
            dpg.set_value('VARIABLES_'+v+'_slider',self.res_dict[v])
            self.callback_calculate_mol_bright('CNTR',dpg.get_value('CNTR'))
            dpg.set_value('results_'+v+'_name',v)
            dpg.set_value('results_'+v+'_value',self.basf.zeros(self.res_dict[v]))
            if not dpg.get_value('VARIABLES_'+v+"_check"):
                dpg.set_value('results_'+v+'_error',self.basf.zeros(self.reserr_dict[v+'_err']))
            else:
                dpg.set_value('results_'+v+'_error','Fixed')
        dpg.set_value('results_bright_name','B')
        dpg.set_value('results_bright_value',self.basf.zeros(self.BR[0]))
        dpg.set_value('results_bright_error',self.basf.zeros(self.BR[1]))
        self.chisqr = fit_output.chisqr
        self.redchi = fit_output.redchi
        self.pvalue = p_gof
        dpg.set_value('chi_sqr','\u03C7\u00B2 = '+ str(self.basf.zeros_chi(self.chisqr))+ '   ||   Reduced \u03C7\u00B2 = '+ str(self.basf.zeros(self.redchi))+ '   || p-value = '+str(self.basf.zeros(self.pvalue)))
        self.plot_scater(self.df,'callback_fit_button')
        dpg.configure_item('group_results', show=True)
        dpg.configure_item('keep_results_butt', enabled=True)
        
        
    def callback_fit_all_button(self,sender, app_data):
        self.unmount_tables()
        self.mount_tables()
        self.define_RES_DF()
        files = dpg.get_item_configuration('file_box')['items']
        dpg.bind_item_theme('Fit_all_button', "fit_button_theme_busy")
        old_Fit_all_button_label = dpg.get_item_label('Fit_all_button')
        for i,file in enumerate(files):
            fittin_label = 'Fitting file '+str(i+1)+' of '+str(len(files))
            dpg.set_item_label('Fit_all_button',fittin_label)
            dpg.set_value('file_box',file)
            self.callback_listbox('file_box',file)
            min_df=self.df.X.min()
            max_df = self.df.X.max()
            averaging_range = min_df*15
            max_averaging_range = max_df/10
            range_index = self.df.index[self.df['X']<=averaging_range].tolist()[-1]
            max_range_index = self.df.index[self.df['X']>=max_averaging_range].tolist()[0]
            pre_N = 1/(self.df.Y[:range_index].mean())
            pre_G_inf = self.df.Y[max_range_index:].mean()
            try:
                dpg.set_value('VARIABLES_N_p_slider',pre_N)
                self.plot_scater(self.df,'callback_fit_all_button pre N')
            except:
                pass
            try:
                dpg.set_value('VARIABLES_G_inf_slider',pre_G_inf)
                self.plot_scater(self.df,'callback_fit_all_button pre Ginf')
            except:
                pass
            self.callback_fit_button('Fit_button',app_data)
            self.callback_keep_res_button('keep_results_butt',app_data)
            
        dpg.bind_item_theme('Fit_all_button', "fit_button_theme")
        dpg.set_item_label('Fit_all_button',old_Fit_all_button_label)

    def write_to_average_table(self): 
        for v in self.VARIABLES:
            if len(self.RES_DF) != 0:
                mean = self.RES_DF[v].mean()
                dpg.set_value('results_'+v+'_value_mean',self.basf.zeros(mean))
                if len(self.RES_DF)<2:
                    STD = '-'
                    dpg.set_value('results_'+v+'_error_mean',STD)
                else:
                    STD = self.RES_DF[v].std(ddof=1)
                    dpg.set_value('results_'+v+'_error_mean',self.basf.zeros(STD))
            else:
                dpg.set_value('results_'+v+'_value_mean','-')
                dpg.set_value('results_'+v+'_error_mean','-')
        
        if len(self.RES_DF) != 0:
            mean_B = self.RES_DF['B'].mean()
            mean_chi = self.RES_DF['Red.chi_sqr'].mean()
            dpg.set_value('results_bright_value_mean',self.basf.zeros(mean_B))
            dpg.set_value('results_chisqr_value_mean',self.basf.zeros(mean_chi))
            if len(self.RES_DF)<2:
                STD = '-'
                dpg.set_value('results_bright_error_mean',STD)
                dpg.set_value('results_chisqr_error_mean',STD)
            else:
                STD_B = self.RES_DF['B'].std(ddof=1)
                STD_chi = self.RES_DF['Red.chi_sqr'].std(ddof=1)
                dpg.set_value('results_bright_error_mean',self.basf.zeros(STD))
                dpg.set_value('results_chisqr_error_mean',self.basf.zeros(STD))
        else:
            dpg.set_value('results_bright_value_mean','-')
            dpg.set_value('results_bright_error_mean','-')
            dpg.set_value('results_chisqr_value_mean','-')
            dpg.set_value('results_chisqr_error_mean','-')
            
        
    def mount_tables(self):
        '''Mount tables containing the results of the fit.'''
        self.clear_error_list()
        self.RESTAB_RELATED_ITEMS=['column_results_variable',
                                   'column_results_value',
                                   'column_results_err']
        with dpg.group(tag='group_results',show=True,parent='file_window'):
            with dpg.group(tag='group_keep_res_tab'):
                with dpg.table(header_row=True,show=True,tag='table_results'):
                    dpg.add_table_column(label='Variable',
                                         tag=self.RESTAB_RELATED_ITEMS[0])
                    dpg.add_table_column(label='Value',
                                         tag=self.RESTAB_RELATED_ITEMS[1])
                    dpg.add_table_column(label='Error',
                                         tag=self.RESTAB_RELATED_ITEMS[2])
                    for v in self.VARIABLES:
                        row_res_item = 'row_results_'+v
                        self.RESTAB_RELATED_ITEMS.extend([row_res_item])
                        with dpg.table_row(tag=row_res_item):
                            res_res_item = 'results_'+v+'_name'
                            self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                            dpg.add_text('',tag=res_res_item)
                            res_res_item = 'results_'+v+'_value'
                            self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                            dpg.add_text('',tag=res_res_item)
                            res_res_item = 'results_'+v+'_error'
                            self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                            dpg.add_text('',tag=res_res_item)
                    with dpg.table_row(tag='row_res_bright_item'):
                        res_res_item = 'results_bright_name'
                        self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                        dpg.add_text('',tag=res_res_item)
                        res_res_item = 'results_bright_value'
                        self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                        dpg.add_text('',tag=res_res_item)
                        res_res_item = 'results_bright_error'
                        self.RESTAB_RELATED_ITEMS.extend([res_res_item])
                        dpg.add_text('',tag=res_res_item)
                            
                tab_tag = 'group_keep_res'
                tab_col0 = 'group_keep_res_col0'
                tab_col1 = 'group_keep_res_col1'
                tab_row = 'group_keep_res_row'
                self.VAR_RELATED_GROUPS.extend([tab_tag,tab_col0,tab_col1,tab_row])
                with dpg.table(header_row=False,tag=tab_tag,width=-1,borders_innerH=False, 
                               borders_outerH=False, borders_innerV=False, borders_outerV=False,
                               no_pad_innerX=False,no_pad_outerX=True,no_host_extendX=True,
                               no_clip=True, policy=dpg.mvTable_SizingStretchSame):
                    dpg.add_table_column(tag=tab_col0,width=self.internal_width_left_panel/2)
                    dpg.add_table_column(tag=tab_col1,width=self.internal_width_left_panel/2)
                    with dpg.table_row(tag=tab_row):
                        dpg.add_button(label='Store results',
                                       tag='keep_results_butt',
                                       width=self.keep_results_butt['width'],
                                       enabled=False,
                                       callback=self.callback_keep_res_button
                                      )
                        dpg.bind_item_theme('keep_results_butt', 'fit_button_theme')
                        with dpg.tooltip('keep_results_butt'):
                            dpg.add_text("Press to store the fitting results in memor, export the current set of data and save the plot. (Alt+s)")
                        dpg.add_button(label='Show results',
                                       tag='show_results_butt',
                                       width=self.show_results_butt['width'],
                                       show=True,
                                       callback=self.callback_show_res_button
                                      )
                        dpg.bind_item_theme('show_results_butt', 'fit_button_theme')
                        with dpg.tooltip('show_results_butt'):
                            dpg.add_text("Press to show the stored fitting results.")
            dpg.add_separator(tag ='sep_left_3')
            with dpg.group(tag='group_keep_res_mean',show=True):
                with dpg.table(header_row=True,show=True,tag='table_results_mean'):
                    dpg.add_table_column(label='Variable',tag='column_results_variable_mean')
                    dpg.add_table_column(label='Mean value',tag='column_results_value_mean')
                    dpg.add_table_column(label='SD',tag='column_results_err_mean')
                    for v in self.VARIABLES:
                        with dpg.table_row(tag='row_results_'+v+'_mean'):
                            try:
                                if len(self.RES_DF) != 0:
                                    mean = self.RES_DF[v].mean()
                                    dpg.add_text(v,tag='results_'+v+'_name_mean') 
                                    dpg.add_text(self.basf.zeros(mean),
                                                 tag='results_'+v+'_value_mean')
                                    if len(self.RES_DF)<2:
                                        STD = '-'
                                        dpg.add_text(STD,tag='results_'+v+'_error_mean')
                                    else:
                                        STD = self.RES_DF[v].std(ddof=1)
                                        dpg.add_text(self.basf.zeros(STD),
                                                     tag='results_'+v+'_error_mean')

                                else:
                                    dpg.add_text(v,tag='results_'+v+'_name_mean')
                                    dpg.add_text('-',tag='results_'+v+'_value_mean')
                                    dpg.add_text('-',tag='results_'+v+'_error_mean')
                            except:
                                dpg.add_text(v,tag='results_'+v+'_name_mean')
                                dpg.add_text('-',tag='results_'+v+'_value_mean')
                                dpg.add_text('-',tag='results_'+v+'_error_mean')
                    with dpg.table_row(tag='row_results_bright_mean'):
                        try:
                            if len(self.RES_DF) != 0:
                                mean = self.RES_DF['B'].mean()
                                dpg.add_text('B',tag='results_bright_name_mean') 
                                dpg.add_text(self.basf.zeros(mean),
                                             tag='results_bright_value_mean')
                                if len(self.RES_DF)<2:
                                    STD = '-'
                                    dpg.add_text(STD,tag='results_bright_error_mean')
                                else:
                                    STD = self.RES_DF['B'].std(ddof=1)
                                    dpg.add_text(self.basf.zeros(STD),
                                                 tag='results_bright_error_mean')

                            else:
                                dpg.add_text('B',tag='results_bright_name_mean')
                                dpg.add_text('-',tag='results_bright_value_mean')
                                dpg.add_text('-',tag='results_bright_error_mean')
                        except:
                            dpg.add_text('B',tag='results_bright_name_mean')
                            dpg.add_text('-',tag='results_bright_value_mean')
                            dpg.add_text('-',tag='results_bright_error_mean')
                    with dpg.table_row(tag='row_results_chisqr_mean'):
                        try:
                            if len(self.RES_DF) != 0:
                                mean = self.RES_DF['Red.chi_sqr'].mean()
                                dpg.add_text('Red. \u03C7\u00B2',tag='results_chisqr_name_mean') 
                                dpg.add_text(self.basf.zeros(mean),
                                             tag='results_chisqr_value_mean')
                                if len(self.RES_DF)<2:
                                    STD = '-'
                                    dpg.add_text(STD,tag='results_chisqr_error_mean')
                                else:
                                    STD = self.RES_DF['Red.chi_sqr'].std(ddof=1)
                                    dpg.add_text(self.basf.zeros(STD),
                                                 tag='results_chisqr_error_mean')

                            else:
                                dpg.add_text('Red. \u03C7\u00B2',tag='results_chisqr_name_mean')
                                dpg.add_text('-',tag='results_chisqr_value_mean')
                                dpg.add_text('-',tag='results_chisqr_error_mean')
                        except:
                            dpg.add_text('Red. \u03C7\u00B2',tag='results_chisqr_name_mean')
                            dpg.add_text('-',tag='results_chisqr_value_mean')
                            dpg.add_text('-',tag='results_chisqr_error_mean')
                    with dpg.table_row(tag='row_results_pval_mean'):
                        try:
                            if len(self.RES_DF) != 0:
                                mean = self.RES_DF['p-value'].mean()
                                dpg.add_text('p-value',tag='results_pval_name_mean') 
                                dpg.add_text(self.basf.zeros(mean),
                                             tag='results_pval_value_mean')
                                if len(self.RES_DF)<2:
                                    STD = '-'
                                    dpg.add_text(STD,tag='results_pval_error_mean')
                                else:
                                    STD = self.RES_DF['p-value'].std(ddof=1)
                                    dpg.add_text(self.basf.zeros(STD),
                                                 tag='results_pval_error_mean')

                            else:
                                dpg.add_text('p-value',tag='results_pval_name_mean')
                                dpg.add_text('-',tag='results_pval_value_mean')
                                dpg.add_text('-',tag='results_pval_error_mean')
                        except:
                            dpg.add_text('p-value',tag='results_pval_name_mean')
                            dpg.add_text('-',tag='results_pval_value_mean')
                            dpg.add_text('-',tag='results_pval_error_mean')
                dpg.add_button(label='Save results to file',
                               tag='save_results_butt',
                               show=True,
                               width = self.save_results_butt['width'],
                               callback=self.callback_save_res_button
                              )
                dpg.bind_item_theme('save_results_butt', 'fit_button_theme')
                with dpg.tooltip('save_results_butt'):
                    dpg.add_text("Export results to file.")

                dpg.add_button(label='Plot all results to files',
                               tag='plot_all_results_butt',
                               show=True,
                               width = self.plot_all_results_butt['width'],
                               callback=self.callback_plot_res_button
                              )
                dpg.bind_item_theme('plot_all_results_butt', 'fit_button_theme')
                with dpg.tooltip('plot_all_results_butt'):
                    dpg.add_text("Plot all results to .png files.")
            dpg.add_separator(tag ='sep_left_4')
        with dpg.window(
                        width=self.show_res_win['width'],
                        pos=self.show_res_win['pos'],
                        tag='show_res_win',
                        show=False,
                        autosize=True,
                        horizontal_scrollbar=True,
                        modal=True
                          ):
            row_number_count = 0
            with dpg.table(header_row=True,
                           show=True,
                           tag='table_results_show',
                           policy=dpg.mvTable_SizingFixedFit,
                           resizable=True):

                dpg.add_table_column(label='File',tag='column_results_show_file')
                for v in self.VARIABLES:
                    dpg.add_table_column(label=v,tag='column_results_show_'+v)
                    dpg.add_table_column(label=v+'_err',tag='column_results_show_'+v+'_err')
                dpg.add_table_column(label='B',tag='column_results_show_B')
                dpg.add_table_column(label='B_err',tag='column_results_show_B_err')
                dpg.add_table_column(label='\u03C7\u00B2',tag='column_results_show_chisqr')
                dpg.add_table_column(label='Red. \u03C7\u00B2',tag='column_results_show_Redchi')
                dpg.add_table_column(label='pvalue',tag='column_results_show_pval')
                dpg.add_table_column(label='Remove?',tag='column_results_show_del') 
            with dpg.group(tag='group_close_results_table',
                           parent='show_res_win',
                           horizontal=True,
                           horizontal_spacing=self.group_spacer, show=True):
                dpg.add_button(label='Close',
                               tag='close_button_results',
                               parent='group_close_results_table',
                               width = self.close_button_results['width'],
                               callback=lambda:dpg.configure_item('show_res_win',show=False)
                              )
                dpg.add_button(label='Remove',
                               parent='group_close_results_table',
                               tag='remove_button_results',
                               width = self.remove_button_results['width'],
                               callback=self.callback_remove_result_button,
                               show=True
                              )

        if len(dpg.get_item_configuration('file_box')['items'])!=0:
            dpg.configure_item('group_results',show=True)
        else:
            dpg.configure_item('group_results',show=False)
            
            
    def callback_calculate_mol_bright(self,sender,app_data):
        NP = dpg.get_value('VARIABLES_N_p_slider')
        if len(self.res_dict) !=0:
            try:
                BR_part = sqrt(((-dpg.get_value('CNTR')/NP**2)**2)*(self.reserr_dict['N_p_err'])**2)
            except:
                BR_part =0
            self.BR = [dpg.get_value('CNTR')/NP,BR_part]
        else:
            BR_part = 0
            self.BR = [dpg.get_value('CNTR')/NP,BR_part]
        dpg.set_value('BRIGHT',self.BR[0])

    def plot_scater(self,DF,sender_function):
        '''Plot the current data and fiting function.'''
        dpg.configure_item('acf_y',label="G("+'\u03C4'+")")
        dpg.configure_item('acf_y_log',label="Log(G("+'\u03C4'+"))")
        dpg.configure_item('res_x',label="Lag time, "+'\u03C4'+" [ms]")
        DF=DF.astype(np.float32)
        xdata=[n for n in DF.loc[(DF['X'] > 0)].dropna().X.values]
        ydata=[n for n in DF.loc[(DF['X'] > 0)].dropna().Y.values]
        ygreks = ydata
        x_fit_data = 10**np.linspace(log10(DF.loc[(DF['X'] > 0)].dropna().X.min()),log10(DF.loc[(DF['X'] > 0)].dropna().X.max()),200)
        y_fit_data = self.my_universal_function(x_fit_data,**self.VARIABLES)
        x_res_data=xdata
        if self.FCS_data_type=='bin':
            if dpg.get_value('FITing_checkbox'):
                weights = [1/n for n in DF.Y_err.values]
            else:
                weights = [1 for n in ydata]
        elif self.FCS_data_type=='3C':
            weights = [1/n for n in DF.Y_err.values]
        elif self.FCS_data_type=='2C':
            weights = [1 for n in ydata]
        y_res_data=weights*(ydata-self.my_universal_function(xdata,**self.VARIABLES))
        self.callback_calculate_mol_bright('CNTR',dpg.get_value('CNTR'))
        dpg.set_axis_limits('acf_y',min(ygreks)-min(ygreks)*0.05,max(ygreks)+max(ygreks)*0.05)
        dpg.set_axis_limits('acf_y_log',min(abs(DF.Y.values))/10,max(abs(DF.Y.values))*10)
        dpg.set_axis_limits('acf_x',min(xdata)-min(xdata)*0.05,max(xdata)+max(xdata)*0.05)
        dpg.set_axis_limits('acf_x_log',min(xdata)-min(xdata)*0.05,max(xdata)+max(xdata)*0.05)
        dpg.set_axis_limits('res_y',min(y_res_data)-min(y_res_data)*0.05,max(y_res_data)+max(y_res_data)*0.05)
        dpg.set_value('ACF_fit', [x_fit_data,y_fit_data ])
        dpg.set_value('RES_plot', [x_res_data,y_res_data ])
        dpg.set_value('ACF_plot', [xdata,ydata ])
        dpg.set_value('ACF_plot_log', [xdata,ydata ])
        dpg.set_value('ACF_fit_log', [x_fit_data,y_fit_data ])


    def callback_keep_res_button(self,sender,app_data):
        '''Stores the fitted data into the pandas Dataframe.'''
        self.res_add = [{**self.res_dict , **self.reserr_dict}]
        RES_ADD = pd.DataFrame.from_dict(self.res_add)
        RES_ADD['file']=self.anal_file
        RES_ADD['B']=self.BR[0]
        RES_ADD['B_err']=self.BR[1]
        RES_ADD['chi_sqr']=self.chisqr
        RES_ADD['Red.chi_sqr']=self.redchi
        RES_ADD['p-value']=self.pvalue
        if len(self.RES_DF) == 0 :
            for col in RES_ADD.columns:
                self.RES_DF.at[0,col] = RES_ADD.at[0,col]     

        else:
            self.RES_DF =pd.concat([self.RES_DF,RES_ADD]).reset_index(drop=True)
        resdf=pd.DataFrame()
        self.row_number_count=int(self.RES_DF.tail(1).index.values)
        self.write_res_to_table()
        dpg.configure_item('group_keep_res_mean', show=True)
        if len(self.RES_DF)>1:
            dpg.configure_item('show_results_butt',show=True)
            dpg.configure_item('group_keep_res_mean', show=True)
            for v in self.VARIABLES:
                mean = self.RES_DF[v].mean()
                STD = self.RES_DF[v].std(ddof=1)
                dpg.set_value('results_'+v+'_name_mean',v)
                dpg.set_value('results_'+v+'_value_mean',self.basf.zeros(mean))
                dpg.set_value('results_'+v+'_error_mean',self.basf.zeros(STD))
            mean_br = self.RES_DF['B'].mean()
            STD_br = self.RES_DF['B'].std(ddof=1)
            dpg.set_value('results_bright_name_mean','B')
            dpg.set_value('results_bright_value_mean',self.basf.zeros(mean_br))
            dpg.set_value('results_bright_error_mean',self.basf.zeros(STD_br))
            mean_chi = self.RES_DF['Red.chi_sqr'].mean()
            STD_chi = self.RES_DF['Red.chi_sqr'].std(ddof=1)
            dpg.set_value('results_chisqr_name_mean','Red. \u03C7\u00B2')
            dpg.set_value('results_chisqr_value_mean',self.basf.zeros(mean_chi))
            dpg.set_value('results_chisqr_error_mean',self.basf.zeros(STD_chi))
            mean_pval = self.RES_DF['p-value'].mean()
            STD_pval = self.RES_DF['p-value'].std(ddof=1)
            dpg.set_value('results_pval_name_mean','p-value')
            dpg.set_value('results_pval_value_mean',self.basf.zeros(mean_pval))
            dpg.set_value('results_pval_error_mean',self.basf.zeros(STD_pval))
            dpg.configure_item('table_results_mean', show=True)
        else:
            dpg.configure_item('show_results_butt',show=True)
            dpg.configure_item('group_keep_res_mean', show=True)
            for v in self.VARIABLES:
                mean = self.RES_DF[v].mean()
                STD = '-'
                dpg.set_value('results_'+v+'_name_mean',v)
                dpg.set_value('results_'+v+'_value_mean',self.basf.zeros(mean))
                dpg.set_value('results_'+v+'_error_mean',STD)

            mean_br = self.RES_DF['B'].mean()
            STD_br = '-'
            dpg.set_value('results_bright_name_mean','B')
            dpg.set_value('results_bright_value_mean',self.basf.zeros(mean_br))
            dpg.set_value('results_bright_error_mean',STD_br)
            mean_chi = self.RES_DF['Red.chi_sqr'].mean()
            STD_chi = '-'
            dpg.set_value('results_chisqr_name_mean','Red. \u03C7\u00B2')
            dpg.set_value('results_chisqr_value_mean',self.basf.zeros(mean_chi))
            dpg.set_value('results_chisqr_error_mean',STD_chi)
            mean_pval = self.RES_DF['p-value'].mean()
            STD_pval = '-'
            dpg.set_value('results_pval_name_mean','p-value')
            dpg.set_value('results_pval_value_mean',self.basf.zeros(mean_pval))
            dpg.set_value('results_pval_error_mean',STD_pval)
        dpg.configure_item('save_results_butt', show=True)
        dpg.configure_item('keep_results_butt', enabled=False)
        Current_model = dpg.get_value('model_choose')
        if Current_model != self.workspace_iso['Model']:
            self.workspace_iso['Model'] = Current_model
        else:
            pass
        tau_min = dpg.get_value('df_min')
        tau_max = dpg.get_value('df_max')
        Time_units = dpg.get_value('Xunits')
        G0_units = dpg.get_value('Yunits')
        Weights_checkbox =dpg.get_value('FITing_checkbox')
        FREEZED_results = {
                           'tau_min':tau_min,
                           'tau_max': tau_max,
                           'Time_units': Time_units,
                           'G0_units': G0_units,
                           'Weights_checkbox': Weights_checkbox,
                           }
        for v  in self.VARIABLES:
            FREEZED_results[v+'_min'] = dpg.get_value('VARIABLES_'+v+'_min')
            FREEZED_results[v+'_max'] = dpg.get_value('VARIABLES_'+v+'_max')
            FREEZED_results[v+'_check'] = dpg.get_value('VARIABLES_'+v+'_check')
        RES_add=RES_ADD.copy().drop(columns=['file'])
        FREEZED_results['RES_ADD']={k:float(RES_add[k].values) for k in RES_add.columns}
        self.workspace_iso['FILES'][self.anal_file]=FREEZED_results
        self.workspace_iso['STORED RESULTS'] = {col:list(self.RES_DF[col].values) for col in self.RES_DF.columns }

    def callback_show_res_button(self,sender,app_data):
        '''Shows the table containing the stored fitting results.'''
        dpg.configure_item('show_res_win',show=True)


    def callback_save_res_button(self,sender,app_data):
        '''Opend the dialog window allowing export of the fitting results to the external file.'''
        dpg.configure_item('file_dialog_export',default_path=self.last_directory)
        self.basf.log_last_directory(self.last_directory)
        self.update_default_directory(self.last_directory)
        dpg.show_item("file_dialog_export")
        
  
    def callback_plot_res_button(self,sender,app_data):
        '''Opend the dialog window allowing export of the fitting results to the external PNG file.'''
        dpg.configure_item('file_dialog_plot_all',default_path=self.last_directory)
        self.basf.log_last_directory(self.last_directory)
        self.update_default_directory(self.last_directory)
        dpg.show_item("file_dialog_plot_all")
        


    def callback_remove_result_button(self,sender,app_data):
        ind_result_to_remove =[]
        for i in self.RES_DF.index:
            if dpg.get_value('results_delete_'+str(i)+'_check'):
                ind_result_to_remove.append(i)
        self.RES_DF.drop(self.RES_DF.index[ind_result_to_remove],inplace=True)
        self.RES_DF.reset_index(drop=True,inplace=True)
        self.write_res_to_table()
        self.write_to_average_table()

    def write_res_to_table(self):
        for alias in dpg.get_aliases():
            if alias.startswith('results_show_'):
                try:
                    dpg.delete_item(alias)
                except:
                    pass
            if alias.startswith('results_delete_'):
                try: 
                    dpg.delete_item(alias)
                except:
                    pass
        for alias in dpg.get_aliases():
            if alias.startswith('row_results_show'):
                try:
                    dpg.delete_item(alias)
                except:
                    pass
        exclude_col = "file" 
        for col in self.RES_DF.select_dtypes(include=["object"]).columns:
            if col == exclude_col:
                continue
            try:
                self.RES_DF[col] = pd.to_numeric(self.RES_DF[col], errors="raise").astype(float)
            except ValueError:
                pass
            
        if dpg.get_value('Sett_export_each'):
            fname = dpg.get_value('default_quick_export_filename')
            if dpg.get_value('Sett_export_to_excel'):
                pth = os.path.join(self.last_directory,fname+'.xlsx')
                self.RES_DF.to_excel(os.path.join(pth),index=False)
            if dpg.get_value('Sett_export_to_csv'):
                pth = os.path.join(self.last_directory,fname+'.csv')
                self.RES_DF.to_csv(os.path.join(pth),index=False)
            if dpg.get_value('Sett_export_to_pickle'):
                pth = os.path.join(self.last_directory,fname+'.pickle')
                self.RES_DF.to_pickle(pth)             

        else:
            pass
        for i in self.RES_DF.index:
            with dpg.table_row(tag='row_results_show'+str(i),parent='table_results_show'):
                dpg.add_text(self.RES_DF.at[i,'file'],tag='results_show_'+str(i)+'_name')
                for v in self.VARIABLES:
                    dpg.add_text(self.basf.zeros(self.RES_DF.at[i,v]),
                                 tag='results_show_'+str(i)+'_'+v+'_value')
                    dpg.add_text(self.basf.zeros(self.RES_DF.at[i,v+'_err']),
                                 tag='results_show_'+str(i)+'_'+v+'_err')
                dpg.add_text(str(self.basf.zeros_chi(self.RES_DF.at[i,'B'])),
                             tag='results_show_'+str(i)+'_'+'B')
                dpg.add_text(str(self.basf.zeros_chi(self.RES_DF.at[i,'B_err'])),
                             tag='results_show_'+str(i)+'_'+'B_err')
                dpg.add_text(str(self.basf.zeros_chi(self.RES_DF.at[i,'chi_sqr'])),
                             tag='results_show_'+str(i)+'_'+'chisqr')
                dpg.add_text(str(self.basf.zeros(self.RES_DF.at[i,'Red.chi_sqr'])),
                             tag='results_show_'+str(i)+'_'+'Redchi')
                dpg.add_text(str(self.basf.zeros(self.RES_DF.at[i,'p-value'])),
                             tag='results_show_'+str(i)+'_'+'p-value')
                dpg.add_checkbox(label='',tag='results_delete_'+str(i)+'_check',
                                 callback=self.callback_remove_result)
    
    def callback_Xunits(self,sender, app_data):
        '''Changes the time units in the FCS mode and replots.'''
        Xunits = dpg.get_value('Xunits')
        Yunits = dpg.get_value('Yunits')
        self.df=self.df_copy.copy()
        current_range=[dpg.get_value('df_min'),dpg.get_value('df_max')]
        mask_min = self.df['X'] <= current_range[0]
        mask_max = self.df['X'] >= current_range[1]
        self.df.loc[mask_min,'X'] = np.nan
        self.df.loc[mask_max,'X'] = np.nan
        self.df.dropna(inplace=True)
        if sender == 'Xunits':
            self.df['X']=self.df.X*dpg.get_value('Xunits')*1e3
            self.plot_scater(self.df,'callback_Xunits')
        elif sender == 'Yunits':
            self.df['Y']=self.df.Y*dpg.get_value('Yunits')
            if self.FCS_data_type == "bin":
                if len(self.df.columns) == 3:
                    self.df['Y_err']=self.df.Y_err*dpg.get_value('Yunits')
                else:
                    pass
            elif self.FCS_data_type == "3C":
                self.df['Y_err']=self.df.Y_err*dpg.get_value('Yunits')
            elif self.FCS_data_type == "2C":
                pass
            self.plot_scater(self.df,'callback_Xunits')
        elif sender == 'both':
            self.df['X']=self.df.X*dpg.get_value('Xunits')*1e3
            self.df['Y']=self.df.Y*dpg.get_value('Yunits')  
            if self.FCS_data_type == "bin":
                if len(self.df.columns) == 3:
                    self.df['Y_err']=self.df.Y_err*dpg.get_value('Yunits')
                else:
                    pass
            elif self.FCS_data_type == "3C":
                self.df['Y_err']=self.df.Y_err*dpg.get_value('Yunits')
            elif self.FCS_data_type == "2C":
                pass
         
    def update_flist(self,fs,multi):
        '''Updates the filelist. '''
        if not len(fs)==0:
            self.workspace_iso_path = os.path.join(self.last_directory,'workspace.dct') 
            Current_model = dpg.get_value('model_choose')
            if not os.path.exists(self.workspace_iso_path):
                self.workspace_iso={'Model':Current_model,'FILES':{f:'' for f in fs},'STORED RESULTS':{}}
            else:
                with open(self.workspace_iso_path) as json_workspace:
                    self.workspace_iso = json.load(json_workspace)
                for k in self.workspace_iso['STORED RESULTS'].keys():
                    self.RES_DF[k] = self.workspace_iso['STORED RESULTS'][k]
            try:
                dpg.configure_item("file_box", items=fs)
                dpg.configure_item("file_box", default_value=fs[0])
            except:
                pass
        else:
            dpg.configure_item("file_box", items=())
            dpg.configure_item("file_box", default_value='')
        dpg.configure_item('reset_workspace_menu_item',enabled=True)


    def load_data(self,director,f):
        '''The function loads the datafile into a pandas DataFrame. Also mounts the X range of the data, the number of points to skip, and the scaler for the X values depending on the defined units.'''
        f_path=os.path.join(director,f)
        xunit=np.round(dpg.get_value('Xunits')*1e3,6)
        if self.FCS_data_type == "bin":
            with open(f_path, 'rb') as file:
                data = pickle.load(file)
            if not dpg.get_value('Sett_preserve_units'):
                dpg.set_value('Xunits',0.001)
                dpg.set_value('Yunits',1.)
            else:
                pass
            self.df = data['Correlation']
            self.cntr = data['CNTR'][0]
            dpg.set_value('CNTR',self.cntr)
            if len(self.df.columns) == 3:
                dpg.set_value('FITing_checkbox', True)
                dpg.configure_item('FITing_checkbox', enabled=False)
            elif len(self.df.columns) == 2:
                dpg.set_value('FITing_checkbox', False)
                dpg.configure_item('FITing_checkbox', enabled=False)
            else:
                pass
            dpg.configure_item('df_min', show=True)
            dpg.configure_item('df_max', show=True)
            dpg.configure_item('df_min', default_value=self.df.X.min())
            dpg.configure_item('df_max', default_value=self.df.X.max())
            dpg.configure_item('df_min',max_value=self.df.X.max())
            dpg.configure_item('df_min',min_value=self.df.X.min())
            dpg.configure_item('df_max',max_value=self.df.X.max())
            dpg.configure_item('df_max',min_value=self.df.X.min())
            if not dpg.get_value('Sett_preserve_time'):
                top_range=self.df.X.max()*xunit
                bottom_range=self.df.X.min()*xunit
            else:
                if self.time_range[0]!= None:
                    bottom_range = self.time_range[0]*xunit
                else:
                    bottom_range=self.df.X.min()*xunit
                if self.time_range[1]!=None:
                    top_range = self.time_range[1]*xunit
                else:
                    top_range=self.df.X.max()*xunit
            self.df_copy=self.df.copy()
            if top_range != self.df.X.max():
                if top_range>self.df.X.max():
                    top_range = self.df.X.max()
                else:
                    mask = self.df['X'] > top_range
                    self.df.loc[mask,'X'] = np.nan
            if bottom_range != self.df.X.max():
                if bottom_range < self.df.X.min():
                    bottom_range = self.df.X.min()
                else:
                    mask = self.df['X'] < bottom_range 
                    self.df.loc[mask,'X'] = np.nan

            self.df.dropna(inplace=True)
            dpg.configure_item('df_min', default_value=bottom_range)
            dpg.configure_item('df_max', default_value=top_range)
        
        elif self.FCS_data_type == "3C":
            cnt,self.df = self.count_skiprows(f_path)
            if not dpg.get_value('Sett_preserve_units'):
                dpg.set_value('Xunits',0.001)
                dpg.set_value('Yunits',1.)
            else:
                pass
            self.df.columns=['X','Y','Y_err']
            dpg.configure_item('df_min', show=True)
            dpg.configure_item('df_max', show=True)
            dpg.configure_item('df_min', default_value=self.df.X.min())
            dpg.configure_item('df_max', default_value=self.df.X.max())
            dpg.configure_item('df_min',max_value=self.df.X.max())
            dpg.configure_item('df_min',min_value=self.df.X.min())
            dpg.configure_item('df_max',max_value=self.df.X.max())
            dpg.configure_item('df_max',min_value=self.df.X.min())
            if not dpg.get_value('Sett_preserve_time'):
                top_range=self.df.X.max()*xunit
                bottom_range=self.df.X.min()*xunit
            else:
                if self.time_range[0]!= None:
                    bottom_range = self.time_range[0]*xunit
                else:
                    bottom_range=self.df.X.min()*xunit

                if self.time_range[1]!=None:
                    top_range = self.time_range[1]*xunit
                else:
                    top_range=self.df.X.max()*xunit
            self.df_copy=self.df.copy()
            if top_range != self.df.X.max():
                if top_range>self.df.X.max():
                    top_range = self.df.X.max()
                else:
                    mask = self.df['X'] > top_range
                    self.df.loc[mask,'X'] = np.nan
            if bottom_range != self.df.X.max():
                if bottom_range < self.df.X.min():
                    bottom_range = self.df.X.min()
                else:
                    mask = self.df['X'] < bottom_range 
                    self.df.loc[mask,'X'] = np.nan

            self.df.dropna(inplace=True)
            dpg.configure_item('df_min', default_value=bottom_range)
            dpg.configure_item('df_max', default_value=top_range)

        elif self.FCS_data_type == "2C":
            cnt,self.df = self.count_skiprows(f_path)
            self.df.columns=['X','Y']
            dpg.configure_item('df_min', show=True)
            dpg.configure_item('df_max', show=True)
            dpg.configure_item('df_min', default_value=self.df.X.min())
            dpg.configure_item('df_max', default_value=self.df.X.max())
            dpg.configure_item('df_min',max_value=self.df.X.max())
            dpg.configure_item('df_min',min_value=self.df.X.min())
            dpg.configure_item('df_max',max_value=self.df.X.max())
            dpg.configure_item('df_max',min_value=self.df.X.min())
            dpg.configure_item('Xunits', show=True)
            if not dpg.get_value('Sett_preserve_time'):
                top_range=self.df.X.max()*xunit
                bottom_range=self.df.X.min()*xunit
            else:
                if self.time_range[0]!= None:
                    bottom_range = self.time_range[0]*xunit
                else:
                    bottom_range=self.df.X.min()*xunit
                if self.time_range[1]!=None:
                    top_range = self.time_range[1]*xunit
                else:
                    top_range=self.df.X.max()*xunit
            self.df_copy=self.df.copy()
            if top_range != self.df.X.max():
                if top_range>self.df.X.max():
                    top_range = self.df.X.max()
                else:
                    mask = self.df['X'] > top_range
                    self.df.loc[mask,'X'] = np.nan
            if bottom_range != self.df.X.max():
                if bottom_range < self.df.X.min():
                    bottom_range = self.df.X.min()
                else:
                    mask = self.df['X'] < bottom_range # change limits of X axis
                    self.df.loc[mask,'X'] = np.nan

        self.callback_Xunits('both',dpg.get_value('Yunits'))
        self.workspace_test(f)  


    def callback_df_range(self,sender, app_data):
        '''Response to change in the x-value's range of analysed data'''
        dmax=self.df_copy.X.max()
        dmin=self.df_copy.X.min()
        current_range=[dpg.get_value('df_min'),dpg.get_value('df_max')]
        if sender =='df_max':
            if app_data ==1:
                dpg.configure_item(sender,speed=abs(app_data/10.))
            if app_data ==0.:
                dpg.set_value(sender,dpg.get_value('df_min')*2)
            dpg.configure_item(sender,max_value=self.df_copy.X.max())
            dpg.configure_item(sender,min_value=dpg.get_value('df_min'))
            dpg.configure_item(sender,format='\u03C4'+' (max)  [ms] = %.'+str(self.basf.decimal_rounds_lim(app_data))+'f',)
        if sender =='df_min':
            dpg.configure_item(sender,max_value=dpg.get_value('df_max'))
            dpg.configure_item(sender,min_value=self.df_copy.X.min())
            dpg.configure_item(sender,format='\u03C4'+' (min)  [ms] = %.'+str(self.basf.decimal_rounds_lim(app_data))+'f',)
        self.df=self.df_copy.copy()
        dpg.configure_item(sender,speed=abs(app_data/10.))
        mask_min = self.df['X'] <= current_range[0]
        mask_max = self.df['X'] >= current_range[1]
        self.df.loc[mask_min,'X'] = np.nan
        self.df.loc[mask_max,'X'] = np.nan
        self.df.dropna(inplace=True)
        if self.df.X.max() != dmax or self.df.X.min()!=dmin:
            dpg.configure_item('Reset_range',enabled=True)
            dpg.bind_item_theme('Reset_range', 'fit_button_theme') 
        else:
            dpg.configure_item('Reset_range',enabled=False)
            dpg.bind_item_theme('Reset_range', 'fit_button_theme_inactive') 
        if len(self.df)!= 0:
            xunit = dpg.get_value('Xunits')
            yunit = dpg.get_value('Yunits')
            self.callback_Xunits('Xunits',xunit)
            self.callback_Xunits('Yunits',yunit)
            self.plot_scater(self.df,'callback_df_range')
        else:
            pass
        if dpg.get_value('Sett_preserve_time'):
            self.time_range = current_range[0],current_range[1]
        else:
            self.time_range=(None,None)

    def  callback_reset_df_range(self,sender,app_data):
        current_range=[dpg.get_value('df_min'),dpg.get_value('df_max')]
        self.df=self.df_copy.copy()
        dpg.set_value('df_min',self.df_copy.X.min())
        dpg.set_value('df_max',self.df_copy.X.max())
        self.time_range = (None,None)
        self.plot_scater(self.df,'callback_reset_df_range')
        dpg.configure_item(sender,enabled=False)
        
        
    def callback_remove_result(self,sender,app_data):
        ind_result_to_remove=sender.split('_')[2]
        
        
    
    def load_data_local(self,director,f):
        f_path=os.path.join(director,f)
        if self.FCS_data_type == "bin":
            with open(f_path, 'rb') as file:
                data = pickle.load(file)
            if not dpg.get_value('Sett_preserve_units'):
                dpg.set_value('Xunits',0.001)
                dpg.set_value('Yunits',1.)
            else:
                pass
        
            dfl = data['Correlation']
            cntr = data['CNTR'][0]
            if len(dfl.columns) == 3:
                dfl['X']=dfl.X*dpg.get_value('Xunits')*1e3
                if not dpg.get_value('Sett_preserve_time'):
                    top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
                    bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3
                else:
                    if self.time_range[0]!= None:
                        bottom_range = self.time_range[0]*dpg.get_value('Xunits')*1e3
                    else:
                        bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3
                    if self.time_range[1]!=None:
                        top_range = self.time_range[1]*dpg.get_value('Xunits')*1e3
                    else:
                        top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
                dfl['Y']=dfl.Y*dpg.get_value('Yunits')    
                dfl['Y_err']=dfl.Y_err*dpg.get_value('Yunits')
                if top_range != dfl.X.max():
                    if top_range>dfl.X.max():
                        top_range = dfl.X.max()
                    else:
                        mask = dfl['X'] >= top_range
                        dfl.loc[mask,'X'] = np.nan
                if bottom_range != dfl.X.max():
                    if bottom_range < dfl.X.min():
                        bottom_range = dfl.X.min()
                    else:
                        mask = dfl['X'] <= bottom_range
                        dfl.loc[mask,'X'] = np.nan
                dfl.dropna(inplace=True)
                
            elif len(dfl.columns) == 2:
                dfl['X']=dfl.X*dpg.get_value('Xunits')*1e3
                top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
                bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3
                dfl['Y']=dfl.Y*dpg.get_value('Yunits') 
                if top_range != dfl.X.max():
                    if top_range>dfl.X.max():
                        top_range = dfl.X.max()
                    else:
                        mask = dfl['X'] >= top_range
                        dfl.loc[mask,'X'] = np.nan
                if bottom_range != dfl.X.min():
                    if bottom_range < dfl.X.min():
                        bottom_range = dfl.X.min()
                    else:
                        mask = dfl['X'] <= bottom_range
                        dfl.loc[mask,'X'] = np.nan
                dfl.dropna(inplace=True)
            else:
                pass
        elif self.FCS_data_type == "3C":
            cnt,dfl = self.count_skiprows(f_path)
            dfl.columns=['X','Y','Y_err']
            dfl['X']=dfl.X*dpg.get_value('Xunits')*1e3
            if not dpg.get_value('Sett_preserve_time'):
                top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
                bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3
            else:
                if self.time_range[0]!= None:
                    bottom_range = self.time_range[0]*dpg.get_value('Xunits')*1e3
                else:
                    bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3

                if self.time_range[1]!=None:
                    top_range = self.time_range[1]*dpg.get_value('Xunits')*1e3
                else:
                    top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
            dfl['Y']=dfl.Y*dpg.get_value('Yunits')    
            dfl['Y_err']=dfl.Y_err*dpg.get_value('Yunits')
            if top_range != dfl.X.max():
                if top_range>dfl.X.max():
                    top_range = dfl.X.max()
                else:
                    mask = dfl['X'] >= top_range
                    dfl.loc[mask,'X'] = np.nan
            if bottom_range != dfl.X.max():
                if bottom_range < dfl.X.min():
                    bottom_range = dfl.X.min()
                else:
                    mask = dfl['X'] <= bottom_range
                    dfl.loc[mask,'X'] = np.nan
            dfl.dropna(inplace=True)

        elif self.FCS_data_type == "2C":
            cnt,dfl = self.count_skiprows(f_path)
            dfl.columns=['X','Y']
            dfl['X']=dfl.X*dpg.get_value('Xunits')*1e3
            top_range=dfl.X.max()*dpg.get_value('Xunits')*1e3
            bottom_range=dfl.X.min()*dpg.get_value('Xunits')*1e3
            dfl['Y']=dfl.Y*dpg.get_value('Yunits') 
            if top_range != dfl.X.max():
                if top_range>dfl.X.max():
                    top_range = dfl.X.max()
                else:
                    mask = dfl['X'] >= top_range
                    dfl.loc[mask,'X'] = np.nan
            if bottom_range != dfl.X.min():
                if bottom_range < dfl.X.min():
                    bottom_range = dfl.X.min()
                else:
                    mask = dfl['X'] <= bottom_range 
                    dfl.loc[mask,'X'] = np.nan
            dfl.dropna(inplace=True)
        else:
            pass
        return dfl
    

    def save_all_to_plot(self,dd,f_path,fnam,varias):
        checkboxes=[
            dpg.get_value('Sett_export_plot_as_png'),
            dpg.get_value('Sett_export_plot_as_csv'),
            dpg.get_value('Sett_export_plot_as_pickle'),
            dpg.get_value('Sett_export_plot_loglog')
                ]
        ts0 = time.time()
        ts0a = time.time()

        dd['FIT']=self.my_universal_function(dd.X,**varias)
        xdata = dd.X
        ydata =dd.Y
        if self.FCS_data_type == "bin":
            if len(dd.columns) == 4:
                ydata_err = dd.Y_err
            else:
                pass
        elif self.FCS_data_type == "3C":
            ydata_err = dd.Y_err
        yfit = dd.FIT
        if self.FCS_data_type == "bin":
            if len(dd.columns) == 4:
                dd['Residues']=(1/dd.Y_err)*(dd.Y-self.my_universal_function(xdata,**varias))
            else:
                dd['Residues']=(dd.Y-self.my_universal_function(xdata,**varias))
        elif self.FCS_data_type == "3C":
            dd['Residues']=(1/dd.Y_err)*(dd.Y-self.my_universal_function(xdata,**varias))
        elif self.FCS_data_type == "2C":
            dd['Residues']=(dd.Y-self.my_universal_function(xdata,**varias))
        res=dd['Residues']
        XX = 10**np.linspace(log10(min(xdata)),log10(max(xdata)),100)
        ts1a = time.time()
        ts0b = time.time()
        fig = Figure(figsize=(16, 10))
        gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3, 1])
        ax2 = fig.add_subplot(gs[1])
        ax1 = fig.add_subplot(gs[0], sharex=ax2)
        ax1.set_xscale('log')
        ax2.set_xscale('log')
        ax1.plot(xdata,ydata,'o',ms=10)
        ax1.axhline(0,ls=':',c='k',lw=1)
        ax1.plot(XX,self.my_universal_function(XX,**varias),ls ='-',lw = 3,c='C1')
        ax2.axhline(0,c='k',ls=':',lw=1)
        ax2.plot(xdata,res,ls ='-',lw = 3,c='C1')
        ax1.tick_params('both',labelsize=19)
        ax2.tick_params('both',labelsize=19)
        ax1.set_ylabel(dpg.get_item_configuration('acf_y')['label'],
                       fontsize=22)
        ax2.set_ylabel(r'Res.', fontsize=22)
        ax2.set_xlabel(dpg.get_item_configuration('res_x')['label'],
                       fontsize=22)
        if checkboxes[0]:
            export_path = os.path.join(f_path,fnam+'.png')
            ts0bb = time.time()
            FigureCanvas(fig).print_png(export_path)
        ts1b = time.time()
        ts0c = time.time()
        if checkboxes[1]:
            export_path = os.path.join(f_path,fnam+'.csv')
            dd.to_csv(export_path,sep='\t',index=False)
        if checkboxes[2]:
            export_path = os.path.join(f_path,fnam+'.pickle')
            dd.to_pickle(export_path)
        if checkboxes[3]:
            export_path = os.path.join(f_path,fnam+'_log.png')
            dd['FIT']=self.my_universal_function(dd.X,**varias)
            xdata = dd.X
            ydata =dd.Y
            yfit = dd.FIT
            if self.FCS_data_type == "bin":
                if len(dd.columns) == 4 and 'Residues' not in dd.columns:
                    dd['Residues']=(1/dd.Y_err)*(dd.Y-self.my_universal_function(xdata,**varias))
                else:
                    dd['Residues']=(dd.Y-self.my_universal_function(xdata,**varias))
            elif self.FCS_data_type == "3C"and 'Residues' not in dd.columns:
                dd['Residues']=(1/dd.Y_err)*(dd.Y-self.my_universal_function(xdata,**varias))
            else:
                dd['Residues']=(dd.Y-self.my_universal_function(xdata,**varias))
            res=dd['Residues']
            XX = 10**np.linspace(log10(min(xdata)),log10(max(xdata)),100)
            fig = Figure(figsize=(16, 10))
            gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[3, 1])
            ax2 = fig.add_subplot(gs[1])
            ax1 = fig.add_subplot(gs[0], sharex=ax2)
            ax1.set_xscale('log')
            ax2.set_xscale('log')
            ax1.set_yscale('log')
            ax1.plot(xdata,ydata,'o',ms=10)
            ax1.axhline(0,ls=':',c='k',lw=1)
            ax1.plot(XX,self.my_universal_function(XX,**varias),ls ='-',lw = 3,c='C1')
            ax2.axhline(0,c='k',ls=':',lw=1)
            ax2.plot(xdata,res,ls ='-',lw = 3,c='C1')
            ax1.tick_params('both',labelsize=19)
            ax2.tick_params('both',labelsize=19)
            # print(dpg.get_item_configuration('acf_y_log')['label'])
            ax1.set_ylabel(dpg.get_item_configuration('acf_y_log')['label'],
                           fontsize=22)
            ax2.set_ylabel(r'Res.', fontsize=22)
            ax2.set_xlabel(dpg.get_item_configuration('res_x')['label'],
                           fontsize=22)
            ts0d = time.time()
            FigureCanvas(fig).print_png(export_path)
            ts1d = time.time()
            ts1c = time.time()
            ts1 = time.time()


    def curves(self,directory,f):
        '''Function extracts a single data curve from a data file containing more than one data curve. Depending on the user-declared data curve size (2 or 3 columns), the set of new files is created in a folder named after the original filename of the multiple-curve data file. '''
        f_path=os.path.join(directory,f)
        ncurves=self.count_curves(f_path)
        self.new_directory=os.path.join(directory,f.replace('.dat','')+'_single_curves')
        try:
            os.stat(self.new_directory)
        except:
            os.mkdir(self.new_directory)
        if ncurves == -1:
            error_text = 'This is not a valid multicolumn file. File must contain 3xN columns, where N is the number of measurements.'
            self.show_error_no_files_close_only(error_text)
            return False
        else:
            cnt,self.df = self.count_skiprows(f_path)
            col_names_base=['X','Y','Y_err']
            col_names=[]
            for i in range(ncurves):
                names=[s+'_'+str(i+1) for s in col_names_base]
                col_names.extend(names)
            self.df.columns = col_names
            curve_names_base=f.replace('.dat','')+'_curve_'
            for i in range(ncurves):
                names=[s+'_'+str(i+1) for s in col_names_base]
                DF = self.df.copy()[names]
                DF.columns = col_names_base
                DF.to_csv(os.path.join(self.new_directory,curve_names_base+str(i+1)+'.dat'),sep='\t',index=False)
            self.last_directory=self.new_directory
            return True
        
    
    def callback_directory_export(self,sender, app_data):
        ''' Export stored results to the external file.'''

        with open(self.workspace_iso_path, 'w') as json_workspace:
            json.dump(self.workspace_iso, json_workspace, indent=4, sort_keys=False)
        export_path = app_data['file_path_name']
        if app_data['current_filter']=='.xlsx':
            self.RES_DF.to_excel(export_path,index=False)
        if app_data['current_filter']=='.csv':
            self.RES_DF.to_csv(export_path,index=False,sep=',')
        if app_data['current_filter']=='.dat':
            self.RES_DF.to_csv(export_path,index=False,sep='\t')
        if app_data['current_filter']=='.pickle':
            self.RES_DF.to_pickle(export_path)
        if app_data['current_filter']=='':
            extension = app_data['file_name'].split('.')[1]
            if extension=='xlsx':
                self.RES_DF.to_excel(export_path,index=False)
            if extension=='csv':
                self.RES_DF.to_csv(export_path,index=False,sep=',')
            if extension=='dat':
                self.RES_DF.to_csv(export_path,index=False,sep='\t')
            if extension=='pickle':
                self.RES_DF.to_pickle(export_path)

        if dpg.get_value('Sett_export_stats'):
            fnam = dpg.get_value('default_quick_stst_filename')
            report_DF=self.RES_DF[[v for v in self.VARIABLES]].describe()
            report_f_path=os.path.join(self.new_directory,fnam)
            if dpg.get_value('Sett_export_stats_to_csv'):
                report_DF.to_csv(report_f_path+'.csv')
            if dpg.get_value('Sett_export_stats_to_pickle'):
                report_DF.to_pickle(report_f_path+'.pickle')
            if dpg.get_value('Sett_export_stats_to_xlsx'):
                report_DF.to_excel(report_f_path+'.xlsx')
        else:
            pass
            
        
    def callback_no_files_dialog_close(self,sender,app_data):
        dpg.configure_item('No_data_files',show=False)
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('no_files_error_butt')
        dpg.delete_item('No_data_files')
        dpg.show_item('file_dialog_id1')


    def callback_plot_all_to_files(self,sender,app_data):
        dpg.configure_item("file_dialog_plot_all",show=False)
        if self.size_ratio['width']>=1:
            ww = 250*self.size_ratio['width']
        else:
            ww = 250
        with dpg.window(tag='load_ind_win',width=ww,height=250,
                                menubar=False,
                                autosize=False,
                                no_title_bar=True,
                                no_move=True,
                                no_background=True,
                                modal=True,

                           show=True):
            dpg.add_button(tag='loading_title',width=ww,label='Ploting your data to files')
            dpg.bind_item_theme('loading_title', 'transparent_theme')
            dpg.add_button(tag='loading_butt',width=ww,label='')
            dpg.bind_item_theme('loading_butt', 'transparent_theme')
        win_width = dpg.get_item_width('load_ind_win')
        win_height = dpg.get_item_height('load_ind_win')
        VP_w = dpg.get_viewport_width()
        VP_h = dpg.get_viewport_height()
        posit = (int(VP_w/2-win_width/2),int(VP_h/2-win_height/2))
        dpg.configure_item('load_ind_win',pos=posit)
        director = app_data['file_path_name']
        if len(self.RES_DF)>0:
            for cnt,i in enumerate(list(self.RES_DF.index)):
                try:
                    dpg.configure_item('loading_butt',label=str(int(100*cnt/len(self.RES_DF)))+'%')
                except:
                    pass
                file = self.RES_DF.at[i,'file']
                varias = {}
                for v in self.VARIABLES:
                    varias[v]=self.RES_DF.at[i,v]
                DATA_frame = self.load_data_local(self.last_directory,file)
                self.save_all_to_plot(DATA_frame,director,file,varias)

        else:
            self.show_error_no_files_close_only('No fitted results to plot.')
        dpg.configure_item('load_ind_win',show=False)
        try:
            dpg.delete_item('loading_butt')
            dpg.delete_item('loading_title')
            dpg.delete_item('load_ind_win')

        except:
            pass
        
    def loading_indicator_close(self):
        dpg.configure_item('load_ind_win',show=False)
        try:
            dpg.delete_item('loading_ind')
            dpg.delete_item('load_ind_win')

        except:
            pass



    def loading_indicator_show(self):
        with dpg.window(tag='load_ind_win',width=50,height=50,
                                menubar=False,
                                autosize=True,
                                no_title_bar=True,
                                no_move=True,
                                no_background=True,
                                modal=True,
                           show=True):
            dpg.add_button(tag='loading_title',width=-1,label='Ploting to file')
            dpg.bind_item_theme('loading_title', 'transparent_theme')
            dpg.add_loading_indicator(tag='loading_ind',
                                      radius=6,
                                      width=50,
                                      height=50,
                                      show=True,
                                      color=self.basf._hsv_to_rgb(2/7.0, 0.7, 0.7),
                                      secondary_color=(116,116,116,0),
                                      speed=2)
            dpg.add_button(tag='loading_butt',width=-1,label='')
            dpg.bind_item_theme('loading_butt', 'transparent_theme')
        win_width = dpg.get_item_width('load_ind_win')
        win_height = dpg.get_item_height('load_ind_win')
        VP_w = dpg.get_viewport_width()
        VP_h = dpg.get_viewport_height()
        posit = (int(VP_w/2-win_width/2),int(VP_h/2-win_height/2))
        dpg.configure_item('load_ind_win',pos=posit)

    def show_error_no_files_2c_csv(self):
        dpg.add_window(pos=(400,150),
                       label='Error!',
                       tag='No_data_files',
                       no_move=True,
                       no_close=False,
                       no_title_bar=False,
                       no_resize=True,
                       show=True,
                       modal=False
                       )
        dpg.add_text('No ".dat" data files found. ".csv"  files found instead. Do you want to import ".csv" files?',
                     tag='no_files_error_text',
                     parent='No_data_files')
        dpg.add_button(label='Yes',
                       parent='No_data_files',
                       tag='no_files_error_butt_yes',
                       callback=self.callback_no_files_dialog_close_yes
                      )
        dpg.add_button(label='Close',
                       parent='No_data_files',
                       tag='no_files_error_butt',
                       callback=self.callback_no_files_dialog_close
                      )
        dpg.bind_item_theme('No_data_files', 'Error_window_theme')


    def show_error_no_files(self):
        try:
            dpg.add_window(pos=(400,150),
                           label='Error!',
                           tag='No_data_files',
                           no_move=True,
                           no_close=False,
                           no_title_bar=False,
                           no_resize=True,
                           show=True,
                           modal=False
                           )
            dpg.add_text('No data files found. Change directory.',
                         tag='no_files_error_text',
                         parent='No_data_files')
            dpg.add_button(label='Close',
                           parent='No_data_files',
                           tag='no_files_error_butt',
                           callback=self.callback_no_files_dialog_close
                          )
            dpg.bind_item_theme('No_data_files', 'Error_window_theme')
        except:
            dpg.show_item('No_data_files')

    def show_delete_Curve_window(self):
        try:
            delete_file_name = dpg.get_value('file_box')
        except:
            self.show_error_no_files_close_only('No files loaded?')
        try:
            dpg.add_window(pos=(400,150),
                           label='Delete curve?',
                           tag='Delete_curve_win',
                           no_move=False,
                           no_close=True,
                           no_title_bar=False,
                           no_resize=True,
                           show=True,
                           autosize=True,
                           modal=True
                           )
            dpg.add_text('Do you realy want to delete the file:',
                         tag='Delete_curve_text_L1',
                         parent='Delete_curve_win')
            dpg.add_text(delete_file_name,
                         tag='Delete_curve_text_L2',
                         parent='Delete_curve_win')
            with dpg.table(header_row=False,tag='del_curve_butt_table',show=True,parent='Delete_curve_win'):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    with dpg.table_cell():
                        dpg.add_button(label='Yes',
                                       tag='Del_curve_yes_butt',
                                       callback=self.callback_delete_Curve_yes_butt
                                      )
                    with dpg.table_cell():
                        dpg.add_button(label='No',
                                       tag='Del_curve_no_butt',
                                       callback=self.callback_delete_Curve_no_butt
                                      )
            dpg.bind_item_theme('Delete_curve_win', 'Error_window_theme')
        except:
            dpg.show_item('Delete_curve_win')


    def callback_delete_Curve_yes_butt(self,sender,app_data):       
        files = dpg.get_item_configuration('file_box')['items']
        def_val = dpg.get_value('file_box')
        index = files.index(def_val)
        if index != 0:
            new_value = files[index-1]
            files.remove(def_val)
            self.update_flist(files,None)
            dpg.set_value('file_box',new_value)
            self.callback_listbox('file_box',new_value)
        else:
            new_value = files[index+1]
            files.remove(def_val)
            self.update_flist(files,None)
            dpg.set_value('file_box',new_value)
            self.callback_listbox('file_box',new_value)
        self.callback_delete_Curve_no_butt('Del_curve_no_butt',None)

    def callback_delete_Curve_no_butt(self,sender,app_data):
        dpg.configure_item('Delete_curve_win',show=False)
        dpg.delete_item('Delete_curve_text_L1')
        dpg.delete_item('Delete_curve_text_L2')
        dpg.delete_item('Del_curve_yes_butt')
        dpg.delete_item('Del_curve_no_butt')
        dpg.delete_item('del_curve_butt_table')
        dpg.delete_item('Delete_curve_win')


    def callback_no_files_dialog_close_only(self,sender,app_data):
        dpg.configure_item('No_data_files',show=False)
        dpg.delete_item('no_files_error_text')
        dpg.delete_item('no_files_error_butt')
        dpg.delete_item('No_data_files')
        if 'no_files_error_butt_yes' in dpg.get_aliases():
            dpg.delete_item('no_files_error_butt_yes')
        else:
            pass


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
            dpg.add_text(error_text,
                         tag='no_files_error_text',
                         parent='No_data_files')
            dpg.add_button(label='Close',
                           parent='No_data_files',
                           tag='no_files_error_butt',
                           callback=self.callback_no_files_dialog_close_only
                          )
            dpg.bind_item_theme('No_data_files', 'Error_window_theme')
        except:
            dpg.show_item('No_data_files')
            
    def callback_directory_select(self,sender, app_data):
        '''Select the directory containing data files to analyse.'''
        def _FCSDATATYPE_initcommoncommands():
            self.define_RES_DF()
            self.unmount_tables()
            self.unmount_variables()
            self.mount_variables()
            self.new_directory=app_data['file_path_name']
            self.last_directory=self.new_directory

        def _FCSDATATYPE_dpgconfig():
            dpg.configure_item('file_box', callback=self.callback_listbox)
            dpg.configure_item('file_dialog_id1', default_path=self.last_directory)
            dpg.configure_item('file_dialog_export', default_path=self.last_directory)
            Variable_groups = [item for item in dpg.get_aliases() if item.startswith('VARIABLES_') and item.endswith('_group')] 
            Variable_groups.extend(['sep_mid_1','sep_mid_2','Fit_button','FITing_checkbox','Fit_all_button'])
            for item in Variable_groups:
                dpg.configure_item(item,show=True)
            dpg.configure_item('model_choice_group', show=True)
            dpg.configure_item('model_choose', enabled=True)
            dpg.configure_item('log_checkbox_group', show=True)
            dpg.configure_item('subplots', show=True)
            dpg.configure_item('plot_1', show=True)
            dpg.configure_item('plot_2', show=True)
            dpg.configure_item('plot_3', show=True)
            dpg.configure_item('file_box', callback=self.callback_listbox)
            if self.FCS_data_type == 'bin':
                dpg.configure_item('FITing_checkbox', enabled=True)
                
            elif self.FCS_data_type == '3C':
                dpg.configure_item('FITing_checkbox', enabled=True)
                dpg.set_value('FITing_checkbox', True)
            elif self.FCS_data_type == '2C':
                dpg.configure_item('FITing_checkbox', enabled=False)
                dpg.set_value('FITing_checkbox', False)
            else:
                pass

        if self.FCS_data_type == 'bin':
            self.files=()
            self.filesbin=()
            _FCSDATATYPE_initcommoncommands()
            self.files=tuple(np.sort([f for f in os.listdir(self.last_directory) if f.endswith(".corr")]))
            if len(self.files)==0:
                self.show_error_no_files()
            else:
                self.filesbin=tuple(self.files)
                self.update_flist(self.filesbin,None)
                self.anal_file=self.filesbin[0]
                self.mount_tables()
                self.load_data(self.new_directory,self.anal_file)
                self.plot_scater(self.df,'callback_directory_select')
                _FCSDATATYPE_dpgconfig()
        elif self.FCS_data_type == '3C':
            self.files=()
            self.files3=()
            _FCSDATATYPE_initcommoncommands()
            self.files=tuple(np.sort([f for f in os.listdir(self.last_directory) if f.endswith(".dat")]))
            if len(self.files)==0:
                self.show_error_no_files()
            else:
                f3=[]
                for f in self.files:
                    f_path=os.path.join(self.new_directory,f)
                    cnt,testdf = self.count_skiprows(f_path)
                    if len(testdf.columns) == 3:
                        f3.append(f)
                self.files3=tuple(f3)
                self.update_flist(self.files3,None)
                self.anal_file=self.files3[0]
                self.mount_tables()
                self.load_data(self.new_directory,self.anal_file)
                self.plot_scater(self.df,'callback_directory_select')
                _FCSDATATYPE_dpgconfig()

        elif self.FCS_data_type == '2C':   
            self.files=()
            self.files2=()
            _FCSDATATYPE_initcommoncommands()
            self.csv_files = tuple(np.sort([f for f in os.listdir(self.last_directory) if f.endswith(".csv")]))
            self.files=tuple(np.sort([f for f in os.listdir(self.last_directory) if f.endswith(".dat")]))
            if len(self.files)==0:
                if len(self.csv_files)==0:
                    self.show_error_no_files()
                elif len(self.csv_files)!=0:
                    f2=[]
                    for f in self.csv_files:
                        f_path=os.path.join(self.new_directory,f)
                        cnt,testdf = self.count_skiprows(f_path)
                        if len(testdf.columns) == 2:
                            f2.append(f)
                    self.files2=tuple(f2)
                    self.update_flist(self.files2,None)
                    self.anal_file=self.files2[0]
                    self.mount_tables()
                    self.load_data(self.new_directory,self.anal_file)
                    self.plot_scater(self.df,'callback_directory_select')
                    try:
                        _FCSDATATYPE_dpgconfig()
                    except:
                        pass
                else:
                    self.show_error_no_files()
            else:
                f2=[]
                for f in self.files:
                    f_path=os.path.join(self.new_directory,f)
                    cnt,testdf = self.count_skiprows(f_path)
                    if len(testdf.columns) == 2:
                        f2.append(f)
                self.files2=tuple(f2)
                self.update_flist(self.files2,None)
                self.anal_file=self.files2[0]
                self.mount_tables()
                self.load_data(self.new_directory,self.anal_file)
                self.plot_scater(self.df,'callback_directory_select')
                try:
                    _FCSDATATYPE_dpgconfig()
                except:
                    pass
        elif self.FCS_data_type == 'MC':
            dat_file_path = app_data['file_path_name']
            filename = app_data['file_name'] 
            directory = app_data['current_path']
            if self.curves(directory,filename):
                self.FCS_data_type = '3C'
                self.callback_directory_select('file_dialog_id1', {'file_path_name':self.new_directory})
            else:
                pass
        self.basf.log_last_directory(self.last_directory)
        self.update_default_directory(self.last_directory)
            
    def callback_Open_FCS_data(self,sender,app_data):
        if sender == 'bin_menu_item':
            self.FCS_data_type = 'bin'
            dpg.show_item("file_dialog_id1")
        elif sender == '3C_menu_item':
            self.FCS_data_type = '3C'
            dpg.show_item("file_dialog_id1")
        elif sender == '2C_menu_item':
            self.FCS_data_type = '2C'
            dpg.show_item("file_dialog_id1")
        elif sender == 'MC_menu_item':
            self.FCS_data_type = 'MC'
            dpg.show_item("multi_file_dialog_id")
        elif sender == 'PTU_menu_item':
            pass
        else:
            pass
    
    def define_file_menu_callbacks(self):
        dpg.configure_item('bin_menu_item',callback=self.callback_Open_FCS_data)
        dpg.configure_item('3C_menu_item',callback=self.callback_Open_FCS_data)
        dpg.configure_item('2C_menu_item',callback=self.callback_Open_FCS_data)
        dpg.configure_item('MC_menu_item',callback=self.callback_Open_FCS_data)
        dpg.configure_item('reset_workspace_menu_item',callback=self.callback_reset_workspace)
        dpg.configure_item('reset_workspace_results_menu_item',callback=self.callback_reset_workspace_results)
        
        
    def callback_reset_workspace(self,sender,app_data):
        self.workspace_iso['FILES']={k:'' for k in self.workspace_iso['FILES'].keys()}
        file_box_items = dpg.get_item_configuration('file_box')['items'][0]
        try:
            self.callback_listbox('file_box',file_box_items)
            dpg.configure_item('model_choose',default_value = self.init_model)
            self.callback_models('model_choose',self.init_model)
            self.callback_reset_df_range('Reset_range',None)
            self.unmount_tables()
            self.mount_tables()
            dpg.set_value('Xunits',0.00100000000)
            dpg.set_value('Yunits',1)
        except:
            pass
    def callback_reset_workspace_results(self,sender,app_data):
        self.define_RES_DF()
        self.unmount_tables()
        self.mount_tables()
        dpg.set_value('Xunits',0.00100000000)
        dpg.set_value('Yunits',1)

        
    def mount_fcs_handlers(self):
        dpg.add_key_press_handler(tag ='keyword_handler_fcs',callback=self.callback_fcs_Keyword_key,parent = 'handlers_registry')
        
    
    def callback_fcs_Keyword_key(self,sender, app_data):
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
                        if app_data == self.s_key:
                            check = dpg.is_key_down(self.LAlt_key)
                            if check:
                                self.callback_keep_res_button('keep_results_butt',None)
                            else:
                                pass
                        if app_data == self.d_key:
                            check = dpg.is_key_down(self.LAlt_key)
                            if check:
                                if dpg.get_item_configuration('reset_workspace_menu_item')['enabled']:
                                    self.callback_reset_workspace('reset_workspace_menu_item',None)
                                else:
                                    pass
                            else:
                                pass
                        if app_data == self.return_key:
                            check = dpg.is_key_down(self.ctrl_key)
                            if check:
                                self.callback_fit_button('Fit_button',None)
                            else:
                                pass
                        if app_data == self.Del:
                            self.show_delete_Curve_window()
                    if app_data == self.w_key:
                        check = dpg.is_key_down(self.LAlt_key)
                        if check:
                            self.callback_Open_FCS_data('3C_menu_item',None)
                        else:
                            pass
                    
                    
    def update_default_directory(self, last_directory):
        dpg.configure_item('file_dialog_id1', default_path=last_directory)
        dpg.configure_item('file_dialog_plot_all', default_path=last_directory)
        dpg.configure_item('file_dialog_export', default_path=last_directory)
        dpg.configure_item('multi_file_dialog_id', default_path=last_directory)


    