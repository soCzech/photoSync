import os
import json
import time
from random import randint
from urllib.request import quote
from xml.etree.ElementTree import fromstring as xml
import hmac
from hashlib import sha1
from binascii import b2a_base64

from . import FLICKR_CLIENT_ID, FLICKR_CLIENT_SECRET

def escape(s):
    return quote(s, safe="~")

def generate_rand_num(length = 8):
	return ''.join([str(randint(0, 9)) for i in range(length)])

def to_utf8(s):
	if isinstance(s, str):
		return s.encode("UTF-8")
	elif isinstance(s, bytes):
		return s.decode("UTF-8")
	else:
		return str(s)

def path_to_array(path):
    array = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:
            array.insert(0, parts[0])
            break
        else:
            path = parts[0]
            array.insert(0, parts[1])
    return array
		
def createJSON(m):
	try:
		d = json.loads(m)
	except:
		try:
			s = xml(m)
			d = s.attrib
			for c in s:
				if c.tag == "err":
					for k, v in c.attrib.items():
						d["message" if k == "msg" else k] = v
				else:
					d[c.tag] = {
						"text": c.text,
						"attrib": c.attrib
					}
		except:
			d = dict()
			n = m.split("=")
			for i in range(len(n)-1):
				k = n[i][n[i].rfind("&")+1:]
				p = n[i+1].rfind("&")
				d[k] = n[i+1][:(len(n[i+1]) if p < 0 else p)]
	return d

def fr_generate_params(url, data, post, secret = None):
	params = {
		"oauth_nonce": generate_rand_num(),
		"oauth_timestamp": str(time.time()),
		"oauth_consumer_key": FLICKR_CLIENT_ID,
		"oauth_signature_method": "HMAC-SHA1",
		"oauth_version": "1.0"
	}
	params.update(data)
	
	key_values = [(escape(to_utf8(k)), escape(to_utf8(v))) \
			for k, v in params.items()]
	key_values.sort()
	s = "&".join(["%s=%s" % (k, v) for k, v in key_values])
	
	sign = fr_build_signature(url, s, post, secret)
	if post:
		params.update({"oauth_signature": sign})
		return params
	else:
		return "%s?%s&oauth_signature=%s" % (url, s, sign)
	
def fr_build_signature(url, s, post, secret):
	signature = [
		"POST" if post else "GET",
		escape(url),
		escape(s),
	]

	key = "%s&" % escape(FLICKR_CLIENT_SECRET)
	if secret != None:
		key += escape(secret)
	raw = "&".join(signature)

	hashed = hmac.new(str.encode(key), str.encode(raw), sha1)
	return to_utf8(b2a_base64(hashed.digest())[:-1])

# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
def getTerminalSize():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return (int(cr[1]), int(cr[0]))
