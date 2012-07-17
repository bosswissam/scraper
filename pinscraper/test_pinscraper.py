import unittest, pinscraper
from _common import *

class PinscraperTestCase(unittest.TestCase):
    '''This TestCase is intended to be a shallow big-picture test for the 
    module since the details are already handled in test_scrapers.py
    '''
    def test_all_files_downloaded(self):
        '''Runs pinscraper and checks that it produced the right number of files.
        '''
        filename = 'test-urls.csv'
        dest = 'results'
        pinscraper.start_pinscraping(filename, dest)
        count = 0
        for root, dirs, files in walk(dest):
            count += len(files)
        f = sopen(filename)
        rows = [x for x in f]

        # Two files per row
        self.assertEqual(count, len(rows)*2)

if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PinscraperTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
