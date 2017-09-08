import requests
from bs4 import BeautifulSoup
from crawlerUtl import preprocessing
url = "https://en.wikipedia.org/wiki/Graybar%23Recent_years"
url = "https://www.anixter.com/en_ca/manufacturers.html"
url = "https://en.wikipedia.org/wiki/Anixter"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'lxml')

[x.extract() for x in soup.findAll('script')]  ##take off script part in html
[x.extract() for x in soup.findAll('style')]
[x.extract() for x in soup.findAll('nav')]
[x.extract() for x in soup.findAll('footer')] 

print(preprocessing(soup.text))