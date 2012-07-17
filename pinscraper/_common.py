import json, re, urllib, os, shutil
from _caching import fetch
from _settings import *

DOMAIN = 'domain'
URL_REGEX = '\w+:/*(?P<{0}>[a-zA-Z0-9.]*)/'.format(DOMAIN)

'''This module contains a number of helper functions.
Some of these functions are defined here because they are used in multiple other
modules (e.g. get_content_as_json). Some are defined here just to keep the code 
clean (e.g. the file system operations).
'''

class SimpleObject:
    '''Not a very special class. I would have used object() instead but I cannot add
    arbitrary attributes to an object().
    '''
    
    def __init__(self):
        pass

#############################################################################
#############################################################################
## FILE SYSTEM OPERATIONS
#############################################################################
#############################################################################

def exists(path):
    if os.path.isabs(path) or STATIC_DIR in os.getcwd():
        return os.path.exists(path)
    else:
        return os.path.exists(os.path.join(STATIC_DIR, path))

def sopen(filename, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True):
    reader = None
    if os.path.isabs(filename) or STATIC_DIR in os.getcwd():
        return open(filename, mode, buffering, encoding, errors, newline, closefd)
    else:
        return open(os.path.join(STATIC_DIR, filename), mode, buffering, encoding, errors, newline, closefd)

def rmtree(path):
    if os.path.isabs(path) or STATIC_DIR in os.getcwd():
        return shutil.rmtree(path)
    else:
        return shutil.rmtree(os.path.join(STATIC_DIR, path))

def mkdir(path):
    if os.path.isabs(path) or STATIC_DIR in os.getcwd():
        os.mkdir(path)
    else:
        os.mkdir(os.path.join(STATIC_DIR, path))

def chdir(path):
    if os.path.isabs(path) or STATIC_DIR in os.getcwd():
        os.chdir(path)
    else:
        os.chdir(os.path.join(STATIC_DIR, path))

def walk(path):
    if os.path.isabs(path) or STATIC_DIR in os.getcwd():
        return os.walk(path)
    else:
        return os.walk(os.path.join(STATIC_DIR, path))


def write_to_file(filename, m, content):
    f = sopen(filename, mode=m)
    f.write(content)
    f.close()

def json_dump_to_file(filename, content):
    f = sopen(filename, 'w')
    json.dump(content, f, indent=2, default=serialize)
    f.close()

def read_from_file(filename):
    f = sopen(filename, 'r')
    content = f.read()
    f.close()
    return content


#############################################################################
#############################################################################
## JSON OPERATIONS
#############################################################################
#############################################################################

def get_content_as_json(url):
    resp, content = fetch(url)
    assert resp.status == 200
    # for some reason the content is in binary
    content = content.decode("utf-8")
    content = json.loads(content)
    return content


def serialize(x):
    return x.__dict__

#############################################################################
#############################################################################
## SIMULTANEOUS
#############################################################################
#############################################################################

def get_domain(url):
    m = re.search(URL_REGEX, url)
    domain = m.group(DOMAIN)
    return domain

def download_image(img_url, dir_name):
    '''Downloads an image. Fails if request is redirected.
    '''

    response, img = fetch(img_url, 'GET')
    if (response['content-location'] != img_url):
        write_to_file(os.path.join(dir_name, 'image_not_found.txt'), 'w', "image at {0} was not found".format(img_url))
        return False

    img_name = os.path.basename(img_url)
    write_to_file(os.path.join(dir_name, img_name), 'wb', img)
    return True
