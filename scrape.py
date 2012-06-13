import httplib2
from bs4 import BeautifulSoup as bfs
conn = httplib2.Http(".cache")
page = conn.request("http://news.ycombinator.com/","GET")
#page[0]
#soup = bfs(page[1])
#titles = soup.findAll('td', 'title')
#titles = [x for x in titles if x.findChildren()][:-1]
#subtexts = soup.findAll('td', 'subtext')
#stories = list(zip(titles,subtexts))
#len(stories)
#stories[0]
