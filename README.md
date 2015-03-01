PictureOrganizer
================
PictureOrganizer is script for advanced sorting of photos. You have full control of naming, and folder structure.
<br><br>
You can download program bundled with gui from SourceForge - http://sourceforge.net/projects/picturemessorganizer/

Features
----------------
- assemble name from many parameters retrieved from original file and folder (<code>%Y_%m_%d ({old})</code> would translate to <code>year_month_day (original filename)</code>)
- filter files by extension
- remove duplicates, based on size and date
- if copying from old archive you can remove date from beginning and keep previous name of already sorted directories. (<code>2014_01_01 new year</code> would set <code>{old}</code> parameter to <code>new year</code>, which means you can change date format)

Usage
----------------
###GUI
Run ```python PictureOrganizer.py``` or ```python PictureOrganizer.py profile.po``` to start copying from saved profile.

###Command line
Import Core.py and create instance with following parameters
```

```
#####Example
``` python
import Core as PictureOrganizer
po = PictureOrganizer(mode='move',
         formats_filter=['jpg', 'mov', 'mp4', 'png', 'wmv', 'avi', 'tif', 'mts', 'jpeg'],
         remove_duplicates=True,
         img_name='%H;%M ({old})',
         folder_name='%Y_%m_%d')

po.rename_and_sort([r'source_dir_a', 'source_dir_b],
                   r'destination_dir')
```




Dependencies
----------------
* Exifread - https://pypi.python.org/pypi/ExifRead
* wxPython >= 2.9 - http://wiki.wxpython.org/CheckInstall
