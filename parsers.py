import re, sys, json, urllib, common, os, httplib2
from etsy import *

class Parser():
    def __init__(self):
        self.parsers = {}
        self.loadParsers()

    def loadParsers(self):
        self.parsers['www.etsy.com'] = etsy_parser
    
    def getParser(self, domain):
        if (domain in self.parsers):
            return self.parsers[domain]
        return None

def etsy_parser(url, img_url):
    listing = EtsyListing(url)
    sys.stdout.write("listing_id = {0}... ".format(listing.id))
    dir_name = '{0}'.format(urllib.parse.quote_plus(listing.url))
    os.mkdir(dir_name)
    image_downloaded = download_image(img_url, dir_name)
    if (listing.is_empty):
        sys.stdout.write("Failed: Empty Listing. ")
    else:
        f = open('{0}/info.json'.format(dir_name), mode = 'w')
        json.dump(listing, f, indent = 2, default=serialize)
        sys.stdout.write("Done. ")
    if(image_downloaded):
        print("Image download succeeded")
    else:
        print("Image download failed")

def download_image(img_url, dir_name):
    response, img = httplib2.Http().request(img_url, 'GET')
    if (response['content-location'] != img_url): # so far this means redirected to no image
        return False
#    img = img.read()
    img_name = os.path.basename(img_url)
    f = open(os.path.join(dir_name, img_name), mode = 'wb')
    f.write(img)
    f.close()
    return True
