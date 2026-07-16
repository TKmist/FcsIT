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

def TB_Corr_resizer(sender,app_data):
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

from Methods.TIME_BIN_Corr.TIME_BIN_Corr_INIT import _TB_corr_init, _TB_corr_common
method_init = _TB_corr_init(inV.init_size_ratio,
                             inV.init_left_indent,
                             inV.init_internal_indent,
                             inV.init_right_indent,
                             inV.init_bottom_indent,
                             inV.init_top_indent,
                             inV.init_group_spacer,
                             inV.init_font_size,
                             globalITEMS.last_directory,basf)

method_cmn = _TB_corr_common( method_init,method_init.size_ratio,
                                     method_init.group_spacer,
                                     globalITEMS.last_directory,
                                     method_init.internal_width_left_panel,
                                     method_init.left_panel_drag_time_binning,
                                     basf,
                                     menu,
                                     globalITEMS
                                    )
method_cmn.mount_TIME_BIN_Corr_handlers()
dpg.set_viewport_resize_callback(TB_Corr_resizer)
#########################################################################
'''Main windows of the method'''
#########################################################################

with dpg.window(label='',
                width=method_init.file_window['width'],
                height=method_init.file_window['height'],
                pos=method_init.file_window['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='file_window',
                show=True
               ):
    pass

with dpg.window(label='',
                width=method_init.TT_window['width'],
                height=method_init.TT_window['height'],
                pos=method_init.TT_window['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='TT_window',
                show=True
               ):
    pass

with dpg.window(label='',
                width=method_init.ACF_window['width'],
                height=method_init.ACF_window['height'],
                pos=method_init.ACF_window['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='ACF_window',
                show=True
               ):
    dpg.add_checkbox(tag='FCS_cross_check',
                 default_value=False,
                 show=False,
                 label='Crosscorrelate',
                 parent='ACF_window',
                callback=method_cmn.callback_crossCorr_check
                )

globalITEMS.windows.extend(['file_window','TT_window','ACF_window','FCS_cross_check'])

#########################################################################
'''Items in the left panel'''
#########################################################################

dpg.add_text('FILES',tag='FILES_window_text_title',parent='file_window')
dpg.add_separator(tag ='sep_left_1',parent='file_window')
'''Window containing file selection panel.'''
list_box = dpg.add_listbox(items=method_cmn.files,
                           width=method_init.file_box['width'],
                           num_items=method_init.file_box['num_items'],
                           tag='file_box',
                           parent='file_window',
                           callback=method_cmn.callback_listbox
                           )

dpg.add_separator(tag ='sep_left_2',parent='file_window')
with dpg.table(header_row=False,
               tag='left_panel_tab_1',
               width=method_init.left_panel_tab_1['width'],
               borders_innerH=False, 
               borders_outerH=False, 
               borders_innerV=False, 
               borders_outerV=False,
               no_pad_innerX=False,
               no_pad_outerX=True,
               no_host_extendX=True,
               no_clip=True, 
               policy=dpg.mvTable_SizingStretchSame,
               parent='file_window'):
    dpg.add_table_column(tag='left_panel_tab_1_col_1',width=method_init.left_panel_tab_1_col_1['width'])
    dpg.add_table_column(tag='left_panel_tab_1_col_2',width=method_init.left_panel_tab_1_col_2['width'])
    with dpg.table_row(tag='left_panel_tab_1_row_1'):
        dpg.add_input_float(tag='left_panel_drag_time_binning', 
                            width = method_init.left_panel_drag_time_binning['width'],
                            default_value=method_init.left_panel_drag_time_binning['default_time_bin'],
                            step=0,
                            format='Binning = %.E [s]',
                            callback = method_cmn.callback_left_panel_drag_time_binning,
                            min_value = 1e-12,
                            on_enter=True
                            )
        dpg.add_drag_int(tag='left_panel_drag_subs',
                         width = method_init.left_panel_drag_subs['width'],
                         default_value=method_init.left_panel_drag_subs['default_value'],
                         speed = method_init.left_panel_drag_subs['speed'],
                         format='Npoints = %i',
                         min_value = 2,
                         max_value = 1000,
                         )
    with dpg.table_row(tag='left_panel_tab_1_row_2'):
        dpg.add_drag_int(tag='left_panel_N_chunks',
                         width = method_init.left_panel_N_chunks['width'],
                         default_value=method_init.left_panel_N_chunks['default_value'],
                         speed = method_init.left_panel_N_chunks['speed'],
                         format='Nchunks = %i',
                         min_value = 1,
                         )
        with dpg.item_handler_registry(tag="left_panel_N_chunks_handlers"):
            dpg.add_item_deactivated_after_edit_handler(callback=method_cmn.on_chunks_released)
        dpg.bind_item_handler_registry("left_panel_N_chunks", "left_panel_N_chunks_handlers")
        dpg.add_checkbox(label="Custom chunks",
                         tag='Custom_chunks_check',
                         default_value = method_init.Custom_chunks_check['default_value'],
                         callback=method_cmn.show_chunks_drag_lines)
        with dpg.tooltip('Custom_chunks_check',tag='Custom_chunks_check_tooltip'):
            dpg.add_text("If unchecked the chunks are equaly distributed. Check to set the chunks manualy.",tag='Custom_chunks_check_tooltip_text')
    with dpg.table_row(tag='left_panel_tab_1_row_3'):
        dpg.add_drag_float(tag='left_panel_tau_min',
                           width = method_init.left_panel_tau_min['width'],
                           default_value=method_init.left_panel_tau_min['default_value'],
                           speed = method_init.left_panel_tau_min['speed'],
                           format='\u03C4'+' (min)  [ms] = %.4f',
                           enabled=True,
                           min_value = 1e-4,
                           )

        dpg.add_drag_float(tag='left_panel_tau_max',
                           width = method_init.left_panel_tau_max['width'],
                           default_value=method_init.left_panel_tau_max['default_value'],
                           speed = method_init.left_panel_tau_max['speed'],
                           format='\u03C4'+' (max)  [ms] = %.f',
                           enabled=True,
                           min_value = 10,
                           max_value = 1e5,
                           )

dpg.add_separator(tag ='sep_left_3',parent='file_window')          
dpg.add_button(label="Calculate correlation once",
               tag='Correlate_once_button',
               parent = 'file_window',
               width = method_init.Correlate_once_button['width'],
               enabled=False
               )
with dpg.tooltip('Correlate_once_button',tag='Correlate_once_button_tooltip'):
    dpg.add_text('This button is enabled only if the output directory is defined. Open "File" -> "Open output directory"',
                 tag='Correlate_once_button_tooltip_text')
    
dpg.bind_item_theme('Correlate_once_button', 'fit_button_theme') 
dpg.add_button(label="Calculate correlation all",
               tag='Correlate_all_button',
               parent = 'file_window',
               width = method_init.Correlate_all_button['width'],
               callback=method_cmn.correlate_all,
               enabled=False
               )
with dpg.tooltip('Correlate_all_button',tag='Correlate_all_button_tooltip'):
    dpg.add_text('This button is enabled only if the output directory is defined. Open "File" -> "Open output directory"',
                 tag='Correlate_all_button_tooltip_text')
dpg.bind_item_theme('Correlate_all_button', 'fit_button_theme') 
                           
globalITEMS.windows.extend(['FILES_window_text_title',
                            'sep_left_1',
                            'file_box',
                           'left_panel_tab_1',
                           'left_panel_tab_1_col_1',
                           'left_panel_tab_1_col_2',
                           'left_panel_tab_1_row_1',
                            'left_panel_tab_1_row_2',
                            'sep_left_2',
                           'left_panel_drag_time_binning',
                            'left_panel_drag_subs',
                            'left_panel_N_chunks',
                            'left_panel_N_chunks_handlers',
                            'Custom_chunks_check',
                            'Custom_chunks_check_tooltip',
                            'Custom_chunks_check_tooltip_text',
                            'left_panel_tau_min',
                            'left_panel_tau_max',
                            'Correlate_once_button',
                            'Correlate_all_button',
                            'Correlate_once_button_tooltip',
                            'Correlate_once_button_tooltip_text',
                            'Correlate_all_button_tooltip',
                            'Correlate_all_button_tooltip_text',
                           'sep_left_3',
                           ])



dpg.add_file_dialog(directory_selector=True,
                    label = 'Select working directory',
                    width = method_init.file_dialog_id_TB['width'],
                    height = method_init.file_dialog_id_TB['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_directory_select,
                    cancel_callback=callback_none,
                    tag="file_dialog_id_TB",
                    modal=False
                   )


dpg.add_file_dialog(directory_selector=True,
                    label = 'Select directory to save correlated files',
                    width = method_init.file_dialog_save_correlated['width'],
                    height = method_init.file_dialog_save_correlated['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_save_path,
                    cancel_callback=callback_none,
                    tag="file_dialog_save_correlated",
                    modal=False
                   )
method_cmn.DialWinList = ['file_dialog_save_correlated',
                          'file_dialog_id_TB']

globalITEMS.windows.extend(method_cmn.DialWinList)



with dpg.subplots(method_init.subplots['rows'],
                  method_init.subplots['columns'],
                  height=method_init.subplots['height'],
                  width=method_init.subplots['width'],
                  row_ratios=method_init.subplots['row_ratios'],
                  link_all_x=True,
                  tag='subplots',
                  show=True,
                  parent='TT_window'):
    pass
globalITEMS.windows.extend(['subplots'])
method_cmn.load_TT_plots()

with dpg.subplots(method_init.FCS_subplots['rows'],
                  method_init.FCS_subplots['columns'],
                  height=method_init.FCS_subplots['height'],
                  width=method_init.FCS_subplots['width'],
                  row_ratios=method_init.subplots['row_ratios'],
                  link_all_x=True,
                  tag=method_init.FCS_subplots['name'],
                  show=True,
                  parent='ACF_window'):
    pass

globalITEMS.windows.extend(['FCS_subplots'])
method_cmn.load_FCS_plots()