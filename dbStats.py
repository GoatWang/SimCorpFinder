from elasticsearch import Elasticsearch
es = Elasticsearch()
import os
import pandas as pd
import string

from pprint import pprint
from collections import Counter

import subprocess

if 'output.json' in os.listdir():
    os.remove("output.json")

## Fill Queue with companyDict
files = os.listdir("labelData")
files = [file for file in files if "csv" in file]
files = [file for file in files if "csv" in file and "亞提爾_進銷貨_電子設備" in file]

for file in files:
# for file in files[17:18]:
# for file in files[14:15]:
# for file in files[3:4]:
# for file in files[19:20]:
    targetComp = file
    df_comps = pd.read_csv("labelData/" + targetComp, index_col=None, header=None)

    companyTupleList = []
    def buildTupleList(row):
        companyTuple = (row[0], row[1])
        companyTupleList.append(companyTuple)

    df_comps.apply(buildTupleList, axis=1)

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



#         count = es.count(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data)['count']
#         print('companyembedding_labeled count', distinctName, count)
#         count = es.count(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data)['count']
#         print('companyembedding_labeled_url count', distinctName, count)




# res = es.search(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], size=200)

# allCompanies = [comp['_source']['distinctName'] for comp in res['hits']['hits']]
# urlCounter = Counter(allCompanies)
# pprint(urlCounter)
# distinctCompanies = set(allCompanies)
# print('there are', len(distinctCompanies), 'urls in companyembedding_labeled_url index' )



queryString = """cable connector metrocast mmds wireless connectors adapter backplane socapex pinout socket motherboard uext trrs adapters catv cables cablevision directv cabling suddenlink comcast"""
data = {
    "query":{
        "match":{
            "info":queryString
        }
    },
    "highlight":{
        "fields":{
            "info":{}
        }
    }
}

outputFilter = ['hits.hits._source.distinctName', 'hits.hits._score', 'hits.hits._source.related' , 'hits.hits.highlight.info']
res = es.search(index='companyembedding_labeled', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter)
distinctNames = [(comp['_source']['distinctName'], comp['_score'], comp['_source']['related'])  for comp in res['hits']['hits']]

file = open("output.json", 'w', encoding='utf8')
file.write("Target compaies: " + targetComp + "\n")
file.write("Total input: " + str(len(df_comps)) + " companies" + "\n")
file.write("Related: " + str((len(distinctNames))) + " companies" + "\n")
file.write("\n")
file.write("\n")

for num, compTuple in enumerate(distinctNames):
    distinctName = compTuple[0]
    file.write(str(num+1) + ". " + distinctName + "\n")
    file.write("score: " + str(compTuple[1]) + "\n")
    file.write("related: " + str(compTuple[2]) + "\n")
    data = {
            "query" : {
                "bool":{
                    "should":[
                            {"match":{"info":queryString}}, 
                            {"match":{"distinctName":distinctName}}
                    ]}},
            "highlight":{
                "fields":{"info":{}}
            }}
    outputFilter = ['hits.hits._source.distinctName', 'hits.hits._source.url', 'hits.hits.highlight.info']
    res = es.search(index='companyembedding_labeled_url', doc_type=companyDict['targetCompany'], body=data, filter_path=outputFilter, size=100)
    for comp in res['hits']['hits']:
        if comp['_source']['distinctName'] == distinctName and comp.get('highlight') != None:
            file.write(comp['_source']['url'] + "\n")
            for info in comp.get('highlight')['info']:
                file.write(info + "\n")
            file.write("------------------------------------------" + "\n")
    file.write("\n")
    file.write("\n")
