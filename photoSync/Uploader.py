import re
import os
import json
import logging
import requests
import collections
import urllib.request

from . import DRIVE_CLIENT_ID
from .helper import fr_generate_params, createJSON, generate_rand_num
from .constants import *

log = logging.getLogger("photoSync-debug")

class Uploader():

	BASE_FOLDER = None

	def __init__(self, sclass):
		self.SCLASS = sclass

		self.upload_file = {
			1: self.fr_upload_file,
			2: self.gd_upload_file
		}
		self.list_albums = {
			1: self.fr_list_albums,
			2: self.gd_list_albums
		}
		self.list_photos = {
			1: self.fr_list_photos,
			2: self.gd_list_photos
		}
		self.download_file = {
			1: self.fr_download_file,
			2: self.gd_download_file
		}
		self.delete_file = {
			1: self.fr_delete_file,
			2: self.gd_delete_file
		}

	"""
		GDRIVE: GET BASE FOLDER
		loads stored, searches Google Drive and/or creates the base folder for the albums if necessary
			args:
				search (optional)
						... [True/False] search the root folder for 'DRIVE_FOLDER_NAME'
				create (optional)
						... [True/False] create the folder
			return values:
				0		... base folder exists
							returned also when it was impossible to store the folder id forever
				1		... error
	"""
	def gd_get_base_folder(self, search = False, create = True):
		data = self.SCLASS.SESSION

		if "gd_base_folder" in data:
			self.BASE_FOLDER = data["gd_base_folder"]
			log.info(i18n_base_folder_found)
			return 0

		if search:
			r = requests.get("%s?maxResults=1&q='root'+in+parents+and+name='%s'\
						+and+mimeType='application/vnd.google-apps.folder'+and+trashed=false&key=%s" \
						% (DRIVE_FILES_METADATA, DRIVE_FOLDER_NAME, DRIVE_CLIENT_ID), \
					headers = self.gd_get_header())
			log.debug(' '.join(r.text.split()))

			response = json.loads(r.text)

			if "error" in response:
				log.error(response["error"]["message"])
				return 1

			if len(response["files"]) > 0:
				data["gd_base_folder"] = response["files"][0]["id"]
				self.BASE_FOLDER = data["gd_base_folder"]

				log.info(i18n_base_folder_found)
				self.SCLASS.session_write(data)
				return 0

		if create:
			body = '{"name": "%s", \
					"mimeType": "application/vnd.google-apps.folder", \
					"parents": ["root"]}' % (DRIVE_FOLDER_NAME)

			r = requests.post("%s?key=%s" % (DRIVE_FILES_METADATA, DRIVE_CLIENT_ID), \
				data = body, headers = self.gd_get_header(True))
			log.debug(' '.join(r.text.split()))

			response = json.loads(r.text)

			if "error" in response:
				log.error(response["error"]["message"])
				return 1

			data["gd_base_folder"] = response["id"]
			self.BASE_FOLDER = data["gd_base_folder"]

			log.info(i18n_base_folder_create)
			self.SCLASS.session_write(data)
			return 0

		log.error(i18n_base_folder_NA)
		return 1

	"""
		GDRIVE: GET HEADER
		prepares header object for google drive requests
			args:
				json (optional)
						... [True/False] add 'Content-type: application/json' to header
			return values:
				{}		... the header
	"""
	def gd_get_header(self, json = False):
		header = {"Authorization": "Bearer %s" % (self.SCLASS.SESSION["gd_access_token"])}
		if json:
			header.update({
				"Content-type": "application/json"
			})
		return header

	"""
		GDRIVE+FLICKR: CREATE ALBUM
		creates Google Drive album folder or creates and adds the first photo to a new album on Flickr
			args:
				name	... album name
				FLICKR:
				primary_photo_id
						... id of a album cover photo (the photo is automaticaly added to the album)
				description (optional)
						... album description
			return values:
				""		... album id
				1		... error
	"""
	def gd_create_album(self, name):
		body = '{{"name": "{}", "mimeType": "application/vnd.google-apps.folder", \
				"parents": ["{}"]}}'.format(name, self.BASE_FOLDER)
		body = body.encode('utf-8')

		r = requests.post("{}?key={}".format(DRIVE_FILES_METADATA, DRIVE_CLIENT_ID), \
				data = body, headers = self.gd_get_header(True))
		log.debug(' '.join(r.text.split()))

		response = json.loads(r.text)

		if "error" in response:
			log.error(response["error"]["message"])
			return 1

		log.info(i18n_album_created, name, response["id"])
		return response["id"]

	def fr_create_album(self, name, primary_photo_id, description = ""):
		log.debug("Creating album %s.", name)

		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"method": "flickr.photosets.create",
			"format": "json",
			"nojsoncallback": 1,
			"title": name,
			"primary_photo_id": primary_photo_id,
			"description": description
		}

		r = requests.post(FLICKR_FILES_METADATA, \
			data = fr_generate_params(FLICKR_FILES_METADATA, \
			params, True, self.SCLASS.SESSION["fr_token_secret"])
		)
		log.debug(' '.join(r.text.split()))

		response = createJSON(r.text)

		if response["stat"] == "fail":
			log.error(response["message"])
			return 1

		return response["photoset"]["id"]

	"""
		GDRIVE+FLICKR: UPLOAD FILE
		uploads file to Google Drive folder of to Flickr and adds it to an album (if specified)
			args:
				path	... path to the file
				name	... file name
				album_id (FLICKR: when uploading first photo of album, leave empty since album does not exit yet)
						... id of an album which the photo is uploaded to
			return values:
				"" or #	... file id
				1		... error
	"""
	def gd_upload_file(self, path, name, album_id):
		body = '{"name": "%s", "parents": ["%s"]}' % (name, album_id)

		try:
			files = collections.OrderedDict()
			files["1"] = (None, body.encode('utf-8'), "application/json; charset=UTF-8")
			files["2"] = (None, open(os.path.join(path, name), "rb"), 'image/jpeg')
		except (OSError, IOError) as e:
			log.error(str(e))
			return 1

		r = requests.post(DRIVE_FILES_UPLOAD, headers = self.gd_get_header(), files = files)

		log.debug(' '.join(r.text.split()))

		response = json.loads(r.text)

		if "error" in response:
			log.error(response["error"]["message"])
			return 1

		log.info(i18n_gd_photo_uploaded, name, response["id"], album_id)
		return response["id"]

	def fr_upload_file(self, path, name, album_id = None):
		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"title": name,
			"description": "",
			"tags": "",
			"is_public": 0,
			"is_friend": 0,
			"is_family": 0,
			"safety_level": 1,
			"content_type": 1,
			"hidden": 2
		}

		boundary = generate_rand_num(20)
		requests.packages.urllib3.filepost.choose_boundary = lambda: boundary

		try:
			r = requests.post(FLICKR_FILES_UPLOAD, \
					data = fr_generate_params(FLICKR_FILES_UPLOAD, params, True, \
							self.SCLASS.SESSION["fr_token_secret"]), \
					files = {"photo": (name, open(os.path.join(path, name), "rb"))}, \
					headers = {"Content-type": "multipart/form-data; boundary=%s" % boundary}
			)
		except (OSError, IOError) as e:
			log.error(str(e))
			return 1

		log.debug(' '.join(r.text.split()))

		response = createJSON(r.text)

		if response["stat"] == "fail":
			log.error(response["message"])
			return 1

		id = response["photoid"]["text"]
		log.info(i18n_fr_photo_uploaded, name, id)

		if album_id == None:
			return id

		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"method": "flickr.photosets.addPhoto",
			"format": "json",
			"nojsoncallback": 1,
			"photo_id": id,
			"photoset_id": album_id
		}

		r = requests.post(FLICKR_FILES_METADATA, \
			data = fr_generate_params(FLICKR_FILES_METADATA, \
			params, True, self.SCLASS.SESSION["fr_token_secret"])
		)
		log.debug(' '.join(r.text.split()))

		response = createJSON(r.text)

		if response["stat"] == "fail":
			log.error(response["message"])
			return 1

		log.info(i18n_fr_photo_added, name, album_id)
		return id

	"""
		GDRIVE+FLICKR: LIST ALBUMS
		lists all folders in Google Drive BASE_FOLDER or lists all albums on Flickr
			args: None
			return values:
				{}		... sorted dictionary of pairs {album name: album id}
				1		... error
	"""
	def gd_list_albums(self):
		albums = {}
		pageToken = ""

		while True:
			r = requests.get("%s?q='%s'+in+parents+and+mimeType='application/vnd.google-apps.folder'\
						+and+trashed=false&pageToken=%s&key=%s" \
						% (DRIVE_FILES_METADATA, self.BASE_FOLDER, pageToken, DRIVE_CLIENT_ID), \
					headers = self.gd_get_header())
			log.debug(' '.join(r.text.split()))

			response = json.loads(r.text)

			if "error" in response:
				log.error(response["error"]["message"])
				return 1


			for album in response["files"]:
				albums[album["name"]] = album["id"]

			# break when no next page availible
			if not "nextPageToken" in response:
				break
			else:
				pageToken = response["nextPageToken"]

		log.info(i18n_albums_listed, len(albums))
		return collections.OrderedDict(sorted(albums.items()))

	def fr_list_albums(self):
		albums = {}
		pages = 1

		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"method": "flickr.photosets.getList",
			"format": "json",
			"nojsoncallback": 1,
			"page": 1
		}

		while params["page"] <= pages:
			r = requests.post(FLICKR_FILES_METADATA, \
				data = fr_generate_params(FLICKR_FILES_METADATA, \
				params, True, self.SCLASS.SESSION["fr_token_secret"])
			)
			log.debug(' '.join(r.text.split()))

			response = createJSON(r.text)

			if response["stat"] == "fail":
				log.error(response["message"])
				return 1

			pages = response["photosets"]["pages"]
			for album in response["photosets"]["photoset"]:
				albums[album["title"]["_content"]] = album["id"]

			params["page"] += 1

		log.info(i18n_albums_listed, len(albums))
		return collections.OrderedDict(sorted(albums.items()))

	"""
		GDRIVE+FLICKR: LIST PHOTOS
		lists all photos in Google Drive folder or lists photos in album on Flickr
			args:
				album_id... album id to list from
			return values:
				{}		... sorted dictionary of pairs
							{photo file name: {photo object as specified in Drive and Flickr API}}
				1		... error
	"""
	def gd_list_photos(self, album_id):
		photos = {}
		pageToken = ""

		while True:
			r = requests.get("%s?q='%s'+in+parents+and+mimeType='image/jpeg'\
						+and+trashed=false&pageToken=%s&pageSize=500&key=%s" \
						% (DRIVE_FILES_METADATA, album_id, pageToken, DRIVE_CLIENT_ID), \
					headers = self.gd_get_header())
			log.debug(' '.join(r.text.split()))

			response = json.loads(r.text)

			if "error" in response:
				log.error(response["error"]["message"])
				return 1


			for photo in response["files"]:
				photos[photo["name"]] = photo

			# break when no next page availible
			if not "nextPageToken" in response:
				break
			else:
				pageToken = response["nextPageToken"]

		log.info(i18n_photos_listed, len(photos))
		return collections.OrderedDict(sorted(photos.items()))

	def fr_list_photos(self, album_id):
		photos = {}
		pages = 1

		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"method": "flickr.photosets.getPhotos",
			"format": "json",
			"nojsoncallback": 1,
			"photoset_id": album_id,
			"extras": "original_format",
			"page": 1
		}

		while params["page"] <= pages:
			r = requests.post(FLICKR_FILES_METADATA, \
				data = fr_generate_params(FLICKR_FILES_METADATA, \
				params, True, self.SCLASS.SESSION["fr_token_secret"])
			)
			log.debug(' '.join(r.text.split()))

			response = createJSON(r.text)

			if response["stat"] == "fail":
				log.error(response["message"])
				return 1

			pages = response["photoset"]["pages"]
			for photo in response["photoset"]["photo"]:
				photos[photo["title"]] = photo

			params["page"] += 1

		log.info(i18n_photos_listed, len(photos))
		return collections.OrderedDict(sorted(photos.items()))

	"""
		GDRIVE+FLICKR: DOWNLOAD FILE
		downloads a photo to a local folder
			args:
				photo	... photo object from list_photos function
				directory
						... path where to store the photo
			return values:
				0		... success
				1		... error
	"""
	def gd_download_file(self, photo, directory):
		url = "%s/%s?alt=media&key=%s" \
				% (DRIVE_FILES_METADATA, photo["id"], DRIVE_CLIENT_ID)
		return self.cm_download_file(photo["name"], directory, url, self.gd_get_header())

	def fr_download_file(self, photo, directory):
		url = "https://farm%s.staticflickr.com/%s/%s_%s_o.%s" \
				% (photo["farm"], photo["server"], photo["id"], \
				photo["originalsecret"], photo["originalformat"])
		return self.cm_download_file(photo["title"], directory, url)

	def cm_download_file(self, name, directory, url, header = {}):
		if re.match("(?:.*)(jpg)$", name, re.IGNORECASE) == None:
			name += ".jpg"
		try:
			r = urllib.request.Request(url, headers = header)
			file = urllib.request.urlopen(r)

			output = open(os.path.join(directory, name), "wb")
			output.write(file.read())
			output.close()
			# to enable write over smb
			os.chmod(os.path.join(directory, name), 0o777)

			log.info(i18n_photo_downloaded, name, directory)
			return 0
		except Exception as e:
			log.error(str(e))
			return 1

	"""
		GDRIVE+FLICKR: DELETE FILE
		deletes file specified by its id
			args:
				id		... file id
			return values:
				0		... success
				1		... error
	"""
	def gd_delete_file(self, id):
		r = requests.delete("{}/{}?&key={}".format(DRIVE_FILES_METADATA, id, DRIVE_CLIENT_ID), \
				headers = self.gd_get_header())

		if not r.status_code == 204:
			log.debug(' '.join(r.text.split()))
			log.error(i18n_file_not_deleted, id)
			return 1

		log.info(i18n_file_deleted, id)
		return 0

	def fr_delete_file(self, id):
		params = {
			"oauth_token": self.SCLASS.SESSION["fr_token"],
			"method": "flickr.photos.delete",
			"photo_id": id,
			"format": "json",
			"nojsoncallback": 1
		}

		r = requests.post(FLICKR_FILES_METADATA, \
			data = fr_generate_params(FLICKR_FILES_METADATA, \
			params, True, self.SCLASS.SESSION["fr_token_secret"])
		)
		log.debug(' '.join(r.text.split()))

		response = createJSON(r.text)

		if response["stat"] == "fail":
			log.error(response["message"])
			return 1

		log.info(i18n_file_deleted, id)
		return 0
