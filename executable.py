from googleCrawler import Main

from elasticUtl import esLogin
# from elasticsearch import Elasticsearch
# es = Elasticsearch()
es = esLogin()

# if es.indices.exists('companyembedding'):
#     es.indices.delete(index='companyembedding')
# if es.indices.exists('companyembedding_url'):
#     es.indices.delete(index='companyembedding_url')
# if es.indices.exists('companyembedding_labeled'):
#     es.indices.delete(index='companyembedding_labeled')
# if es.indices.exists('companyembedding_labeled_url'):
#     es.indices.delete(index='companyembedding_labeled_url')

if not es.indices.exists('companyembedding'):
    es.indices.create('companyembedding')
if not es.indices.exists('companyembedding_url'):
    es.indices.create('companyembedding_url')
if not es.indices.exists('companyembedding_labeled'):
    es.indices.create('companyembedding_labeled')
if not es.indices.exists('companyembedding_labeled_url'):
    es.indices.create('companyembedding_labeled_url')


Main().startThread()

