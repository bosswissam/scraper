import argparse, os
from _scrapers import Scraper
from _common import *


'''This module uses _scrapers to scrape a csv file of urls. The csv file must contain two columns: item url and image url.
Please run with -h for details on how to use.

'''

def start_pinscraping(filename, dest):
    '''Start scraping the specified csv file, and stores downloaded contents 
    in the dest directory.

    Arguments:
    filename -- absolute or relative path to csv file. Relative paths must be under 
    _settings.STATIC_DIR
    dest -- absolute or relative path to destination directory. Relative paths must 
    be under _settings.STATIC_DIR
    
    '''
    if exists(dest):
        rmtree(dest)
    mkdir(dest)
    reader = sopen(filename)
    curdir = os.getcwd()
    chdir(dest)

    print("Starting scraper on '{0}', storing results in '{1}'".format(filename, dest))    

    row_num = 0
    for row in reader:
        row_num +=1
        # we can only have two columns
        row = row.split(",", 1)
        ret = _pinscraperow(row, row_num)
        if(ret != True):
            print("Domain '{0}' not recognized by scraper at line {1} in {2}".format(ret, row_num, filename))
    chdir(curdir)
    print("Done scraping!")


def _pinscraperow(row, row_num):
    scraper = Scraper()
    url = row[0].strip()
    img_url = row[1].strip()
    dir_name = urllib.parse.quote_plus(url)
    mkdir(dir_name)
    download_image(img_url, dir_name)
    domain = get_domain(url)
    scraper = scraper.get_scraper(domain)
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
    parser.add_argument('filename', help = 'csv file of product and image urls. If path is relative, file is assumed to be in {0}'.format(STATIC_DIR))
    parser.add_argument('dest', help = 'destination directory to store results. If path is relative, it will be created under {0}'.format(STATIC_DIR))
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

