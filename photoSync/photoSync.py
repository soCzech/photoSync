import os
import time
import logging
import sys

from .OAuth import OAuth
from .Session import Session
from .Uploader import Uploader
from .Explorer import Explorer

from .helper import getTerminalSize, path_to_array
from .constants import *


logging.basicConfig(format = "%(module)-12s %(funcName)-20s : %(levelname)-8s %(message)s", \
	filename = LOG_FILE_NAME, filemode="w", level = logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)

log = logging.getLogger("photoSync")

class photoSync():

	session = None
	upldr = None
	prg = None

	def __init__(self, directory = os.path.dirname(os.path.realpath(__file__)), scope = 0):
		self.session = Session(directory)
		self.session.set_scope(scope)
		self.prg = progressTracker()
		log.info("photoSync" + " @ " + time.strftime("%Y/%m/%d %H:%M:%S", \
			time.localtime(time.time())))

	"""
		CHECK
		checks if authorization required
			args: None
			return values:
				0		... already signed in
				1		... authorization required
	"""
	def check(self):
		log.info(i18n_check_tokens_info)

		if self.session.session_check() == 1:
			log.error(i18n_check_tokens_NA)
			return 1

		if self.session.SCOPE == 0 or self.session.SCOPE == 2:
			auth = OAuth(self.session)
			if auth.gd_refresh() == 1:
				log.error(i18n_check_tokens_Drive)
				return 1

		self.upldr = Uploader(self.session)
		if self.session.SCOPE == 0 or self.session.SCOPE == 2:
			return self.upldr.gd_get_base_folder(True)
		return 0

	"""
		AUTHORIZE
		makes the authorization given the scope
		NEEDS USER INTERACTION AND WEB BROWSER
			args: None
			return values:
				0		... success (signed in)
				1		... error
	"""
	def authorize(self):
		auth = OAuth(self.session)

		if self.session.session_check() == 0:
			if not input(i18n_force_auth).lower().startswith("y"):
				self.upldr = Uploader(self.session)
				return 0

		if self.session.SCOPE == 0 or self.session.SCOPE == 1:
			if auth.fr_auth() == 1:
				return 1
		if self.session.SCOPE == 0 or self.session.SCOPE == 2:
			if auth.gd_auth() == 1:
				return 1

		log.info(i18n_auth_success)

		self.upldr = Uploader(self.session)
		if self.session.SCOPE == 0 or self.session.SCOPE == 2:
			return self.upldr.gd_get_base_folder(True)
		return 0

	"""
		SYNC
		synchronizes local photos with the cloud services
		IF ANY ERRORS OCCUR, IT SKIPS THE FILE/ALBUM AND TRIES TO CONTINUE
			args:
				directory
						... the 'root' folder where the albums are
				upload, save, delete
						... [True/False] whether to upload, save or/and delete photos in cloud
				max		... maximal number of operations for each service (0 means unlimited)
				wait	... time in seconds to wait between operations
			return values:
				None	... -
				1		... error that made impossible to continue
	"""
	def sync(self, directory, upload = True, save = True, delete = False, max = 0, wait = 0):
		if self.session.SCOPE == 0:
			scope = [1, 2]
		else:
			scope = [self.session.SCOPE]

		for scp in scope:
			log.info(i18n_scope_sync, SCOPE_ALIAS[scp])
			processed = 0
			end = False

			cloud_albums = self.upldr.list_albums[scp]()
			if cloud_albums == 1: # error
				return 1
			local_albums = Explorer.get_all_albums(directory)

			log.info(i18n_albums_found, len(cloud_albums), len(local_albums))

			for album in local_albums:
				if self.check_max(processed, max):
					break;
				self.prg.info(i18n_album_sync, album)

				ps_local = Explorer.get_photos_in_directories(local_albums[album])
				if album in cloud_albums:
					ps_cloud = self.upldr.list_photos[scp](cloud_albums[album])
					if ps_cloud == 1: # error
						continue
					(down, up) = Explorer.compare_photosets(ps_local, ps_cloud)
				else:
					(down, up) = ({}, ps_local)

				files = (len(up) if upload else 0) + (len(down) if (save or (delete and not save)) else 0)
				if files != 0:
					self.prg.createProgressBar(files)

				if upload and up: # files for upload exist
					if not album in cloud_albums: # album in cloud does not exist
						if scp == 1:
							name = list(up)[0]

							photo_id = self.upldr.fr_upload_file(up[name], name)
							self.prg.increment(); processed += 1
							if photo_id == 1: # error
								self.prg.warning(i18n_upload_error, photo, album)
								continue


							album_id = self.upldr.fr_create_album(album, photo_id)
							if album_id == 1: # error
								self.prg.warning(i18n_create_album_error, album)
								self.upldr.fr_delete_file(photo_id) # delete photo
								continue

							del up[name]
						elif scp == 2:
							album_id = self.upldr.gd_create_album(album)
							if album_id == 1: # error
								self.prg.warning(i18n_create_album_error, album)
								continue
					else:
						album_id = cloud_albums[album]

					for photo in up:
						if self.check_max(processed, max):
							end = True
							break;

						if self.upldr.upload_file[scp](up[photo], photo, album_id) == 1:
							self.prg.warning(i18n_upload_error, photo, album)

						self.prg.increment(); processed += 1
						if wait:
							time.sleep(wait)

					if end:
						break;

				if (save or (delete and not save)) and down: # files for download exist
					(processed, _continue, _break) = self.save_or_delete(save, delete, down, \
							os.path.join(directory, album), album, cloud_albums[album], scp, processed, max, wait)
					if _continue:
						continue
					if _break:
						break

			# go to next service
			if not (max and processed >= max):
				for album in cloud_albums:
					if not album in local_albums:
						self.prg.info(i18n_album_sync, album)

						ps_cloud = self.upldr.list_photos[scp](cloud_albums[album])
						if ps_cloud == 1: # error
							continue

						files = len(ps_cloud)
						if files != 0:
							self.prg.createProgressBar(files)

						if (save or (delete and not save)) and ps_cloud: # files for download exist
							(processed, _continue, _break) = self.save_or_delete(save, delete, ps_cloud, \
									os.path.join(directory, album), album, cloud_albums[album], scp, processed, max, wait)
							if _continue:
								continue
							if _break:
								break

			self.prg.clearProgressBar()
			log.info(i18n_processed, processed)

	"""
		SUPPORT STUFF
		just to make sync function shorter and simpler to read
	"""
	def check_max(self, processed, max):
		if max and processed >= max:
			self.prg.info(i18n_max_reached, max)
			return True
		return False

	def save_or_delete(self, save, delete, down, album_dir, album, album_id, scp, processed, max, wait):
		if save and not os.path.exists(album_dir):
			try:
				os.makedirs(album_dir, 0o777)
			except Exception as e:
				self.prg.warning(i18n_makedir_error, album, str(e))
				return (processed, True, False)

		for photo in down:
			if self.check_max(processed, max):
				return (processed, False, True)

			if save:
				if self.upldr.download_file[scp](down[photo], album_dir) == 1:
					self.prg.warning(i18n_download_error, photo, album_dir)
			else:
				if self.upldr.delete_file[scp](down[photo]["id"]) == 1:
					self.prg.warning(i18n_delete_error, photo, album)

			self.prg.increment(); processed += 1
			if wait:
				time.sleep(wait)

		if (delete and not save) and scp == 2: # delete GDrive folder
			if not self.upldr.gd_list_photos(album_id):
				if self.upldr.gd_delete_file(album_id) == 1:
					log.warning(i18n_delete_album_error, album)

		return (processed, False, False)

"""
	progressTracker
	handles the progress bar which shows in console when syncing albums via the sync function
"""
class progressTracker():

	def createProgressBar(self, total):
		self.current = 0
		self.total = total
		self.digits = len(str(total))

		self.calculateBarWidth()
		self.drawProgressBar()

	def calculateBarWidth(self):
		(self.tw, self.th) = getTerminalSize()
		self.bar_width = self.tw - (2 * self.digits + 3 + 5)

	def drawProgressBar(self):
		self.clearProgressBar()

		print("%-*s%3d%% (%*d/%*d)" % (
			self.bar_width,
			"=" * round(self.bar_width * self.current / self.total),
			round(self.current / self.total * 100),
			self.digits,
			self.current,
			self.digits,
			self.total
		), end='\r')

	def clearProgressBar(self):
		sys.stdout.write("\033[K")
		# to fix bug when logging to console
		print("", end='\r')
		sys.stdout.write("\033[K")


	def setProgress(self, current):
		self.current = current

		self.drawProgressBar()

	def increment(self):
		self.setProgress(self.current + 1)

	def info(self, message, *args):
		self.clearProgressBar()
		log.info(message, *args)

	def warning(self, message, *args):
		self.clearProgressBar()
		log.warning(message, *args)
		self.drawProgressBar()
