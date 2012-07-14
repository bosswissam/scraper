# I ran into a lot of setup problems while attempting to use the etsy-python library
# to communicate with the etsy api, hence I decided to use my own simple request for
# the purposes of this project


import httplib2, json, urllib
from common import *

API_KEY = 'g9styowjvlxaew7h8u5ue85e'
GET_LISTING_URL = 'http://openapi.etsy.com/v2/private/listings/'
GET_USER_URL = 'http://openapi.etsy.com/v2/private/users/'
product_id = '88017614'

def getListing(product_id):

    listing = EtsyListing('{0}{1}?api_key={2}'.format(GET_LISTING_URL, product_id, API_KEY))

    user_id = x['user_id']

    resp, seller_info = httplib2.Http().request('{0}{1}?api_key={2}'.format(GET_USER_URL, user_id, API_KEY), 'GET')

    seller_info = seller_info.decode("utf-8")
    z = json.loads(seller_info)
    z = z['results'][0]
    
    result = {}
    result['id'] = product_id
    result['url'] = x['url']
    result['title'] = x['title']
    result['description'] = x['description']
    result['seller_info'] = {'user_id':z['user_id'], 'login_name':z['login_name'], 'feedback_info':z['feedback_info']}
    result['tags'] = x['tags']
    result['quantity'] = x['quantity']
    if (result['quantity']):
        result['price'] = {'currency_code' : x['currency_code'], 'price' : x['price']}
    result['details'] = {'category':x['category_path']}
    result['rating'] = {'views':x['views'], 'num_favorers': x['num_favorers']}
    f = open('results/{0}.json'.format(urllib.parse.quote_plus(result['url'])), mode = 'w')
    json.dump(result, f, indent = 2)
    return True

# Creating this class to abstract away the parsing of the information about the object. 
# This "interface" would make it easier to create EtsyListings using other means (by hand
# for example, for testing).

class EtsyListing():
    
    def __init__(self, url):
        self.url = url
        content = self.get_content()
        # introduced a new field to make it easier to check if the content is empty
        self.is_empty = (content==None)
        if (is_empty):
            return
        self.id = content['id']
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
        self.ratings = [Views(content['views']), Favorers(content['favorers'])]

    def is_empty(self):
        return self.is_empty
        
    def get_content(self):
        resp, content = httplib2.Http().request(self.url, 'GET')
        # for some reason the content is in binary
        content = content.decode("utf-8")
        content = json.loads(content)
        # doing some parsing
        content = x['results'][0]
        if (x['state'] != 'active' and x['state'] != 'sold_out'):
            # This can change in the future, for now I noticed if a Listing does not have
            # one of those states then it has little information to get
            return None
        return content

    def __init__(self, listing_id, title, description, seller, tags, quantity, price, currency_code, details, ratings):
        self.id = listing_id
        self.title = title
        self.description = description
        self.seller = seller
        self.tags = tags
        self.quantity = quantity
        self.price = price
        self.currency_code = currency_code
        


# Storing the information about a seller on Etsy using the EtsySeller object allows us more
# flexibility in what we would like to store about the seller.

class EtsySeller():
    
    def __init__(self, url):

#getListing(product_id)
