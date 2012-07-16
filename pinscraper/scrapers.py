import re, sys, json, urllib, os, caching
from bs4 import BeautifulSoup as bs
from common import *

def download_image(img_url, dir_name):
    response, img = caching.fetch(img_url, 'GET')
    print(img_url)
    if (response['content-location'] != img_url): # so far this means redirected to no image
        write_to_file(os.path.join(dir_name, 'image_not_found.txt'), 'w', "image at {0} was not found".format(img_url))
        return False
#    img = img.read()
    img_name = os.path.basename(img_url)
    write_to_file(os.path.join(dir_name, img_name), 'wb', img)
    return True

class Scraper:

    _URL_REGEX = '\w+:/*(?P<domain>[a-zA-Z0-9.]*)/'
    
    def __init__(self):
        # maintain a dict of scrapers so we don't have to recreate them
        self.scrapers = {}
        # map domain names to scrapers
        self.scraper_classes = {}
        self.load_scrapers()

    def load_scrapers(self):
        self.scraper_classes['www.etsy.com'] = EtsyScraper
        self.scraper_classes['www.thesartorialist.com'] = TheSartorialistScraper
    
    def get_scraper(self, domain):
        if domain in self.scrapers:
            return self.scrapers[domain]
        elif domain in self.scraper_classes:
            scraper = self.scraper_classes[domain]()
            self.scrapers[domain] = scraper
            return scraper
        else:
            return None

    def get_item_info(self, url, image_url=None):
        path = re.split(self._URL_REGEX, url)[2]
        if (path.strip() == ''):
            if (image_url==None):
                return None
            # the url posted is just the homepage
            url = self.grab_real_url(image_url)
        # get content for item and parse it
        resp, content = caching.fetch(url)
        return self.scrape(content)
    
    def grab_real_url(self, search_key):
        ''' Given the homepage and a key that identifies an item, try to search the website for the item's "real" url.
        
        Keyword arguments:
        search_key -- key that uniquely identifies the item (e.g. image url)

        '''
        pass
        
    def scrape(self, content):
        ''' Scrapes content and returns an item
        '''
        pass
    
    def download(self, url):
        ''' Download the content of a page for late usage. The content is saved to a file
        with the url as filename
        '''
        pass

    def load(self, url):
        ''' Load the content of a page from disk.
        '''
        filename = urllib.parse.quote_plus(url)
        item = read_from_file(filename)
        return [item]


class EtsyScraper(Scraper):

    '''A Scraper class to handle scraping content for items on www.etsy.com. Instead of actually scraping the contents of pages of items, it makes a request through the etsy API to get information about the item in json format, then "scrapes" it into our desired schema.
    
    Note: in the future recommend using python2.x to be able to use etsy-python (could not get it to work for python3.1)
    
    '''
    
    _API_KEY = 'g9styowjvlxaew7h8u5ue85e'
    _LISTING_API_URL = 'http://openapi.etsy.com/v2/private/listings/'
    _USER_API_URL = 'http://openapi.etsy.com/v2/private/users/'
    _URL_ID_NAME = 'listing_id'
    _URL_ID_REGEX = "/(?P<{0}>[0-9]+)/".format(_URL_ID_NAME)

    def scrape(self, content):
        item = SimpleItem()
        content = content['results'][0]
        item.id = content['listing_id']
        # introduced a new field to make it easier to check if the content is empty (from 
        # outside the class)
        # This can change in the future, for now I noticed if a Listing does not have
        # one of those states then it has little information to get
        if (content['state'] != 'active' and content['state'] != 'sold_out'):
            return
        item.url = content['url']
        item.title = content['title']
        item.seller = self._get_etsy_seller(content['user_id'])
        item.tags = content['tags']
        item.tags.extend(content['category_path'])
        item.quantity = content['quantity']
        if (item.quantity):
            item.price = content['price']
        else:
            item.price = -1 # if price <  0, my json serializer will write null
        item.currency_code = content['currency_code']
        item.details = SimpleObject()
        item.details.category_path = content['category_path']
        item.details.description = content['description']
        item.ratings = SimpleObject()
        item.ratings.views = content['views']
        item.ratings.num_favorers = content['num_favorers']
        return item

    def get_item_info(self, url, image_url=None):
        content = get_content_as_json(self._get_etsy_listing_api_url(url))
        return self.scrape(content)

    def scrape_seller(self, content):
        seller = SimpleObject()
        content = content['results'][0]
        seller.id = content['user_id']
        seller.login_name = content['login_name']
        seller.feedback_info = SimpleObject()
        seller.feedback_info.count = content['feedback_info']['count']
        seller.feedback_info.score = content['feedback_info']['score']
        return seller
    
    def _get_etsy_seller(self, user_id):
        content = get_content_as_json(self._get_etsy_seller_api_url(user_id))
        seller = self.scrape_seller(content)
        return seller

    def _get_etsy_seller_api_url(self, user_id):
        return '{0}{1}?api_key={2}'.format(self._USER_API_URL, user_id, self._API_KEY)

    def _get_etsy_listing_api_url(self, url):
        listing_id = re.search(self._URL_ID_REGEX, url).group(self._URL_ID_NAME)
        return '{0}{1}?api_key={2}'.format(self._LISTING_API_URL, listing_id, self._API_KEY)
        
    def download(self, url):
        seller_id = self.get_item_info(url).seller.id
        item = get_content_as_json(self._get_etsy_listing_api_url(url))
        seller = get_content_as_json(self._get_etsy_seller_api_url(seller_id))
        filename = urllib.parse.quote_plus(url)
        json_dump_to_file(filename, item)
        json_dump_to_file(filename + '-seller', seller)


    def load(self, url):
        filename = urllib.parse.quote_plus(url)
        item = read_from_file(filename)
        seller = read_from_file(filename+'-seller')
        return [item, seller]


class TheSartorialistScraper(Scraper):
    '''Scraper class that scrapes thesartorialist urls for information about items.

    Fields:
    _search_url -- used to figure out the real url of an item given a search key

    '''
    _search_url = 'http://www.thesartorialist.com/?s={0}'

    def grab_real_url(self, search_key):
        resp, content = caching.fetch(self._search_url.format(search_key))
        soup = bs(content)
        result_list = soup.find('a', 'overhand')
        url = result_list['href']
        return url

    def scrape(self, content):
        ''' Parse content to object
        '''
        item = SimpleItem()
        soup = bs(content)
        item.details.category = soup.find('a', {'rel':'category tag'}).string
        item.tags = [x.string for x in soup.findAll('a', {'rel':'tag'})]
        item.details.comments_num = soup.find('span', 'nb-comment').string
        item.details.date_posted = soup.find('p', 'date-post').contents[1]
        item.title = soup.find('a', {'rel':'bookmark'}).string
        return item

    def download(self, url):
        resp, content = caching.fetch(url)
        write_to_file(urllib.parse.quote_plus(url), 'w', content.decode('utf-8'))
    

if __name__ == '__main__':
    x = TheSartorialistParser()
    url = x.grab_real_url('http://images.thesartorialist.com/thumbnails/2011/12/101411IMG_4766Web1.jpg')
    print(url)
    x.get_item_info('http://www.thesartorialist.com/','http://images.thesartorialist.com/thumbnails/2011/12/101411IMG_4766Web1.jpg')

