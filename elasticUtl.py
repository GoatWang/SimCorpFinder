# def datetimeReader():

import numpy as np
from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

def datetimeReader(timeStr):
# timeStr = '2017-09-06T11:06:28.468035'
    year = int(timeStr.split('-')[0])
    month = int(timeStr.split('-')[1])
    day = int(timeStr.split('-')[2].split('T')[0])
    hour = int(timeStr.split('-')[2].split('T')[1].split(':')[0])
    minute = int(timeStr.split('-')[2].split('T')[1].split(':')[1])
    second = int(timeStr.split('-')[2].split('T')[1].split(':')[2].split('.')[0])
    microsecond = int(timeStr.split('-')[2].split('T')[1].split(':')[2].split('.')[1])
    return datetime(year, month, day, hour, minute, second, microsecond) 


def getExactDistinctNameData(distinctName):
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
    return data

def checkExist(index, doc_type ,distinctName):
    data = getExactDistinctNameData(distinctName)
    count = es.count(index=index, doc_type=doc_type, body=data)['count']
    if count > 1:
        return True
    else:
        return False


# def checkDeleteExist(companyDict, input_companies, index, doc_type ,distinctName):
#     data = getExactDistinctNameData(distinctName)
#     outputFilter = ['hits.hits._source.name', 'hits.hits._id', 'hits.hits._source.distinctName', 'hits.hits._source.createTime', 'hits.hits._score']
#     res = es.search(index=index, doc_type=doc_type, body=data, filter_path=outputFilter)
#     for comp in res['hits']['hits']:
#         createTime = datetimeReader(comp['_source']['createTime'])
#         nowTime = datetime.utcnow()
#         ## basically, the situation will not exist: comp['_source']['distinctName'] != distinctName
#         if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).days > 30:
#         # if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).seconds > 50:
#             print("delete ", distinctName)
#             _id = comp['_id']
#             es.delete(index=index, doc_type=doc_type, id=_id)
#             es.delete(index=index + '_url', doc_type=doc_type, id=_id)
#             input_companies.put(companyDict)
#     return input_companies



def checkDateoutAndDelete(index, doc_type ,distinctName):
    data = getExactDistinctNameData(distinctName)
    outputFilter = ['hits.hits._source.name', 'hits.hits._id', 'hits.hits._source.distinctName', 'hits.hits._source.createTime', 'hits.hits._score']

    ## deal with first index
    res = es.search(index=index, doc_type=doc_type, body=data, filter_path=outputFilter)
    ## this is list type, however, there will be only one object(company) in it
    for comp in res['hits']['hits']:
        createTime = datetimeReader(comp['_source']['createTime'])
        nowTime = datetime.utcnow()
        ## basically, the situation will not exist: comp['_source']['distinctName'] != distinctName
        if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).days > 30:
        # if comp['_source']['distinctName'] == distinctName and (nowTime-createTime).seconds > 50:
            print("delete ", distinctName)
            _id = comp['_id']
            es.delete(index=index, doc_type=doc_type, id=_id)
            delete = True
        else:
            delete=False

    ## deal with second index(+ _url)
    res = es.search(index=index + '_url', doc_type=doc_type, body=data, filter_path=outputFilter)
    for comp in res['hits']['hits']:
        createTime = datetimeReader(comp['_source']['createTime'])
        nowTime = datetime.utcnow()
        ## if that distinctName's daat was delete in first index, all its urls' data should be deleted
        if comp['_source']['distinctName'] == distinctName and delete:
            print("delete ", distinctName, )
            _id = comp['_id']
            es.delete(index=index + '_url', doc_type=doc_type, id=_id)

    if delete:
        return True
    else:
        return False








