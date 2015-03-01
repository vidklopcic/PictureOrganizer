# coding=utf-8
import os
import time
import re
import shutil
import datetime
import exifread
import sys

__author__ = 'vid'


class Core(object):
    def __init__(self, source_dirs=None, output_dir=None, formats_filter=None, mode='move', remove_duplicates=True,
                 img_name='{old}', folder_name='{old}', remove_date_from_old_dir_name=False, reference=None,
                 go_back=False):
        self.go_back = go_back
        self.reference = reference
        self.duplicate_names = [''] + [' (' + str(i) + ')' for i in range(1000)]
        self.mode = mode
        self.filter = formats_filter
        self.recursive = True  # TODO
        self.remove_duplicate_images = remove_duplicates

        # dir naming
        self.folder_name = folder_name  # %Y-ear %m-onth %d-day %H-hour %M-minute %S-second {old} - old name
        self.remove_date_from_dir_name = remove_date_from_old_dir_name  # remove everything from beginning to first alphabet character

        # image naming
        self.img_name = img_name  # %Y-ear %m-onth %d-day %H-hour %M-minute %S-second {old} - old name | %H;%M ({old})
        if source_dirs and output_dir:
            self.rename_and_sort(source_dirs, output_dir)

    def update_gui(self, back=False, close=False):
        if close:
            self.reference.dialog.Close()
        if back:
            self.reference.dialog.browser.GoBack()
            return
        self.reference.dialog.browser.RunScript('''
        $('#progressbar>div').width('{percent}%');
        '''.replace('{percent}', self.percentage))

    def rename_and_sort(self, source_dirs, destination):
        not_coppied = 0
        if self.remove_duplicate_images:
            files_list = self.no_duplicates(source_dirs)
        else:
            files_list = self.allow_duplicates(source_dirs)
        for img in files_list:
            self.percentage = str(float(files_list.index(img)) / len(files_list) * 100.)
            if self.reference:
                from wx.richtext import wx
                wx.CallAfter(self.update_gui)
            root, filename, extension = img
            if destination not in root:
                date_taken = self.get_date_created(os.path.join(root, filename))

                # folder naming
                new_dir_name = date_taken.strftime(self.folder_name)
                old_dir_name = os.path.basename(root)
                if self.remove_date_from_dir_name:
                    old_dir_name = re.split('^[0-9-_.\s]+', old_dir_name, 1)[-1]
                try:
                    new_dir_name = new_dir_name.replace('{old}', old_dir_name).strip()
                except:
                    pass

                # img naming
                new_img_name = date_taken.strftime(self.img_name)
                try:
                    new_img_name = new_img_name.replace('{old}', filename.split('.')[0])
                except:
                    pass
                new_img_name += '.' + extension

                # copy / move, mkdirs
                dest_path = os.path.join(destination, new_dir_name)
                try:
                    os.makedirs(dest_path)
                except Exception, e:
                    if 'File exists' not in str(e):
                        print e
                for i in self.duplicate_names:
                    try:
                        print filename + ' --> ' + dest_path, new_img_name + i
                        if self.mode == 'copy':
                            shutil.copy(os.path.join(root, filename), os.path.join(dest_path, new_img_name + i))
                        elif self.mode == 'move':
                            shutil.move(os.path.join(root, filename), os.path.join(dest_path, new_img_name + i))
                        break
                    except Exception, e:
                        print e
            else:
                not_coppied += 1
        print not_coppied, 'images not copied'
        self.percentage = '100'
        if self.reference:
            wx.CallAfter(self.update_gui)
            time.sleep(.2)
        if self.go_back and self.reference:
            wx.CallAfter(lambda: self.update_gui(back=True))
        elif self.reference:
            self.reference.dialog.Close()

    def get_date_created(self, path):
        with open(path, 'rb') as f:
            try:
                date_taken = datetime.datetime.fromtimestamp(time.mktime(
                    time.strptime(str(exifread.process_file(f)['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S'))
                )
            except:
                date_taken = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        return date_taken

    def no_duplicates(self, source_dirs):
        result = {}
        counter = 0
        for source_dir in source_dirs:
            for root, dirnames, filenames in os.walk(unicode(source_dir)):
                for filename in filenames:
                    counter += 1
                    path = os.path.join(root, filename)
                    if len(filename.split('.')) > 1:
                        result[filename + str(os.path.getsize(path))] = [root, filename,
                                                                         filename.split('.')[-1].lower()]
                    else:
                        result[filename + str(os.path.getsize(path))] = [root, filename, '']
        print 'removed ' + str(counter - len(result)) + ' duplicates'
        if self.filter:
            result = [result[i] for i in result if result[i][2] in self.filter]
        else:
            result = [result[i] for i in result]
        return result

    def allow_duplicates(self, source_dirs):
        result = []
        for source_dir in source_dirs:
            for root, dirnames, filenames in os.walk(unicode(source_dir)):
                for filename in filenames:
                    if len(filename.split('.')) > 1:
                        result.append([root, filename, filename.split('.')[-1].lower()])
                    else:
                        result.append([root, filename, ''])
        if self.filter:
            result = [i for i in result if i[2] in self.filter]
        return result


if __name__ == '__main__':
    t = Core(mode='move',
             formats_filter=['jpg', 'mov', 'mp4', 'png', 'wmv', 'avi', 'tif', 'mts', 'jpeg'],
             remove_duplicates=True,
             img_name='%H;%M ({old})',
             folder_name='%Y_%m_%d')

    t.rename_and_sort([r'source_dir'],
                       r'destination_dir')