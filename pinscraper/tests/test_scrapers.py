import csv, argparse, os, json, urllib, sys, unittest
from common import *
from scrapers import Scraper

REWRITE_STATIC = False
STATIC_DIR = 'saved_pages'
TEST_URLS = 'test-urls.csv'


class ScraperTestCase(unittest.TestCase):
    ''' Test class for my scraper.
    This test class allows for information to be pre-stored, this way the hard-coded tests for the scrapers do not fail simply because the actual content changed.
    params:
    REWRITE_STATIC -- specify whether to re-download urls for the tests. Setting to True will mean some assertions will have to be modified to reflect new values.
    STATIC_DIR -- where the program will pre-download urls
    TEST-URLS -- a csv file with two columns: item url, image url
    
    Note: To make the test run faster, set the scraping_request_stagger in the cache to a lower value.
    '''

    _test_is_set = False

    def setUp(self):
        if self._test_is_set is False:
            self.setUpClass()

    @classmethod
    def setUpClass(cls):
        '''Sets up saved pages for all urls in URLS, and loads them to be easily accessible for tests.
        The most important thing happening here is population of cls.rows. Here's what's happening:
        - at the start, cls.rows contains only the item and image urls from the csv file
        - since my code will load a file from disk from each test case, I pre-load it into cls.rows. The code appends after the second element a list of objects the test will use (e.g. etsy listing object and etsy seller object)
        - finally, I append to that row the appropriate scraper object, this way I don't have to keep calling constructors in my code, instead I can simply retrieve the last element.
        '''
        cls.cur_dir = os.getcwd()
        reader = csv.reader(open(TEST_URLS, 'r'))
        scraper = Scraper()
        
        os.chdir(STATIC_DIR)
        cls.rows = [x for x in reader]
        
        for row in cls.rows:
            domain = get_domain(row[0])
            scraper = scraper.get_scraper(domain)
            if (REWRITE_STATIC or os.path.exists(STATIC_DIR) is False):
                scraper.download(row[0])
            row.extend(scraper.load(row[0]))
            row.append(scraper)

        cls._test_is_set = True
       
    def test_etsy_listing(self):
        '''Here we only test if the information is parsed correctly, with the option of using pre-downloaded data (so that hardcoded values in the test don't become incorrect)
        '''
        content = json.loads(self.rows[0][2])
        listing = self.rows[0][-1].scrape(content)
        self.assertEqual(listing.price, '46.00')
        self.assertEqual(listing.currency_code, 'USD')
        self.assertEqual(listing.ratings.views, 923)
        self.assertEqual(listing.ratings.num_favorers, 302)
        self.assertEqual(listing.quantity, 1)
        self.assertSameElements(listing.tags, ['Books and Zines', 'Journal', 'Leather', 'journal', 'diary', 'travel journal', 'book', 'leather', 'blank', 'guestbook', 'brown', 'antique looking', 'bound', 'homespunsociety', 'fathers day', 'men'])
        self.assertEqual(listing.title, 'Brown Leather Journal')
        self.assertTrue('This is a soft cover antique looking brown leather Journal hand sewn with about 440 pages(front and back)  .' in listing.details.description)
        
    def test_etsy_seller(self):
        '''Test that seller info was parsed correctly. Could fail if seller_id changes
        '''
        content = json.loads(self.rows[1][3])
        seller = self.rows[1][-1].scrape_seller(content)
        self.assertEqual(seller.feedback_info.count, 76)
        self.assertEqual(seller.feedback_info.score, 100)

    def test_thesartorialist_scraper(self):
        '''Test that information is parsed correctly
        '''
        item = self.rows[2][-1].scrape(self.rows[2][2])
        self.assertEqual(item.title, 'On the Street…Rue Pierre Sarrazin, Paris')
        self.assertEqual(item.details.date_posted, 'Saturday, December 10, 2011')
        self.assertEqual(item.details.category, 'Women')
        self.assertEqual(item.details.comments_num, '62')
        self.assertSameElements(item.tags, ['Paris', 'Prints', 'Women'])

    def test_thesartorialist_grab_real_url(self):
        p = self.rows[2][-1]
        url = p.grab_real_url(self.rows[2][1].strip())
        self.assertEqual(self.rows[2][0], url)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        os.chdir(self.cur_dir)

if __name__ == '__main__':
    unittest.main()
