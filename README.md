# Product Information:
Please go to our [website](https://goatwang.github.io/SimCorpFinder/index_eng.html)

# berfore build this app
you should add a python file contain these code called selfpwd.py
```
def getMongoUrl():
    url = "<your_mongo_url>"
    return url
```

# build shell script
1. Prerequests
```
git checkout fileretrieval
pip install -r requirements.txt
```

2. Build
* if you want to build entire project into a directory 
```
python setup.py build
```

* if you want to build entire project as wondows installer(.msi)
```
python setup.py bdist_msi
```
