import sys
import time
import os.path
import logging
import argparse
try:
	from photoSync import photoSync
	import_error = False
except ImportError:
	import_error = True

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-a", "--authorize", action="store_true", help="authorize the online services")
	parser.add_argument("-f", "--folder", action="store", help="folder to synchronize")
	parser.add_argument("-u", "--upload", action="store_true", help="files missing in cloud will be uploaded")
	parser.add_argument("-s", "--save", action="store_true", help="files missing localy will be downloaded")
	parser.add_argument("-d", "--delete", action="store_true", help="files missing localy will be deleted")
	parser.add_argument("-m", "--max", action="store", help="maximal number of operations for each service (0 means unlimited)")
	parser.add_argument("-w", "--wait", action="store", help="time in seconds to wait between operations")
	parser.add_argument("-p", "--scope", action="store", help="specify what services to use {Flickr: 1, Drive: 2, both: 0 (default)}")
	args = parser.parse_args()

	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	console.setFormatter(logging.Formatter("%(message)s"))

	logging.getLogger("photoSync").addHandler(console)

	LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

	args.max = 0 if not args.max else int(float(args.max))
	args.wait = 0 if not args.wait else float(args.wait)
	args.scope = 0 if not args.scope else int(args.scope)

	if (args.folder or args.authorize) and not import_error:
		INSTANCE = photoSync(LOCAL_DIR, args.scope)

		if args.authorize:
			authorized = INSTANCE.authorize()
		else:
			authorized = INSTANCE.check()
		if not authorized and args.folder:
			INSTANCE.sync(args.folder, args.upload, args.save, args.delete, args.max, args.wait)
	elif import_error:
		print("app.py script error @ " + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time())))
		print("ERROR: photoSync module cannot be imported.")
	else:
		parser.print_help()
