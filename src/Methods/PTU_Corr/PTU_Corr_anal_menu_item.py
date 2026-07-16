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

class _PTU_Corr_mounting_functions:
    def unmount_me(self,fcs_items):
        for item in reversed(fcs_items):
            dpg.delete_item(item)
        dpg.delete_item('keyword_handler_PTU_Corr')
        dpg.set_viewport_resize_callback(callback_none)
        self.is_mounted = False
        inV.mounted_method = None        
        
    def mount_me(self):
        dpg.add_menu_item(label="Open PTU/PT3 files directory",
                  tag='open_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                         )
        dpg.add_menu_item(label="Forget measurement data",
                  tag='Forget_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                          )
        dpg.add_menu_item(label="Forget all measurements data",
                  tag='ForgetAll_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                          )
        dpg.add_separator(tag ='menu_sep_left_1',parent = 'menu_file_dropout',
                  before = 'menu_item_exit',)
        dpg.add_menu_item(label="Open output directory",
                  tag='Save_corr_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                          )
        dpg.add_separator(tag ='menu_sep_left_2',parent = 'menu_file_dropout',
                  before = 'menu_item_exit',)
            
        globalITEMS.windows.extend(['open_menu_item',
                                    'menu_sep_left_1',
                                    'Save_corr_item',
                                    'menu_sep_left_2',
                                    'Forget_menu_item',
                                    'ForgetAll_menu_item'
                                   ])


class _PTU_Corr_menu_functions:
    def __init__(self):
        self.is_mounted = False
        self.mnt = _PTU_Corr_mounting_functions()
        
    def unmnt_evthn(self,items,MTHD_conf):
        for item in reversed(items):
            dpg.delete_item(item)
        dpg.delete_item(MTHD_conf['keyword_handler_tag'])
        exec(MTHD_conf['menu_class_func']+'.is_mounted = False')
        dpg.set_viewport_resize_callback(callback_none)
        self.is_mounted = False
        inV.mounted_method = None
        globalITEMS.windows=[]
        
        
        
    def callback_PTU_Corr_menu(self):
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
        self.mount_PTU_Corr_windows()
        self.is_mounted = True
        inV.mounted_method = 'Methods/PTU_Corr'
    
    def mount_PTU_Corr_windows(self):
        inV.mounted_method = 'Methods/PTU_Corr'
        path_to_layout = os.path.join('Methods/PTU_Corr',basf.path_to_method_anal_layout('Methods/PTU_Corr'))
        execfile(path_to_layout)
        method_cmn.define_file_menu_callbacks()
        

        
PTU_Corr_manu_F = _PTU_Corr_menu_functions()

dpg.add_menu_item(label="Import PTU/PT3",
                          parent ='menu_analysis_method_dropout' ,
                          tag='Analysis_submenu_item_PTU_Corr',
                          callback=PTU_Corr_manu_F.callback_PTU_Corr_menu)



