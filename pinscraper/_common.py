import json, re, urllib, os
from _caching import fetch

DOMAIN = 'domain'
URL_REGEX = '\w+:/*(?P<{0}>[a-zA-Z0-9.]*)/'.format(DOMAIN)

'''This module contains a number of helper functions.
'''

class SimpleObject:
    '''Not a very special class. I would have used object() instead but I cannot add
    arbitrary attributes to an object().
    '''
    
    def __init__(self):
        pass

def write_to_file(path, m, content):
    f = open(path, mode=m)
    f.write(content)
    f.close()

def json_dump_to_file(filename, content):
    f = open(filename, 'w')
    json.dump(content, f, indent=2, default=serialize)
    f.close()

def read_from_file(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content


def get_content_as_json(url):
    resp, content = fetch(url)
    assert resp.status == 200
    # for some reason the content is in binary
    content = content.decode("utf-8")
    content = json.loads(content)
    return content


# json.dumps is expecting a method, __dict__ is an attribute, hence this hack.
def serialize(x):
    return x.__dict__

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
