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

class _Template_mounting_functions:
    '''Class containing all functions for mounting this your add-on and unmounting the other add-ons'''
    def unmount_me(self,items):
        ''' Unmount different method '''
        
        for item in reversed(items):
            dpg.delete_item(item)
        
        dpg.set_viewport_resize_callback(callback_none)
        
        self.is_mounted = False
        inV.mounted_method = None        
    def mount_me(self):

        ''' Mount your method '''

        '''add menu items'''
        dpg.add_menu_item(label="Template item",
                  tag='Template_item',
                  parent = 'menu_dropout',
                  before = 'menu_item_exit',
                         )

            
        globalITEMS.windows.extend(['Template_item'])


class _Template_menu_functions:

    ''' This class holds the functions and methods related to the menu. '''
    
    def __init__(self):
        self.is_mounted = False
        self.mnt = _Template_mounting_functions()

    
    def unmnt_evthn(self,items,MTHD_conf):
        for item in reversed(items):
            dpg.delete_item(item)
            
        dpg.delete_item(MTHD_conf['keyword_handler_tag'])
        exec(MTHD_conf['menu_class_func']+'.is_mounted = False')
        
        dpg.set_viewport_resize_callback(callback_none)
        
        self.is_mounted = False
        inV.mounted_method = None
        
        globalITEMS.windows=[]
        
        
        
    def callback_Template_menu(self):
        if self.is_mounted:
            othm_conf = basf.method_config_dict(inV.mounted_method)
            self.unmnt_evthn(globalITEMS.windows,othm_conf)
        else:
            if inV.mounted_method != None:
                othm_conf = basf.method_config_dict(inV.mounted_method)
                self.unmnt_evthn(globalITEMS.windows,othm_conf)
            else:
                pass
                
        self.mnt.mount_me()
        self.mount_Template_windows()
        self.is_mounted = True
        inV.mounted_method = os.path.join('Methods','add_on_template')
        
    def mount_Template_windows(self):
        inV.mounted_method = os.path.join('Methods','add_on_template')
        path_to_layout = os.path.join(inV.mounted_method,basf.path_to_method_anal_layout(inV.mounted_method))
        execfile(path_to_layout)
        method_cmn.define_file_menu_callbacks()
        
        
Template_menu_F = _Template_menu_functions()

dpg.add_menu_item(label="Add_on_tempplate",
                          parent ='menu_analysis_method_dropout' ,
                          tag='Analysis_submenu_item_Template',
                          callback=Template_menu_F.callback_Template_menu)


# Template_menu_F.callback_Template_menu()