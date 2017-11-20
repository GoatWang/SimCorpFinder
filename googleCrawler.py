#multiprocessing and async
import aiohttp
import asyncio
import async_timeout
import queue
import threading
import random

# data processing
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

#write into DB
from datetime import datetime

#delete dir
import shutil

#user write
from setting_selenium import cross_selenium
from crawlerUtl import getDistinctName, QueueTransfering, preprocessing
from collections import Counter
from crawlerUtl import BingLinkParser, GoogleLinkParser


#log writing and other
import json
import os
import time



class googleCrawler:
    def __init__(self, input_companies, fail_log, companyInfo, urlInfo):
        self.input_companies = input_companies
        self.oriCompLength = input_companies.qsize()
        self.fail_log = fail_log
        self.companyInfo = companyInfo
        self.urlInfo = urlInfo

    async def fetch_coroutine(self, client, url):
        with async_timeout.timeout(10):
            status = None
            contentType = None
            html = None

            def processhtml(html):
                soup = BeautifulSoup(html ,'lxml')
                [x.extract() for x in soup.findAll('script')]  ##take off script part in html
                [x.extract() for x in soup.findAll('style')]
                [x.extract() for x in soup.findAll('nav')]
                [x.extract() for x in soup.findAll('footer')]
                info = preprocessing(soup.text)
                return info

            try: 
                async with client.get(url) as response:
                    status = response.status
                    assert status == 200
                    contentType = str(response.content_type)
                    if 'html' in str(contentType).lower():
                        html = await response.text()
                        info = processhtml(html)
                        self.accCompInfo += info
                        ## write data per url into first DB index(companyembedding_labeled_url) 
                        if info != "" and info != None:
                            urldata = self.data.copy()
                            urldata['info'] = info
                            urldata['url'] = url
                            self.urlInfo.put(urldata)
                            
                    return await response.release()
            except:
                # import traceback
                # traceback.print_exc()
                ## generallt is CancelError
                try:
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
                    res = requests.get(url, verify=False, headers=headers, timeout=10)
                    status = res.status_code
                    assert status == 200

                    contentType = res.headers.get("Content-Type", res.headers)
                    if 'html' in str(contentType).lower():
                        html = res.text
                        info = processhtml(html)
                        self.accCompInfo += info
                        ## write data per url into first DB index(companyembedding_labeled_url) 
                        if info != "" and info != None:
                            urldata = self.data.copy()
                            urldata['info'] = info
                            urldata['url'] = url
                            self.urlInfo.put(urldata)
                except AssertionError:
                    self.failLinks.append("StatusCodeError" + "------" + url)
                except urllib3.exceptions.ConnectTimeoutError:
                    self.failLinks.append("ConnectTimeoutError" + "------" + url)
                except urllib3.exceptions.ReadTimeoutError:
                    self.failLinks.append("ReadTimeoutError" + "------" + url)
                except:
                    # import traceback
                    # traceback.print_exc()
                    self.failLinks.append("OtherError" + "------" + url)
                    

    async def main(self, loop):
        driver = cross_selenium()
        # urls = BingLinkParser(driver, self.query)
        urls = GoogleLinkParser(driver, self.query)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=10, connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
            # tasks = [self.fetch_coroutine(client, url) for url in urls]
            tasks = []
            for url in urls:
                tasks.append(self.fetch_coroutine(client, url))
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
            self.accCompInfo = ""  ##Build self.companyInfo
            self.findingCompany = self.companyAnnotation['name']
            self.failLinks = []  ##Build self.failLinks
            self.query = self.companyAnnotation['query']  ##Build self.query
            self.targetCompany = self.companyAnnotation['targetCompany']  ##Build self.targetCompany

            self.data = {
                    "name":self.findingCompany,
                    "distinctName": self.companyAnnotation['distinctName'],  ##Build self.distinctName
                    "createTime":str(datetime.utcnow())
                    }
            
            ## start running loop
            self.loop.run_until_complete(self.main(self.loop))
            # self.driver.close()

            ## After loop: write log
            self.fail_log.put((self.targetCompany, self.findingCompany, self.failLinks))

            ## After loop: write data per company into DB
            self.data['info'] = self.accCompInfo
            self.data.pop('url', None)  ##if url not found, None is returned
            
            self.companyInfo.put(self.data)
            
            totalLength = self.oriCompLength
            processedNum = totalLength - self.input_companies.qsize()
            progess = int(processedNum/totalLength * 100 - 10)
            print(str(progess)+"%", str(id(self))[-5:], self.findingCompany + " success")




class Main():
    def buildQueue(self, findingCorps, targetComp, forceDelete=False):
        """findingCorps is list of finding companies"""
        self.input_companies = queue.Queue()
        self.fail_log = queue.Queue()
        self.companyInfo = queue.Queue()
        self.urlInfo = queue.Queue()

        headDir = 'companyInfo'
        targetDir = os.path.join(headDir, targetComp)
        
        if (targetComp in os.listdir(headDir)) and forceDelete:
            shutil.rmtree(targetDir)
            import time 
            time.sleep(1)

        if not targetComp in os.listdir(headDir):
            os.mkdir(targetDir)
            for company in findingCorps:
                companyDict = {}
                companyDict['name'] = company
                companyDict['query'] = "{} product".format(company)
                companyDict['targetCompany'] = targetComp
                companyDict['distinctName'] = getDistinctName(company)
                self.input_companies.put(companyDict)


    def startThread(self, findingCorps, targetComp, forceDelete, threadNum):
        self.buildQueue(findingCorps, targetComp, forceDelete)

        starttime = time.time()
        threads = []
        for i in range(threadNum):
            entity = googleCrawler(self.input_companies, self.fail_log, self.companyInfo, self.urlInfo)
            newthread = threading.Thread(target=entity)
            newthread.start()
            threads.append(newthread)

        for thread in threads:
            thread.join()
        endtime = time.time()
        
        print("90%", str(id(self))[-5:], "Crawling Time: " + "{0:.2f}".format(endtime - starttime) + " seconds")


        ## log writing
        nowtime = datetime.now()
        filetime = str(nowtime).split()[0].replace("-","") + str(nowtime).split()[1].split(":")[0] + str(nowtime).split()[1].split(":")[1]

        faillogs = QueueTransfering(self.fail_log)
        if faillogs != []:
            fileLoc = os.path.join('logs', targetComp + filetime + '.json')
            with open(fileLoc, 'w', encoding='utf8') as fp:
                json.dump(faillogs, fp)


        if self.companyInfo.qsize() != 0:
            companyInfos = QueueTransfering(self.companyInfo)
            fileLoc = os.path.join('companyInfo', targetComp, "companyInfo.json")
            with open(fileLoc, 'w', encoding='utf8') as fp:
                json.dump(companyInfos, fp)


        if self.urlInfo.qsize() != 0:
            urlInfos = QueueTransfering(self.urlInfo)
            fileLoc = os.path.join('companyInfo', targetComp, "urlInfo.json")
            with open(fileLoc, 'w', encoding='utf8') as fp:
                json.dump(urlInfos, fp)


