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


'''Font definitions'''

def add_font_to_registry(font_size):
    font_path = os.path.join('res','Fonts','DejaVuSansCondensed.ttf')
    bold_font_path = os.path.join('res','Fonts','DejaVuSansCondensed-Bold.ttf')
    with dpg.font_registry(tag='Font_registry'):
        '''Add a font registry.'''
        
        with dpg.font(font_path, font_size,tag='DejaVu') as font_18:
            dpg.add_font_range(0x0300, 0x03ff)
            dpg.add_font_range(0x0200, 0x02ff)
            dpg.add_font_range(0x2080, 0x209C)
            dpg.add_font_range(0x2190, 0x2193)
            default_font = font_18

        with dpg.font(bold_font_path, font_size,tag='DejaVu_bold') as bold_font_18:
                dpg.add_font_range(0x0300, 0x03ff)
                dpg.add_font_range(0x0200, 0x02ff)
                dpg.add_font_range(0x2080, 0x209C)
                dpg.add_font_range(0x2190, 0x2193)
        dpg.bind_font(default_font)

init_font_size = font_size = 18
add_font_to_registry(init_font_size)
