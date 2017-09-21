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

                "should":[
                            {"match":{"info":"measurement measure gauge analyze"}},
                            {"match":{"info":{"query":"test","boost":2}}},
                    ],


                "must_not":{"match":{"info":"analog"}}

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
    











## delete user log
# from elasticsearch import Elasticsearch

# def esLogin():
#     es = Elasticsearch(
#         ['1106bb4be3a4d722dd7d157d9d7d8c06.us-east-1.aws.found.io'],
#         http_auth=('elastic', 'QoMDn4EACa7vEOoEzuG9lghz'),
#         port=9243,
#         use_ssl=True
#     )
#     return es

# es = esLogin()



# es.delete_by_query(index="user_log", doc_type="search", body={"query":{"match_all":{}}})

