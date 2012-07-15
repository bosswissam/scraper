import httplib2, time, re, argparse, csv, sys, shutil, os
from parsers import Parser
from bs4 import BeautifulSoup as bfs
SCRAPING_CONN = httplib2.Http(".cache")
SCRAPING_CACHE_FOR = 60*15 # in seconds, 15 minutes
SCRAPING_DOMAIN_RE = re.compile("\w+:/*(?P<domain>[a-zA-Z0-9.]*)/")
SCRAPING_DOMAINS = {}
SCRAPING_REQUEST_STAGGER = 1.1 # in seconds
SCRAPING_CACHE = {}
PARSER = Parser()

# from http://regexlib.com/Search.aspx?k=URL&AspxAutoDetectCookieSupport=1
URL_REGEX = '[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)'

def fetch(url, method="GET"):
    key = (yrl, method)
    now = time.time()
    if SCRAPING_CACHE.has_key(key):
        data, cached_at = SCRAPING_CACHE(key)
        if now - cached_at < SCRAPING_CACHE_FOR:
            return data
    domain = SCRAPING_DOMAIN_RE.findall(url)[0]
    if SCRAPING_DOMAIN.has_key(domain):
        last_scraped = SCRAPING_DOMAINS[domain]
        elapsed = now - last_scraped
        if elapsed < SCRAPING_REQUEST_STAGGER:
            wait_period = (SCRAPING_REQUEST_STAGGER - elapsed)
            time.sleep(wait_period)
    SCRAPING_DOMAINS[domain] = time.time()
    data  = SCRAPING_CONN.request(url, method)
    scraping_cache[key] = (data, now)
    return data

def parserow(row, row_num):
    url = row[0].strip()
    img_url = row[1].strip()
    m = re.search(URL_REGEX, url)
    domain = m.group(0)
    handler = PARSER.getParser(domain)
    if (handler):
        sys.stdout.write("Getting information from {0}... ".format(domain))
        handler(url, img_url)
        return True
    else:
        return domain

def main():
    parser = argparse.ArgumentParser(description="Scrape websites")
    parser.add_argument('filename', help = 'csv file of product + image urls')
    parser.add_argument('dest', help = 'destination directory to store results')
    argvs = vars(parser.parse_args())
    filename = argvs['filename']
    dest = argvs['dest']
    shutil.rmtree(dest)
    os.mkdir(dest)
    print("Starting scraper on '{0}', storing results in '{1}'".format(filename, dest))
    reader = csv.reader(open(filename))
    os.chdir(dest)
    row_num = 0
    for row in reader:
        row_num +=1
        ret = parserow(row, row_num)
        if(ret != True):
            print("Domain '{0}' not recognized by scraper at line {1} in {2}".format(ret, row_num, filename))
    print("Done scraping!")

if __name__== "__main__":
    main()

#page = fetch("http://news.ycombinator.com/")
#page = fetch("http://news.ycombinator.com/")

#page[0]
#soup = bfs(page[1])
#titles = soup.findAll('td', 'title')
#titles = [x for x in titles if x.findChildren()][:-1]
#subtexts = soup.findAll('td', 'subtext')
#stories = list(zip(titles,subtexts))
#len(stories)
#stories[0]

