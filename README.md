PictureOrganizer
================
PictureOrganizer is script for advanced sorting of photos. You have full control of naming, and folder structure.
<br>
You can download program with gui included from SourceForge - http://sourceforge.net/projects/picturemessorganizer/

Features
----------------
- assemble name from many parameters retrieved from original file and folder (<code>%Y_%m_%d ({old})</code> would translate to <code>year_month_day (original filename)</code>)
- filter files by extension
- remove duplicates, based on size and date
- if copying from old archive you can remove date from beginning and keep previous name of already sorted directories. (<code>2014_01_01 new year</code> would set <code>{old}</code> parameter to <code>new year</code>, which means you can change date format)

Dependencies
----------------
- Exifread - https://pypi.python.org/pypi/ExifRead
