from googleCrawler import Main
import os 
from pprint import pprint
import json



dirs = [filename for filename in os.listdir("processed_key") if filename.endswith(".json")]
for filename in dirs[-4:-3]:
    print(filename)
    file = open(os.path.join("processed_key",filename), 'r', encoding='utf8')
    data = json.loads(file.read())
    keywords = data['keywords']['Keywords']
    keyWords_Emphasize = data['keywords']['KeyWords(Emphasize)']
    main = Main()
    main.startThread(data['compLi'], filename.replace(".json", ""), True, 4)