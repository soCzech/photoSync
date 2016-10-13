import re
import os
import collections

from .helper import path_to_array
from .constants import EXCLUDE, EXCLUDE_IN_TITLE

class Explorer():

	"""
		GET ALL ALBUMS
		searches through the folders to create album list
			args:
				directory
						... 'root' folder for the albums
			return values:
				{}		... sorted dictionary of {album name: [all matching folders]}
							due to the 'EXCLUDE_IN_TITLE' and naming of subfolders,
							there can be multiple folders to one album name
	"""
	@staticmethod
	def get_all_albums(directory):
		directory = os.path.normpath(directory) # necessary otherwise relative_path breaks
		albums = {}
		root_index = len(path_to_array(directory))

		for root, dirs, files in os.walk(directory):
			if not os.path.isdir(root):
				continue
			relative_path = path_to_array(root)[root_index:]
			save = True

			for exc in EXCLUDE:
				for dir in relative_path:
					if re.match("(%s)" % (exc), dir) != None:
						save = False
			if not save:
				continue

			to_remove = []
			for exc in EXCLUDE_IN_TITLE:
				for dir in relative_path:
					if re.match("(%s)" % (exc), dir) != None:
						to_remove.append(dir)
			for dir in to_remove:
				relative_path.remove(dir)

			if relative_path:
				album_name = " - ".join(relative_path)
			else:
				path = os.path.split(directory)
				if path[1]:
					album_name = path[1]
				else:
					album_name = os.path.split(path[0])[1]

			if album_name in albums:
				albums[album_name].append(root)
			else:
				albums[album_name] = [root]

		return collections.OrderedDict(sorted(albums.items()))

	"""
		GET PHOTOS IN DIRECOTRIES
		finds all photos in given directories
			args:
				directories
						... array of directories to search through
							ALL FILENAMES ACROSS THE DIRECTORIES HAVE TO BE UNIQUE
			return values:
				{}		... sorted dictionary of {photo file name: path to the photo}
	"""
	@staticmethod
	def get_photos_in_directories(directories):
		photos = {}
		for directory in directories:
			for file in os.listdir(directory):
				if os.path.isdir(os.path.join(directory, file)):
					continue

				ext = file.lower().split(".")[-1]
				if (ext == "jpg"):
					photos[file] = directory

		return collections.OrderedDict(sorted(photos.items()))

	"""
		COMPARE PHOTOSETS
		compares photosets and returns missing files in each one
			args:
				ps1		... first photoset (dictionary of {'name': anything})
				ps2		... second photoset
			return values:
				tuple	... (dictionary of {'name': anything} missing in the first one, the same for the 2nd)
	"""
	@staticmethod
	def compare_photosets(ps1, ps2):
		(missing_in_ps1, missing_in_ps2) = ({}, {})

		for photo in ps2:
			if not photo in ps1:
				missing_in_ps1[photo] = ps2[photo]
		for photo in ps1:
			if not photo in ps2:
				missing_in_ps2[photo] = ps1[photo]

		return (missing_in_ps1, missing_in_ps2)
