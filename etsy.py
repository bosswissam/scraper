# I ran into a lot of setup problems while attempting to use the etsy-python library
# to communicate with the etsy api, hence I decided to use my own simple request for
# the purposes of this project


import httplib2, json, urllib, re
from common import *


API_KEY = 'g9styowjvlxaew7h8u5ue85e'
LISTING_API_URL = 'http://openapi.etsy.com/v2/private/listings/'
USER_API_URL = 'http://openapi.etsy.com/v2/private/users/'
URL_ID_NAME = 'listing_id'
URL_ID_REGEX = "/(?P<{0}>[0-9]+)/".format(URL_ID_NAME)


product_id = '88017614'


def get_etsy_listing(url):
    content = get_content(get_etsy_listing_api_url(url))
    listing = EtsyListing(content)
    if(not listing.is_empty):
        listing.seller = get_etsy_seller(listing.seller)
    listing.url = url
    return listing

def get_etsy_seller(user_id):
    content = get_content(get_etsy_seller_api_url(user_id))
    seller = EtsySeller(content)
    return seller

def get_etsy_seller_api_url(user_id):
    return '{0}{1}?api_key={2}'.format(USER_API_URL, user_id, API_KEY)

def get_etsy_listing_api_url(url):
    listing_id = re.search(URL_ID_REGEX, url).group(URL_ID_NAME)
    return '{0}{1}?api_key={2}'.format(LISTING_API_URL, listing_id, API_KEY)

def get_content(url):
    resp, content = httplib2.Http().request(url, 'GET')
    assert resp.status == 200
    # for some reason the content is in binary
    content = content.decode("utf-8")
    content = json.loads(content)
    return content




class EtsyListing():

    '''Creating this class to abstract away the parsing of the information about the object. This "interface" would make it easier to create EtsyListings using other means (by hand for example, for testing). content is a dict formated as the 'results' object in the json object returned by the Etsy API. You can find samples in saved_pages/etsy
    '''
    
    def __init__(self, content):
        content = content['results'][0]
        self.id = content['listing_id']
        # introduced a new field to make it easier to check if the content is empty (from 
        # outside the class)
        # This can change in the future, for now I noticed if a Listing does not have
        # one of those states then it has little information to get
        self.is_empty = (content['state'] != 'active' and content['state'] != 'sold_out')
        if (self.is_empty):
            return
        self.url = content['url']
        self.title = content['title']
        self.seller = content['user_id']
        # expecting a list
        self.tags = content['tags']
        # for etsy listings, categories are viewed as tags on the web page
        self.tags.extend(content['category_path'])
        self.quantity = content['quantity']
        if (self.quantity):
            self.price = content['price']
        else:
            self.price = -1 # if price <  0, my json serializer will write null
        self.currency_code = content['currency_code']
        # details is a list of objects, e.g. [ 'dimensions':{'weight' : x, 'height': y}] - from amazon
        self.details = SimpleObject()
        self.details.category_path = content['category_path']
        self.details.description = content['description']
        # ratings is a list of Rating objects
        self.ratings = SimpleObject()
        self.ratings.views = content['views']
        self.ratings.num_favorers = content['num_favorers']



# Storing the information about a seller on Etsy using the EtsySeller object allows us more
# flexibility in what we would like to store about the seller.

class EtsySeller():
    
    def __init__(self, content):
        content = content['results'][0]
        self.id = content['user_id']
        self.login_name = content['login_name']
        self.feedback_info = SimpleObject()
        self.feedback_info.count = content['feedback_info']['count']
        self.feedback_info.score = content['feedback_info']['score']

        
#getListing(product_id)
