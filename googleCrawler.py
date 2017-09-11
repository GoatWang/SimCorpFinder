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
from elasticUtl import datetimeReader, checkExist, checkDateoutAndDelete
from elasticsearch import Elasticsearch
es = Elasticsearch()

#user write
from setting_selenium import cross_selenium
from crawlerUtl import getDistinctName, QueueTransfering, preprocessing
from crawlerUtl import BingLinkParser, GoogleLinkParser

#log writing and other
import json
import os
import time



class googleCrawler:
    def __init__(self, input_companies, fail_log, empty_log):
        self.input_companies = input_companies
        self.fail_log = fail_log
        self.empty_log = empty_log
        
    async def fetch_coroutine(self, client, url):
        with async_timeout.timeout(10):
            status = None
            try: 
                async with client.get(url) as response:
                    status = response.status
                    assert status == 200
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
                        if companyInfo != "" and companyInfo != None:
                            self.data['info'] = companyInfo
                            self.data['url'] = url
                            es.create(index='companyembedding_labeled_url', doc_type=self.targetCompany, id=uuid.uuid4(), body=self.data)  

                    return await response.release()
            except:
                self.failLinks.append(str(status) + "------" + url)

    async def main(self, loop):
        driver = cross_selenium()
        # urls = BingLinkParser(driver, self.query)
        urls = GoogleLinkParser(driver, self.query)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=10 ) as client:
            tasks = [self.fetch_coroutine(client, url) for url in urls]
            await asyncio.gather(*tasks)


    def __call__(self):
        # self.loop = asyncio.new_event_loop()
        policy = asyncio.get_event_loop_policy()
        self.loop = policy.new_event_loop()
        asyncio.set_event_loop(self.loop)
        while True:
            try:
                self.companyAnnotation = self.input_companies.get(timeout=1)   ##Build self.query
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
                    "distinctName": self.companyAnnotation['distinctName'],  ##Build self.distinctName
                    "createTime":datetime.utcnow()
                    }
            if self.companyAnnotation['related'] != None:
                    self.data["related"] = self.companyAnnotation['related']  ##Build self.related,
            

            ## start running loop
            self.loop.run_until_complete(self.main(self.loop))

            ## After loop: write log
            self.fail_log.put((self.targetCompany, self.findingCompany, self.failLinks))
            if self.companyInfo == "":
                self.empty_log.put((self.targetCompany, self.findingCompany))

            ## After loop: write data per company into DB
            self.data['info'] = self.companyInfo
            self.data.pop('url', None)  ##if url not found, None is returned
            es.create(index='companyembedding_labeled', doc_type=self.targetCompany, id=uuid.uuid4(), body=self.data)  
            

            print(str(id(self))[-5:], self.findingCompany + " success")









class Main():
    def buildQueue(self, compLi=None, targetComp=None, keywords=None):
        """compLi is list of finding companies"""
        self.input_companies = queue.Queue()
        self.fail_log = queue.Queue()
        self.empty_log = queue.Queue()

        if compLi != None:
            for company in compLi:
                companyDict = {}
                companyDict['name'] = company
                companyDict['query'] = "{} product".format(company)
                companyDict['related'] = None
                companyDict['targetCompany'] = targetComp
                companyDict['distinctName'] = getDistinctName(company)

                ## if data doesn't exist, directly put it in queue
                if not checkExist('companyembedding', companyDict['targetCompany'], companyDict['distinctName']):
                    print(companyDict['distinctName'], 'does not exist')
                    self.input_companies.put(companyDict)
                    continue

                ## if the data has existed over 30 days, delete it and put it in queue
                if checkDateoutAndDelete('companyembedding', companyDict['targetCompany'], companyDict['distinctName']):
                    self.input_companies.put(companyDict)

        else:
            ## Fill Queue with companyDict
            files = os.listdir("labelData")
            files = [file for file in files if "csv" in file and "亞提爾_進銷貨_電子設備" in file]
            # for file in files:
            # for file in files[17:18]:
            # for file in files[14:15]:
            # for file in files[3:4]:
            # for file in files[19:20]:
            for file in files[0:1]:
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
                    companyDict['related'] = related
                    companyDict['targetCompany'] = file.replace(".csv", "")
                    companyDict['distinctName'] = getDistinctName(company)
                
                    if not checkExist('companyembedding_labeled', companyDict['targetCompany'], companyDict['distinctName']):
                        print(companyDict['distinctName'], 'does not exist')
                        self.input_companies.put(companyDict)
                        continue

                    if checkDateoutAndDelete('companyembedding_labeled', companyDict['targetCompany'], companyDict['distinctName']):
                        self.input_companies.put(companyDict)

    def startThread(self, compLi=None, targetComp=None, keywords=None):
        self.buildQueue(compLi, targetComp, keywords)

        starttime = time.time()
        threads = []
        for i in range(4):
            entity = googleCrawler(self.input_companies, self.fail_log, self.empty_log)
            newthread = threading.Thread(target=entity)
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

        faillogs = QueueTransfering(self.fail_log)
        with open("logs/" + filetime + "FailLink.json", 'w', encoding='utf8') as fp:
            json.dump(faillogs, fp)

        emptylogs = QueueTransfering(self.empty_log)
        with open("logs/" + filetime + "Empty.json", 'w', encoding='utf8') as fp:
            json.dump(emptylogs, fp)


