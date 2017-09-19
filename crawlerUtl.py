from bs4 import BeautifulSoup
import re
import string

def getDistinctName(compName):
    exclude = set(string.punctuation)
    distinctName = ''.join(p for p in compName if p not in exclude)
    distinctName = distinctName.replace(" ", "_").lower()  ##Build self.distinctName
    return distinctName

def QueueTransfering(Queue):
	Qlist = []
	while True:
		try:
			Qlist.append(Queue.get(timeout=1))
		except:
			break
	return Qlist


def replaceEscapeChar(url):
    escapeDict = {
            '%20': ' ',
            '%21': '!',
            '%22': '"',
            '%23': '#',
            '%24': '$',
            '%25': '%',
            '%26': '&',
            '%27': "'",
            '%28': '(',
            '%29': ')',
            '%2A': '*',
            '%2B': '+',
            '%2C': ",",
            '%2D': '-',
            '%2E': '.',
            '%2F': '/',
            '%30': '0',
            '%31': '1',
            '%32': '2',
            '%33': '3',
            '%34': '4',
            '%35': '5',
            '%36': '6',
            '%37': '7',
            '%38': '8',
            '%39': '9',
            '%3A': ':',
            '%3B': ';',
            '%3C': '<',
            '%3D': '=',
            '%3E': '>',
            '%3F': '?',
            '%40': '@'}
    for key, value in escapeDict.items():
        url = url.replace(key, value)
    return url

def BingLinkParser(driver, query):
    url = "https://www.bing.com/"
    driver.get(url)
    elem = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
    elem.send_keys(query)
    elem = driver.find_element_by_xpath('//*[@id="sb_form_go"]')
    elem.submit()
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, 'lxml')
    Links = soup.find_all('a')

    Goodlinks = []
    for link in Links:
        linkstr = str(link)
        if (('http' in linkstr) and ('href' in linkstr) and (not 'href="#"' in linkstr) and (not 'href="http://go.microsoft' in linkstr)and (not 'microsofttranslator' in linkstr)):
            Goodlinks.append(link)

    urls = []
    for link in Goodlinks:
        if link['href'] not in urls and link['href'].split("%23")[0] not in urls:
            urls.append(replaceEscapeChar(link['href']))

    return urls



def GoogleLinkParser(driver, query):
    url = "https://www.google.com.hk/webhp?hl=en-us"
    driver.get(url)
    elem = driver.find_element_by_css_selector('.lst')
    elem.send_keys(query)
    elem.submit()
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, 'lxml')
    urls = []
    for link in soup.find_all('a'):
        if "/url?q=" in str(link).lower() and not 'googleusercontent' in str(link).lower():
            url = link['href'].split('&sa')[0].replace('/url?q=', '')
            if re.findall(r'^http', url.lower()) and url.split("%23")[0] not in urls:
                urls.append(replaceEscapeChar(url))

    return urls





import nltk
import os

if not "nltkDataDownloaded" in os.listdir():
    nltk.download('stopwords')
    nltk.download('wordnet')
    print('download nltk data success')
    file = open("downloaded", 'w')
    file.write("downloaded")
    file.close()

import re
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from os import listdir, stat

def preprocessing(companyStr):

    companyStr = companyStr.replace("\n"," ").replace("\t"," ").replace("\r"," ")

    i = 0
    while i < 30 :
        companyStr = companyStr.replace("  "," ")
        i+=1

    #re_words = re.compile(u"[\u4e00-\u9fa5]+")  ##drop chinese 
    re_words = re.compile(u"[\u3400-\u9FFF]+?") ##drop chinese korean japanese
    dropStrs = re.findall(re_words, companyStr)
    if len(dropStrs) != 0:
        for ds in dropStrs:
            companyStr = companyStr.replace(ds,"")

    re_words = re.compile('\{.*\}' )
    dropStrs = re.findall(re_words, companyStr)
    if len(dropStrs) != 0:
        for ds in dropStrs:
            companyStr = companyStr.replace(ds,"")

    re_words = re.compile('[\d]+')
    dropStrs = re.findall(re_words, companyStr)
    if len(dropStrs) != 0:
        for ds in dropStrs:
            companyStr = companyStr.replace(ds,"")

    for pun in string.punctuation+"©":
        companyStr = companyStr.replace(pun, "")

    stops = list(set(stopwords.words('english')))
    lemmer = WordNetLemmatizer()

    file = open('statesFilter/stateSimilars', 'r',encoding='utf8')

    for line in file:
        stops.append(line.replace("\n",""))
    file.close()

    def isfilter(s):
        return any(not i.encode('utf-8').isalpha() for i in s)

    companyStr = companyStr.lower().strip()
    companyStr.replace('®','')

    paramStr = ""
    for i in companyStr.split():
        try:
            if ((i not in stops) and (not isfilter(i))):
                paramStr += lemmer.lemmatize(i)+ " "
        except:
            continue

    return paramStr

# if __name__ == '__main__':
#     testingStr = "brands the cocacola company the cocacola company the cocacola company locations africa morocco french asia pacific australia china hong kong india japan new zealand eurasia middle east arabic middle east english pakistan english pakistan urdu russia europe austria belgium dutch belgium french denmark finland france germany great britain ireland italy netherlands norway portugal poland spain sweden switzerland ukraine latin america argentina bolivia brazil chile colombia costa rica dominican republic ecuador el salvador guatemala honduras mexico nicaragua panama paraguay peru uruguay venezuela north america global canada english canada french locations investors  the cocacola company our company our company main about cocacola journey mission vision  values diversity  inclusion human and workplace rights workplace overview supplier diversity cocacola leaders the cocacola system company history company reports sustainability report cocacola product facts us the cocacola foundation world of cocacola cocacola store investors investors main  year in review investors info financial reports and information investors info stock information investors info investor webcasts and events shareowner information corporate governance investors info sec filings press center press center main press releases company statements leadership video library image library press contacts careers careers main contact us contact us main faqs by cokestyle  sustainability report water replenishment giving back diversity  inclusion our commitment to transparency brands the cocacola company cocacola sprite fanta diet coke cocacola zero cocacola life dasani minute maid ciel powerade simply orange cocacola light fresca glacéau vitaminwater del valle glacéau smartwater mello yello fuze fuze tea honest tea odwalla powerade zero cocacola freestyle world of cocacola cocacola store close the cocacola company view product description all social facebook instagram twitter google youtube linkedin visit facebook visit instagram visit twitter visit google visit youtube visit linkedin load more cocacola on social likes followers followers views followers"
#     print(preprocessing(testingStr))        
#     # preprocessing(testingStr)    