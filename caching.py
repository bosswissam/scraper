import httplib2, re, time, os, shutil

CACHE_PATH = '{0}/.cache'.format(os.path.dirname(os.path.realpath(__file__)))

class Cache:
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
        data, cached_at = cache.scraping_cache(key)
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
