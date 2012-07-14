import etsy, re, sys

etsy_url_id = 'listing_id'
etsy_url_regex = "/(?P<{0}>[0-9]+)/".format(etsy_url_id)

class Parser():
    def __init__(self):
        self.parsers = {}
        self.loadParsers()

    def loadParsers(self):
        self.parsers['www.etsy.com'] = etsy_parser
    
    def getParser(self, domain):
        if (domain in self.parsers):
            return self.parsers[domain]
        return None

def etsy_parser(url, img_url):
    # parses out the listing_id and calls the etsy api on it
    listing_id = re.search(etsy_url_regex, url).group(etsy_url_id)
#    print(etsy_url_regex)
#    print(url)
    sys.stdout.write("Getting information for {0} from Etsy".format(listing_id))
    if (etsy.getListing(listing_id)):
        print("... Done")
    else:
        print("... Failed")
    
