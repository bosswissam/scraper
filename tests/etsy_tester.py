import csv, argparse, os, json, urllib, sys, unittest
sys.path.insert(0, os.path.split(os.getcwd())[0])
from etsy import *

ETSY_TEST_CSV = 'etsy-urls.csv'
REWRITE_STATIC = False
STATIC_DIR = 'saved_pages'
URLS = 'etsy-urls.csv'
LISTING_FILENAME = '{0}.json'
SELLER_FILENAME = '{0}-seller.json'

def _format(s, url):
    ''' to make code more readable
    '''
    return s.format(urllib.parse.quote_plus(url))

def save_etsy_page(url):
    ''' download json objects from Etsy into saved_pages for testing later
    '''
    download(get_etsy_listing_api_url(url), _format(LISTING_FILENAME, url))
    listing = get_etsy_listing(url)
    seller_url = get_etsy_seller_api_url(listing.seller.id)
    download(seller_url, SELLER_FILENAME.format(urllib.parse.quote_plus(url)))

def download(url, filename):
    f = open(filename, mode ='w')
    json.dump(get_content(url), f, indent=2)
    f.close()

def read_saved_content(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content
    

class EtsyScraperTestCase(unittest.TestCase):
    ''' This test class will be used to group tests for the scraping of Etsy urls
    '''
    def setUp(self):
        '''Sets up saved pages for all urls in URLS, and loads them to be easily accessible for tests
        '''
        self.reader = csv.reader(open(URLS, 'r'))
        self.cur_dir = os.getcwd()
        os.chdir(STATIC_DIR)
        self.rows = [x for x in self.reader]
        
        if (REWRITE_STATIC):
            for row in self.rows:
                save_etsy_page(row[0])
        for row in self.rows:
            row.extend([read_saved_content(_format(LISTING_FILENAME, row[0])), read_saved_content(_format(SELLER_FILENAME, row[0]))])
       
    def test_etsy_listing(self):
        '''Here we only test if the information is parsed correctly, with the option of using pre-downloaded data (so that hardcoded values in the test don't become incorrect)
        '''
        content = json.loads(self.rows[0][2])
        listing = EtsyListing(content)
        self.assertEqual(listing.price, '46.00')
        self.assertEqual(listing.currency_code, 'USD')
        self.assertEqual(listing.ratings.views, 920)
        self.assertEqual(listing.ratings.num_favorers, 302)
        self.assertEqual(listing.quantity, 1)
        self.assertSameElements(listing.tags, ['Books and Zines', 'Journal', 'Leather', 'journal', 'diary', 'travel journal', 'book', 'leather', 'blank', 'guestbook', 'brown', 'antique looking', 'bound', 'homespunsociety', 'fathers day', 'men'])
        self.assertEqual(listing.title, 'Brown Leather Journal')
        self.assertTrue('This is a soft cover antique looking brown leather Journal hand sewn with about 440 pages(front and back)  .' in listing.details.description)
        
    def test_seller(self):
        '''Test that seller info was parsed correctly. Could fail if seller_id changes
        '''
        content = json.loads(self.rows[1][3])
        seller = EtsySeller(content)
        self.assertEqual(seller.feedback_info.count, 75)
        self.assertEqual(seller.feedback_info.score, 100)
        

    def tearDown(self):
        os.chdir(self.cur_dir)

if __name__ == '__main__':
    unittest.main()
