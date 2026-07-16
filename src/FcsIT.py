'''
Copyright (C) 2026 TKmist (https://github.com/TKmist)

This file is part of the FcsIT repository.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
'''

with open('LICENSE', 'r',encoding='utf-8') as file:
    License = file.read()
with open('GPLv3_short', 'r',encoding='utf-8') as file:
    License_short = file.read()
with open('VERSION', 'r',encoding='utf-8') as file:
    VERSION = file.read()
line='=============================================================================='

import dearpygui.dearpygui as dpg
import datetime
import os
import include.INIT as inits
import argparse
import faulthandler
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = os.path.join(BASE_DIR , "doc" , "assets" , "help_html")
faulthandler.enable()
parser = argparse.ArgumentParser(description="Example program with optional timing log.")
parser.add_argument("--timing", action="store_true", help="Enable timing log for functions.")
args = parser.parse_args()


def execfile(exec_file, globals=globals(), locals=None):
    '''Import module allowing execution of external python scripts as part of the main code. This part of the code is based on the following source: https://stackoverflow.com/a/41658338 '''
    filepath = os.path.join(exec_file)
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)
def callback_none():
    pass
logfile=os.path.join('Logs','log.txt')
docs_server = inits.LocalDocsServer(DOCS_DIR)
basf = inits._basicF(logfile, args)

basf.log_it("STARTED on "+str(datetime.datetime.now()),'w') 
basf.timeit_it_init("STARTED on "+str(datetime.datetime.now()),'w') 
updt = inits.FcsITUpdater(basf._hsv_to_rgb,VERSION)
inV=inits._init_varaibles()
viewport = inV.VIEWPORT_prop
menu = inits._init_Menu(VERSION=VERSION,
                        docs_dir=DOCS_DIR,
                        docs_server=docs_server)

lprint=basf.lnprint

print(line)
print(line,end='\n\n')
print(License_short)
print('\n')
print('VERSION = ',VERSION,end='\n')
print(line)
print(line,end='\n\n')

execfile('dep/Required.py')           

inf_w, inf_h = get_monitors()[0].width, get_monitors()[0].height

dpg.create_context()
execfile('dep/Themes.py')             
execfile('dep/Fonts.py') 
execfile('dep/Handlers.py') 

dpg.create_viewport(title='FcsIT',small_icon = inV.icopath(),width=viewport['width'], height=viewport['height'],x_pos=viewport['pos'][0],y_pos  =viewport['pos'][1]) 
dpg.setup_dearpygui()
dpg.show_viewport()
globalITEMS = inits._common_VARIABLES()
  
VP_w = dpg.get_viewport_width()            
VP_h = dpg.get_viewport_height()           
dpg.maximize_viewport() 
menu.mount_main_Menu_bar()
settwin = inits.sett_window(viewport,inV.init_left_indent,
                             inV.init_internal_indent,
                             inV.init_right_indent,
                             inV.init_bottom_indent,
                             inV.init_top_indent,
                             inV.init_group_spacer)
THEME = settwin.OPTIONS['theme_choose']
build_themes(THEME)
updt.run_updater()
print('updt.updater_state =', updt.updater_state)
    
inV.METHODS = basf.search_for_methods()

for method in inV.METHODS:

    path =os.path.join(method,basf.path_to_method_anal_menu_item(method))
    execfile(path)

dpg.start_dearpygui()
dpg.destroy_context()
