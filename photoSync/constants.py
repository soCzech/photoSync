from . import DRIVE_CLIENT_ID

# USER VARIABLES
EXCLUDE					= ["^\.", "^__", "^@eaDir$"] # Matching folders and its subfolders will not be synced
EXCLUDE_IN_TITLE		= ["^_"] # Matching folders will be synced but its parent folder will be chosen as an album name

LOG_FILE_NAME			= "photoSync.log"
SESSION_FILE_NAME		= "photoSync.session"

# PHOTOSYNC SETTINGS
HOST					= "localhost"
PORT					= 8000
CALLBACK				= "http://" + HOST + ":" + str(PORT)

# DRIVE SETTINGS
DRIVE_SCOPE				= "https://www.googleapis.com/auth/drive"
DRIVE_FOLDER_NAME		= "photoSync"

# DRIVE URLs
DRIVE_OAUTH				= "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&access_type=offline" \
						+ "&redirect_uri=%s&client_id=%s&scope=%s&approval_prompt=force" % (CALLBACK, DRIVE_CLIENT_ID, DRIVE_SCOPE)
DRIVE_ACCESS_TOKEN		= "https://www.googleapis.com/oauth2/v4/token"
DRIVE_FILES_METADATA	= "https://www.googleapis.com/drive/v3/files"
DRIVE_FILES_UPLOAD		= "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&key=%s" % (DRIVE_CLIENT_ID)

# FLICKR URLs
FLICKR_OAUTH			= "https://api.flickr.com/services/oauth/authorize"
FLICKR_FILES_METADATA	= "https://api.flickr.com/services/rest"
FLICKR_FILES_UPLOAD		= "https://api.flickr.com/services/upload"
FLICKR_ACCESS_TOKEN		= "https://api.flickr.com/services/oauth/access_token"
FLICKR_REQUEST_TOKEN	= "https://api.flickr.com/services/oauth/request_token"

SCOPE_ALIAS = {
	1: "Flickr",
	2: "Google Drive"
}

""" MESSAGES """
# Session
i18n_session_write_err	= "Session data could not be stored. (%s)"
i18n_session_load_err	= "Session data could not be loaded. (%s)"

# OAuth
i18n_use_browser		= "Can I use your browser? Use 'No' only if problems occur. [Yes/No] "
i18n_open_url			= "Open this URL in any browser: "
i18n_insert_url			= "Please, insert the URL from your browser: "
i18n_oauth_server		= "Server %s:%d started."
i18n_oauth_server_url	= "Authorization URL: %s"
i18n_oauth_server_cback	= "Callback URL: %s"
i18n_oauth_code			= "Authorization code: %s"
i18n_refresh_token_NA	= "Refresh token does not exist."

# Uploader
i18n_base_folder_NA		= "Google Drive base folder is missing."
i18n_base_folder_found	= "Google Drive base folder found."
i18n_base_folder_create	= "Google Drive base folder created."
i18n_file_not_deleted	= "File %s could not be deleted."
i18n_file_deleted		= "File %s deleted."
i18n_album_created		= "Album %s created with id %s."
i18n_gd_photo_uploaded	= "Photo %s (%s) uploaded to album %s."
i18n_fr_photo_uploaded	= "Photo %s (%s) uploaded to server."
i18n_fr_photo_added		= "Photo %s added to album %s."
i18n_albums_listed		= "%d albums found."
i18n_photos_listed		= "%d photos found."
i18n_photo_downloaded	= "Photo %s downloaded to %s."

# photoSync
i18n_check_tokens_info	= "Checking authorization tokens."
i18n_check_tokens_NA	= "Authorization tokens missing, please authorize."
i18n_check_tokens_Drive	= "Google Drive token could not be refreshed."
i18n_force_auth			= "Authorization not needed, force it? [Yes/No] "
i18n_auth_success		= "Authorization successful."

i18n_albums_found		= "%d albums found in cloud, %d albums found localy."
i18n_scope_sync			= "Syncing photos with %s."
i18n_album_sync			= "Syncing album %s."
i18n_processed			= "%d photos processed totaly."

i18n_max_reached		= "Number of synchronized files reached limit of %s."
i18n_makedir_error		= "A local folder for album %s could not created, skipping it. (%s)"
i18n_upload_error		= "Photo %s could not uploaded to album %s, skipping it."
i18n_create_album_error	= "Album %s could not created, skipping it."
i18n_download_error		= "Photo %s could not be downloaded to %s, skipping it."
i18n_delete_error		= "Photo %s in album %s could not deleted, skipping it."
i18n_delete_album_error	= "Empty album %s could not be deleted."
