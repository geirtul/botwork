"""
Fetches relevant information from Request Tracker using
the RT API.
"""

import getpass
import urllib.request
import urllib.parse

import requests


uname = getpass.getpass("rt-user:")
upw = getpass.getpass("rt-pw: ")

# here is the RequestTracker URI we try to access
base_url = 'http://rt.uio.no/REST/1.0/'

r = requests.get(base_url + '?user=' + uname +'&pass=' + upw)
print(r.status_code)
print(r.text)
jar = r.cookies
a = requests.get(base_url, cookies=jar)
print(a.text)



