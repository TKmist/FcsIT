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
# from __future__ import annotations
import os
import numpy as np
from numpy import log10
import dearpygui.dearpygui as dpg
import json
import webbrowser
import inspect
import math
import time
import socket
import argparse
from functools import wraps
from datetime import datetime



import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path


import re
import shutil
import zipfile

import requests


class FcsITUpdater:
    _VERSION_RE = re.compile(r"^\s*[vV]?(\d+)\.(\d+)\.(\d+)(?:rc(\d+)|([A-Za-z]))?\s*$")
   

    def __init__(self, hsv, version: str):
        """
        :param version: local application version, e.g. '1.1.0' or '1.1.0a'
        """
        print(version)
        self.VERSION = version
        self.version = version.strip()
        self.updater_state = False
        self.hsv = hsv

        self.owner = "TKmist"
        self.repo = "FcsIT"
        self.branch = "main"
        self.path = "VERSION"

    def _parse_version(self, ver: str):
        
        m = self._VERSION_RE.match(ver)
        if not m:
            raise ValueError(
                f"Invalid version format: {ver!r}. Expected e.g. 'v1.2.3', 'v1.2.3rc1', 'v1.2.3a'."
            )
    
        major, minor, patch = map(int, m.group(1, 2, 3))
        rc_num = m.group(4)     # digits after 'rc', e.g. '1'
        letter = m.group(5)     # single letter, e.g. 'a'
    
        # newest: final > rcN > a > b > ...
        if rc_num is None and letter is None:
            stage_rank = 3   # final
            detail_rank = 0
        elif rc_num is not None:
            stage_rank = 2   # rc
            detail_rank = int(rc_num)   # rc2 > rc1
        else:
            stage_rank = 1   # pre-release letter
            s = letter.lower()
            if not ("a" <= s <= "z"):
                raise ValueError(f"Invalid version suffix: {letter!r}")
            detail_rank = 26 - (ord(s) - ord("a"))  # a newest among letters
    
        return (major, minor, patch, stage_rank, detail_rank)

    def _raw_version_url(
        self, owner: str, repo: str, branch: str, path: str = "VERSION"
    ) -> str:
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

    def check_remote_version(
        self,
        owner: str,
        repo: str,
        branch: str,
        *,
        path: str = "VERSION",
        token: str | None = None,
        timeout: float = 10.0,
    ) -> tuple[bool, str | None]:
        """
        Checks whether the version on GitHub (VERSION file on a given branch)
        is newer than the local self.version.

        :param owner: GitHub repository owner
        :param repo: repository name
        :param branch: branch name (e.g. 'develop', 'release/2.0')
        :param path: path to the version file (default: 'VERSION')
        :param token: optional GitHub token for private repositories
        :param timeout: HTTP request timeout
        :return: (is_newer, remote_version)
        """
        url = self._raw_version_url(owner, repo, branch, path)
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code != 200:
                print(f"[Updater] Failed to download VERSION from {url} ({resp.status_code})")
                return (False, None)
            
            remote_txt = resp.text.strip()
            

        except requests.RequestException as e:
            print(f"[Updater] Network error: {e}")
            return (False, None)

        try:
            

            remote_tuple = self._parse_version(remote_txt)
            local_tuple = self._parse_version(self.version)
        except ValueError as e:
            print(f"[Updater] Version parsing error: {e}")
            return (False, remote_txt)
        
        is_newer = remote_tuple > local_tuple
        
        return (is_newer, remote_txt)

    def proceed_update_window(self):
        window_width, window_height = 400, 400
        viewport_width, viewport_height = (
            dpg.get_viewport_client_width(),
            dpg.get_viewport_client_height(),
        )
        pos_x = (viewport_width - window_width) // 2
        pos_y = (viewport_height - window_height) // 2
        try:
            with dpg.window(
                pos=(pos_x, pos_y),
                label="Update now?",
                tag="proceed_to_update_window",
                no_move=True,
                no_close=False,
                no_title_bar=False,
                show=True,
                modal=True,
                autosize=True,
                no_scrollbar=True,
            ):
                dpg.add_text(
                    "Press OK to install the files and close the program.",
                    tag="proceed_to_update_window_text",
                )
                dpg.bind_item_font("proceed_to_update_window_text", "DejaVu_bold")
                with dpg.group(tag="proceed_to_update_window_group", horizontal=True):
                    dpg.add_button(
                        label="OK",
                        tag="proceed_to_update_window_ok_butt",
                        show=True,
                        callback=self.proceed_window_OK,
                    )

                    dpg.add_button(
                        label="Close",
                        tag="proceed_to_update_window_close_butt",
                        show=True,
                        callback=self.proceed_window_close,
                    )

                dpg.bind_item_theme("proceed_to_update_window_ok_butt", "fit_button_theme")
                dpg.bind_item_theme("proceed_to_update_window_close_butt", "Error_window_theme")

        except Exception:
            dpg.show_item("No_data_files")

    def proceed_window_close(self):
        dpg.configure_item("proceed_to_update_window", show=False)
        dpg.delete_item("proceed_to_update_window_text")
        dpg.delete_item("proceed_to_update_window_ok_butt")
        dpg.delete_item("proceed_to_update_window_close_butt")
        dpg.delete_item("proceed_to_update_window_group")
        dpg.delete_item("proceed_to_update_window")

    def proceed_window_OK(self):
        # print("proceed_window_OK")
        window_size = dpg.get_item_rect_size("proceed_to_update_window")

        dpg.delete_item("proceed_to_update_window_ok_butt")
        dpg.delete_item("proceed_to_update_window_close_butt")
        dpg.delete_item("proceed_to_update_window_group")

        dpg.add_loading_indicator(
            parent="proceed_to_update_window",
            width=50,
            tag="tag_load_ind_update",
            pos=(
                dpg.get_item_width("proceed_to_update_window") / 2
                - (int(dpg.get_global_font_scale() * 25)),
                1 * dpg.get_item_height("proceed_to_update_window")
                - dpg.get_global_font_scale() * 25,
            ),
            color=self.hsv(2 / 7.0, 0.6, 0.6),
            secondary_color=self.hsv(0.223, 0.404, 0.846),
        )
        dpg.add_button(
            label="",
            tag="progress_button",
            show=True,
            pos=(
                0,
                1 * dpg.get_item_height("proceed_to_update_window")
                + dpg.get_global_font_scale() * 50,
            ),
            # callback=self.proceed_window_close
            parent="proceed_to_update_window",
            width=window_size[0],
        )

        dpg.bind_item_theme("progress_button", "transparent_theme")
        dpg.set_item_label("progress_button", "Downloading files")

        self.download_update(owner=self.owner, repo=self.repo, branch=self.branch)
        self.backup_old_files()

        self.Copying_new_files()

        for i in range(3, -1, -1):
            dpg.set_item_label(
                "progress_button",
                "Finished. FcsIT closes in: " + str(i) + " sec.",
            )
            time.sleep(1)

        dpg.delete_item("progress_button")
        dpg.delete_item("tag_load_ind_update")

        self.proceed_window_close()

        dpg.delete_item("proceed_to_update_window")
        dpg.stop_dearpygui()

    def backup_old_files(self):
        print('backup_old_files')
        current_dir = os.path.abspath(os.getcwd())

        bckp_dir = os.path.join(current_dir, "..", "old_backup")

        if os.path.exists(bckp_dir):
            print("[Updater] Removing old backup directory...")
            dpg.set_item_label("progress_button", "Removing old backup files")
            shutil.rmtree(bckp_dir, ignore_errors=True)

        os.makedirs(bckp_dir, exist_ok=True)
        metafiles = ["LICENSE",  'GPLv3_short',"VERSION"]
        
        print("[Updater] Backing up metafiles")
        dpg.set_item_label("progress_button", "Backing up meta files")
        for f in metafiles:
            
            source = os.path.join(current_dir, f)
            target = os.path.join(bckp_dir, f)
            # print(source)
            # print(target)
            shutil.copy2(source, target)

        # for d in FoldersToBackup:
        dpg.set_item_label("progress_button", "Backing up software directories")
        source = os.path.join(current_dir, "..")
        target = os.path.join(bckp_dir)
        # print(source)
        # print(target)
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                "*updt_tmp", "__pycache__", ".ipynb_checkpoints"
            ),
        )

    def Copying_new_files(self):
        current_dir = os.path.abspath(os.getcwd())
        tmp_dir = os.path.join(current_dir, "..", "updt_tmp")
        zip = os.listdir(tmp_dir)
        zip = [f for f in zip if f.endswith(".zip")][0]
        print(zip)
        dpg.set_item_label("progress_button", "Unzipping update")
        zip_path = os.path.join(tmp_dir, zip)
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmp_dir)
        except zipfile.BadZipFile:
            return None

        subfolders = [
            d for d in os.listdir(tmp_dir)
            if os.path.isdir(os.path.join(tmp_dir, d))
        ]

        if not subfolders:
            return None

        extracted_dir = subfolders[0]
        updt_dir = os.path.join(tmp_dir, extracted_dir)
        metafiles = ["LICENSE",  'GPLv3_short', "VERSION"]
        for f in metafiles:
            print("[Updater] Updating meta files ")
            dpg.set_item_label("progress_button", "Updating meta files")
            source = os.path.join(updt_dir, f)
            target = os.path.join(current_dir, f)
            # print(source)
            # print(target)
            shutil.copy(source, target)

        # FoldersToBackup = ["REWRITE_ROI", "smICA"]
        # for d in FoldersToBackup:
        print("[Updater] Updating software directories")
        dpg.set_item_label("progress_button", "Updating software directories")
        source = os.path.join(updt_dir, "src")
        target = os.path.join(current_dir)
        # print(source)
        # print(target)
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                "*updt_tmp", "__pycache__", ".ipynb_checkpoints"
            ),
        )

        dpg.set_item_label("progress_button", "Removing temporary files")
        # shutil.rmtree(tmp_dir, ignore_errors=True)

    def download_update(
        self,
        owner: str,
        repo: str,
        branch: str,
        *,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> str | None:
        """
        Downloads the current program files as a ZIP archive from the GitHub repository
        and saves them into the temporary directory 'updt_tmp'.

        :param owner: GitHub repository owner
        :param repo: repository name
        :param branch: branch name (e.g. 'develop', 'main')
        :param token: optional GitHub token (for private repositories)
        :param timeout: timeout in seconds
        :return: path to the temporary directory with downloaded/unpacked files, or None on error
        """
        current_dir = os.path.abspath(os.getcwd())

        tmp_dir = os.path.join(current_dir, "..", "updt_tmp")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)
        os.makedirs(tmp_dir, exist_ok=True)

        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        zip_path = os.path.join(tmp_dir, f"{repo}-{branch}.zip")

        try:
            with requests.get(zip_url, headers=headers, timeout=timeout, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.RequestException:
            return None

    def run_updater(self):
        is_newer, remote = self.check_remote_version(
            owner=self.owner,
            repo=self.repo,
            branch=self.branch,
            path=self.path,
        )
        theme_tag = dpg.get_item_theme("menu_about_dropout")

        if is_newer:
            self.updater_state = True
            dpg.bind_item_theme("menu_about_dropout", "menu_update_available")
            children = dpg.get_item_children("menu_about_dropout", 1)  # slot 1 = normal children

            for child in children:
                if str(child).isdigit():
                    child = dpg.get_item_alias(child)

                if child == "menu_Version_dropout_item":
                    dpg.bind_item_theme(child, "menu_update_available")
                    dpg.set_item_label(child, label="Current version: " + self.VERSION + "!")
                    dpg.bind_item_font(child, "DejaVu_bold")
                    dpg.add_menu_item(
                        label="New version: " + remote + " available, click to update now",
                        enabled=True,
                        tag="menu_Version_dropout_item_new",
                        parent="menu_about_dropout",
                        callback=self.proceed_update_window,
                    )
                    dpg.bind_item_theme("menu_Version_dropout_item_new", "menu_update_available_new")
                    dpg.bind_item_font("menu_Version_dropout_item_new", "DejaVu_bold")
                else:
                    dpg.bind_item_theme(child, "menu_normal")
        else:
            self.updater_state = False

class _basicF:
    
    
    def __init__(self, logfile,args):
        self.logfile = logfile
        if not args == None:
            self.ENABLE_TIMING = args.timing
            self.HOSTNAME = socket.gethostname()
            today_str = datetime.today().strftime('%Y-%m-%d')
            self.TIMING_FILE = os.path.join(self.logfile.replace('log.txt',''),"timelog_"+self.HOSTNAME+'_'+today_str+".txt")
        else:
            pass
    def log_it(self,text_to_log,mode):
        logf = open(self.logfile, mode)

        logf.write(text_to_log+'\n')
        logf.close()
    def timeit_it_init(self,text_to_log,mode):
        if not self.ENABLE_TIMING:
            pass
        else:
            cwd = os.getcwd()
            tfile = os.path.join(cwd,self.TIMING_FILE)
            logf = open(tfile, mode)

            logf.write(text_to_log+'\n')
            logf.close()
            
    
    def lnprint(self,*args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        line_number = caller_frame.f_lineno
        file_name = caller_frame.f_code.co_filename
        function_name = caller_frame.f_code.co_name
        print(f"File {file_name}, Function '{function_name}', Line {line_number}: ", end="\n")
        print(*args, **kwargs)    
        
    def _hsv_to_rgb(self,h, s, v):
        '''Funtion converts HSV color notation to the RGB values'''
        if s == 0.0: return (v, v, v)
        i = int(h*6.) 
        f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
        if i == 0: return (255*v, 255*t, 255*p)
        if i == 1: return (255*q, 255*v, 255*p)
        if i == 2: return (255*p, 255*v, 255*t)
        if i == 3: return (255*p, 255*q, 255*v)
        if i == 4: return (255*t, 255*p, 255*v)
        if i == 5: return (255*v, 255*p, 255*q)
    
    def decimal_rounds(self,num):
        '''Counts the meaning decimal places for the input value.'''
        if num > 0:
            lg=-log10((num))+4
        else:
            lg=0
        res = int(np.ceil(lg))
        if res<0:
            res=0

        return res
    
    def decimal_rounds_lim(self,num):
        '''Counts the meaning decimal places for the input value.'''
        if num > 0:
            lg=-log10((num))+4
        else:
            lg=0
        res = int(np.ceil(lg))
        if res>3:
            res=3
        elif res<0:
            res=0
        return res
    
    
    def zeros(self,num):
    
        '''Function rounds the input value.'''

        if num == 0:
            return 0
        else:
            dec = self.decimal_rounds(abs(num))
            if dec<=0:
                return int(np.round(num,dec))
            else:
                return np.round(num,dec)

#####################################################

    def zeros_chi(self,num):

        '''Function rounds the input value.'''

        if num == 0:
            return 0
        else:
            dec = self.decimal_rounds(abs(num))-2
            if dec<=0:
                return int(np.round(num,dec))
            else:
                return np.round(num,dec)

    #####################################################


    def callback_empty(self,sender,app_data):
        '''Empty function. Do nothing.'''
        pass
    
    def search_for_methods(self):
        path = 'Methods'
        methods = os.listdir(path)
        ind = []
        methods = [os.path.join(path,ad) for ad in methods if os.path.isdir(os.path.join(path,ad))]
        for i, method in enumerate(methods):
            met_files = os.listdir(method)
            met_files = [f for f in met_files if f.endswith('_config.json')]
            if len(met_files) == 1:
                ind.append(i)
        methods = list(np.array(methods)[ind])
        return methods
        
    def ifso(self,f):
            if type(f)  == bytes:
                f = f.decode("utf-8")
            else:
                pass
            return f
    
    def path_to_method_anal_menu_item(self,method_dir):
        met_files = os.listdir(method_dir)
        met_files = [ self.ifso(f) for f in met_files]
        met_files = [f for f in met_files if f.endswith('_config.json')]
        met_file = met_files[0]
        path = os.path.join(method_dir,met_file)
        with open(path) as json_settings:
            method_tree = json.load(json_settings)
        return method_tree['ANAL_MENU_ITEM']
    
    def method_config_dict(self,method_dir):
        met_files = os.listdir(method_dir)
        met_files = [ self.ifso(f) for f in met_files]
        met_files = [str(f) for f in met_files if str(f).endswith('_config.json')]
        met_file = met_files[0]
        path = os.path.join(method_dir,met_file)
        with open(path) as json_settings:
            method_tree = json.load(json_settings)

        return method_tree
    
    
    def path_to_method_anal_layout(self,method_dir):
        met_files = os.listdir(method_dir)
        met_files = [ self.ifso(f) for f in met_files]
        met_files = [f for f in met_files if f.endswith('_config.json')]
        met_file = met_files[0]
        path = os.path.join(method_dir,met_file)
        with open(path) as json_settings:
            method_tree = json.load(json_settings)
            
        return method_tree['LAYOUT']
    
    
    def split_path_into_folders(self,path):
        folders = []
        while True:
            path, folder = os.path.split(path)
            if folder != "":
                folders.append(folder)
            else:
                if path != "":
                    folders.append(path)
                break
        folders.reverse()
        return folders
    
    def log_last_directory(self,path):
        last_directory = {'last_directory':path}
        with open(self.logfile.replace('log.txt','last_dir.txt'), 'w') as f:
                json.dump(last_directory, f, indent=4, sort_keys=False)
    
    def recall_last_directory(self):
        path = self.logfile.replace('log.txt','last_dir.txt')
        try:
            with open(path) as directory:
                last_directory = json.load(directory)
            
            return last_directory['last_directory']
        except:
            pass
    @staticmethod
    def some_fail():
        caller_frame = inspect.currentframe().f_back
        line_number = caller_frame.f_lineno
        
        file_name = caller_frame.f_code.co_filename
        function_name = caller_frame.f_code.co_name
        print('Coś się zdupcyło \U0001F633','\n',end='\n')
        print(f"File:\n \t{file_name},\n Function: \t'{function_name}',\n Line: \t{line_number} ", end="\n")
BASF = None 
    
    
##############################################################################    
class _init_varaibles:
    
    def __init__(self):
        
        self.init_size_ratio = {'width':1,
                          'height':1}
        self.init_top_indent = 24+11
        self.init_bottom_indent = 11
        self.init_left_indent = 11
        self.init_right_indent = 11
        self.init_internal_indent = 11
        self.init_group_spacer = 2
        self.init_font_size = 18
        self.VIEWPORT_prop = {'width':1523,
                              'height':935+2*11,
                              'pos':(0,0)
                                }
        
        
        
        
        
        self.mounted_method = None
        self.icopath()
        
        
        
    def icopath(self):
        osname = os.name

        if osname == 'posix':

            ico_path=os.path.join('res','icons','FcsIT.png')
            
        else:
            ico_path=os.path.join('res','icons','FcsIT.ico')
            self.init_bottom_indent = 2*11
            self.init_right_indent = 2*11
        return ico_path
    
    
class _init_Menu:
    def __init__(self, VERSION, docs_dir, docs_server):
        self.VERSION = VERSION
        self.docs_dir = docs_dir
        self.docs_server = docs_server

    def callback_help(self, sender, app_data):
        self.show_docs_callback()

    def show_docs_callback(self):
        try:
            url = self.docs_server.start()
            print(f"[DOCS] Documentation opened: {url}")
        except Exception as exc:
            print(f"[DOCS] Failed to open documentation: {exc}")

    def on_exit(self):
        self.docs_server.stop()

    
    def callback_full_screen(self,sender,app_data):
        dpg.toggle_viewport_fullscreen()
        
        
    def callback_main_Keyword_key(self,sender,app_data):
        F1_key = dpg.mvKey_F1
        F11_key = dpg.mvKey_F11
        if app_data == F1_key:
            callback_help('helpclick',False)
        if app_data == F11_key:
            self.callback_full_screen('fullscreenclick',app_data)
        
    def callback_help(self,sender,app_data):
        # url = os.path.join(self.docs_dir,'index.html')
        # webbrowser.open(url,new=2)
        self.show_docs_callback()
        
    def callback_license(self,sender,app_data):
        if not 'License_title' in dpg.get_aliases():
            with dpg.window(tag='License_win',width=dpg.get_viewport_width()/2,
                            height=dpg.get_viewport_height()/2,
                                pos = (dpg.get_viewport_width()/4,
                                       dpg.get_viewport_height()/4),
                                menubar=False,
                                autosize=False,
                                no_resize=True,
                                no_title_bar=False,
                                no_move=True,
                            modal=True,
                            show=True):
                dpg.add_button(tag='License_title',width=dpg.get_viewport_width()/2,label='LICENSE')
                dpg.bind_item_theme('License_title', 'transparent_theme')
                with open('LICENSE', 'r') as file:
                    License = file.read()
                dpg.add_text(label='License',
                             tag='license_text',
                             default_value = License,
                             wrap = int(0.95*(dpg.get_viewport_width()/2)))
        else:
            dpg.delete_item('license_text')
            dpg.delete_item('License_title')
            dpg.delete_item('License_win')
            with dpg.window(tag='License_win',width=dpg.get_viewport_width()/2,
                            height=dpg.get_viewport_height()/2,
                            pos = (dpg.get_viewport_width()/4,
                                   dpg.get_viewport_height()/4),
                            menubar=False,
                            autosize=False,
                            no_resize=True,
                            no_title_bar=False,
                            no_move=True,
                            modal=True,
                            show=True):
                dpg.add_button(tag='License_title',width=dpg.get_viewport_width()/2,label='LICENSE')
                dpg.bind_item_theme('License_title', 'transparent_theme')
                with open('LICENSE', 'r') as file:
                    License = file.read()
                dpg.add_text(label='License',
                             tag='license_text',
                             default_value = License,
                             wrap = int(0.95*(dpg.get_viewport_width()/2)))
    
    
    def callback_no_feature_yet(self):
        try:
            dpg.add_window(pos=(400,150),
                           label='Error!',
                           tag='No_feature_window',
                           no_move=True,
                           no_close=True,
                           no_title_bar=False,
                           no_resize=True,
                           show=True,
                           modal=False
                           )
            dpg.add_text('This Feature is not yet available!',
                         tag='No_feature_error_text',
                         parent='No_feature_window')
            dpg.add_button(label='Close',
                           parent='No_feature_window',
                           tag='No_feature_error_butt',
                           callback=self.callback_no_feature_dialog_close_only
                          )
            dpg.bind_item_theme('No_feature_window', 'Error_window_theme')
            
        except:
            dpg.show_item('No_feature_window')

    def callback_no_feature_dialog_close_only(self,sender,app_data):
        dpg.configure_item('No_feature_window',show=False)
        dpg.delete_item('No_feature_error_text')
        dpg.delete_item('No_feature_error_butt')
        dpg.delete_item('No_feature_window')
    
    
    
    
    def mount_main_Menu_bar(self):
        with dpg.viewport_menu_bar(tag="vieport's_menubar"):
            with dpg.menu(label="File",tag='menu_file_dropout'):
                dpg.add_menu_item(label="Exit",callback=lambda: dpg.stop_dearpygui(),tag='menu_item_exit')
            with dpg.menu(label="Methods",tag='menu_analysis_method_dropout'):
                pass
            with dpg.menu(label="Settings",tag='menu_settings_dropout'):
                dpg.add_menu_item(label="Full Screen (F11)",tag='fullscreenclick',callback=self.callback_full_screen)
                dpg.add_menu_item(label="Settings",
                                  # callback=lambda: dpg.show_item("Settings_window"),
                                  parent = 'menu_settings_dropout',
                                  before='fullscreenclick',
                                  tag='sett_menu_item')
            with dpg.menu(label="About",tag='menu_about_dropout'):
                dpg.add_menu_item(label="Help",tag='helpclick',callback=self.callback_help)
                dpg.add_menu_item(label='License',callback = self.callback_license,tag='Licenseclick')
                dpg.add_menu_item(label='Version: '+self.VERSION,tag='menu_Version_dropout_item',enabled=False)


                
                
                
class _common_VARIABLES:
    def __init__(self):
        self.windows = []
        self.items = []
        self.last_directory = 'samples'
        self.directory = ''


class ChunksMinMax:
    def __init__(self, x: np.ndarray, block_size: int = 32768):
        x = np.asarray(x, dtype=float)
        self.x = x
        self.n = x.size
        self.bs = int(block_size)
        self.nb = int(math.ceil(self.n / self.bs))
        bmin = np.empty(self.nb, dtype=float)
        bmax = np.empty(self.nb, dtype=float)
        for i in range(self.nb):
            a = i * self.bs
            b = min(self.n, a + self.bs)
            seg = x[a:b]
            bmin[i] = np.nanmin(seg) if seg.size else np.inf
            bmax[i] = np.nanmax(seg) if seg.size else -np.inf

        self.bmin = bmin
        self.bmax = bmax

    def query(self, l: int, r: int):
        if l < 0: l = 0
        if r > self.n: r = self.n
        if r <= l:
            return np.nan, np.nan

        x = self.x
        bs = self.bs
        bmin = self.bmin
        bmax = self.bmax
        bl = l // bs
        br = (r - 1) // bs
        if bl == br:
            seg = x[l:r]
            return np.nanmin(seg), np.nanmax(seg)
        mn = np.inf
        mx = -np.inf
        left_end = (bl + 1) * bs
        seg = x[l:left_end]
        v = np.nanmin(seg); mn = v if v < mn else mn
        v = np.nanmax(seg); mx = v if v > mx else mx
        for b in range(bl + 1, br):
            v = bmin[b]; mn = v if v < mn else mn
            v = bmax[b]; mx = v if v > mx else mx

        right_start = br * bs
        seg = x[right_start:r]
        v = np.nanmin(seg); mn = v if v < mn else mn
        v = np.nanmax(seg); mx = v if v > mx else mx

        return mn, mx




class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        path = Path(self.directory) / self.path.lstrip("/")

        if path.exists():
            return super().do_GET()

        self.path = "/index.html"
        return super().do_GET()



class LocalDocsServer:
    """
    Lightweight local HTTP server for static HTML documentation.
    """

    def __init__(self, root_dir, host="127.0.0.1", port=0):
        self.root_dir = Path(root_dir).resolve()
        self.host = host
        self.port = port
        self.httpd = None
        self.thread = None
        self.url = None

    def start(self):
        handler = lambda *args, **kwargs: SPARequestHandler(
            *args,
            directory=str(self.root_dir),
            **kwargs
        )

        if self.httpd:
            webbrowser.open(self.url)
            return self.url
        
        self.httpd = socketserver.TCPServer((self.host, self.port), handler)
        port = self.httpd.server_address[1]
        self.url = f"http://{self.host}:{port}"

        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

        print(f"Server running at: {self.url}")
        webbrowser.open(self.url)
        return self.url

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()



class sett_window:
    def __init__(self,init_VP_size,left_indent,internal_indent,right_indent,bottom_indent,top_indent,group_spacer):
        self.init_VP_size = init_VP_size

    
        
        
        self.size_ratio = {'width': np.round(dpg.get_viewport_width()/self.init_VP_size['width'],4),
             'height': np.round(dpg.get_viewport_height()/self.init_VP_size['height'],4)} 

        self.left_indent = int(left_indent*self.size_ratio['width'])
        self.internal_indent = int(internal_indent*self.size_ratio['width'])
        self.right_indent = int(right_indent*self.size_ratio['width'])
        self.bottom_indent = int(bottom_indent*self.size_ratio['width'])
        self.top_indent = int(top_indent*self.size_ratio['width'])
        self.group_spacer = int(group_spacer*self.size_ratio['width'])
        
        self.Settings_window = {'width':int(600*self.size_ratio['width']),
                              'height':int(700*self.size_ratio['height']),
                              'pos':(int(300*self.size_ratio['width']),int(200*self.size_ratio['height']))
                                }
        self.Setts_save_defaults = int(150*self.size_ratio['width'])
        self.Setts_cancel = int(150*self.size_ratio['width'])

        self.default_quick_export_filename = int(200*self.size_ratio['width'])
        self.default_quick_stst_filename = int(200*self.size_ratio['width'])
        
        self.settings_items = []

        dpg.configure_item('sett_menu_item',callback=self.show_set_win)
        self.OPTIONS = {}
        self.MountSettingsWindow()
        self.load_default_settings()
        print('init')

        
    def load_default_settings(self):
        path = os.path.join('res','JSON_files','Default_settings.json')

        with open(path) as json_settings:
            self.OPTIONS = json.load(json_settings)

        for item in self.OPTIONS.keys():
            dpg.set_value(item,self.OPTIONS[item])
    def show_set_win(self):
        

        self.size_ratio = {'width': np.round(dpg.get_viewport_width()/self.init_VP_size['width'],4),
             'height': np.round(dpg.get_viewport_height()/self.init_VP_size['height'],4)} 

        left_indent = int(self.left_indent*self.size_ratio['width'])
        internal_indent = int(self.internal_indent*self.size_ratio['width'])
        right_indent = int(self.right_indent*self.size_ratio['width'])
        bottom_indent = int(self.bottom_indent*self.size_ratio['width'])
        top_indent = int(self.top_indent*self.size_ratio['width'])
        group_spacer = int(self.group_spacer*self.size_ratio['width'])
        
        Settings_window = {'width':int(600*self.size_ratio['width']),
                              'height':int(700*self.size_ratio['height']),
                              'pos':(int(300*self.size_ratio['width']),int(200*self.size_ratio['height']))
                                }

        Setts_save_defaults_width = int(150*self.size_ratio['width'])
        Setts_cancel_width = int(150*self.size_ratio['width'])

        default_quick_export_filename_width = int(200*self.size_ratio['width'])
        default_quick_stst_filename_width = int(200*self.size_ratio['width'])
        
        
        dpg.configure_item('Settings_window',
                           width = Settings_window['width'],
                           height = Settings_window['height'],
                           pos = Settings_window['pos']
                          )
        # print(dpg.get_item_width('Settings_window'),dpg.get_item_height('Settings_window'))
        button_pos = (left_indent,dpg.get_item_height('Settings_window')-24-bottom_indent)
        # print(button_pos)
        dpg.configure_item('default_theme_group',
                           horizontal_spacing = group_spacer
                          )

        dpg.configure_item('theme_choose',
                           width = int(Settings_window['width']/3),
                          )

        dpg.configure_item('default_quick_res_exp_group',
                           horizontal_spacing = group_spacer
                          )

        dpg.configure_item('default_quick_res_stat_group',
                           horizontal_spacing = group_spacer
                          )

        dpg.configure_item('default_quick_stst_filename',
                           width = default_quick_export_filename_width,
                          )

        dpg.configure_item('Setts_buttons_group',
                           horizontal_spacing = group_spacer,
                           pos = (left_indent,dpg.get_item_height('Settings_window')-24-bottom_indent)
                          )

        dpg.configure_item('Setts_save_defaults',
                           width = Setts_save_defaults_width
                          )

        dpg.configure_item('Setts_cancel',
                           width = Setts_cancel_width
                          )
                           

        
        dpg.show_item('Settings_window')

    def hide_set_win(self):
        dpg.hide_item('Settings_window')
    def callback_save_as_def(self,sender,app_data):
        items = ['Sett_export_each',
                 'Sett_export_to_excel',
                 'Sett_export_plot_as_png',
                 'Sett_export_to_csv',
                 'Sett_export_plot_as_csv',
                 'Sett_export_to_pickle',
                 'Sett_export_plot_as_pickle',
                 'Sett_export_stats',
                 'Sett_export_plot_loglog',
                 'Sett_export_stats_to_csv',
                 'Sett_export_stats_to_xlsx',
                 'Sett_export_stats_to_pickle',
                 'Sett_preserve_time',
                 'Sett_preserve_units',
                 'default_quick_export_filename',
                 'default_quick_stst_filename',
                 'theme_choose']
        
        self.OPTIONS = {}
        
        for item in items:
            
            self.OPTIONS[item]=dpg.get_value(item)

        
        path = os.path.join('res','JSON_files','Default_settings.json')
        with open(path, 'w') as f:
            json.dump(self.OPTIONS, f, indent=4, sort_keys=False)
        dpg.configure_item(sender,enabled=False)   
        self.hide_set_win()
    def callback_settings_data_stats(self,sender,app_data):   
        items = ['Sett_export_stats_to_csv','Sett_export_stats_to_xlsx',]
        dpg.configure_item('Setts_save_defaults',enabled=True)
        if app_data:
            for item in items:
                dpg.configure_item(item, enabled = True)
        else:
            for item in items:

                dpg.configure_item(item, enabled = False)
    def callback_settings_data_export_each(self,sender,app_data): 
        items = ['Sett_export_to_excel','Sett_export_to_csv','Sett_export_to_pickle']
        dpg.configure_item('Setts_save_defaults',enabled=True)
        if app_data:
            for item in items:
                dpg.configure_item(item, enabled = True)
        else:
            for item in items:
                dpg.configure_item(item, enabled = False)

    

    def UnMountSettingsWindow(self):
        # print('Unmounting')
        # print(self.settings_items)
        for item in self.settings_items:
            # print(item)
            dpg.delete_item(item)
    def MountSettingsWindow(self):
        with dpg.window(label='Settings',
                    tag="Settings_window",
                    width=self.Settings_window['width'],
                    height=self.Settings_window['height'],
                    pos=self.Settings_window['pos'],
                    no_resize=True,
                    show=False,
                    modal = True,
                    autosize=False,
                    on_close = self.hide_set_win
                   ):
            dpg.add_text('General settings',
                         tag='General_settings_text')
            dpg.add_separator(tag ='Settings_sep1',show=True)  
            with dpg.group(tag='default_theme_group',
                       horizontal=True,
                       horizontal_spacing=self.group_spacer,
                              before = 'Settings_sep2'
                      ):
                dpg.add_text('Theme: ',tag = 'sett_theme_group_text_01')
                dpg.add_combo(['dark','light'],
                          label="",
                          width=int(self.Settings_window['width']/3),
                          height_mode=dpg.mvComboHeight_Large,
                          tag='theme_choose',
                          default_value='dark',
                          callback=None,
                          enabled=True
                          )
                with dpg.tooltip('theme_choose',tag='theme_choose_tooltip'):
                            dpg.add_text('The change will be visible after restarting the FcsIT.',
                                         tag='theme_choose_tooltip_text')
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
                                     callback=self.callback_settings_data_export_each
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
                        dpg.add_checkbox(label='Export as .xlsx',
                                     tag='Sett_export_to_excel',
                                     default_value=False,
                                     enabled = True,
                                     callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                                    )
                        with dpg.tooltip('Sett_export_to_excel',tag='Setts_c1_r2_cell_tooltip'):
                            dpg.add_text('Each data will be quick saved to ".xlsx" file.',
                                         tag='Setts_c1_r2_cell_tooltip_text')
                            
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
                                     callback=self.callback_settings_data_stats
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
                        dpg.add_checkbox(label="Statistics to .xlsx",
                                     tag='Sett_export_stats_to_xlsx',
                                     default_value=True,
                                     enabled = True,
                                     callback=lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                                    )
                       
                        with dpg.tooltip('Sett_export_stats_to_xlsx',tag='Setts_c1_r7_cell_tooltip'):
                            dpg.add_text('Export stats to the ".xlsx" file.',
                                        tag='Setts_c1_r7_cell_tooltip_text')
                            
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
                           horizontal_spacing=self.group_spacer
                          ):
                dpg.add_text('Filename for quick export: ',tag = 'sett_group_01_text_01')
                dpg.add_input_text(tag = 'default_quick_export_filename',
                                   width=self.default_quick_export_filename,
                                   default_value = 'results_temp',
                                   callback = lambda: dpg.configure_item('Setts_save_defaults',enabled=True)
                                  )
                dpg.add_text('.*',tag = 'sett_group_01_text_02')
                with dpg.tooltip('default_quick_export_filename',tag='sett_group_01_text_02_tooltip'):
                    dpg.add_text('Enter the filename without extension.',tag='sett_group_01_text_02_tooltip_text')
            with dpg.group(tag='default_quick_res_stat_group',
                           horizontal=True,
                           horizontal_spacing=self.group_spacer):
                dpg.add_text('Filename for statistics export: ',tag='default_quick_res_stat_group_text_1')
                dpg.add_input_text(tag = 'default_quick_stst_filename',
                                   width=self.default_quick_stst_filename,
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
                           horizontal_spacing=self.group_spacer,pos = (self.left_indent,dpg.get_item_height('Settings_window')-24-self.bottom_indent)):
                dpg.add_button(label='Save as defaults',
                                       tag='Setts_save_defaults',
                                       show=True,
                                       width = self.Setts_save_defaults,
                                       callback=self.callback_save_as_def
                                      )
                # dpg.bind_item_theme('Setts_save_defaults', 'fit_button_theme')
                
                dpg.add_button(label='Close',
                                       tag='Setts_cancel',
                                       show=True,
                                       
                                       width = self.Setts_cancel,
                                       callback=self.hide_set_win
                                      )
                dpg.bind_item_theme('Setts_save_defaults', 'fit_button_theme')
                dpg.bind_item_theme('Setts_cancel', 'fit_button_theme')
                
        dpg.bind_item_theme('Settings_window', 'Inactive_checkbox') 
        
        
        self.settings_items = ['Settings_window',
                          'General_settings_text',
                          'Settings_sep1',
                          'default_theme_group',
                          'sett_theme_group_text_01',
                          'theme_choose',
                               'theme_choose_tooltip',
                               'theme_choose_tooltip_text',
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
                          'Setts_c1_r2_cell', 'Sett_export_to_excel','Setts_c1_r2_cell_tooltip','Setts_c1_r2_cell_tooltip_text',
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
                          'Setts_c1_r7_cell','Sett_export_stats_to_xlsx','Setts_c1_r7_cell_tooltip','Setts_c1_r7_cell_tooltip_text',
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
        
                