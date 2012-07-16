import time, re, argparse, csv, sys, shutil, os
from _scrapers import Scraper
from _common import *
from bs4 import BeautifulSoup as bfs
SCRAPER = Scraper()

# from http://regexlib.com/Search.aspx?k=URL&AspxAutoDetectCookieSupport=1
URL_REGEX = '\w+:/*(?P<domain>[a-zA-Z0-9.]*)/'#'[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)'


def start_pinscraping(filename, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    print("Starting scraper on '{0}', storing results in '{1}'".format(filename, dest))    
    reader = open(filename)
    os.chdir(dest)
    row_num = 0
    for row in reader:
        row_num +=1
        # we only have two columns
        row = re.split(",", row, maxsplit=1)
        ret = pinscraperow(row, row_num)
        if(ret != True):
            print("Domain '{0}' not recognized by scraper at line {1} in {2}".format(ret, row_num, filename))
    print("Done scraping!")


def pinscraperow(row, row_num):
    url = row[0].strip()
    img_url = row[1].strip()
    m = re.search(URL_REGEX, url)
    dir_name = urllib.parse.quote_plus(url)
    os.mkdir(dir_name)
    download_image(img_url, dir_name)
    domain = m.group('domain')
    scraper = SCRAPER.get_scraper(domain)
    if (scraper):
        print("Getting information from {0}... ".format(domain))
        content = scraper.get_item_info(url, img_url)
        if (content):
            json_dump_to_file('{0}/info.json'.format(dir_name), content)
        else:
            write_to_file('{0}/not_found.txt'.format(dir_name), 'w', 'The url at {0} was not found'.format(url))
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
    start_pinscraping(filename, dest)

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

