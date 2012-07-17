import httplib2, re, time, os, shutil, sys

CACHE_PATH = '{0}/.cache'.format(os.path.dirname(os.path.realpath(__file__)))


class Cache:

    '''This is a class to allow for caching for my scrapers. It was inspired by a simple python tutorial here: http://dev.lethain.com/an-introduction-to-compassionate-screenscraping/

    important attributes:
    scraping_cache_for -- how long to wait before invalidating a cached page
    scraping_domains -- a dictionarly that maintains the last time a domain was scraped by us
    scraping_cache -- a cache that stores the content of pages visited.

    Note 1: If I did not make the mistake of implementing this in python3, I would have imported the webscraping library and used pdict for the scraping_cache - it is a cache that uses a database.
    Note 2: This could could possibly have two cache layers (one in CACHE_PATH, if the domain specifies directives, and the second is our scraping_cache).
    '''
    _instance = None
    
    def __init__(self):
        self.scraping_conn = httplib2.Http(CACHE_PATH)
        self.scraping_cache_for = 60*15 # in seconds, 15 minutes
        self.scraping_domain_re = re.compile("\w+:/*(?P<domain>[a-zA-Z0-9.]*)/")
        self.scraping_domains = {}
        self.scraping_request_stagger = 1.1 # in seconds
        self.scraping_cache = {}


def get_instance():
    if(Cache._instance==None):
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)
        Cache._instance = Cache()
    return Cache._instance

def fetch(url, method="GET"):
    cache = get_instance()
    key = (url, method)
    now = time.time()
    if key in cache.scraping_cache:
        data, cached_at = cache.scraping_cache[key]
        if now - cached_at < cache.scraping_cache_for:
            return data
    domain = cache.scraping_domain_re.findall(url)[0]
    if domain in cache.scraping_domains:
        last_scraped = cache.scraping_domains[domain]
        elapsed = now - last_scraped
        if elapsed < cache.scraping_request_stagger:
            wait_period = (cache.scraping_request_stagger - elapsed)
            time.sleep(wait_period)
    cache.scraping_domains[domain] = time.time()
    data  = cache.scraping_conn.request(url, method)
    cache.scraping_cache[key] = (data, now)
    return data
