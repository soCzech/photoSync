photoSync
=========
Flickr and Google Drive photo synchronization in Python

- OAuth sign in
- Upload/download photos to/from Flickr albums and Google Drive folders
- Delete photos photos from Flickr and Google Drive
- Synchronize photos with Flickr and Google Drive

Installation
------------
1. Depending on what service you plan to use, go to [Flickr API](https://www.flickr.com/services/apps/create/apply/) and/or [Drive API](https://console.developers.google.com) page to optain key and secret. Update them in **photoSync/\_\_init\_\_.py** respectively.

2. If you wish to specify folders to exclude from syncing, do so by changing **EXCLUDE** and/or **EXCLUDE\_IN\_TITLE** in **photoSync/constants.py**.

    Default values:
    - `EXCLUDE` = `["^\.", "^__", "^@eaDir$"]` # Matching folders and its subfolders will not be synced
    - `EXCLUDE_IN_TITLE` = `["^_"]` # Matching folders will be synced but its parent folder will be chosen as an album name

3. Install the package

        $ python3 setup.py install

Requires [**requests** library](https://github.com/kennethreitz/requests/) and **Python v3.+**

Usage
-----
For the most common usage is the **app.py** file located in the **bin** folder. This script can synchronize all your photos with Flickr and/or Google Drive. Run `python3 app.py --help` to see how to use it. See **bin/run.sh** for an example.

Known errors
------------
While authorizing Flickr it usually throws signature_invalid error. If it occurs, authorize again, it should succeed after a couple of tries.

Signature is created in **helper.py** by **fr_build_signature**(url, s, post, secret) function. Weirdly it always works when logged in but sometimes fails when not.

Documentation
-------------
Classes:
- [photoSync.py](#photoSync)
- [Explorer.py](#Explorer)
- [OAuth.py](#OAuth)
- [Session.py](#Session)
- [Uploader.py](#Uploader)

Other files:
- \_\_init\_\_.py
- constants.py
- helper.py

### <a name="photoSync"></a>photoSync class
- **\_\_init\_\_**(directory = os.path.dirname(os.path.realpath(\_\_file\_\_)), scope = 0)
    - arguments
            directory -- session file folder
            scope -- 1: use Flickr only, 2: use Google Drive only, 0: use both
- **check**()
    - checks if authorization required
    - arguments `None`
    - return values
            0 -- already signed in
            1 -- authorization required
- **authorize**()
    - makes the authorization given the scope

    NEEDS USER INTERACTION AND WEB BROWSER
    - arguments `None`
    - return values
            0 -- success (signed in)
            1 -- error
- **sync**(self, directory, upload = True, save = True, delete = False, max = 0, wait = 0)
    - synchronizes local photos with the cloud services

    IF ANY ERRORS OCCUR, IT SKIPS THE FILE/ALBUM AND TRIES TO CONTINUE
    - arguments
            directory -- the 'root' folder where the albums are
            upload, save, delete -- [True/False] whether to upload, save or/and delete photos in cloud
            max -- maximal number of operations for each service (0 means unlimited)
            wait -- time in seconds to wait between operations
    - return values
            1 -- error that made impossible to continue
            None -- otherwise

### <a name="Explorer"></a>Explorer class
Static class to handle local files.
- **get_all_albums**(directory) *@static*
    - searches through the folders to create album list
    - arguments
			directory -- 'root' folder for the albums
    - return values
			{} -- sorted dictionary of {album name: [all matching folders]}
				due to the 'EXCLUDE_IN_TITLE' and naming of subfolders,
				there can be multiple folders to one album name
- **get_photos_in_directories**(directories) *@static*
    - finds all photos in given directories
    - arguments
            directories -- array of directories to search through
                ALL FILENAMES ACROSS THE DIRECTORIES HAVE TO BE UNIQUE
    - return values
            {} -- sorted dictionary of {photo file name: path to the photo}
- **compare_photosets**(ps1, ps2) *@static*
    - compares photosets and returns missing files in each one
    - arguments
            ps1 -- first photoset (dictionary of {'name': object})
            ps2 -- second photoset
    - return values
            tuple -- (dictionary of {'name': object} missing in the first one, the same for the 2nd)

### <a name="OAuth"></a>OAuth class
Class to handle both Flickr and Google Drive authorization.
- **\_\_init\_\_**(sclass)
    - arguments
            sclass -- Session-class object
- **fr_auth**(), **gd_auth**()
    - makes the authorization and stores user's credentials to the session file
    - arguments `None`
    - return values
    		0 -- success
            1 -- error
- **get_authorization_code**(url) -- *called by fr_auth and gd_auth*
    - gets authorization code which is passed as paremeter in callback URL
    - arguments
            url -- url to open in browser
    - return values
    		string -- callback URL with the needed parameter
- **gd_refresh**()
    - refreshes the Google access token (required at least every hour)
    - arguments `None`
    - return values
    		0 -- success
            1 -- error

### <a name="Session"></a>Session class
Class to handle loading and storing login data to a *.session* file.
- **SCOPE** -- 1: use Flickr only, 2: use Google Drive only, 0: use both
- **SESSION** -- the session variable
- **\_\_init\_\_**(directory)
    - arguments
            directory -- session file folder
- **set_scope**(scope)
    - sets scope variable used throughout the app to determine what to sync
    - arguments
            scope -- scope to use (sets the SCOPE variable)
- **session_load**()
    - loads session file to variable
- **session_write**(data)
    - updates the session variable and the session file
    - arguments
            data -- (updated) session variable
- **session_check**(scope = None)
    - checks if session file contains necessary tokens given the scope
    - arguments
            scope -- 1: use Flickr only, 2: use Google Drive only, 0: use both
                if None, the scope variable is used

### <a name="Uploader"></a>Uploader class
Class to handle the cloud work

scope -- 1: Flickr function, 2: Google Drive function, 0 not permitted
- **\_\_init\_\_**(sclass)
    - arguments
            sclass -- Session-class object
- **gd_get_base_folder**(search = False, create = True)
    - loads stored, searches Google Drive and/or creates the base folder for the albums if necessary
    - arguments
            search (optional) -- [True/False] search the root folder for 'DRIVE_FOLDER_NAME'
            create (optional) -- [True/False] create the folder
    - return values
            0 -- base folder exists
                returned also when it was impossible to store the folder id forever
            1 -- error
- **create_album**\[*scope*](name[, primary_photo_id, description = ""])
    - creates Google Drive album folder or creates and adds the first photo to a new album on Flickr
    - arguments
            name -- album name
            FLICKR:
                primary_photo_id -- id of a album cover photo (the photo is automaticaly added to the album)
                description (optional) -- album description
    - return values
    		string -- album id
            1 -- error
- **upload_file**\[*scope*](path, name, album_id)
    - uploads file to Google Drive folder of to Flickr and adds it to an album (if specified)
    - arguments
            path -- path to the file
            name -- file name
            album_id -- id of an album which the photo is uploaded to (FLICKR: when uploading first photo of album, leave empty since album does not exit yet)
    - return values
            string or integer -- file id
            1 -- error
- **list_albums**\[*scope*]()
    - lists all folders in Google Drive BASE_FOLDER or lists all albums on Flickr
    - arguments `None`
    - return values
            {} -- sorted dictionary of pairs {album name: album id}
            1 -- error
- **list_photos**\[*scope*](album_id)
    - lists all photos in Google Drive folder or lists photos in album on Flickr
    - arguments
            album_id -- album id to list from
    - return values
            {} -- sorted dictionary of pairs
                {photo file name: {photo object as specified in Drive and Flickr API}}
            1 -- error
- **download_file**\[*scope*](photo, directory)
    - downloads a photo to a local folder
    - arguments
            photo -- photo object from list_photos function
            directory -- path where to store the photo
    - return values
            0 -- success
            1 -- error
- **delete_file**\[*scope*](id)
    - deletes file specified by its id
    - arguments
            id -- file id
    - return values
            0 -- success
            1 -- error
