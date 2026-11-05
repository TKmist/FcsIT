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


with dpg.window(label='Settings',
                tag="Settings_window",
                width=Settings_window['width'],
                height=Settings_window['height'],
                pos=Settings_window['pos'],
                no_resize=True,
                show=False,
                modal = True,
                autosize=True,
               ):
    dpg.add_text('General settings',
                 tag='General_settings_text')
    dpg.add_separator(tag ='Settings_sep1',show=True)  
    with dpg.group(tag='default_theme_group',
               horizontal=True,
               horizontal_spacing=inV.init_group_spacer
              ):
        dpg.add_text('Theme: ',tag = 'sett_theme_group_text_01')
        dpg.add_combo(['dark','light'],
                  label="",
                  width=int(Settings_window['width']/3),
                  height_mode=dpg.mvComboHeight_Large,
                  tag='theme_choose',
                  default_value='dark',
                  callback=None,
                  enabled=True
                  )
    dpg.add_separator(tag ='Settings_sep2',show=True)
    dpg.add_text('FCS fitting settings',
                 tag='FCS_fitting_settings_text')
    dpg.add_separator(tag ='Settings_sep3',show=True)
    with dpg.table(header_row=False, show=True,pos = (0,50),tag='sett_table_00'):
        dpg.add_table_column(tag='Setts_column_1')
        dpg.add_table_column(tag='Setts_column_2')
        with dpg.table_row(tag='Setts_row_0'):
            with dpg.table_cell(tag = 'Setts_c1_r0_cell'):
                dpg.add_text("Results export options",tag = 'Setts_c1_r0_cell_text')
            with dpg.table_cell(tag = 'Setts_c2_r0_cell'):
                dpg.add_text("Plot export options",tag = 'Setts_c2_r0_cell_text')
        with dpg.table_row(tag='Setts_row_1'):
            
            '''####################
            Row 1
            ####################'''
            
            with dpg.table_cell(tag = 'Setts_c1_r1_cell'):
                dpg.add_checkbox(label='Export each keept result',
                             tag='Sett_export_each',
                             default_value=True,
                             callback=method_init.callback_settings_data_export_each
                            )
                with dpg.tooltip('Sett_export_each',tag='Setts_c1_r1_cell_tooltip'):
                    dpg.add_text('Check to export all stored data each time the "Store results" button is pressed.',
                                 tag='Setts_c1_r1_cell_tooltip_text')
                    
            with dpg.table_cell(tag = 'Setts_c2_r1_cell'):
                dpg.add_checkbox(label='Export plot as .png',
                             tag='Sett_export_plot_as_png',
                             default_value=True,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
               
                with dpg.tooltip('Sett_export_plot_as_png',tag='Setts_c2_r1_cell_tooltip'):
                    dpg.add_text('Each plot will be quick saved to ".png" file.',tag='Setts_c2_r1_cell_tooltip_text')
        with dpg.table_row(tag='Setts_row_2'):
            
            '''####################
            Row 2
            ####################'''
            
            
            with dpg.table_cell(tag = 'Setts_c1_r2_cell'):
                pass
                    
            with dpg.table_cell(tag = 'Setts_c2_r2_cell'):
                dpg.add_checkbox(label='Export plot as .csv',
                             tag='Sett_export_plot_as_csv',
                             default_value=False,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
               
                with dpg.tooltip('Sett_export_plot_as_csv',tag='Setts_c2_r2_cell_tooltip'):
                    dpg.add_text('Each plot will be quick saved to ".csv" file.',
                                tag='Setts_c2_r2_cell_tooltip_text')
                
        with dpg.table_row(tag='Setts_row_3'):
            
            '''####################
            Row 3
            ####################'''
            with dpg.table_cell(tag = 'Setts_c1_r3_cell'):
                dpg.add_checkbox(label='Export as .csv',
                             tag='Sett_export_to_csv',
                             default_value=True,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_export_to_csv',tag='Setts_c1_r3_cell_tooltip'):
                    dpg.add_text('Each data will be quick saved to ".csv" file.',
                                tag='Setts_c1_r3_cell_tooltip_text')
                    
            with dpg.table_cell(tag = 'Setts_c2_r3_cell'):
                dpg.add_checkbox(label='Export plot as .pickle',
                             tag='Sett_export_plot_as_pickle',
                             default_value=False,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_export_plot_as_pickle',tag='Setts_c2_r3_cell_tooltip'):
                    dpg.add_text('Each plot will be quick saved to ".pickle" file.',
                                tag='Setts_c2_r3_cell_tooltip_text')
                
        with dpg.table_row(tag='Setts_row_4'):
            
            '''####################
            Row 4
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r4_cell'):
                dpg.add_checkbox(label='Export as .pickle',
                             tag='Sett_export_to_pickle',
                             default_value=True,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_export_to_pickle',tag='Setts_c1_r4_cell_tooltip'):
                    dpg.add_text('Each data will be quick saved to ".pickle" file. (Pandas binary format).',
                                tag='Setts_c1_r4_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r4_cell'):
                dpg.add_checkbox(label='Export plot in the loglog mode',
                             tag='Sett_export_plot_loglog',
                             default_value=True,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_export_plot_loglog',tag='Setts_c2_r4_cell_tooltip'):
                    dpg.add_text('Each plot will be quick saved to png as a loglog plot.',
                                tag='Setts_c2_r4_cell_tooltip_text')
        with dpg.table_row(tag='Setts_row_5'):
            
            '''####################
            Row 5
            ####################'''
            with dpg.table_cell(tag='Setts_c1_r5_cell'):
                dpg.add_checkbox(label="Export results' statistics",
                             tag='Sett_export_stats',
                             default_value=True,
                             enabled = True,
                             callback=method_init.callback_settings_data_stats
                            )
                with dpg.tooltip('Sett_export_stats',tag='Setts_c1_r5_cell_tooltip'):
                    dpg.add_text('Each time the reulst will saved with the "Export results to file" button, the file containing the statistics of the results will be exported.',
                                tag='Setts_c1_r5_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r5_cell'):
                pass
        with dpg.table_row(tag='Setts_row_6'):
            
            '''####################
            Row 6
            ####################'''
            with dpg.table_cell(tag='Setts_c1_r6_cell'):
                dpg.add_checkbox(label="Statistics to .csv",
                             tag='Sett_export_stats_to_csv',
                             default_value=False,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_export_stats_to_csv',tag='Setts_c1_r6_cell_tooltip'):
                    dpg.add_text('Export stats to the ".csv" file.',
                                tag='Setts_c1_r6_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r6_cell'):
                pass
        with dpg.table_row(tag='Setts_row_7'):
            
            '''####################
            Row 7
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r7_cell'):
                pass
                    
            with dpg.table_cell(tag='Setts_c2_r7_cell'):
                pass
        with dpg.table_row(tag='Setts_row_8'):
            
            '''####################
            Row 8
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r8_cell'):
                dpg.add_checkbox(label="Statistics to .pickle",
                             tag='Sett_export_stats_to_pickle',
                             default_value=True,
                             enabled = True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
               
                with dpg.tooltip('Sett_export_stats_to_pickle',tag='Setts_c1_r8_cell_tooltip'):
                    dpg.add_text('Export stats to the ".pickle" file.',
                                 tag='Setts_c1_r8_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r8_cell'):
                pass
            
    with dpg.table(header_row=False, show=True,pos = (0,50),tag='sett_table_01'):

        dpg.add_table_column(tag='Setts_column_11')
        dpg.add_table_column(tag='Setts_column_22')
        with dpg.table_row(tag='Setts_row_9'):
            
            '''####################
            Row 9
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r9_cell'):
                dpg.add_text("Other options",tag='Setts_c1_r9_cell_text')
            with dpg.table_cell(tag='Setts_c2_r9_cell'):
                pass
        with dpg.table_row(tag='Setts_row_10'):
            
            '''####################
            Row 10
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r10_cell'):
                dpg.add_checkbox(label='Preserve data time range',
                             tag='Sett_preserve_time',
                             default_value=True,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_preserve_time',tag='Setts_c1_r10_cell_tooltip'):
                    dpg.add_text('Check to keep the same \u03C4(min)-\u03C4(max) range between each fitted curve.',
                                 tag='Setts_c1_r10_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r10_cell'):
                pass
        with dpg.table_row(tag='Setts_row_11'):
            
            '''####################
            Row 11
            ####################'''
            
            
            with dpg.table_cell(tag='Setts_c1_r11_cell'):
                dpg.add_checkbox(label='Preserve X/Y units',
                             tag='Sett_preserve_units',
                             default_value=False,
                             callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                            )
                with dpg.tooltip('Sett_preserve_units',tag='Setts_c1_r11_cell_tooltip'):
                    dpg.add_text('Check to keep the same X, and Y units between each fitted curve.',
                                     tag='Setts_c1_r11_cell_tooltip_text')
                    
            with dpg.table_cell(tag='Setts_c2_r11_cell'):
                pass
    dpg.add_separator(tag ='Settings_sep4',show=True)
    with dpg.group(tag='default_quick_res_exp_group',
                   horizontal=True,
                   horizontal_spacing=inV.init_group_spacer
                  ):
        dpg.add_text('Filename for quick export: ',tag = 'sett_group_01_text_01')
        dpg.add_input_text(tag = 'default_quick_export_filename',
                           width=inV.default_quick_export_filename,
                           default_value = 'results_temp',
                           callback = lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                          )
        dpg.add_text('.*',tag = 'sett_group_01_text_02')
        with dpg.tooltip('default_quick_export_filename',tag='sett_group_01_text_02_tooltip'):
            dpg.add_text('Enter the filename without extension.',tag='sett_group_01_text_02_tooltip_text')
    with dpg.group(tag='default_quick_res_stat_group',
                   horizontal=True,
                   horizontal_spacing=inV.init_group_spacer):
        dpg.add_text('Filename for statistics export: ',tag='default_quick_res_stat_group_text_1')
        dpg.add_input_text(tag = 'default_quick_stst_filename',
                           width=inV.default_quick_stst_filename,
                           default_value = 'report_result_stats',
                           callback = lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                          )
        dpg.add_text('.*',tag='default_quick_res_stat_group_text_2')
        with dpg.tooltip('default_quick_export_filename',
                         tag='default_quick_res_stat_group_text_2_tooltip'):
            dpg.add_text('Enter the filename without extension.',
                        tag='default_quick_res_stat_group_text_2_tooltip_text')
    
        

        
            
        
        
    with dpg.group(tag='Setts_buttons_group',
                   horizontal=True,
                   horizontal_spacing=inV.init_group_spacer,pos = (inV.init_left_indent,dpg.get_item_height('Settings_window')-24-inV.init_bottom_indent)):
        dpg.add_button(label='Save as defaults',
                               tag='Setts_save_defaults',
                               show=True,
                               width = method_init.Setts_save_defaults,
                               callback=method_init.callback_save_as_def
                              )
        dpg.bind_item_theme('Setts_save_defaults', 'fit_button_theme')
        
        dpg.add_button(label='Close',
                               tag='Setts_cancel',
                               show=True,
                               
                               width = method_init.Setts_cancel,
                               callback=lambda: dpg.configure_item('Settings_window',show=False)
                              )
        dpg.bind_item_theme('Setts_save_defaults', 'fit_button_theme')
        dpg.bind_item_theme('Setts_cancel', 'fit_button_theme')
        
dpg.bind_item_theme('Settings_window', 'Inactive_checkbox') 


settings_items = ['Settings_window',
                  'General_settings_text',
                  'Settings_sep1',
                  'default_theme_group',
                  'sett_theme_group_text_01',
                  'theme_choose',
                  'Settings_sep2',
                  'FCS_fitting_settings_text',
                  'Settings_sep3',
                  'sett_table_00',
                  'Setts_column_1',
                  'Setts_column_2',
                  'Setts_row_0',
                  'Setts_c1_r0_cell','Setts_c1_r0_cell_text',
                  'Setts_c2_r0_cell','Setts_c2_r0_cell_text',
                  'Setts_row_1',
                  'Setts_c1_r1_cell', 'Sett_export_each', 'Setts_c1_r1_cell_tooltip', 'Setts_c1_r1_cell_tooltip_text',
                  'Setts_c2_r1_cell', 'Sett_export_plot_as_png', 'Setts_c2_r1_cell_tooltip', 'Setts_c2_r1_cell_tooltip_text',
                  'Setts_c1_r2_cell',
                  'Setts_c2_r2_cell','Sett_export_plot_as_csv', 'Setts_c2_r2_cell_tooltip','Setts_c2_r2_cell_tooltip_text',
                  'Setts_row_3',
                  'Setts_c1_r3_cell','Sett_export_to_csv','Setts_c1_r3_cell_tooltip','Setts_c1_r3_cell_tooltip_text',
                  'Setts_c2_r3_cell','Sett_export_plot_as_pickle','Setts_c2_r3_cell_tooltip','Setts_c2_r3_cell_tooltip_text',
                  'Setts_row_4',
                  'Setts_c1_r4_cell','Sett_export_to_pickle','Setts_c1_r4_cell_tooltip','Setts_c1_r4_cell_tooltip_text',
                  'Setts_c2_r4_cell','Sett_export_plot_loglog','Setts_c2_r4_cell_tooltip','Setts_c2_r4_cell_tooltip_text',
                  'Setts_row_5',
                  'Setts_c1_r5_cell','Sett_export_stats','Setts_c1_r5_cell_tooltip','Setts_c1_r5_cell_tooltip_text',
                  'Setts_c2_r5_cell',
                  'Setts_row_6',
                  'Setts_c1_r6_cell','Sett_export_stats_to_csv','Setts_c1_r6_cell_tooltip','Setts_c1_r6_cell_tooltip_text',
                  'Setts_c2_r6_cell',
                  'Setts_row_7',
                  'Setts_c1_r7_cell',
                  'Setts_c2_r7_cell',
                  'Setts_row_8',
                  'Setts_c1_r8_cell','Sett_export_stats_to_pickle''Setts_c1_r8_cell_tooltip','Setts_c1_r8_cell_tooltip_text'
                  'Setts_c2_r8_cell',
                  'sett_table_01',
                  'Setts_column_11','Setts_column_22',
                  'Setts_row_9',
                  'Setts_c1_r9_cell','Setts_c1_r9_cell_text',
                  'Setts_c2_r9_cell',
                  'Setts_row_10',
                  'Setts_c1_r10_cell','Sett_preserve_time','Setts_c1_r10_cell_tooltip','Setts_c1_r10_cell_tooltip_text' ,
                  'Setts_c2_r10_cell',
                  'Setts_row_11',
                  'Setts_c1_r11_cell','Sett_preserve_units','Setts_c1_r11_cell_tooltip','Setts_c1_r11_cell_tooltip_text',
                  'Setts_c2_r11_cell'
                  'default_quick_res_exp_group',
                  'sett_group_01_text_01','default_quick_export_filename','sett_group_01_text_02',
                  'sett_group_01_text_02_tooltip','sett_group_01_text_02_tooltip_text',
                  'Settings_sep4',
                  'default_quick_res_stat_group',
                  'default_quick_res_stat_group_text_1','default_quick_stst_filename','default_quick_res_stat_group_text_2',
                  'default_quick_res_stat_group_text_2_tooltip','default_quick_res_stat_group_text_2_tooltip_text',
                  'Setts_buttons_group',
                  'Setts_save_defaults','Setts_cancel'
                  ]




globalITEMS.windows.extend(settings_items)

