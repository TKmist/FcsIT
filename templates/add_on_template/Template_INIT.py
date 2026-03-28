"""
Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)

This file is just a template for add-on methods for FcsIT.

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
import os
import numpy as np
import dearpygui.dearpygui as dpg
import include.INIT as inits

####################################
####################################
'''Here plase all imports required by your method add-on.'''
####################################
####################################

logfile=os.path.join('Logs','log.txt')
bf = inits._basicF(logfile,None)
lprint = bf.lnprint

class _Template_init:  
    '''The class holding the add-on's initial variables. Rename the class as you prefer, but keep the "_init" string. ''' 
    def __init__(self,
                 size_ratio,
                 left_indent,
                 internal_indent,
                 right_indent,
                 bottom_indent,
                 top_indent,
                 group_spacer,
                 font_size,
                 last_directory, bf):
        
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
        
        ''' Definitions of the layout elements. Rename objects' names according to your preference. '''
        
        self.window_1 = {'name':'window_1',
                            'width':int(340*self.size_ratio['width']),
                            'height':dpg.get_viewport_height()-4*self.bottom_indent,
                            'pos':(self.left_indent,self.top_indent)
                            }
        self.window_2 = {'name':'window_2',
                            'width':dpg.get_viewport_width()-self.left_indent-self.window_1['width']-self.internal_indent-self.right_indent,
                            'height':int(300*self.size_ratio['height']),
                            'pos':(self.window_1['pos'][0]+self.window_1['width']+self.internal_indent,
                                  self.top_indent)
                            }
        self.window_3 = {'name':'window_3',
                            'width':dpg.get_viewport_width()-self.left_indent-self.window_1['width']-self.internal_indent-self.right_indent,
                            'height':self.window_1['height']-self.internal_indent-self.window_2['height'],
                            'pos':(self.window_1['pos'][0]+self.window_1['width']+self.internal_indent,
                                  self.window_2['pos'][1]+self.window_2['height']+self.internal_indent)
                            }
        self.file_dialog_window_1 = {'name':'file_dialog_window_1',
                               'width':int(dpg.get_viewport_width())-11*self.left_indent,
                               'height':int(dpg.get_viewport_height()*3/4)
                              }
        self.new_button = {'name':'new_button',
                               'width':-1,
                               'height':int(40*self.size_ratio['height'])
                              }
        
        self.internal_width_left_panel = int(self.window_1['width']-self.internal_indent-self.group_spacer*3)
        
        
class _Template_common:  
    '''The main working class of the add-on.  Rename the class as you prefer, but keep the "_common" string.  '''
    def __init__(self,
                 INIT,
                 size_ratio,
                 group_spacer,
                 last_directory,
                 internal_width_left_panel,
                 basf,
                 menu,
                 globalITEMS
                 ):
        self.basf=basf
        self.method_init=INIT
        self.last_directory=last_directory
        self.DialWinLis = []

    ''' Here, define all variables related to the GUI items and variables related to the backend of your add-on. '''
        
    #########################################################################           
    #########################################################################           
    #########################################################################   

    """ Here, place all callbacks and functions related to your add-on. """
    

    
    def callback_directory_select(self, sender, app_data):
        self.last_directory = app_data['current_path']
        self.update_default_directory(self.last_directory)


    def update_default_directory(self, last_directory):
        self.basf.log_last_directory(last_directory)
        for dw in self.DialWinLis:
            dpg.configure_item(dw, default_path=last_directory)
    def define_file_menu_callbacks(self):
        ''' Define callbacs for your submenu items '''
        pass
        # dpg.configure_item('AC_menu_item',callback=self.callback_Open_TT_data)
        # dpg.configure_item('Save_corr_item',callback=lambda: dpg.show_item('file_dialog_save_correlated'))
        # dpg.configure_item('Forget_menu_item',callback=self.callback_Forget_PTU_data)
        # dpg.configure_item('ForgetAll_menu_item',callback=self.callback_Forget_all_PTU_data)
    
    #########################################################################           
    #########################################################################           
    #########################################################################   
            
    
  
                    

        
