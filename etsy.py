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


# Creating this class to abstract away the parsing of the information about the object. 
# This "interface" would make it easier to create EtsyListings using other means (by hand
# for example, for testing).

class EtsyListing():
    
    def __init__(self, url):
        self.id = re.search(URL_ID_REGEX, url).group(URL_ID_NAME)
        self.url = url
        content = self.get_content('{0}{1}?api_key={2}'.format(LISTING_API_URL, self.id, API_KEY))
        # introduced a new field to make it easier to check if the content is empty (from 
        # outside the class)
        self.is_empty = (content==None)
#        print(content)
        if (self.is_empty):
            return
        self.title = content['title']
        self.description = content['description']
        self.seller = EtsySeller(content['user_id'])
        # expecting a list
        self.tags = content['tags']
        self.quantity = content['quantity']
        if (self.quantity):
            self.price = content['price']
        else:
            self.price = -1 # if price <  0, my json serializer will write null
        self.currency_code = content['currency_code']
        # details is a list of objects, e.g. [ 'dimensions':{'weight' : x, 'height': y}] - from amazon
        self.details = [SimpleDetail('category', content['category_path'])]
        # ratings is a list of Rating objects
        self.ratings = [Views(content['views']), Favorers(content['num_favorers'])]
        self.url = content['url'] #keep the real url


    def get_content(self, url):
        resp, content = httplib2.Http().request(url, 'GET')
        # for some reason the content is in binary
        content = content.decode("utf-8")
        content = json.loads(content)
        # doing some parsing
        content = content['results'][0]
        if (content['state'] != 'active' and content['state'] != 'sold_out'):
            # This can change in the future, for now I noticed if a Listing does not have
            # one of those states then it has little information to get
            return None
        return content



# Storing the information about a seller on Etsy using the EtsySeller object allows us more
# flexibility in what we would like to store about the seller.

class EtsySeller():
    
    def __init__(self, user_id):
        self.url = '{0}{1}?api_key={2}'.format(USER_API_URL, user_id, API_KEY)
        self.id = user_id
        content = self.get_content()
        self.login_name = content['login_name']
        self.feedback_info = content['feedback_info']

    def get_content(self):
        resp, seller_info = httplib2.Http().request(self.url, 'GET')
        content = seller_info.decode("utf-8")
        content = json.loads(content)
        content = content['results'][0]
        return content
        
#getListing(product_id)
