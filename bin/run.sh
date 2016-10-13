# run app.py
#	-f (set folder to "/path/to/photo/folder/") ! mandatory
#	-s (download files which are not in /path/to/photo/folder/)
#	-d (delete files which are not in /path/to/photo/folder/, ignored when -s set)
#	-u (upload files from /path/to/photo/folder/ which are not in cloud)
#	-m (upload only 100 files at once)
#	-w (wait 1 seconds between uploads)
#	-p (use only Google Drive (2), other options 1: Flickr, 0: both)
python3 /path/to/app.py -f "/path/to/photo/folder/" -s -d -u -m 100 -w 1 -p 2
