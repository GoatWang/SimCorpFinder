#multiprocessing and async
import aiohttp
import asyncio
import async_timeout
import queue
import threading
import random

# data processing
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

#write into DB
import uuid
from datetime import datetime
import string
from elasticUtl import datetimeReader
from elasticsearch import Elasticsearch
es = Elasticsearch()

# if es.indices.exists('companyembedding'):
#     es.indices.delete(index='companyembedding')
# if not es.indices.exists('companyembedding'):
#     es.indices.create('companyembedding')

if es.indices.exists('companyembedding_labeled'):
    es.indices.delete(index='companyembedding_labeled')
if not es.indices.exists('companyembedding_labeled'):
    es.indices.create('companyembedding_labeled')

if es.indices.exists('companyembedding_labeled_url'):
    es.indices.delete(index='companyembedding_labeled_url')
if not es.indices.exists('companyembedding_labeled_url'):
    es.indices.create('companyembedding_labeled_url')




#user write
from setting_selenium import cross_selenium
from preprocessing import preprocessing
from crawlerUtl import QueueTransfering
from crawlerUtl import BingLinkParser, GoogleLinkParser

#log writing and other
import json
import os
import time



class googleCrawler:
    async def fetch_coroutine(self, client, url):
        with async_timeout.timeout(10):
            try: 
                async with client.get(url) as response:
                    assert response.status == 200
                    contentType = str(response.content_type)
                    if 'html' in str(contentType).lower():
                        html = await response.text()
                        soup = BeautifulSoup(html ,'lxml')
                        [x.extract() for x in soup.findAll('script')]  ##take off script part in html
                        [x.extract() for x in soup.findAll('style')]
                        [x.extract() for x in soup.findAll('nav')]
                        [x.extract() for x in soup.findAll('footer')]
                        companyInfo = preprocessing(soup.text)
                        self.companyInfo += companyInfo

                        ## write data per url into first DB index(companyembedding_labeled_url) 
                        self.data['info'] = companyInfo
                        self.data['url'] = url
                        es.create(index='companyembedding_labeled_url', doc_type=self.targetCompany, id=uuid.uuid4(), body=data)  

                    return await response.release()
            except:
                self.failLinks.append(url)

    async def main(self, loop):
        driver = cross_selenium()
        # urls = BingLinkParser(driver, self.query)
        urls = GoogleLinkParser(driver, self.query)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=5 ) as client:
            tasks = [self.fetch_coroutine(client, url) for url in urls]
            await asyncio.gather(*tasks)


    def __call__(self):
        # self.loop = asyncio.new_event_loop()
        policy = asyncio.get_event_loop_policy()
        self.loop = policy.new_event_loop()
        asyncio.set_event_loop(self.loop)
        while True:
            try:
                self.companyAnnotation = input_companies.get(timeout=1)   ##Build self.query
            except:
                break
            
            ## build self attr
            self.companyInfo = ""  ##Build self.companyInfo
            self.findingCompany = self.companyAnnotation['name']
            self.failLinks = []  ##Build self.failLinks
            self.query = self.companyAnnotation['query']  ##Build self.query
            self.targetCompany = self.companyAnnotation['targetCompany']  ##Build self.targetCompany

            self.data = {
                    "name":self.findingCompany,
                    # "related":self.companyAnnotation['related'],  ##Build self.related,
                    "distinctName": self.companyAnnotation['distinctName'],  ##Build self.distinctName
                    "createTime":datetime.utcnow()
                    }

            ## start running loop
            self.loop.run_until_complete(self.main(self.loop))

            ## After loop: write log
            fail_log.put((self.targetCompany, self.findingCompany, self.failLinks))
            if self.companyInfo == "":
                empty_log.put((self.targetCompany, self.findingCompany))

            ## After loop: write data per company into DB
            self.data['info'] = self.companyInfo
            es.create(index='companyembedding_labeled', doc_type=self.targetCompany, id=uuid.uuid4(), body=self.data)  
            

            print(id(self), self.findingCompany + " success")










## Build Queue
input_companies = queue.Queue()
fail_log = queue.Queue()
empty_log = queue.Queue()

## Fill Queue with companyDict
files = os.listdir("labelData")
files = [file for file in files if "csv" in file]
# for file in files:
# for file in files[17:18]:
# for file in files[14:15]:
for file in files[3:4]:
# for file in files[19:20]:
    print(file)
    df_comps = pd.read_csv("labelData/" + file, index_col=None, header=None)

    companyTupleList = []
    def buildTupleList(row):
        companyTuple = (row[0], row[1])
        companyTupleList.append(companyTuple)

    df_comps.apply(buildTupleList, axis=1)
    print(len(df_comps), 'companies')

    for company, related in companyTupleList:
        companyDict = {}
        companyDict['name'] = company
        companyDict['query'] = "{} product".format(company)
        # companyDict['related'] = related
        companyDict['targetCompany'] = file.replace(".csv", "")

        exclude = set(string.punctuation)
        distinctName = ''.join(p for p in company if p not in exclude)
        distinctName = distinctName.replace(" ", "_").lower()  ##Build self.distinctName
        companyDict['distinctName'] = distinctName

        # data = {"query": {"match": {"distinctName": distinctName}}}
        data = {
            "query" : {
                "constant_score" : {
                    "filter" : {
                        "term" : {
                            "distinctName" : distinctName
                            }
                        }
                    }
                }
            }
        count = es.count(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data)['count']
        if count < 1:
            print(distinctName, 'does not exist')
            input_companies.put(companyDict)
            continue

        outputFilter = ['hits.hits._source.name', 'hits.hits._id', 'hits.hits._source.distinctName', 'hits.hits._source.createTime', 'hits.hits._score']
        res = es.search(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
        for comp in res['hits']['hits']:
            createTime = datetimeReader(comp['_source']['createTime'])
            nowTime = datetime.utcnow()
            ## basically, the situation will not exist: comp['_source']['distinctName'] != distinctName
            if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).days > 30:
            # if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).seconds > 50:
                print("delete ", distinctName)
                _id = comp['_id']
                es.delete(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], id=_id)
                es.delete(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], id=_id)
                input_companies.put(companyDict)




















starttime = time.time()
threads = []
for i in range(3):
    newthread = threading.Thread(target=googleCrawler())
    newthread.start()
    threads.append(newthread)

for thread in threads:
    thread.join()
endtime = time.time()
print(endtime - starttime)


## log writing
nowtime = datetime.now()
filetime = str(nowtime).split()[0].replace("-","") + str(nowtime).split()[1].split(":")[0] + str(nowtime).split()[1].split(":")[1]

if 'logs' not in os.listdir():
    os.mkdir('logs') 

faillogs = QueueTransfering(fail_log)
with open("logs/" + filetime + "FailLink.json", 'w', encoding='utf8') as fp:
    json.dump(faillogs, fp)

emptylogs = QueueTransfering(empty_log)
with open("logs/" + filetime + "Empty.json", 'w', encoding='utf8') as fp:
    json.dump(emptylogs, fp)



# data = {
#     "query" : {
#         "constant_score" : {
#             "filter" : {
#                 "term" : {
#                     "distinctName" : distinctName
#                     }
#                 }
#             }
#         }
#     }
count = es.count(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data)['count']
print('companyembedding_labeled count', count)
count = es.count(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data)['count']
print('companyembedding_labeled_url count', count)


outputFilter = ['hits.hits._source.name', 'hits.hits._id', 'hits.hits._source.distinctName', 'hits.hits._source.createTime', 'hits.hits._score']
res = es.search(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
res = es.search(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
