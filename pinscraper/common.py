import json, caching, re

DOMAIN = 'domain'
URL_REGEX = '\w+:/*(?P<{0}>[a-zA-Z0-9.]*)/'.format(DOMAIN)

class SimpleObject:    
    def __init__(self):
        pass

class SimpleItem:
    def __init__(self):
        self.details = SimpleObject()
        self.ratings = SimpleObject()

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
    resp, content = caching.fetch(url)
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
