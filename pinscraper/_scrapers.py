import re, sys, json, urllib, os
from bs4 import BeautifulSoup as bs
from _common import *
from _caching import fetch

'''In this module scrapers for the different websites are defined. A scraper object contains
the necessary logic to get an item's information given the url.
'''

class Scraper:

    '''This class maintains a dictionary of scrapers that will scrape different websites.

    use get_scraper to retrieve a scraper for a particular domain.

    '''
    _URL_REGEX = '\w+:/*(?P<domain>[a-zA-Z0-9.]*)/'
    
    def __init__(self):
        self.scrapers = {}
        self.scraper_classes = {}
        self._load_scrapers()

    def _load_scrapers(self):
        self.scraper_classes['www.etsy.com'] = EtsyScraper
        self.scraper_classes['www.thesartorialist.com'] = TheSartorialistScraper
        self.scraper_classes['www.amazon.com'] = AmazonScraper
    
    def get_scraper(self, domain):
        '''Returns scraper for domain if it exists
        '''
        if domain in self.scrapers:
            return self.scrapers[domain]
        elif domain in self.scraper_classes:
            scraper = self.scraper_classes[domain]()
            self.scrapers[domain] = scraper
            return scraper
        else:
            return None

    def get_item_info(self, url, image_url=None):
        ''' Given a item url and image url, returns a json representation of the item's
        information. image url is usefl in case actual url is not - it can be used for finding
        the item's "real" url
        '''
        path = re.split(self._URL_REGEX, url)[2]
        if (path.strip() == ''):
            if (image_url==None):
                return None
            # the url posted is just the homepage
            url = self.grab_real_url(image_url)
        # get content for item and parse it
        resp, content = fetch(url)
        item = self.scrape(content)
        item.url = url
        return item
    
    def download(self, url):
        ''' Download the content of a page for late usage. The content is saved to a file
        with the url as filename
        '''
        resp, content = fetch(url)
        write_to_file(urllib.parse.quote_plus(url), 'w', content.decode('utf-8'))

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
        ''' Scrapes content and returns an item
        '''

        item = SimpleObject()
        content = content['results'][0]

        if (content['state'] != 'active' and content['state'] != 'sold_out'):
            # From some examples, this seemed to mean most json content is empty
            return

        # Get item url + title + seller info
        item.url = content['url']
        item.title = content['title']
        item.seller = self._get_etsy_seller(content['user_id'])

        # Get item tags
        item.tags = content['tags']
        item.tags.extend(content['category_path'])
        
        # Get item quantity + pricing
        item.quantity = content['quantity']
        if (item.quantity):
            item.price = content['price']
        item.currency_code = content['currency_code']

        # Get item details - category + description
        item.details = SimpleObject()
        item.details.category_path = content['category_path']
        item.details.description = content['description']
        item.user_interaction = SimpleObject()

        # Get user interaction - views + num_favorers
        item.user_interaction.views = content['views']
        item.user_interaction.num_favorers = content['num_favorers']

        return item

    def get_item_info(self, url, image_url=None):
        '''Same as Scraper.get_info
        '''
        content = get_content_as_json(self._get_etsy_listing_api_url(url))
        return self.scrape(content)

    def scrape_seller(self, content):
        '''Scrapes json content from Etsy API response
        '''

        seller = SimpleObject()
        content = content['results'][0]

        # Get seller id
        seller.id = content['user_id']

        # Get login_name
        seller.login_name = content['login_name']
        
        # Get seller feedback info
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
        '''Same idea as download for Scraper, but a little more trick: url is transformed into 
        the API url and information is also fetched for the seller.
        '''
        seller_id = self.get_item_info(url).seller.id
        item = get_content_as_json(self._get_etsy_listing_api_url(url))
        seller = get_content_as_json(self._get_etsy_seller_api_url(seller_id))
        filename = urllib.parse.quote_plus(url)
        json_dump_to_file(filename, item)
        json_dump_to_file(filename + '-seller', seller)


    def load(self, url):
        '''Load information for both item and seller
        '''
        filename = urllib.parse.quote_plus(url)
        item = read_from_file(filename)
        seller = read_from_file(filename+'-seller')
        return [item, seller]


class TheSartorialistScraper(Scraper):
    '''Scraper class that scrapes thesartorialist urls for information about items.

    Attributes:
    _search_url -- used to figure out the real url of an item given a search key

    '''
    _search_url = 'http://www.thesartorialist.com/?s={0}'

    def grab_real_url(self, search_key):
        ''' Given the homepage and a key that identifies an item, try to search the 
        website for the item's "real" url.
        
        Keyword arguments:
        search_key -- key that uniquely identifies the item (e.g. image url)

        '''

        resp, content = fetch(self._search_url.format(search_key))
        soup = bs(content)
        result_list = soup.find('a', 'overhand')
        url = result_list['href']
        return url

    def scrape(self, content):
        ''' Scrapes content and returns an item
        '''

        item = SimpleObject()
        soup = bs(content)

        # Get item details
        item.details = SimpleObject()
        item.details.category = soup.find('a', {'rel':'category tag'}).string
        item.details.date_posted = soup.find('p', 'date-post').contents[1]

        # Get item tags
        item.tags = [x.string for x in soup.findAll('a', {'rel':'tag'})]
        
        # Get user interaction - number of comments
        item.user_interaction = SimpleObject()
        item.user_interaction.comments_num = soup.find('span', 'nb-comment').string
        
        # Get item title
        heading = soup.find('a', {'rel':'bookmark'})
        item.title = heading.string
        return item

class AmazonScraper(Scraper):
    '''Scraper to scrape amazon.com urls
    '''
    
    def scrape(self, content):
        item = SimpleObject()
        soup = bs(content)

        # Get pricing info
        pricing = soup.find('b', 'priceLarge').string
        item.price = float(pricing[1:])
        item.currency_code = pricing[0]
        
        # Get ratings + likes
        item.user_interaction = SimpleObject()
        item.user_interaction.likes = int(soup.find('span', 'amazonLikeCount').string)
        item.user_interaction.five_star_rating = SimpleObject()
        item.user_interaction.five_star_rating.score = soup.find('span', 'swSprite s_star_4_5 ').string.split('out of')[0].strip()
        item.user_interaction.five_star_rating.count = re.search('(?P<count>\d+) customer reviews', str(soup.findAll('a'))).group('count')

        # Get more item details
        item.details = SimpleObject()
        discount = soup.find('span', {'id':'youSaveValue'}).string
        item.details.discount = SimpleObject()
        item.details.discount.value = float(discount.split(" ")[0][1:])
        item.details.discount.percentage = float(discount.split(" ")[-1][1:-2])

        # Get item quantity
        item.quantity = SimpleObject()
        quantities = [re.search('(?P<quantity>\d+).+', x.string).group('quantity') for x in soup.findAll('a', 'buyAction olpBlueLink')]
        item.quantity.new = int(quantities[0])
        if len(quantities) > 1:
            item.quantity.old = int(quantities[1])
        if len(quantities) > 2:
            item.quantity.refurbished = int(quantities[2])
        
        # Get item title
        item.title = soup.find('title').string

        # Get item tags
        item.tags = [x.string for x in soup.findAll('a', {'rel':'tag'})]
        return item

class GapScraper(Scraper):
    '''Scraper to scrape gap.com urls
    '''

    def scrape(self, content):
        ''' Gap uses javascrpting to load content on their page. To parse that I have to set up Webkit or something similar.
        '''
#        item = SimpleObject()
#        soup = bs(content)

        # Get item title
#        item.title = soup.find('div', 'brand1')

        # Get user interaction
#        item.user_interaction = SimpleObject()
#        item.user_interaction.five_star_rating = SimpleObject()
#        item.user_interaction.five_star_rating.score = soup.find('span', 'cssHide').split(" ")[1]
#        item.user_interaction.five_star_rating.count = soup.find('span', {'id':'reviewCount'}).split(" ")[0]

#        return item
        pass


if __name__=='__main__':
    x = GapScraper()
    x.get_item_info('http://www.gap.com/browse/product.do?cid=5231&vid=1&pid=768628&scid=768628352','http://www2.assets-gap.com/Asset_Archive/GPWeb/Assets/Product/768/768628/main/gp768628-35p01v01.jpg')

