from numpy import dot
from numpy.linalg import norm

def cosine(keywordVector, docVector, tfidfnorm):
	""" related documents j and q are in the concept space by comparing the vectors :
		cosine  = ( V1 * V2 ) / ||V1|| x ||V2|| """
	# return float(dot(vector1,vector2) / (norm(vector1) * norm(vector2)))
	return float(dot(keywordVector, docVector) / (norm(keywordVector) * tfidfnorm))

from crawlerUtl import getDistinctName
import json
import math
import pandas as pd
from collections import Counter
import os

from docx import Document
import docx
from docx.shared import RGBColor, Pt
import re
from docx.enum.text import WD_LINE_SPACING
from datetime import datetime
from nltk.stem import WordNetLemmatizer
lemmer = WordNetLemmatizer()

import numpy as np

def processKeywordLi(keyWords):
    keyWordLi = []
    keyWordLi.extend([lemmer.lemmatize(term).lower() for term in keyWords])
    return keyWordLi


# def processInfo(info, multiTermKeywords):
def processInfo(info, keywords):
    infoTerms = []
    for keyword in keywords:
        infoTerms.extend(re.findall(keyword, info))
        info = info.replace(keyword, "")
    infoTerms.extend(info.split())
    return Counter(infoTerms)


def writeStats(targetCorp, keyWords, keywords_emphasize, keywords_filtered, outputDir, findingCorpsLi):
    keyWordLi = processKeywordLi(keyWords)
    keywords_emphasizeLi = processKeywordLi(keywords_emphasize)
    keywords_filteredLi = processKeywordLi(keywords_filtered)
    allKeywords = keyWordLi + keywords_emphasizeLi + keywords_filteredLi
    keywords_positive = keyWordLi + keywords_emphasizeLi  ## for averaging balance count of each word

    companyInfoDir = os.path.join("companyInfo", targetCorp, "companyInfo.json")
    with open(companyInfoDir, 'r', encoding='utf8') as f:
        companyInfoDict = json.loads(f.read())

    ## IDF
    docLen = len(companyInfoDict)
    idfDict = {}
    for word in allKeywords:
        f = 0
        for info in companyInfoDict:
            if word in processInfo(info['info'], allKeywords).keys():        
                f += 1
        idfDict[word] = math.log(docLen / (f + 1))

    keyTfidf = []
    for word in allKeywords:
        if word in keywords_emphasizeLi:
            keyTfidf.append(2 * idfDict[word])
        elif word in keywords_filteredLi:
            keyTfidf.append(-10 * idfDict[word])
        else:
            keyTfidf.append(1 * idfDict[word])

    ##　TF
    companyScoreDict = {}
    companyLenDict = {}
    companyKeywordsDict = {}
    for info in companyInfoDict:
        companyInfo = processInfo(info['info'], allKeywords)
        companyScore = 0
        companyInfoLen = sum([times for term, times in companyInfo.items()])
        tfidfLi = []
        tfCount = []
        tfPositiveCount = []
        for word in allKeywords:
            tfCount.append(companyInfo.get(word, 0))
            tf = companyInfo.get(word, 0)
            tfidf = tf * idfDict[word]
            tfidfLi.append(tfidf)
            if word in keywords_positive:
                tfPositiveCount.append(tf)

        # print(info['name'])
        # print(allKeywords)
        # print(tfCount)
        
        # print(keyTfidf)
        # print(tfidfLi)
        tfidfnorm = norm([count for term, count in companyInfo.items()])
        score = cosine(keyTfidf, tfidfLi, tfidfnorm) * 10 if tfidfLi != [0.0] * len(allKeywords) else 0  ## tfidf cosine score

        ## give them weight to balabce the distribution of count of each word
        if score > 0:
            tfPositiveCount = np.array([count for count in tfPositiveCount if count >= 1])
            weight = np.prod(tfPositiveCount) / ((sum(tfPositiveCount)/len(keywords_positive)) ** len(keywords_positive))
            weight = weight if weight <= 1 else 1
            weight = weight ** (1/len(keywords_positive))
            score = score * weight

        companyScoreDict[info['name']] = score
        companyLenDict[info['name']] = companyInfoLen
        companyKeywordsDict[info['name']] = dict([(allKeywords[i], tfCount[i])for i in range(len(tfCount))])

    ## sort output score
    scoreTupleList = sorted(companyScoreDict.items(), key=lambda x: x[1], reverse=True)
    scoreTupleList = [(comp, score) for (comp, score) in scoreTupleList if score != 0.00]

    urlInfoDir = os.path.join("companyInfo", targetCorp, "urlInfo.json")
    with open(urlInfoDir, 'r', encoding='utf8') as f:
        urlInfoDict = json.loads(f.read())

    df = pd.DataFrame(urlInfoDict)


    # ================ Start Writing ================
    outputdist = []
    for num, compTuple in enumerate(scoreTupleList):
        compName = compTuple[0]
        score = compTuple[1]
        outputDict = {}
        outputDict['name'] = compName
        outputDict['score'] = score
        outputDict['document_length'] = companyLenDict.get(compName)
        outputDict['Keywords'] = companyKeywordsDict.get(compName)
        
        outputDict['order_list'] = []
        # for each url
        pageCount = 0
        for row in df[df['name'] == compName].iterrows():
            row = row[1]
            info = row['info']

            if len(set(allKeywords) & set(processInfo(info, allKeywords).keys())) > 0:
                pageCount += 1
                urlDict = {}
                urlDict['number'] = pageCount
                urlDict['url'] = row['url']
                urlDict['keywords_existence'] = {}
                urlDict['keywords_emphasize_existence'] = {}
                urlDict['keywords_filtered_existence'] = {}

                for word in allKeywords:
                    count = processInfo(info, allKeywords).get(word, 0)
                    if count != 0:
                        if word in keyWordLi:
                            urlDict['keywords_existence'][word] = count
                        elif word in keywords_emphasizeLi:
                            urlDict['keywords_emphasize_existence'][word] = count
                        else:
                            urlDict['keywords_filtered_existence'][word] = count

                outputDict['order_list'].append(urlDict)
        outputdist.append(outputDict)

    nowtime = datetime.now()
    filetime = str(nowtime).split()[0].replace("-","") + str(nowtime).split()[1].split(":")[0] + str(nowtime).split()[1].split(":")[1]
    filename = os.path.join(outputDir, targetCorp + filetime + '.json')
    with open(filename, 'w', encoding='utf8') as fp:
        json.dump(outputdist, fp, ensure_ascii=False)