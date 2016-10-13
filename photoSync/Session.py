import json
import os.path
import logging

from .constants import SESSION_FILE_NAME, i18n_session_write_err, i18n_session_load_err

log = logging.getLogger("photoSync-debug")

class Session():
	
	SCOPE = 0
	SESSION = {}
	
	def __init__(self, directory):
		self.SESSION_FILE = os.path.join(directory, SESSION_FILE_NAME)
		self.SESSION = self.session_load()
	
	def set_scope(self, scope):
		self.SCOPE = scope
	
	def session_load(self):
		try:
			with open(self.SESSION_FILE, "r") as fp:
				data = json.load(fp)
		except Exception as e:
			data = {}
			log.warning(i18n_session_load_err, str(e))
		return data
	
	def session_write(self, data):
		self.SESSION = data
		
		try:
			with open(self.SESSION_FILE, "w") as fp:
				json.dump(data, fp, sort_keys=True, indent=4)
		except Exception as e:
			log.error(i18n_session_write_err, str(e))
			return 1
		return 0
	
	def session_check(self, scope = None):
		if scope == None:
			scope = self.SCOPE
		if scope == 0 or scope == 1:
			if not ("fr_token" in self.SESSION and "fr_token_secret" in self.SESSION):
				return 1
		if scope == 0 or scope == 2:
			if not ("gd_access_token" in self.SESSION and "gd_refresh_token" in self.SESSION):
				return 1
		return 0
