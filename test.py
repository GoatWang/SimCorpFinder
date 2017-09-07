from os import listdir
import pandas as pd

from elasticsearch import Elasticsearch
es = Elasticsearch()

import string
from datetime import datetime

from elasticUtl import datetimeReader

files = listdir("labelData")
files = [file for file in files if "csv" in file]
# for file in files[5:6]:
for file in files[3:4]:
# for file in files[19:20]:
# for num, file in enumerate(files):
    # print(num, file)
    print(file)
    df_comps = pd.read_csv("labelData/" + file, index_col=None, header=None)

    companyTupleList = []
    def buildTupleList(row):
        companyTuple = (row[0], row[1])
        companyTupleList.append(companyTuple)

    df_comps.apply(buildTupleList, axis=1)
    print(len(df_comps))
    print(es.count(index='companyembedding', doc_type=file.replace(".csv", "")))
    for company, related in companyTupleList:
        exclude = set(string.punctuation)
        distinctName = ''.join(p for p in company if p not in exclude)
        distinctName = distinctName.replace(" ", "_").lower()  ##Build self.distinctName
        companyDict = {}
        companyDict['targetCompany'] = file.replace(".csv", "")



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
        # count = es.count(index='companyembedding', doc_type=companyDict['targetCompany'], body=data)['count']
        count = es.count(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data)['count']
        print('companyembedding_labeled count', count)
        count = es.count(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data)['count']
        print('companyembedding_labeled_url count', count)

        outputFilter = ['hits.hits._source.name', 'hits.hits._id', 'hits.hits._source.distinctName', 'hits.hits._source.createTime', 'hits.hits._score']
        # res = es.search(index='companyembedding', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
        res = es.search(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
        res = es.search(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
        if count < 1:
            print('count less than one', distinctName)
            continue


        for comp in res['hits']['hits']:
            createTime = datetimeReader(comp['_source']['createTime'])
            nowTime = datetime.utcnow()
            print((nowTime-createTime).seconds)
            if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).days > 30:
            # if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).seconds > 5100:
                print(distinctName)
                # print("delete ", distinctName)
                # _id = comp['_id']
                # es.delete(index='companyembedding', doc_type=companyDict['targetCompany'], id=_id)
        print("--------------")
        print("--------------")





        # # data = {"query": {"match": {"name": 'Yleiselektroniikka Oyj'}}}
        # data = {"query": {"match": {"distinctName": distinctName}}}
        # count = es.count(index='companyembedding', doc_type='亞提爾_進銷貨_電子設備', body=data)['count']
        # # print(company, count)
        # print(distinctName, count)

        # outputFilter = ['hits.hits._source.name', 'hits.hits._source.distinctName', 'hits.hits._score']
        # res = es.search(index='companyembedding', doc_type='亞提爾_進銷貨_電子設備', body=data, filter_path=outputFilter)
        # for comp in res['hits']['hits']:
        #     print(comp['_source']['distinctName'], comp['_score'])
