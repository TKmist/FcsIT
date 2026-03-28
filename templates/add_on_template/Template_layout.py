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

def Template_resizer(sender,app_data):

    ''' The function for resizing the main window and adapting the size of the GUI items. Rename the class as you prefer, but keep the "__resizer" string. '''  
    
    init_resizable_items = []
    cmn_resizable_items = []
    obj_var = [eval('method_init.'+str(m)) for m in vars(method_init)]
    for m in obj_var:
        if type(m) == dict:
            if 'name' in m.keys():
                init_resizable_items.append(m['name'])
        else:
            pass
    obj_var = [eval('method_cmn.'+str(m)) for m in vars(method_cmn)]
    for m in obj_var:
        if type(m) == dict:
            if 'name' in m.keys():
                cmn_resizable_items.append(m['name'])
        else:
            pass    

    ratio = {'width': np.round(app_data[0]/inV.VIEWPORT_prop['width'],4),
             'height': np.round(app_data[1]/inV.VIEWPORT_prop['height'],4)} 
    inV.init_size_ratio = ratio
    forbidden_list = ['self',
                     'size_ratio',
                     'font_size',
                     'last_directory',
                     ]
    temp_inits = method_init.__init__.__code__.co_varnames
    temp_inits = [v for v in temp_inits if v not in forbidden_list]
    temp_inits_values  = {}
    for v in temp_inits:
        temp_inits_values[v] = eval('method_init.'+v)
    method_init.__init__(inV.init_size_ratio,
                         inV.init_left_indent,
                         inV.init_internal_indent,
                         inV.init_right_indent,
                         inV.init_bottom_indent,
                         inV.init_top_indent,
                         inV.init_group_spacer,
                         inV.init_font_size,
                         globalITEMS.last_directory,basf)

    for item in init_resizable_items:
        props =eval('method_init.'+item) 
        if 'width' in props.keys():
            dpg.configure_item(item,width=props['width'])
        if 'height' in props.keys():
            dpg.configure_item(item,height=props['height'])
        if 'pos' in props.keys():
            dpg.configure_item(item,pos=props['pos'])

from Methods.add_on_template.Template_INIT import _Template_init, _Template_common
method_init = _Template_init(inV.init_size_ratio,
                             inV.init_left_indent,
                             inV.init_internal_indent,
                             inV.init_right_indent,
                             inV.init_bottom_indent,
                             inV.init_top_indent,
                             inV.init_group_spacer,
                             inV.init_font_size,
                             globalITEMS.last_directory,basf)

method_cmn = _Template_common( method_init,
                               method_init.size_ratio,
                               method_init.group_spacer,
                               globalITEMS.last_directory,
                               method_init.internal_width_left_panel,
                               basf,
                               menu,
                               globalITEMS
                               )
# method_cmn.mount_TIME_BIN_Corr_handlers()
dpg.set_viewport_resize_callback(Template_resizer)
#########################################################################
'''Windows of the method'''
#########################################################################

with dpg.window(label='',
                width=method_init.window_1['width'],
                height=method_init.window_1['height'],
                pos=method_init.window_1['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='window_1',
                show=True
               ):
    dpg.add_button(tag='new_button',
                   width=method_init.new_button['width'],
                   height=method_init.new_button['height'],
                   label='Button',
                   callback = lambda: dpg.show_item('file_dialog_window_1'))

with dpg.window(label='',
                width=method_init.window_2['width'],
                height=method_init.window_2['height'],
                pos=method_init.window_2['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='window_2',
                show=True
               ):
    pass

with dpg.window(label='',
                width=method_init.window_3['width'],
                height=method_init.window_3['height'],
                pos=method_init.window_3['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='window_3',
                show=True
               ):
    
    pass
globalITEMS.windows.extend(['window_1','window_2','window_3','new_button'])





dpg.add_file_dialog(directory_selector=True,
                    label = 'file_dialog_window_1',
                    width = method_init.file_dialog_window_1['width'],
                    height = method_init.file_dialog_window_1['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_directory_select,
                    cancel_callback=callback_none,
                    tag="file_dialog_window_1",
                    modal=False
                   )
method_cmn.DialWinList = ['file_dialog_window_1']

globalITEMS.windows.extend(method_cmn.DialWinList)

