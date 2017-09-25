# Product Information: 

# berfore build this app

you should add a python file contain these code
```
from elasticsearch import Elasticsearch

def esPwdLogin():
    es = Elasticsearch(
        ['<es_url>'],
        http_auth=('<user_name>', '<password>'),
        port=<your_port>,
        use_ssl=<true_or_false>
    )
    return es

def getMongoUrl():
    url = "<your_mongo_url>"
    return url
```

# build: sheel script
* if you want to build entire project into a directory 
```
python setup.py build
```

* if you want to build entire project into a directory 
```
python setup.py bdist_msi
```
