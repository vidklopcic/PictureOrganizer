import codecs
import pickle
import threading
import urllib2
import sys
import time
import requests
import os
import wx
import wx.html2
import json
from core import Core

codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

try:
    import uniconsole

    config_path = os.getenv('appdata')
    script_path = sys.argv[0]
except:
    print 'op sys is linux'
    script_path = os.path.realpath(__file__)
    config_path = os.path.dirname(script_path)
print script_path


class PicturesOrganizer():
    def __init__(self):
        self.html_events = {
            'source_dir_selector': self.source_dir_selector,
            'output_dir_selector': self.output_dir_selector,
            'naming_help': self.open_naming_help,
            'save_setting': self.save_profile,
            'start_setting': self.start_copying_with_parameters,
            'load_config': self.load_config  # loads directories from previous usage if there save file
        }
        threading.Thread(target=self.add_to_run_counter).start()
        self.gui_thread()

    def add_to_run_counter(self):
        try:
            requests.request('GET', 'http://bit.ly/po_stats')
        except:
            pass

    def gui_thread(self):
        app = wx.App()
        monitor_size = wx.Display(0).GetGeometry().GetSize()
        self.dialog = MainWindow(self, None, -1)
        self.dialog.Show()
        self.dialog.SetSize((monitor_size[0] / 2, monitor_size[1] / 1.2))
        self.dialog.Maximize()
        try:
            with open(sys.argv[1], 'r') as f:
                args = pickle.load(f)
                self.start_copying_with_parameters(args, goback=False)
        except:
            self.dialog.browser.LoadURL(
                'file:///' + os.path.join(os.path.dirname(script_path), 'gui', 'main.html').replace('\\', '/'))
        app.MainLoop()

    def load_config(self):
        try:
            with open(os.path.join(config_path, 'config'), 'r') as f:
                prev_params = pickle.load(f)
                self.change_source_dir(prev_params[0][0], '0')
                for i in range(len(prev_params[0]) - 1):
                    self.dialog.browser.RunScript('''
                    $('#source_section').append('<input type="text" class="source_dir" id="source_dir' + src_counter + '"><button class="select_source_dir" onclick="window.location=\'event:source_dir_selector|'+src_counter+\';">...</button><br>');
                    src_counter ++;
                    ''')
                    self.change_source_dir(prev_params[i], str(i))
                print prev_params
                self.change_output_dir(prev_params[1])
        except Exception, e:
            print e

    def html_catch(self, event):
        if 'event' in event.GetURL():
            command = urllib2.unquote(event.GetURL().split('event:')[1])
            if '|' in command:
                command, args = command.split('|')
                self.html_events[command](args)
            else:
                self.html_events[event.GetURL().split('event:')[1]]()
            event.Veto()

    def source_dir_selector(self, nr):
        dialog = wx.DirDialog(None, "Choose the source directory", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.change_source_dir(dialog.GetPath(), nr)
        dialog.Destroy()

    def output_dir_selector(self):
        dialog = wx.DirDialog(None, "Choose the output directory", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.change_output_dir(dialog.GetPath())
        dialog.Destroy()

    def change_source_dir(self, path, nr):
        if not path:
            return
        self.dialog.browser.RunScript('''
            $('#source_dir{nr}').val('{value}');
        '''.replace('{value}', path.replace('\\', '\\\\')).replace('{nr}', nr))

    def change_output_dir(self, path):
        if not path:
            return
        self.dialog.browser.RunScript('''
            $('#output_dir').val('{value}');
        '''.replace('{value}', path.replace('\\', '\\\\')))

    def open_naming_help(self):
        self.helper = HelperWindow(None, -1)
        self.helper.Show()
        self.helper.SetSize((500, 500))
        self.helper.browser.LoadURL(
            'file:///' + os.path.join(os.path.dirname(script_path), 'gui', 'helper.html').replace('\\', '/'))
        try:
            self.helper.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.helper_navigating, self.helper.browser)
        except:
            self.helper.Bind(wx.html2.EVT_WEB_VIEW_NAVIGATING, self.helper_navigating, self.helper.browser)

    def helper_navigating(self, event):
        if not 'helper.html' in event.GetURL():
            monitor_size = wx.Display(0).GetGeometry().GetSize()
            self.helper.SetSize((monitor_size[0] / 2, monitor_size[1] / 1.2))

    def start_copying_with_parameters(self, params, goback=True):
        self.dialog.browser.LoadURL(
            'file:///' + os.path.join(os.path.dirname(script_path), 'gui', 'progress.html').replace('\\', '/'))
        with open(os.path.join(config_path, 'config'), 'w') as f:
            pickle.dump(json.loads(params), f)
        t = threading.Thread(target=self.working_thread, args=[params, goback])
        t.start()

    def working_thread(self, params, go_back):
        time.sleep(0.5)
        Core(*json.loads(params), reference=self, go_back=go_back)
        wx.CallAfter(self.kill)

    def kill(self):
        self.dialog.Close()

    def save_profile(self, params):
        with open(os.path.join(config_path, 'config'), 'w') as f:
            pickle.dump(json.loads(params), f)
        save_file = easygui.filesavebox(default='organize_profile', filetypes=['*.po']) + '.po'
        with open(save_file, 'w') as f:
            pickle.dump(params, f)
        print params


class MainWindow(wx.Frame):
    def __init__(self, pic_org, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        try:
            self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, pic_org.html_catch, self.browser)
        except:
            self.Bind(wx.html2.EVT_WEB_VIEW_NAVIGATING, pic_org.html_catch, self.browser)


class HelperWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)


if __name__ == '__main__':
    a = PicturesOrganizer()
