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
import sys
def resizer(sender,app_data):
    init_resizable_items = []
    cmn_resizable_items = []
    init_forbiden_list = ['Add_model_window',
                         'Close_Add_model_button',
                         'Save_model_button',
                         'model_input_name',
                         'model_input_describe',
                         'model_input_text1',
                         'model_input_variables']
    obj_var = [eval('method_init.'+str(m)) for m in vars(method_init)]
    for m in obj_var:
        if type(m) == dict:
            if 'name' in m.keys() and not m['name'] in init_forbiden_list:
                if not m['name'] == 'image_id1':
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
                     'Add_model_window'
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
    

dpg.set_viewport_resize_callback(resizer)

from Methods.FCS_fitting.FCS_FITTING_INIT import _FCS_Fitting_init, _FCS_Fitting_vars_funct

method_init = _FCS_Fitting_init(inV.init_size_ratio,
                             inV.init_left_indent,
                             inV.init_internal_indent,
                             inV.init_right_indent,
                             inV.init_bottom_indent,
                             inV.init_top_indent,
                             inV.init_group_spacer,
                             inV.init_font_size,
                             basf.recall_last_directory())
method_cmn = _FCS_Fitting_vars_funct(method_init.size_ratio,
                                     method_init.group_spacer,
                                     method_init.image_1['width'],
                                     method_init.image_1['height'],
                                     basf.recall_last_directory(),
                                     method_init.internal_width_left_panel,
                                     method_init.internal_width_middle_panel,
                                     basf
                                    )
method_cmn.mount_fcs_handlers()

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

with dpg.window(tag="Model_selection_panel",
                    width=method_init.Model_selection_panel['width'],
                height=method_init.Model_selection_panel['height'],
                pos=method_init.Model_selection_panel['pos'],
                    no_move=True,
                    no_close=True,
                    no_title_bar=True,
                    no_resize=True,
                    show=True
                   ):
    pass

with dpg.window(label='Error Messages',tag="comm_window",
                    width=method_init.comm_window['width'],
                height=method_init.comm_window['height'],
                pos=method_init.comm_window['pos'],
                
                    no_close=True,
                    no_move=True,
                    no_collapse=True,
                    no_title_bar=False,
                    no_resize=True,
                    show=True

                   ):
    
    dpg.add_listbox(items=method_init.comm_box['items'],
                    width=method_init.comm_box['width'],
                    num_items=method_init.comm_box['num_items'],
                    tag='comm_box',
                    parent='comm_window',
                    callback = method_cmn.callback_comm_box
                    )

with dpg.window(label = "",
                    tag = "plot_win",
                    width=method_init.plot_win['width'],
                height=method_init.plot_win['height'],
                pos=method_init.plot_win['pos'],
                    no_move = True,
                    no_close = True,
                    no_title_bar = True,
                    no_resize = True,
                    show = True
                   ):
    pass


globalITEMS.windows.extend(['file_window',
                            'Model_selection_panel',
                            'comm_window',
                            'plot_win',
                            'comm_box']
                          )

#########################################################################
'''Dialogue windows of the method'''
#########################################################################

dpg.add_file_dialog(directory_selector=True,
                    label = 'Select working directory',
                    width = method_init.file_dialog_id1['width'],
                    height = method_init.file_dialog_id1['height'],
                    show=False,
                    file_count=2,
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_directory_select,
                    cancel_callback=callback_none,
                    tag="file_dialog_id1",
                    modal=False
                   )
with dpg.file_dialog(directory_selector=False,
                    label = 'Select multicolumn file',
                    width = method_init.multi_file_dialog_id['width'],
                    height = method_init.multi_file_dialog_id['height'],
                    show=False,
                    file_count=5,
                    default_filename ='*',
                    default_path=method_cmn.last_directory,
                    callback=method_cmn.callback_directory_select,
                    cancel_callback=callback_none,
                    tag="multi_file_dialog_id",
                    modal=False
                   ):
    dpg.add_file_extension("")
    dpg.add_file_extension(".dat", color=(150, 255, 150, 255))

with dpg.file_dialog(directory_selector=True,
                    show=False,
                    file_count=15,
                    default_path=method_init.last_directory,
                    width = method_init.file_dialog_plot_all['width'],
                    height = method_init.file_dialog_plot_all['height'],
                    callback=method_cmn.callback_plot_all_to_files,
                    cancel_callback=callback_none,
                    tag="file_dialog_plot_all",
                    modal=False):
    ''' Dialogue window for exporting the results of the fitting.'''
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    
'''Export results window'''

with dpg.file_dialog(directory_selector=False,
                    show=False,
                    file_count=15,
                    default_path=method_init.last_directory,
                    width = method_init.file_dialog_export['width'],
                    height = method_init.file_dialog_export['height'],
                    callback=method_cmn.callback_directory_export,
                    cancel_callback=callback_none,
                    tag="file_dialog_export",
                    default_filename = 'results',
                    modal=False):
    ''' Dialogue window for exporting the results of the fitting.'''
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension("{.xlsx,.csv,.dat}")
    dpg.add_file_extension(".xlsx", color=(255, 0, 255, 255), custom_text="[Excel]")
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")
    dpg.add_file_extension(".pickle", color=(0, 255, 255, 255), custom_text="[Pandas]")


method_cmn.DialWinList = ['file_dialog_id1',
               'multi_file_dialog_id',
               'file_dialog_plot_all',
               'file_dialog_export']
globalITEMS.windows.extend(method_cmn.DialWinList)


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

                      )
globalITEMS.windows.extend(['FILES_window_text_title',
                            'sep_left_1',
                            'file_box'])                           
                           
#########################################################################
'''Items in the middle panel'''
#########################################################################                           
                           
with dpg.group(tag='model_choice_group',
                       horizontal=True,
                       horizontal_spacing=method_init.group_spacer,
                       show=True,
                       parent = 'Model_selection_panel'
                      ):
    dpg.add_combo(method_cmn.Models,
                  label="",
                  width=method_init.model_choose['width'],
                  height_mode=dpg.mvComboHeight_Large,
                  tag='model_choose',
                  default_value=method_cmn.init_model,
                  callback=method_cmn.callback_models,
                  enabled=False
                  )

    with dpg.tooltip('model_choose'):
        dpg.add_text("Select the model.")
    dpg.add_button(label="Add model",
                   tag='Add_model_button',
                   width = method_init.Add_model_button['width'],
                   callback=method_cmn.callback_show_new_model_window
                   )
    dpg.bind_item_theme('Add_model_button', 'fit_button_theme')    
    with dpg.tooltip('Add_model_button'):
        dpg.add_text("Add user-defined model. Opens a new window where the user can input and save the new model.")
dpg.add_separator(tag ='sep_mid_1',show=True,parent='Model_selection_panel')
with dpg.table(header_row=False,
               tag='CNTR_bright_table',
               width=-1,
               borders_innerH=False,
               borders_outerH=False,
               borders_innerV=False,
               borders_outerV=False,
               no_pad_innerX=False,
               no_pad_outerX=True,
               no_host_extendX=True,
               no_clip=True,
               policy=dpg.mvTable_SizingStretchSame,
               parent ='Model_selection_panel'):
    dpg.add_table_column(tag='CNTR_bright_table_col0',width=method_init.internal_width_middle_panel/2)
    dpg.add_table_column(tag='CNTR_bright_table_col1',width=method_init.internal_width_middle_panel/2)
    with dpg.table_row(tag='CNTR_bright_table_row0'):
        dpg.add_drag_float(label='',
                           width=method_init.CNTR['width'],
                           tag='CNTR',
                           show=True,
                           default_value=0,
                           enabled=True,
                           min_value=0,
                           max_value=1e5,
                           format="CNTR (Hz) =%.1f",
                           callback=method_cmn.callback_calculate_mol_bright
                           )
        with dpg.tooltip('CNTR'):
            dpg.add_text("Set the mean count rate value recorded for the given fcs curve.")
        dpg.add_drag_float(label='',
                           width=method_init.BRIGHT['width'],
                           tag='BRIGHT',
                           show=True,
                           default_value=0,
                           enabled=False,
                           format="B (Hz/MOL) =%.0f",
                           )
        with dpg.tooltip('BRIGHT'):
            dpg.add_text("Displays the molecular brightness value calculated from the count rate and the number of molecules.")

    with dpg.table_row(tag='CNTR_bright_table_row1'):
        dpg.add_checkbox(label="Include weights",
                         tag='FITing_checkbox',
                         default_value = True,
                         enabled=True,
                         show=True
                        )
        with dpg.tooltip('FITing_checkbox'):
                        dpg.add_text("Check to include weights during fitting (not available for the two column data).")

dpg.add_separator(tag ='sep_mid_2',show=True,parent='Model_selection_panel')                          
                           
globalITEMS.windows.extend(['model_choice_group',
                            'model_choose',
                            'Add_model_button',
                            'sep_mid_1',
                            'sep_mid_2',
                            'CNTR_bright_table_row1',
                            'CNTR_bright_table_row0',
                            'CNTR_bright_table_col1',
                            'CNTR_bright_table_col0',
                            'CNTR_bright_table',
                            'CNTR',
                            'BRIGHT',
                            'FITing_checkbox',
                            ])

#########################################################################
'''Items in the right panel'''
######################################################################### 

with dpg.group(tag='log_checkbox_group',
               horizontal=True,
               horizontal_spacing=method_init.group_spacer,
               show=True,
               parent ='plot_win'):
    dpg.add_drag_float(label='',
                       width=method_init.Xunits['width'],
                       tag='Xunits',
                       show=True,
                       default_value=0.00100000000,
                       format='Time units: %.0e [s]',
                       callback=method_cmn.callback_Xunits
                       )
    with dpg.tooltip('Xunits'):
        dpg.add_text("Default value is 10\u02C9\u00B3 s. If your data file has different units modify this value. Otherwise keep the default value.")

    dpg.add_drag_float(label='',
                       width=method_init.Yunits['width'],
                       tag='Yunits',
                       show=True,
                       default_value=1,
                       format="%.0e \u00D7 G("+'\u03C4'+")",
                       callback=method_cmn.callback_Xunits
                       )
    with dpg.tooltip('Yunits'):
                dpg.add_text("Default value is 1. If your data file has different units modify this value. Otherwise keep the default value.")
    dpg.add_text('',show=True,tag='chi_sqr')

with dpg.group(tag='df_range_group',
               horizontal=True,
               horizontal_spacing=method_init.group_spacer,
               show=True,
               parent ='plot_win'):
    dpg.add_drag_float(label='',
                       width=method_init.df_min['width'],
                       tag='df_min',
                       show=True,
                       min_value=-1e312,
                       max_value=-1e312,
                       callback=method_cmn.callback_df_range,
                       format='\u03C4'+' (min)  [ms] = %.4f',
                      )
    with dpg.tooltip('df_min'):
                dpg.add_text("Define lowest value of lag time to plot.")
    dpg.add_drag_float(label='',
                       width=method_init.df_max['width'],
                       tag='df_max',
                       show=True,
                       min_value=-1e312,
                       max_value=-1e312,
                       callback=method_cmn.callback_df_range,
                       format='\u03C4'+' (max) [ms] = %.1f',
                      )
    with dpg.tooltip('df_max'):
                dpg.add_text("Define highest value of lag time to plot.")
    dpg.add_button(label='Reset range',
                     width=method_init.Reset_range['width'],
                     tag='Reset_range',
                      show=True,
                       enabled=True,
                     callback=method_cmn.callback_reset_df_range
                     )
    dpg.bind_item_theme('Reset_range', 'fit_button_theme')   
    dpg.configure_item('Reset_range',enabled=False)   

with dpg.subplots(3,1,
                  height=method_init.subplots['height'],
                  width=method_init.subplots['width'],
                  row_ratios=[3.0,3.0, 1.0],
                  link_all_x=True,
                  tag='subplots',
                  show=True,
                  parent='plot_win'
                 ) as subplot_id:
    with dpg.plot(no_title=True,tag='plot_1',show=True):
        acf_plt_x = dpg.add_plot_axis(dpg.mvXAxis, label="", tag='acf_x',log_scale=True)
        acf_plt_y = dpg.plot_axis(dpg.mvYAxis, label="G("+'\u03C4'+")",tag='acf_y',log_scale=False)
        with acf_plt_y:
            dpg.add_scatter_series([], [],tag='ACF_plot')
            dpg.add_line_series([], [],tag='ACF_fit')
            dpg.bind_item_theme("ACF_plot", "plot_theme")
            dpg.bind_item_theme("ACF_fit", "plot_theme")
    with dpg.plot(no_title=True,tag='plot_2',show=True):
        acf_plt_x = dpg.add_plot_axis(dpg.mvXAxis, label="", tag='acf_x_log',log_scale=True)
        acf_plt_y = dpg.plot_axis(dpg.mvYAxis, label="Log(G("+'\u03C4'+"))",tag='acf_y_log',log_scale=True)
        with acf_plt_y:
            dpg.add_scatter_series([], [],tag='ACF_plot_log')
            dpg.add_line_series([], [],tag='ACF_fit_log')
            dpg.bind_item_theme("ACF_plot_log", "plot_theme")
            dpg.bind_item_theme("ACF_fit_log", "plot_theme")  
    with dpg.plot(no_title=True,tag='plot_3',show=True):
        dpg.configure_item('Xunits', format='Time units: %.0e [s]')
        dpg.add_plot_axis(dpg.mvXAxis, label="Lag time, "+'\u03C4'+" [ms]",tag='res_x',log_scale=True)
        with dpg.plot_axis(dpg.mvYAxis,
                           label="Residues",
                           tag='res_y'):
            dpg.add_line_series([], [],
                                tag='RES_plot')
            dpg.bind_item_theme("RES_plot", "plot_theme")
        dpg.set_axis_limits_auto('res_y')
        
        
globalITEMS.windows.extend(['log_checkbox_group',
                            'Xunits',
                            'Yunits',
                            'df_range_group',
                            'df_min',
                            'df_max',
                            'Reset_range',
                           'subplots',
                            'plot_1',
                            'acf_x',
                            'acf_y',
                            'ACF_plot',
                            'ACF_fit',
                            'plot_2',
                            'acf_x_log',
                            'acf_y_log',
                            'ACF_plot_log',
                            'ACF_fit_log',
                            'plot_3',
                            'res_x',
                            'res_y',
                            'RES_plot'
                           ])


