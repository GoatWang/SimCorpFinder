# from elasticsearch import Elasticsearch
# es = Elasticsearch()
from elasticUtl import esLogin
es = esLogin()

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

from crawlerUtl import getDistinctName
a = getDistinctName("Agilysys, Inc.")
data = getExactDistinctNameData(a)

# count = es.count(index="companyembedding", doc_type="太克_測試_電子儀器", body=data)['count']
count = es.count(index="companyembedding", doc_type="太克_測試_電子儀器")['count']
# print(count)

from elasticUtl import checkExist

print(str(checkExist("companyembedding", "太克_測試_電子儀器", a)))




# res = es.search(index="companyembedding", body=data)

# queryString = "test measurement measure gauge analyze analog"
outputFilter = ['hits.hits._source.distinctName', 'hits.hits._score', 'hits.hits._source.related' , 'hits.hits.highlight.info']

data = {
        "size":10,
        "query":{
            "bool":{
                "should":{
                    "match":{
                        "info":"test measurement measure gauge analyze"
                    }
                },
                "must_not":{
                    "match":{
                        "info":"analog"
                    }
                }

            }
        },
        "highlight":{
            "fields":{
                "info":{}
            }
        }
    }


res = es.search('companyembedding', "太克_測試_電子儀器", body=data, filter_path=outputFilter)
# res = es.search('companyembedding', "太克_測試_電子儀器", filter_path=outputFilter)
from pprint import pprint
pprint(res)
print(len(res['hits']['hits']))
    
    ## must, should: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
    ## must not: https://www.elastic.co/guide/en/elasticsearch/guide/1.x/_combining_queries_with_filters.html
    
