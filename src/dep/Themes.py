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
DARK = {
    # Window base colors
    "viewport_bg":        (0, 0, 0, 255),
    "window_bg": (37, 37, 38),
    "child_bg":  (34, 34, 36),
    "popup_bg":           (40, 50, 52, 255),

    # Text
    "text":               (235, 235, 235, 255),
    "text_disabled":      (150, 150, 150, 255),

    # Fields and inputs
    "frame_bg":           (51, 51, 55, 255),
    "frame_bg_hovered":   (66, 66, 72, 255),
    "frame_bg_active":    (78, 78, 84, 255),

    # General buttons
    "button":             (66, 66, 70, 255),
    "button_hovered":     (86, 86, 92, 255),
    "button_active":      (98, 98, 106, 255),
    "button_disabled":    (55, 55, 58, 255),

    # fit_button_theme
    "fit_button":              (87, 153, 61, 255),
    "fit_button_hovered":      (117, 178, 71, 255),
    "fit_button_active":       (117, 178, 71, 255),
    "fit_button_disabled":     (54, 76, 54, 255),
    "fit_button_inactive":     (92, 153, 92, 255),

    # fit_button_theme_busy
    "fit_button_busy":         (202, 95, 72, 255),
    "fit_button_busy_hovered": (180, 80, 60, 255),
    "fit_button_busy_active":  (160, 70, 50, 255),

    # Collapsible sections, selectors, and table-like headers
    "header":             (70, 70, 74, 255),
    "header_hovered":     (90, 90, 96, 255),
    "header_active":      (102, 102, 110, 255),

    # title / menu
    "title_bg":           (45, 45, 48, 255),
    "title_bg_active":    (60, 60, 65, 255),
    "menu_bar_bg":        (45, 45, 48, 255),

    # Details
    "check_mark":         (0, 119, 200, 153),
    "check_mark_disabled":(194, 194, 194, 45),
    "separator": (45, 45, 48, 255),
    "modal_dim":          (5, 5, 5, 215),

    # Menu statuses
    "menu_text":          (255, 255, 255, 255),
    "menu_warn":          (246, 115, 10, 255),
    "menu_warn_disabled": (246, 136, 10, 255),
    "menu_ok":            (62, 190, 15, 255),

    # error window
    "error_window_bg":    (139, 16, 16, 255),
    "error_title_bg":     (83, 23, 23, 255),
    "error_button":       (56, 5, 15, 255),

    # plot_theme
    "plot_scatter_green":   (31, 255, 0, 255),
    "plot_line_orange":     (229, 80, 48, 255),
    "plot_fill_green":      (62, 122, 56, 64),
    "plot_fill_green_line": (62, 122, 56, 90),

    # plot_green_theme
    "plot_green_line":      (31, 255, 0, 255),

    # plot_green_inactive_theme
    "plot_green_inactive":  (128, 138, 126, 255),

    # plot_yellow_theme
    "plot_yellow_line":     (200, 206, 75, 255),
    "plot_yellow_fill":     (122, 62, 56, 90),
    "plot_yellow_fill_line":(122, 62, 56, 90),

    # border / outlines
    "border": (70, 70, 75, 255),
    "border_shadow":       (0, 0, 0, 0),

    # scrollbars
    "scrollbar_bg":           (43, 43, 46, 255),
    "scrollbar_grab":         (95, 120, 100, 255),
    "scrollbar_grab_hovered": (110, 140, 115, 255),
    "scrollbar_grab_active":  (125, 155, 130, 255),

    # tabs
    "tab":                 (54, 76, 54, 255),
    "tab_hovered":         (41, 204, 41, 255),
    "tab_active":          (54, 178, 54, 255),
    "tab_unfocused":       (50, 52, 54, 255),
    "tab_unfocused_active":(72, 88, 76, 255),

    "table_header":        (60, 60, 65, 255),
    "table_border_strong": (90, 90, 95, 255),
    "table_border_light":  (60, 60, 65, 255),
    "table_row":           (0, 0, 0, 0),
    "table_row_alt":       (255, 255, 255, 5),
}


LIGHT = {
    # Window base colors
    "viewport_bg":        (246, 247, 246, 255),
    "window_bg":          (246, 247, 246, 255),
    "child_bg":           (252, 253, 252, 255),
    "popup_bg":           (255, 255, 255, 255),

    # Text
    "text":               (40, 42, 40, 255),
    "text_disabled":      (50, 55, 50, 255),

    # Fields and inputs
    "frame_bg":           (225, 227, 225, 255),
    "frame_bg_hovered":   (232, 235, 232, 255),
    "frame_bg_active":    (204, 218, 204, 255),

    # General buttons
    "button":             (226, 230, 226, 255),
    "button_hovered":     (214, 220, 214, 255),
    "button_active":      (202, 210, 202, 255),
    "button_disabled":    (235, 238, 235, 255),

    # fit_button_theme
    "fit_button":              (150, 175, 140, 255),
    "fit_button_hovered":      (165, 190, 155, 255),
    "fit_button_active":       (165, 190, 155, 255),
    "fit_button_disabled":     (190, 205, 185, 255),
    "fit_button_inactive":     (190, 205, 185, 255),

    # fit_button_theme_busy
    "fit_button_busy":         (225, 145, 125, 255),
    "fit_button_busy_hovered": (210, 130, 110, 255),
    "fit_button_busy_active":  (190, 115, 95, 255),

    # Sections
    "header":             (206, 209, 206, 255),
    "header_hovered":     (200, 202, 200, 255),
    "header_active":      (200, 205, 200, 255),

    # title / menu
    "title_bg":           (240, 243, 240, 255),
    "title_bg_active":    (230, 235, 230, 255),
    "menu_bar_bg":        (242, 245, 242, 255),

    # Details
    "check_mark":         (110, 150, 120, 180),
    "check_mark_disabled":(190, 195, 190, 90),
    "separator":          (200, 205, 200, 255),
    "modal_dim":          (250, 250, 250, 220),

    # Menu statuses
    "menu_text":          (40, 42, 40, 255),
    "menu_warn":          (246, 115, 10, 255),
    "menu_warn_disabled": (246, 136, 10, 255),
    "menu_ok":            (150, 175, 140, 255),

    # error window
    "error_window_bg":    (255, 245, 245, 255),
    "error_title_bg":     (220, 120, 120, 255),
    "error_button":       (200, 100, 100, 255),

    # plot_theme
    "plot_scatter_green":   (140, 170, 135, 255),
    "plot_line_orange":     (229, 120, 90, 255),
    "plot_fill_green":      (140, 170, 135, 48),
    "plot_fill_green_line": (140, 170, 135, 90),

    # plot_green_theme
    "plot_green_line":      (140, 170, 135, 255),

    # plot_green_inactive_theme
    "plot_green_inactive":  (170, 178, 168, 255),

    # plot_yellow_theme
    "plot_yellow_line":     (200, 206, 75, 255),
    "plot_yellow_fill":     (180, 130, 120, 70),
    "plot_yellow_fill_line":(180, 130, 120, 90),

    # border / outlines
    "border":              (185, 190, 185, 255),
    "border_shadow":       (0, 0, 0, 0),

    # scrollbars
    "scrollbar_bg":           (236, 239, 236, 255),
    "scrollbar_grab":         (170, 188, 165, 255),
    "scrollbar_grab_hovered": (150, 175, 140, 255),
    "scrollbar_grab_active":  (130, 160, 125, 255),

    # tabs
    "tab":                 (190, 205, 185, 255),
    "tab_hovered":         (165, 190, 155, 255),
    "tab_active":          (150, 175, 140, 255),
    "tab_unfocused":       (215, 220, 215, 255),
    "tab_unfocused_active":(185, 198, 182, 255),

    "table_header":        (210, 215, 210, 255),
    "table_border_strong": (185, 190, 185, 255),
    "table_border_light":  (210, 215, 210, 255),
    "table_row":           (0, 0, 0, 0),
    "table_row_alt":       (120, 140, 120, 20),
}


def create_global_theme(p, tag="global_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,         p["window_bg"],        category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,          p["child_bg"],         category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,          p["popup_bg"],         category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_Text,             p["text"],             category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,     p["text_disabled"],    category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,          p["frame_bg"],         category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,   p["frame_bg_hovered"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,    p["frame_bg_active"],  category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_Button,           p["button"],           category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,    p["button_hovered"],   category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,     p["button_active"],    category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_Header,           p["header"],           category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,    p["header_hovered"],   category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive,     p["header_active"],    category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,          p["title_bg"],         category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,    p["title_bg_active"],  category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg,        p["menu_bar_bg"],      category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_CheckMark,        p["check_mark"],       category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Separator,        p["separator"],        category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, p["modal_dim"],        category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_Border,             p["border"],             category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow,       p["border_shadow"],      category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,        p["scrollbar_bg"],       category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,      p["scrollbar_grab"],     category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, p["scrollbar_grab_hovered"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive,  p["scrollbar_grab_active"],  category=dpg.mvThemeCat_Core)

            dpg.add_theme_color(dpg.mvThemeCol_Tab,                p["tab"],                category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered,         p["tab_hovered"],        category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive,          p["tab_active"],         category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused,       p["tab_unfocused"],      category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, p["tab_unfocused_active"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg,        p["table_header"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong,    p["table_border_strong"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight,     p["table_border_light"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg,           p["table_row"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt,        p["table_row_alt"], category=dpg.mvThemeCat_Core)


def create_fit_button_theme(p, tag="fit_button_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,         p["fit_button"],          category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   p["fit_button_active"],   category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  p["fit_button_hovered"],  category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Button,         p["fit_button_disabled"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   p["fit_button_disabled"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  p["fit_button_disabled"], category=dpg.mvThemeCat_Core)


def create_fit_button_theme_inactive(p, tag="fit_button_theme_inactive"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,         p["fit_button_inactive"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  p["fit_button_hovered"],  category=dpg.mvThemeCat_Core)


def create_fit_button_theme_busy(p, tag="fit_button_theme_busy"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,         p["fit_button_busy"],         category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  p["fit_button_busy_hovered"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   p["fit_button_busy_active"],  category=dpg.mvThemeCat_Core)


def create_plot_themes(p, tag="plot_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_scatter_green"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_line_orange"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvShadeSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Fill, p["plot_fill_green"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_fill_green_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)


def create_plot_green_theme(p, tag="plot_green_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_green_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_green_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvShadeSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Fill, p["plot_fill_green"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_fill_green_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)


def create_plot_green_inactive_theme(p, tag="plot_green_inactive_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_green_inactive"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_green_inactive"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvShadeSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Fill, p["plot_fill_green"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_fill_green_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)


def create_plot_yellow_theme(p, tag="plot_yellow_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvScatterSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_yellow_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 5, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_yellow_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)

        with dpg.theme_component(dpg.mvShadeSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Fill, p["plot_yellow_fill"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_color(dpg.mvPlotCol_Line, p["plot_yellow_fill_line"], category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 4, category=dpg.mvThemeCat_Plots)


def create_error_window_theme(p, tag="Error_window_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvWindowAppItem):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,       p["error_window_bg"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,  p["error_title_bg"],  category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,         p["error_button"],    category=dpg.mvThemeCat_Core)


def create_checkbox_themes(p, inactive_tag="Inactive_checkbox", active_tag="Active_checkbox"):
    with dpg.theme(tag=inactive_tag):
        with dpg.theme_component(dpg.mvCheckbox):
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, p["check_mark"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvCheckbox, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, p["check_mark_disabled"], category=dpg.mvThemeCat_Core)

    with dpg.theme(tag=active_tag):
        with dpg.theme_component(dpg.mvCheckbox):
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, p["check_mark"], category=dpg.mvThemeCat_Core)


def create_transparent_theme(tag="transparent_theme"):
    with dpg.theme(tag=tag):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,        (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)


def create_menu_themes(p, normal_tag="menu_normal", update_tag="menu_update_available", update_new_tag="menu_update_available_new"):
    with dpg.theme(tag=normal_tag):
        with dpg.theme_component(dpg.mvMenu):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_text"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvMenuItem):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_text"], category=dpg.mvThemeCat_Core)

    with dpg.theme(tag=update_tag):
        with dpg.theme_component(dpg.mvMenu):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_warn"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvMenuItem, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_warn_disabled"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvMenuItem):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_warn"], category=dpg.mvThemeCat_Core)

    with dpg.theme(tag=update_new_tag):
        with dpg.theme_component(dpg.mvMenu):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_warn"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvMenuItem, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_ok"], category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvMenuItem):
            dpg.add_theme_color(dpg.mvThemeCol_Text, p["menu_ok"], category=dpg.mvThemeCat_Core)


def apply_viewport_color(p):
    dpg.set_viewport_clear_color(p["viewport_bg"])


def build_themes(mode: str):
    p = DARK if mode == "dark" else LIGHT

    create_global_theme(p)
    create_fit_button_theme(p)
    create_fit_button_theme_inactive(p)
    create_fit_button_theme_busy(p)
    create_plot_themes(p)
    create_plot_green_theme(p)
    create_plot_green_inactive_theme(p)
    create_plot_yellow_theme(p)
    create_error_window_theme(p)
    create_checkbox_themes(p)
    create_transparent_theme()
    create_menu_themes(p)

    dpg.bind_theme("global_theme")
    apply_viewport_color(p)


def callback_theme(sender, app_data):
    theme = dpg.get_item_label(sender)

    if theme == 'Dark theme':
        THEME = 'dark'
        dpg.set_item_label(sender, 'Light theme')
        build_themes(THEME)

    elif theme == 'Light theme':
        THEME = 'light'
        dpg.set_item_label(sender, 'Dark theme')
        build_themes(THEME)
