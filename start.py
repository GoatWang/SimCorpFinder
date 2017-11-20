from googleCrawler import Main
import os 
from pprint import pprint
import json
from outputReader import writeStats



dirs = [filename for filename in os.listdir("processed_data") if filename.endswith(".json")]
# for filename in dirs:
# for filename in dirs[35:36]:
# for filename in dirs[11:12]:
for num, filename in list(enumerate(dirs)):
# for num, filename in list(enumerate(dirs))[29:30]:
# for num, filename in list(enumerate(dirs))[1:2]:
    print(num, filename)
    file = open(os.path.join("processed_data",filename), 'r', encoding='utf8')
    
    data = json.loads(file.read())

    targetCorp = data['target']
    keyWords = data['keywords']['Keywords']
    keywords_emphasize = data['keywords']['KeyWords(Emphasize)']
    keywords_filtered = ""
    findingCorpsLi = data['compLi']
    
    main = Main()
    # main.startThread(findingCorpsLi, targetCorp, True, 7)
    main.startThread(findingCorpsLi, targetCorp, False, 7)

    writeStats(targetCorp, keyWords, keywords_emphasize, keywords_filtered, "output", findingCorpsLi)
