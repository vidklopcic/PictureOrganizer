import codecs
import pickle
import threading
import urllib2
import sys
import time
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
    date_from_name = False

    def __init__(self):
        self.html_events = {
            'source_dir_selector': self.source_dir_selector,
            'output_dir_selector': self.output_dir_selector,
            'naming_help': self.open_naming_help,
            'all_codes': self.open_all_codes_help,
            'save_setting': self.save_profile,
            'start_setting': self.start_copying_with_parameters,
            'toggle_date_from_name': self.toggle_date_from_name,
            'load_config': self.load_config  # loads directories from previous usage if there save file
        }
        self.gui_thread()

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
                self.change_date_from_name(prev_params[8], prev_params[9])
                if prev_params[3] == 'copy':
                    self.dialog.browser.RunScript('''
                        $('#mode_copy').click();
                    ''')
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

    def open_all_codes_help(self):
        self.helper = HelperWindow(None, -1)
        self.helper.Show()
        self.helper.SetSize((500, 500))
        self.helper.browser.LoadURL(
            'file:///' + os.path.join(os.path.dirname(script_path), 'gui', 'all_codes.html').replace('\\', '/'))
        try:
            self.helper.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.helper_navigating, self.helper.browser)
        except:
            self.helper.Bind(wx.html2.EVT_WEB_VIEW_NAVIGATING, self.helper_navigating, self.helper.browser)

    def helper_navigating(self, event):
        if not 'helper.html' in event.GetURL():
            monitor_size = wx.Display(0).GetGeometry().GetSize()
            self.helper.SetSize((monitor_size[0] / 2, monitor_size[1] / 1.2))

    def toggle_date_from_name(self):
        if self.date_from_name:
            self.dialog.browser.RunScript('''
                $('#date_from_name').addClass('date_from_name_disabled');
                $('#date_from_name').prop('disabled', true);
                $('#date_from_name_help').css('visibility', 'hidden');
                                ''')
        else:
            self.dialog.browser.RunScript('''
                $('#date_from_name').removeClass('date_from_name_disabled');
                $('#date_from_name').prop('disabled', false);
                $('#date_from_name_help').css('visibility', 'visible');
                                            ''')
        self.date_from_name = not self.date_from_name

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
        dialog = wx.FileDialog(None, "Save profile as", os.path.expanduser("~/Desktop"), "", "*.po",
                               wx.SAVE | wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            with open(dialog.GetPath(), 'w') as f:
                pickle.dump(params, f)
        dialog.Destroy()

    def change_date_from_name(self, use, param):
        if use == 'true':
            self.toggle_date_from_name()
            self.dialog.browser.RunScript('''
                            $('#enable_date_from_name').prop('checked', true);
                                                        ''')
        self.dialog.browser.RunScript('''
                        $('#date_from_name').val('%s');
                                                    ''' % param)


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
