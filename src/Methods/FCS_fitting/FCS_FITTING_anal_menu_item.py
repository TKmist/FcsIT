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
    
class _FCS_FITTING_mounting_functions:
    def unmount_me(self,fcs_items):
        for item in reversed(fcs_items):
            dpg.delete_item(item)
        dpg.delete_item('keyword_handler_fcs')
        dpg.set_viewport_resize_callback(callback_none)
        self.is_mounted = False
        inV.mounted_method = None        
    def mount_me(self):
        dpg.add_menu_item(label="Open binary .corr files directory",
                  tag='bin_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                         )
        dpg.add_menu_item(label="Open three-column data directory",
                  tag='3C_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                         )
        dpg.add_menu_item(label="Open two-column data directory",
                  tag='2C_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                         )

        dpg.add_menu_item(label="Open multicolumn file",
                  tag='MC_menu_item',
                  parent = 'menu_file_dropout',
                  before = 'menu_item_exit',
                         )
        with dpg.menu(label="Workspace",
                      tag='menu_workspace_dropout',
                      parent="vieport's_menubar",
                      before='menu_analysis_method_dropout'):
            dpg.add_menu_item(label="Reset workspace data  (Alt + d)",
                              enabled=False,
                              tag='reset_workspace_menu_item')
            dpg.add_menu_item(label="Reset workspace only results",
                              enabled=True,
                              tag='reset_workspace_results_menu_item')
            
        globalITEMS.windows.extend(['MC_menu_item',
                                    '2C_menu_item',
                                    '3C_menu_item',
                                    'bin_menu_item',
                                   'menu_workspace_dropout',
                                   'reset_workspace_menu_item',
                                   'reset_workspace_results_menu_item',
                                   ])
        
        
class _FCS_FITTING_menu_functions:
    
    def __init__(self):
        self.is_mounted = False
        self.mnt = _FCS_FITTING_mounting_functions()
    
    def unmnt_evthn(self,items,MTHD_conf):
        for item in reversed(items):
            dpg.delete_item(item)
            
        dpg.delete_item(MTHD_conf['keyword_handler_tag'])
        exec(MTHD_conf['menu_class_func']+'.is_mounted = False')
        dpg.set_viewport_resize_callback(callback_none)
        self.is_mounted = False
        inV.mounted_method = None
        globalITEMS.windows=[]
        
    def callback_FCS_FITTING_menu(self):
        if self.is_mounted:
            self.mnt.unmount_me(globalITEMS.windows)
            globalITEMS.windows=[]
        else:
            if inV.mounted_method != None:
                othm_conf = basf.method_config_dict(inV.mounted_method)
                self.unmnt_evthn(globalITEMS.windows,othm_conf)
            else:
                pass
                
        self.mnt.mount_me()
        self.is_mounted = True
        inV.mounted_method = 'Methods/FCS_fitting'
        path_to_layout = os.path.join('Methods/FCS_fitting',basf.path_to_method_anal_layout('Methods/FCS_fitting'))
        execfile(path_to_layout)
        method_cmn.load_json()
        method_cmn.define_file_menu_callbacks()
        
fcs_manu_F = _FCS_FITTING_menu_functions()
dpg.add_menu_item(label="FCS fitting",
                          parent ='menu_analysis_method_dropout' ,
                          tag='Analysis_submenu_item_FCS_Fitting',
                          callback=fcs_manu_F.callback_FCS_FITTING_menu)

fcs_manu_F.callback_FCS_FITTING_menu()