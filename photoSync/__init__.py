"""
	photoSync
	Flickr and Google Drive photo synchronization in Python

	Tomáš Souček
	Created as a project at Faculty of Mathematics and Physics of Charles University in Prague, Czech Republic.
"""

__ver__ = "0.9.3"


# DRIVE API KEYS
DRIVE_CLIENT_ID = ""
DRIVE_CLIENT_SECRET = ""
# FLICKR API KEYS
FLICKR_CLIENT_ID = ""
FLICKR_CLIENT_SECRET = ""

from .photoSync import photoSync
