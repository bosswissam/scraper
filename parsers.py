import re, sys, json, urllib, common, os, caching
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
    listing = get_etsy_listing(url)
#    sys.stdout.write("listing_id = {0}... ".format(listing.id))
    dir_name = urllib.parse.quote_plus(url)
    os.mkdir(dir_name)
    image_downloaded = download_image(img_url, dir_name)
    if (listing):
        f = open('{0}/info.json'.format(dir_name), mode = 'w')
        json.dump(listing, f, indent = 2, default=serialize)
        f.close()
        sys.stdout.write("Done. ")
    else:
        sys.stdout.write("Failed: Empty Listing. ")
        f = open('{0}/listing_not_found.txt'.format(dir_name), mode = 'w')
        f.write('The listing at {0} was not found'.format(url))
        f.close()
    if(image_downloaded):
        print("Image download succeeded")
    else:
        print("Image download failed")

def download_image(img_url, dir_name):
    response, img = caching.fetch(img_url, 'GET')
    if (response['content-location'] != img_url): # so far this means redirected to no image
        return False
#    img = img.read()
    img_name = os.path.basename(img_url)
    f = open(os.path.join(dir_name, img_name), mode = 'wb')
    f.write(img)
    f.close()
    return True
