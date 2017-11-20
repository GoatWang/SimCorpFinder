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
from sklearn.preprocessing import normalize

def processKeywordLi(keyWords):
    keyWordLi = []
    for idx, keyword in enumerate(keyWords):
        if len(keyword.split()) > 1:
            words = []
            for word in keyword.split():
                word = lemmer.lemmatize(word.lower())
                words.append(word)
            keyword = " ".join(words)
        keyWords[idx] = keyword
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
    keyWordLi = list(set(processKeywordLi(keyWords)))
    keywords_emphasizeLi = list(set(processKeywordLi(keywords_emphasize)))
    keywords_filteredLi = list(set(processKeywordLi(keywords_filtered)))
    allKeywords = keyWordLi + keywords_emphasizeLi + keywords_filteredLi
    keywords_positive = keyWordLi + keywords_emphasizeLi  ## for averaging balance count of each word

    companyInfoDir = os.path.join("companyInfo", targetCorp, "companyInfo.json")
    with open(companyInfoDir, 'r', encoding='utf8') as f:
        companyInfoDict = json.loads(f.read())

    ## IDF
    docLen = len(companyInfoDict)
    # idfDict = {}
    # for word in allKeywords:
    #     f = 0
    #     for info in companyInfoDict:
    #         if word in processInfo(info['info'], allKeywords).keys():        
    #             f += 1
    #     idfDict[word] = math.log(docLen / (f + 1))

    idfDict_pre = {}
    for word in allKeywords:
        idfDict_pre[word] = 0

    for info in companyInfoDict:
        matched_words = list(set(allKeywords) & set(processInfo(info['info'], allKeywords).keys()))
        for word in matched_words:
            idfDict_pre[word] += 1

    # print("docLen = ", docLen)
    # print("idfDict_pre = ", idfDict_pre)
    # print("keyWordLi = ", keyWordLi)
    # print("keywords_emphasizeLi = ", keywords_emphasizeLi)
    # print("keywords_filteredLi = ", keywords_filteredLi)
    # print("allKeywords = ", allKeywords)
    # print("keywords_positive = ", keywords_positive)

    idfDict = {}
    for word, count in idfDict_pre.items():
        if count == 0:
            if word in keyWordLi:
                keyWordLi.pop(keyWordLi.index(word)) 
            if word in keywords_emphasizeLi:
                keywords_emphasizeLi.pop(keywords_emphasizeLi.index(word))
            if word in keywords_filteredLi:
                keywords_filteredLi.pop(keywords_filteredLi.index(word))
            if word in allKeywords:
                allKeywords.pop(allKeywords.index(word))
            if word in keywords_positive:
                keywords_positive.pop(keywords_positive.index(word))
        else:
            idfDict[word] = math.log(docLen / (count + 1))
            # print(word, count)

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

        tfidfnorm = norm([count for term, count in companyInfo.items()])
        score = cosine(keyTfidf, tfidfLi, tfidfnorm) * 10 if tfidfLi != [0.0] * len(allKeywords) else 0  ## tfidf cosine score

        ## give them weight to balabce the distribution of count of each word
        if score > 0:
            bigger_than_one = np.sum(np.array([tfPositiveCount]) ==1)
            bigger_than_two = np.sum(np.array([tfPositiveCount]) > 2)
            weight = (bigger_than_one * 1 + bigger_than_two * 2) / (len(tfPositiveCount)*2)
            score = score * (weight)

        companyScoreDict[info['name']] = score
        companyLenDict[info['name']] = companyInfoLen
        companyKeywordsDict[info['name']] = dict([(allKeywords[i], tfCount[i])for i in range(len(tfCount))])

    ## sort output score

    scoreTupleList = sorted(companyScoreDict.items(), key=lambda x: x[1], reverse=True)
    df_score = pd.DataFrame(scoreTupleList)
    df_score.loc[df_score[1] > 0, 1] = normalize(df_score.loc[df_score[1] > 0, 1].values.reshape(1,-1))[0]   ##normalize positive value
    scoreTupleList = [(comp, score) for (comp, score) in df_score.values if score != 0.00]

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
        outputDict['url_count'] = len(df[df['name'] == compName])
        
        outputDict['document_length'] = companyLenDict.get(compName)
        outputDict['Keywords'] = companyKeywordsDict.get(compName)
        outputDict['order_list'] = []
        # for each url
        pageCount = 0
        for row in df[df['name'] == compName].iterrows():
            row = row[1]
            info = row['info']
            keyword_counter = processInfo(info, allKeywords)

            if len(set(allKeywords) & set(keyword_counter.keys())) > 0:
                pageCount += 1
                urlDict = {}
                urlDict['number'] = pageCount
                urlDict['url'] = row['url']
                urlDict['keywords_existence'] = {}
                urlDict['keywords_emphasize_existence'] = {}
                urlDict['keywords_filtered_existence'] = {}

                for word in allKeywords:
                    count = keyword_counter.get(word, 0)
                    if count != 0:
                        if word in keyWordLi:
                            urlDict['keywords_existence'][word] = count
                        elif word in keywords_emphasizeLi:
                            urlDict['keywords_emphasize_existence'][word] = count
                        else:
                            urlDict['keywords_filtered_existence'][word] = count

                outputDict['order_list'].append(urlDict)
        outputdist.append(outputDict)

    # ## write json file
    nowtime = datetime.now()
    filetime = str(nowtime).split()[0].replace("-","") + str(nowtime).split()[1].split(":")[0] + str(nowtime).split()[1].split(":")[1]
    filename = os.path.join(outputDir, targetCorp + filetime + '.json')
    with open(filename, 'w', encoding='utf8') as fp:
        json.dump(outputdist, fp, ensure_ascii=False)

    ## generating csv file for comparason  
    for comparable in outputdist:
        for key in comparable['Keywords'].keys():
            comparable[key]= comparable['Keywords'][key]


    df_output = pd.DataFrame(outputdist)
    df_output = df_output.drop('order_list', axis=1)
    df_output = df_output.drop('Keywords', axis=1)
    def deletezeroscolumn(df):
        for column in df.columns:
            if (df[column] == 0).all():
                df.drop(column, axis=1, inplace=True)
        return df
    df_output = deletezeroscolumn(df_output)

    showing_columns = ['name', 'score', 'document_length', 'url_count']
    keywords = [keyword for keyword in df_output.columns if keyword not in showing_columns]
    showing_columns.extend(keywords)
    df_output = df_output[showing_columns]

    # ## write csv file
    filename = os.path.join(outputDir, targetCorp + filetime + '.csv')
    df_output.to_csv(filename, index=False)