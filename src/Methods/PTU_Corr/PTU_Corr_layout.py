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

def PTU_Corr_resizer(sender,app_data):
    print('PTU_Corr_resizer - resizing')
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
                     'last_directory'
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
                         globalITEMS.last_directory)
    
    for item in init_resizable_items:
        props =eval('method_init.'+item) 
        if 'width' in props.keys():
            dpg.configure_item(item,width=props['width'])
        if 'height' in props.keys():
            dpg.configure_item(item,height=props['height'])
        if 'pos' in props.keys():
            dpg.configure_item(item,pos=props['pos'])

from Methods.PTU_Corr.PTU_Corr_INIT import _PTU_Corr_init, _PTU_Corr_common


method_init = _PTU_Corr_init(inV.init_size_ratio,
                             inV.init_left_indent,
                             inV.init_internal_indent,
                             inV.init_right_indent,
                             inV.init_bottom_indent,
                             inV.init_top_indent,
                             inV.init_group_spacer,
                             inV.init_font_size,
                             basf.recall_last_directory())


method_cmn = _PTU_Corr_common(method_init,
                              basf.recall_last_directory(),
                              basf,
                              menu,
                              globalITEMS,
                                      
                                    )
method_cmn.mount_PTU_Corr_handlers()
dpg.set_viewport_resize_callback(PTU_Corr_resizer)


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
                width=method_init.Anal_window['width'],
                height=method_init.Anal_window['height'],
                pos=method_init.Anal_window['pos'],
                no_move=True,
                no_close=True,
                no_title_bar=True,
                no_resize=True,
                tag='Anal_window',
                show=True
               ):
    with dpg.tab_bar(tag='Anal_window_tab_bar',callback=method_cmn.tab_callback):
        with dpg.tab(label="TCPSC",tag = 'Anal_window_TCSPC_tab',user_data=True):
            pass

        
        with dpg.tab(label="Correlation",tag = 'Anal_window_Correlation_tab',user_data=False):
            pass

            
globalITEMS.windows.extend(['file_window',
                            'TT_window',
                            'Anal_window',
                            'Anal_window_tab_bar',
                            'Anal_window_TCSPC_tab',
                            'Anal_window_Correlation_tab',
                           ])




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
                            format='Time bin = %.E [s]',
                            callback = method_cmn.callback_left_panel_drag_time_binning,
                            min_value = 1e-5,
                            on_enter=True
                            )
        dpg.add_drag_int(tag='left_panel_drag_subs',
                         width = method_init.left_panel_drag_subs['width'],
                         default_value=method_init.left_panel_drag_subs['default_value'],
                         speed = method_init.left_panel_drag_subs['speed'],
                         format='Npoints = %i',
                         enabled=True,
                         min_value = 2,
                         )
    with dpg.table_row(tag='left_panel_tab_1_row_2'):
        dpg.add_drag_int(tag='left_panel_N_chunks',
                         width = method_init.left_panel_N_chunks['width'],
                         default_value=method_init.left_panel_N_chunks['default_value'],
                         speed = method_init.left_panel_N_chunks['speed'],
                         format='Nchunks = %i',
                         enabled=True,
                         min_value = 1
                         )
        with dpg.item_handler_registry(tag="left_panel_N_chunks_handlers"):
            dpg.add_item_deactivated_after_edit_handler(callback=method_cmn.on_chunks_released)
        dpg.bind_item_handler_registry("left_panel_N_chunks", "left_panel_N_chunks_handlers")
        dpg.add_checkbox(label="Custom chunks",
                         tag='Custom_chunks_check',
                         default_value = method_init.Custom_chunks_check['default_value'],
                         enabled=True,
                         callback=method_cmn.show_chunks_drag_lines
                        )
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
    with dpg.table_row(tag='left_panel_tab_1_row_4'):
        dpg.add_text("",tag='left_panel_tab_1_row_4_cntr_text_ch_0')
        dpg.add_text("",tag='left_panel_tab_1_row_4_cntr_text_ch_1')
dpg.add_separator(tag ='sep_left_3',parent='file_window')
dpg.add_button(label="Calculate filter",
               tag='Calculate_filter_once_button',
               parent = 'file_window',
               width = method_cmn.method_init.Calculate_filter_once_button['width'],
               callback=method_cmn.callback_calc_fltr_one,
               enabled=False,
               show=True
               )
with dpg.tooltip('Calculate_filter_once_button',tag='Calculate_filter_once_button_tooltip'):
    dpg.add_text('Calculate TCSPC filters for single file. Press even if no filters are used.',tag='Calculate_filter_once_button_tooltip_text')
    
    
dpg.bind_item_theme('Calculate_filter_once_button', 'fit_button_theme')

dpg.add_button(label="Calculate filter for all",
               tag='Calculate_filter_all_button',
               parent = 'file_window',
               width = method_cmn.method_init.Calculate_filter_all_button['width'],
               callback=method_cmn.callback_calc_fltr_all,
               enabled=False,
               show=True
               )
with dpg.tooltip('Calculate_filter_all_button',tag='Calculate_filter_all_button_tooltip'):
    dpg.add_text('Calculate TCSPC filters for all files. Press even if no filters are used.',tag='Calculate_filter_all_button_tooltip_text')
    
    
dpg.bind_item_theme('Calculate_filter_all_button', 'fit_button_theme')

dpg.add_separator(tag ='sep_left_but_1',parent='file_window')
dpg.add_button(label="Calculate correlation",
               tag='Calculate_correlation_once_button',
               parent = 'file_window',
               width = method_cmn.method_init.Calculate_correlation_once_button['width'],
               callback=method_cmn.callback_calc_corr_one,
               enabled=False,
               show=True
               )
with dpg.tooltip('Calculate_correlation_once_button',tag='Calculate_correlation_once_button_tooltip'):
    dpg.add_text('Calculate correlation for single file.',tag='Calculate_correlation_button_tooltip_text')
    
    
dpg.bind_item_theme('Calculate_correlation_once_button', 'fit_button_theme')

dpg.add_button(label="Calculate correaltion for all",
               tag='Calculate_correlation_all_button',
               parent = 'file_window',
               width = method_cmn.method_init.Calculate_correlation_all_button['width'],
               callback=method_cmn.callback_calc_corr_all,
               enabled=False,
               show=True
               )
with dpg.tooltip('Calculate_correlation_all_button',tag='Calculate_correlation_all_button_tooltip'):
    dpg.add_text('Calculate correlation for all files.',tag='Calculate_correlation_all_button_tooltip_text')
    
dpg.bind_item_theme('Calculate_correlation_all_button', 'fit_button_theme')

dpg.add_separator(tag ='sep_left_but_2',parent='file_window')


with dpg.table(header_row=False,
               tag='left_panel_tab_2',
               width=method_init.left_panel_tab_2['width'],
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
    dpg.add_table_column(tag='left_panel_tab_2_col_1',width=method_init.left_panel_tab_2_col_1['width'])
    dpg.add_table_column(tag='left_panel_tab_2_col_2',width=method_init.left_panel_tab_2_col_2['width'])
    with dpg.table_row(tag='left_panel_tab_2_row_1'):
        dpg.add_button(label="Export one curve (.dat)",
                       tag='Export_correlation_curve_button',
                       width = method_cmn.method_init.Export_correlation_curve_button['width'],
                       callback=method_cmn.callback_Export_correlation_curve_button,
                       enabled=False,
                       show=True
                       )
        with dpg.tooltip('Export_correlation_curve_button',tag='Export_correlation_curve_button_tooltip'):
            dpg.add_text('Export single correlation curve to .dat file.',tag='Export_correlation_curve_button_tooltip_text')
            
        dpg.bind_item_theme('Export_correlation_curve_button', 'fit_button_theme')
        dpg.add_button(label="Export all curves (.dat)",
                       tag='Export_all_correlation_curves_button',
                       width = method_cmn.method_init.Export_all_correlation_curves_button['width'],
                       callback=method_cmn.callback_Export_correlation_curve_button,
                       enabled=False,
                       show=True
                       )
        with dpg.tooltip('Export_all_correlation_curves_button',tag='Export_all_correlation_curves_button_tooltip'):
            dpg.add_text('Export all correlation curves to .dat files.',
                         tag='Export_all_correlation_curves_button_tooltip_text')
    
    
        dpg.bind_item_theme('Export_all_correlation_curves_button', 'fit_button_theme')

    with dpg.table_row(tag='left_panel_tab_2_row_2'):
        dpg.add_button(label="Export one curve (.corr)",
                       tag='Export_correlation_curve_binary_button',
                       width = method_cmn.method_init.Export_correlation_curve_button['width'],
                       callback=method_cmn.callback_Export_correlation_curve_binary_button,
                       enabled=False,
                       show=True
                       )
        with dpg.tooltip('Export_correlation_curve_binary_button',tag='Export_correlation_curve_binary_tooltip'):
            dpg.add_text('Export single correlation curve to .corr file. This is a binary file containing the correlation data and brightness.',
                         tag='Export_correlation_curve_binary_button_tooltip_text')
            
            
        dpg.bind_item_theme('Export_correlation_curve_binary_button', 'fit_button_theme')
        dpg.add_button(label="Export all curves (.corr)",
                       tag='Export_all_correlation_curves_binary_button',
                       width = method_cmn.method_init.Export_all_correlation_curves_button['width'],
                       callback=method_cmn.callback_Export_correlation_curve_binary_button,
                       enabled=False,
                       show=True
                       )
        with dpg.tooltip('Export_all_correlation_curves_binary_button',tag='Export_all_correlation_curves_binary_button_tooltip'):
            dpg.add_text('Export all correlation curves to .corr files. This is a binary file containing the correlation data and brightness.',
                         tag='Export_all_correlation_curves_binary_button_tooltip_text')
    
    
        dpg.bind_item_theme('Export_all_correlation_curves_binary_button', 'fit_button_theme')



                           
globalITEMS.windows.extend(['FILES_window_text_title',
                            'sep_left_1',
                            'file_box',
                            'left_panel_tab_1',
                            'left_panel_tab_1_col_1',
                            'left_panel_tab_1_col_2',
                            'left_panel_tab_1_row_1',
                            'sep_left_2',
                            'left_panel_drag_time_binning',
                            'left_panel_drag_subs',
                            'left_panel_tab_1_row_2',
                            'left_panel_N_chunks',
                            'left_panel_N_chunks_handlers',
                            'Custom_chunks_check',
                            'Custom_chunks_check_tooltip',
                            'Custom_chunks_check_tooltip_text',
                            'left_panel_tab_1_row_3',
                            'left_panel_tau_min',
                            'left_panel_tau_max',
                            'left_panel_tab_1_row_4',
                            'left_panel_tab_1_row_4_cntr_text_ch_0',
                            'left_panel_tab_1_row_4_cntr_text_ch_0',
                            'sep_left_3',
                            'Calculate_filter_once_button_tooltip_text',
                            'Calculate_filter_once_button_tooltip',
                            'Calculate_filter_once_button',
                            'Calculate_filter_all_button_tooltip_text',
                            'Calculate_filter_all_button_tooltip',
                            'Calculate_filter_all_button',
                            'Calculate_correlation_once_button_tooltip_text',
                            'Calculate_correlation_once_button_tooltip',
                            'Calculate_correlation_once_button',
                            'Calculate_correlation_all_button_tooltip_text',
                            'Calculate_correlation_all_button_tooltip',
                            'Calculate_correlation_all_button',
                            'Export_correlation_curve_button_tooltip_text',
                            'Export_correlation_curve_button_tooltip',
                            'Export_correlation_curve_button',
                            'Export_all_correlation_curves_button_tooltip_text',
                            'Export_all_correlation_curves_button_tooltip',
                            'Export_all_correlation_curves_button',
                            'sep_left_but_1',
                            'sep_left_but_2',
                            'left_panel_tab_2',
                            'left_panel_tab_2_row_1',
                            'Export_correlation_curve_binary_button_tooltip_text',
                            'Export_correlation_curve_binary_button_tooltip',
                            'Export_correlation_curve_binary_button',
                            'Export_all_correlation_curves_binary_button_tooltip_text',
                            'Export_all_correlation_curves_binary_button_tooltip',
                            'Export_all_correlation_curves_binary_button',
                            ])



dpg.add_file_dialog(directory_selector=True,
                    label = 'Select working directory',
                    width = method_init.file_dialog_id_PTU['width'],
                    height = method_init.file_dialog_id_PTU['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_directory_select,
                    cancel_callback=callback_none,
                    tag="file_dialog_id_PTU",
                    modal=False
                   )



with dpg.file_dialog(directory_selector=True,
                    label = 'Select directory to save correlated files',
                    width = method_init.file_dialog_save_correlated['width'],
                    height = method_init.file_dialog_save_correlated['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_export_correlation,
                    cancel_callback=callback_none,
                    tag="file_dialog_save_correlated",
                    modal=False
                   ):
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension("{.dat,.corr}")
    dpg.add_file_extension(".dat", color=(255, 0, 255, 255), custom_text="[DAT]")
    dpg.add_file_extension(".corr", color=(0, 255, 0, 255), custom_text="[CORR]")
    




method_cmn.DialWinList = ['file_dialog_id_PTU',
                          'file_dialog_save_correlated']


globalITEMS.windows.extend(method_cmn.DialWinList)

with dpg.subplots(method_init.TT_subplots['rows'],
                  method_init.TT_subplots['columns'],
                  height=method_init.TT_subplots['height'],
                  width=method_init.TT_subplots['width'],
                  row_ratios=method_init.TT_subplots['row_ratios'],
                  link_all_x=True,
                  tag='TT_subplots',
                  show=True,
                  parent='TT_window'):
    pass
dpg.add_group(tag='TCSPC_checks_group',
              show=True,
              horizontal=True,
              horizontal_spacing=method_init.group_spacer,
              parent='Anal_window_TCSPC_tab')

dpg.add_button(label="Update TCSPC histogram",
               tag='Update_TCSPC_histogram',
               width = method_cmn.method_init.Update_TCSPC_histogram['width'],
               callback=method_cmn.call_back_update_TCSPC,
               enabled=False,
               parent = 'TCSPC_checks_group',
               show=True
               )
with dpg.tooltip('Update_TCSPC_histogram',tag='Update_TCSPC_histogram_tooltip'):
    dpg.add_text('Update the TCSPC histogram after changing the timtrace data.',
                 tag='Update_TCSPC_histogram_tooltip_text')
    
    
dpg.bind_item_theme('Update_TCSPC_histogram', 'fit_button_theme')
dpg.add_checkbox(tag='TCSPC_timegate_check',
                 default_value=True,
                 show=True,
                 label='Use time-gating',
                 parent='TCSPC_checks_group',
                 callback=method_cmn.callback_tcspc_timegate
                 )
dpg.add_checkbox(tag='TCSPC_BG_correction_check',
                 default_value=False,
                 show=True,
                 label='TCSPC background filtering',
                 parent='TCSPC_checks_group',
                 callback=method_cmn.callback_tcspc_BG
                 )
with dpg.subplots(method_init.TCSPC_subplots['rows'],
                  method_init.TCSPC_subplots['columns'],
                  height=method_init.TCSPC_subplots['height'],
                  width=method_init.TCSPC_subplots['width'],
                  column_ratios=method_init.TCSPC_subplots['column_ratios'],
                  link_all_x=True,
                  tag='TCSPC_subplots',
                  show=True,
                  parent='Anal_window_TCSPC_tab'):
    pass



dpg.add_group(tag='FCS_checks_group',
              show=True,
              horizontal=True,
              horizontal_spacing=method_init.group_spacer,
              parent='Anal_window_Correlation_tab')

    
dpg.add_checkbox(tag='FCS_cross_check',
                 default_value=False,
                 show=False,
                 label='Crosscorrelate',
                 parent='FCS_checks_group',
                 callback=method_cmn.callback_crossCorr_check
                 )

with dpg.subplots(method_init.FCS_subplots['rows'],
                  method_init.FCS_subplots['columns'],
                  height=method_init.FCS_subplots['height'],
                  width=method_init.FCS_subplots['width'],
                  column_ratios=method_init.FCS_subplots['column_ratios'],
                  link_all_x=True,
                  tag='FCS_subplots',
                  show=True,
                  parent='Anal_window_Correlation_tab'):
    pass
globalITEMS.windows.extend(['TT_subplots',
                            'TCSPC_subplots',
                            'TCSPC_checks_group',
                            'TCSPC_timegate_check',
                            'TCSPC_BG_correction_check',
                            'Update_TCSPC_histogram',
                            'Update_TCSPC_histogram_tooltip',
                            'Update_TCSPC_histogram_tooltip_text',
                            'FCS_subplots',
                            'FCS_checks_group',
                            'FCS_cross_check'])
method_cmn.load_TT_plots()
method_cmn.load_TCSPC_plots()
method_cmn.load_FCS_plots()

