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

'''The themes definitions.'''
with dpg.theme(tag='global'):

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (5, 5, 5,215))
        dpg.add_theme_color(dpg.mvThemeCol_Tab,
                            basf._hsv_to_rgb(2/7.0, 0.3, 0.3),category=dpg.mvThemeCat_Core
                           )
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered,
                            basf._hsv_to_rgb(2/7.0, 0.8, 0.8),category=dpg.mvThemeCat_Core
                           )
        dpg.add_theme_color(dpg.mvThemeCol_TabActive,
                            basf._hsv_to_rgb(2/7.0, 0.7, 0.7),category=dpg.mvThemeCat_Core
                           )
        dpg.bind_theme('global')
        
with dpg.theme(tag="fit_button_theme"):
    '''Theme for active buttons'''
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            basf._hsv_to_rgb(0.2857, 0.6, 0.6)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,
                            basf._hsv_to_rgb(2/7.0, 0.8, 0.8)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,
                            basf._hsv_to_rgb(2/7.0, 0.7, 0.7)
                           )
    with dpg.theme_component(dpg.mvButton,enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            basf._hsv_to_rgb(2/7.0, 0.3, 0.3)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,
                            basf._hsv_to_rgb(2/7.0, 0.3, 0.3)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,
                            basf._hsv_to_rgb(2/7.0, 0.3, 0.3)
                           )
                           
        
with dpg.theme(tag="fit_button_theme_inactive"):
    '''Theme for inactive buttons'''
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            basf._hsv_to_rgb(2/7.0, 0.4, 0.6)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,
                            basf._hsv_to_rgb(2/7.0, 0.7, 0.7)
                           )
                           
with dpg.theme(tag="fit_button_theme_busy"):
    '''Theme for inactive (busy) buttons'''
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            (202, 95, 72, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,
                            (180, 80, 60, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,
                            (160, 70, 50, 255))  

        
with dpg.theme(tag="plot_theme"):
    '''Themes for plot.'''
    with dpg.theme_component(dpg.mvScatterSeries):
        '''Theme for scattered points.'''
        dpg.add_theme_color(dpg.mvPlotCol_Line, (31, 255, 0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)
        
    with dpg.theme_component(dpg.mvLineSeries):
        '''Theme for solid lines.'''        
        dpg.add_theme_color(dpg.mvPlotCol_Line, (229, 80, 48), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)
        
    with dpg.theme_component(dpg.mvShadeSeries):
        '''Theme for shade areas (errors).'''
        dpg.add_theme_color(dpg.mvPlotCol_Fill, (62, 122, 56, 64), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Line, (62, 122, 56, 90), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)
        
        
with dpg.theme(tag="Error_window_theme"):
    '''Theme for Error windows'''
    with dpg.theme_component(dpg.mvWindowAppItem):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg,
                            (139,16,16,255)
                           )
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,
                            (83,23,23,255)
                           )
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            (56,5,15,255)
                           )
        
with dpg.theme(tag="Inactive_checkbox"):
    '''Theme for inactive checkboxes'''
    with dpg.theme_component(dpg.mvCheckbox):
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark,
                            (0,119,200,153)#(194,194,194,45)
                           )
    with dpg.theme_component(dpg.mvCheckbox,enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark,
                            (194,194,194,45)
                           )

        
with dpg.theme(tag="Active_checkbox"):
    '''Theme for inactive checkboxes'''
    with dpg.theme_component(dpg.mvCheckbox):
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark,
                            (0,119,200,153)#
                           )
BACKGROUND_COLOUR = (0,0,0,0)
with dpg.theme(tag='transparent_theme'):
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button,
                            BACKGROUND_COLOUR
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,
                            BACKGROUND_COLOUR
                           )
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,
                            BACKGROUND_COLOUR
                           )
with dpg.theme(tag="menu_update_available"):
    with dpg.theme_component(dpg.mvMenu):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (246, 115, 10))
    with dpg.theme_component(dpg.mvMenuItem,enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (246, 136, 10))
    with dpg.theme_component(dpg.mvMenuItem):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (246, 115, 10))


with dpg.theme(tag="menu_update_available_new"):
    with dpg.theme_component(dpg.mvMenu):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (246, 115, 10))
    with dpg.theme_component(dpg.mvMenuItem,enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (62, 190, 15))
    with dpg.theme_component(dpg.mvMenuItem):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (62, 190, 15))

with dpg.theme(tag="menu_normal"):
    with dpg.theme_component(dpg.mvMenu):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
    with dpg.theme_component(dpg.mvMenuItem):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        
        
with dpg.theme(tag="plot_green_theme"):
            '''Themes for plot.'''
            with dpg.theme_component(dpg.mvScatterSeries):
                '''Theme for scattered points.'''
                dpg.add_theme_color(dpg.mvPlotCol_Line, (31, 255, 0), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

            with dpg.theme_component(dpg.mvLineSeries):
                '''Theme for solid lines.'''        
                dpg.add_theme_color(dpg.mvPlotCol_Line, (31, 255, 0), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)

            with dpg.theme_component(dpg.mvShadeSeries):
                '''Theme for shade areas (errors).'''
                dpg.add_theme_color(dpg.mvPlotCol_Fill, (62, 122, 56, 64), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_color(dpg.mvPlotCol_Line, (62, 122, 56, 90), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)

with dpg.theme(tag="plot_green_inactive_theme"):
            '''Themes for plot.'''
            with dpg.theme_component(dpg.mvScatterSeries):
                '''Theme for scattered points.'''
                dpg.add_theme_color(dpg.mvPlotCol_Line, (128, 138, 126), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

            with dpg.theme_component(dpg.mvLineSeries):
                '''Theme for solid lines.'''        
                dpg.add_theme_color(dpg.mvPlotCol_Line, (128, 138, 126), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)

            with dpg.theme_component(dpg.mvShadeSeries):
                '''Theme for shade areas (errors).'''
                dpg.add_theme_color(dpg.mvPlotCol_Fill, (62, 122, 56, 64), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_color(dpg.mvPlotCol_Line, (62, 122, 56, 90), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)


with dpg.theme(tag="plot_yellow_theme"):
            '''Themes for plot.'''
            with dpg.theme_component(dpg.mvScatterSeries):
                '''Theme for scattered points.'''
                dpg.add_theme_color(dpg.mvPlotCol_Line, (200, 206, 75), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

            with dpg.theme_component(dpg.mvLineSeries):
                '''Theme for solid lines.'''        
                dpg.add_theme_color(dpg.mvPlotCol_Line, (200, 206, 75), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)
            with dpg.theme_component(dpg.mvShadeSeries):
                '''Theme for shade areas (errors).'''
                dpg.add_theme_color(dpg.mvPlotCol_Fill, (122, 62, 56, 90), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_color(dpg.mvPlotCol_Line, (122, 62, 56, 90), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)

            