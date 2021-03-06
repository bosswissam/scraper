import os, json, unittest
from _common import *
from _scrapers import Scraper

REWRITE = False
DOWNLOAD_DIR = 'saved_pages'
TEST_URLS = 'test-urls.csv'


class StaticScraperTestCase(unittest.TestCase):
    ''' Test class for pinscraper.
    This test class allows for information to be pre-stored, this way the hard-coded tests for the scrapers do not fail simply because the actual content changed.
    params:
    REWRITE -- specify whether to re-download urls for the tests. Setting to True will mean some assertions will have to be modified to reflect new values.
    DOWNLOAD_DIR -- where the program will pre-download urls
    TEST-URLS -- a csv file with two columns: item url, image url
    
    Note: To make the test run faster, set the scraping_request_stagger in the cache to a lower value.
    '''

    _test_is_set = False

    def setUp(self):
        if self._test_is_set is False:
            self.setUpClass()

    @classmethod
    def setUpClass(cls):
        '''Sets up saved pages for all urls in URLS, and loads them to be easily accessible 
        for tests.
        The most important thing happening here is population of cls.rows. Here's what's 
        happening:
        - at the start, cls.rows contains only the item and image urls from the csv file
        - since my code will load a file from disk from each test case, I pre-load it into 
        cls.rows. The code appends after the second element a list of objects the test will 
        use (e.g. etsy listing object and etsy seller object)
        - finally, I append to that row the appropriate scraper object, this way I don't have 
        to keep calling constructors in my code, instead I can simply retrieve the last 
        element.

        Note: the only requirement here is that the writer of the test knows which row to use
        for each test
        '''
        cls.cur_dir = os.getcwd()
        reader = sopen(TEST_URLS)
        scraper = Scraper()
        chdir(DOWNLOAD_DIR)        

        cls.rows = []
        for row in reader:
            row = row.split(",", 1)
            domain = get_domain(row[0])
            scraper = scraper.get_scraper(domain)
            if (REWRITE or exists(DOWNLOAD_DIR) is False):
                scraper.download(row[0])
            row.extend(scraper.load(row[0]))
            row.append(scraper)
            cls.rows.append(row)

        cls._test_is_set = True
       
    def test_etsy_listing(self):
        '''Test if the information is parsed correctly
        '''
        content = json.loads(self.rows[0][2])
        listing = self.rows[0][-1].scrape(content)
        self.assertEqual(listing.price, '46.00')
        self.assertEqual(listing.currency_code, 'USD')
        self.assertEqual(listing.user_interaction.views, 931)
        self.assertEqual(listing.user_interaction.num_favorers, 303)
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
        '''Test scrape for TheSartorialistScraper
        '''
        item = self.rows[2][-1].scrape(self.rows[2][2])
        self.assertEqual(item.title, 'On the Street…Rue Pierre Sarrazin, Paris')
        self.assertEqual(item.details.date_posted, 'Saturday, December 10, 2011')
        self.assertEqual(item.details.category, 'Women')
        self.assertEqual(item.user_interaction.comments_num, '62')
        self.assertSameElements(item.tags, ['Paris', 'Prints', 'Women'])


    def test_thesartorialist_grab_real_url(self):
        ''' Test grab_real_url function for TheArtorialistScraper
        '''
        p = self.rows[2][-1]
        url = p.grab_real_url(self.rows[2][1].strip())
        self.assertEqual(self.rows[2][0], url)
    

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        chdir(self.cur_dir)

class DynamicScraperTestCase(unittest.TestCase):
    '''I created this TestCase mainly to include amazon's test case. Some urls
    from amazon have malformed html content are causing my static tester to 
    fail. In the long run, the real solution to this is to use the Amazon
    Products API.

    IMPORTANT: remember that this test might fail simply because the actual
    online content changed
    '''
    def test_amazon_scraper(self):
        '''Test get_item_info for AmazonScraper
        '''
        scraper = Scraper()
        scraper = scraper.get_scraper('www.amazon.com')
        item = scraper.get_item_info('http://www.amazon.com/gp/product/B002P8T0L0/ref=s9_simh_gw_p23_d0_g23_i1?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-2&pf_rd_r=0WQ1VFHRSY7ZTB93FGYG&pf_rd_t=101&pf_rd_p=470938631&pf_rd_i=507846','http://ecx.images-amazon.com/images/I/31hak2cSIOL.jpg')
        self.assertEqual(item.price, 75.99)
        self.assertEqual(item.currency_code, '$')
        self.assertEqual(item.user_interaction.likes, 42)
        self.assertEqual(item.quantity.new, 5)
        self.assertEqual(item.details.discount.value, 43.96)


if __name__ == '__main__':
    #unittest.main()
    suite1 = unittest.TestLoader().loadTestsFromTestCase(StaticScraperTestCase)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(DynamicScraperTestCase)
    alltests = unittest.TestSuite([suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(alltests)
