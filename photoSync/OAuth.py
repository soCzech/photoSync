import json
import logging
import requests
from webbrowser import open_new
from urllib.request import unquote
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import DRIVE_CLIENT_ID, DRIVE_CLIENT_SECRET
from .helper import fr_generate_params, createJSON
from .constants import *

log = logging.getLogger("photoSync-debug")

class OAuth():

	def __init__(self, sclass):
		self.SCLASS = sclass

	"""
		GET AUTHORIZATION CODE
		gets authorization code which is passed as paremeter in callback URL
			args:
				url		... url to open in browser
			return values:
				string	... callback URL with the needed parameter
	"""
	def get_authorization_code(self, url):
		if input(i18n_use_browser).lower().startswith("y"):
			httpServer = HTTPServer((HOST, PORT),
					lambda request, address, server: HTTPServerHandler(request, address, server))
			log.debug(i18n_oauth_server, HOST, PORT)

			open_new(url)
			log.debug(i18n_oauth_server_url, url)

			httpServer.handle_request()
			log.debug(i18n_oauth_server_cback, httpServer.callback)
			return httpServer.callback

		else:
			print(i18n_open_url + url)
			return input(i18n_insert_url)

	"""
		GDRIVE+FLICKR: AUTH
		makes the authorization and stores user's credentials to the session file
			args: None
			return values:
				0		... success
				1		... error
	"""
	def fr_auth(self):
		data = self.SCLASS.SESSION

		r = requests.get(fr_generate_params(FLICKR_REQUEST_TOKEN, \
				{"oauth_callback": CALLBACK}, False))

		log.debug(r.text)

		response = createJSON(r.text)

		if "oauth_problem" in response:
			log.error(response["oauth_problem"])
			return 1

		# only temporary tokens
		data["fr_token"] = response["oauth_token"]
		data["fr_token_secret"] = response["oauth_token_secret"]

		url = "%s?oauth_token=%s" % (FLICKR_OAUTH, data["fr_token"])
		code = self.get_authorization_code(url).split("=")[-1].split("#")[0]
		log.info(i18n_oauth_code, code)

		r = requests.get(fr_generate_params(FLICKR_ACCESS_TOKEN, {
			"oauth_verifier": code,
			"oauth_token": data["fr_token"]
		}, False, data["fr_token_secret"]))

		log.debug(r.text)

		response = createJSON(r.text)

		if "oauth_problem" in response:
			log.error(response["oauth_problem"])
			return 1

		data["fr_token"] = response["oauth_token"]
		data["fr_token_secret"] = response["oauth_token_secret"]
		data["fr_fullname"] = unquote(response["fullname"])

		return self.SCLASS.session_write(data)

	def gd_auth(self):
		code = self.get_authorization_code(DRIVE_OAUTH).split("=")[-1].split("#")[0]
		log.info(i18n_oauth_code, code)

		r = requests.post(DRIVE_ACCESS_TOKEN, {
			"code": code,
			"redirect_uri": CALLBACK,
			"client_id": DRIVE_CLIENT_ID,
			"client_secret": DRIVE_CLIENT_SECRET,
			"scope": "",
			"grant_type": "authorization_code"
		})
		log.debug(' '.join(r.text.split()))

		response = json.loads(r.text)

		if "error" in response:
			log.error(response["error_description"])
			return 1

		data = self.SCLASS.SESSION

		data["gd_access_token"] = response["access_token"]
		if "refresh_token" in response:
			data["gd_refresh_token"] = response["refresh_token"]

		return self.SCLASS.session_write(data)

	"""
		GDRIVE: REFRESH
		refreshes the Google access token (required at least every hour)
			args: None
			return values:
				0		... success
				1		... error
	"""
	def gd_refresh(self):
		data = self.SCLASS.SESSION

		if not "gd_refresh_token" in data:
			log.error(i18n_refresh_token_NA)
			return 1

		r = requests.post(DRIVE_ACCESS_TOKEN, {
			"refresh_token": data["gd_refresh_token"],
			"client_id": DRIVE_CLIENT_ID,
			"client_secret": DRIVE_CLIENT_SECRET,
			"grant_type": "refresh_token"
		})
		log.debug(' '.join(r.text.split()))

		response = json.loads(r.text)

		if "error" in response:
			log.error(response["error_description"])
			return 1

		data["gd_access_token"] = response["access_token"]

		return self.SCLASS.session_write(data)

"""
	HTTPServerHandler
	gets the callback URL when get_authorization_code called
"""
class HTTPServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		self.wfile.write(bytes("<html>You may now close this window.</html>", "utf-8"))
		self.server.callback = self.path
