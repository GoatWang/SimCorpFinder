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


from docx import Document
import docx
from docx.shared import RGBColor, Pt
import re
from docx.enum.text import WD_LINE_SPACING
from datetime import datetime

def writeStats(targetCorp, keyWords, keywords_emphasize, keywords_filtered, outputDir, findingCorpsLi):
    companyInfoDir = "C:\\SimCorpFinderData\\companyInfo\\" + targetCorp + "\\companyInfo.json"
    keyWordLi = keyWords.split() 
    keywords_emphasizeLi = keywords_emphasize.split()
    keywords_filteredLi = keywords_filtered.split()
    allKeywords = keyWordLi + keywords_emphasizeLi + keywords_filteredLi

    with open(companyInfoDir, 'r', encoding='utf8') as f:
        companyInfoDict = json.loads(f.read())

    ## IDF
    docLen = len(companyInfoDict)
    idfDict = {}
    for word in allKeywords:
        f = 0
        for info in companyInfoDict:
            if word in info['info'].keys():        
                f += 1
        idfDict[word] = math.log(docLen / (f + 1))

    keyTfidf = []
    for word in allKeywords:
        if word in keywords_emphasizeLi:
            keyTfidf.append(2/4 * idfDict[word])
        elif word in keywords_filteredLi:
            keyTfidf.append(-2/4 * idfDict[word])
        else:
            keyTfidf.append(1/4 * idfDict[word])

    ##　TF
    companyScoreDict = {}
    
    ##
    companyInfoLi = []
    for info in companyInfoDict:
        ##
        companyInfoDict = []
        companyInfo = info['info']
        companyScore = 0
        companyInfoLen = sum([times for term, times in companyInfo.items()])
        tfidfLi = []

        tfCount = []
        for word in allKeywords:
            tfCount.append(companyInfo.get(word, 0))
            tf = companyInfo.get(word, 0)
            tfidf = tf * idfDict[word]
            tfidfLi.append(tfidf)
        
        tfidfnorm = norm([count for term, count in info['info'].items()])
        score = cosine(keyTfidf, tfidfLi, tfidfnorm) * 10 if tfidfLi != [0.0] * len(allKeywords) else 0


        companyScoreDict[info['name']] = score

        ##
        companyInfoDict.append(info['name'])
        companyInfoDict.append(allKeywords)
        companyInfoDict.append(tfCount)
        companyInfoDict.append(str(keyTfidf))
        companyInfoDict.append(companyInfoLen)
        companyInfoDict.append(score)
        companyInfoLi.append(companyInfoDict) 
    from pprint import pprint
    pprint(sorted(companyInfoLi, key=lambda x: x[5], reverse=True))

    scoreTupleList = sorted(companyScoreDict.items(), key=lambda x: x[1], reverse=True)
    scoreTupleList = [(comp, score) for (comp, score) in scoreTupleList if score != 0.00]





    document = Document()
    document.add_heading(targetCorp, 0)
    par = document.add_paragraph()
    par.add_run("Made By SimCorpFinder (")
    addHyperlink(par, "https://goatwang.github.io/SimCorpFinder/index.html", "20")
    par.add_run("), contact us(linkedin: ")
    addHyperlink(par, "https://www.linkedin.com/in/wanghsuanchung/", "20")
    par.add_run(", Email: jeremy4555@yahoo.com.tw)")
    document.add_paragraph()

    for run in par.runs:    
        run.font.size = Pt(10)


    document.add_heading("Simple Statistics", level=1)
    document.add_paragraph("Total Input: " + str(len(findingCorpsLi)) + " companies")
    document.add_paragraph("Related: " + str((len(scoreTupleList))) + " companies")
    document.add_paragraph("Keywords: " + ", ".join(keyWords.split()))
    document.add_paragraph("Keywords(Emphasize): " + ", ".join(keywords_emphasize.split()))
    document.add_paragraph("Keywords(Filtered): " + ", ".join(keywords_filtered.split()))
    document.add_paragraph()


    heading = document.add_heading("Ordered List", level=1)
    for num, compTuple in enumerate(scoreTupleList):
        document.add_paragraph(str(num+1) + ". " + compTuple[0] + " (score: " + "{:.4f}".format(compTuple[1]) + ")")
    document.add_paragraph()







    heading = document.add_heading("Detail", level=1)
    urlInfoDir = "C:\\SimCorpFinderData\\companyInfo\\" + targetCorp + "\\urlInfo.json"
    with open(urlInfoDir, 'r', encoding='utf8') as f:
        urlInfoDict = json.loads(f.read())

    df = pd.DataFrame(urlInfoDict)
    # for each company
    for num, compTuple in enumerate(scoreTupleList):
        compName = compTuple[0]
        heading = document.add_heading(str(num+1) + ". " + compName + " (score: " + "{:.4f}".format(compTuple[1]) + ")", level=2)
        heading.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        count = 0

        # for each url
        pageCount = 0
        for row in df[df['name'] == compName].iterrows():
            row = row[1]
            info = row['info']
            if len(set(allKeywords) & set(info.split())) > 0:
                pageCount += 1
                # page source 1: "http://XXXXXXXXXXXXXXX.com"
                par = document.add_paragraph()
                run = par.add_run("page source "+ str(pageCount) +": ")
                run.bold = True
                hyperlink = addHyperlink(par, row['url'])

                par = document.add_paragraph()
                run = par.add_run("Keyword Existence: ")
                run.bold = True
                for word in allKeywords:
                    count = Counter(info.split()).get(word, 0)
                    if count != 0:
                        if word in keyWords:
                            par = document.add_paragraph()
                            run = par.add_run("\t" + word + ": " + str(count))
                            font = run.font
                            font.color.rgb = RGBColor(255, 0, 0)
                        elif word in keywords_emphasizeLi:
                            par = document.add_paragraph()
                            run = par.add_run("\t" + word + ": " + str(count))
                            font = run.font
                            font.color.rgb = RGBColor(255, 0, 0)
                        else:
                            par = document.add_paragraph()
                            run = par.add_run("\t" + word + ": " + str(count))
                            font = run.font
                            font.color.rgb = RGBColor(0, 255, 0)

        par = document.add_paragraph()




    # heading = document.add_heading("Detail", level=1)
    # urlInfoDir = "C:\\SimCorpFinderData\\companyInfo\\" + targetCorp + "\\urlInfo.json"
    # with open(urlInfoDir, 'r', encoding='utf8') as f:
    #     urlInfoDict = json.loads(f.read())

    # df = pd.DataFrame(urlInfoDict)
    # # for each company
    # for num, compTuple in enumerate(scoreTupleList):
    #     compName = compTuple[0]
    #     heading = document.add_heading(str(num+1) + ". " + compName + " (score: " + "{:.4f}".format(compTuple[1]) + ")", level=2)
    #     heading.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    #     count = 0

    #     # for each url
    #     for row in df[df['name'] == compName].iterrows():
    #         row = row[1]
    #         info = row['info']
    #         if len(set(allKeywords) & set(info.split())) > 0:
    #             count += 1
    #             # page source 1: "http://XXXXXXXXXXXXXXX.com"
    #             par = document.add_paragraph()
    #             run = par.add_run("page source "+ str(count) +": ")
    #             run.bold = True
    #             hyperlink = addHyperlink(par, row['url'])
    #             # for each para
    #             # para = document.add_paragraph()
    #             # run = para.add_run('para' + '. ')
    #             # run.bold = True
    #             indices = []
    #             infoTermLi = info.split()
    #             for i in range(len(infoTermLi)):
    #                 if infoTermLi[i] in allKeywords:
    #                     indices.append(i)
                
    #             sliceLi = []
    #             for idx in indices:
    #                 subLi = []
    #                 currentidx = indices.index(idx)
    #                 while True:
    #                     subLi.append(indices[currentidx])
    #                     lowerBound = max(0, subLi[0]-10)
    #                     upperBound = min(subLi[-1]+10, indices[-1])

    #                     if indices[currentidx] == indices[-1]:
    #                         sliceLi.append(range(lowerBound, upperBound))
    #                         break
                        
    #                     elif  indices[currentidx+1] - indices[currentidx] > 10:
    #                         sliceLi.append(range(lowerBound, upperBound))
    #                         break
    #                     indices.pop(currentidx)

    #             for num, sli in enumerate(sliceLi):
    #                 para = document.add_paragraph()
    #                 run = para.add_run('para' + str(num+1) + '. ')
    #                 run.bold = True
    #                 for idx in sli:
    #                     term = infoTermLi[idx]
    #                     if term in keyWordLi + keywords_emphasizeLi:
    #                         run = para.add_run(term + " ")
    #                         run.bold = True
    #                         font = run.font
    #                         font.color.rgb = RGBColor(255, 0, 0)
    #                     elif term in keywords_filteredLi:
    #                         run = para.add_run(term + " ")
    #                         run.bold = True
    #                         font = run.font
    #                         font.color.rgb = RGBColor(0, 255, 0)
    #                     else:
    #                         para.add_run(term + " ")

    #                 document.add_paragraph("--------------------------")
    #             document.add_paragraph()
    #     document.add_paragraph()

    for para in document.paragraphs:
        para.paragraph_format.space_before = Pt(3)
        para.paragraph_format.space_after = Pt(3)


    nowtime = datetime.now()
    filetime = str(nowtime).split()[0].replace("-","") + str(nowtime).split()[1].split(":")[0] + str(nowtime).split()[1].split(":")[1]
    document.save(outputDir + "\\" + targetCorp + filetime + '.docx')



def addHyperlink(paragraph, url, font_size="22"):
    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a w:r element
    new_run = docx.oxml.shared.OxmlElement('w:r')

    # Create a new w:rPr element
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    fontcolor = docx.oxml.shared.OxmlElement('w:color')
    fontcolor.set(docx.oxml.shared.qn('w:val'), "0000FF", )
    
    underline = docx.oxml.shared.OxmlElement("w:u")
    underline.set(docx.oxml.shared.qn('w:val'), "single", )

    underline = docx.oxml.shared.OxmlElement("w:sz")
    underline.set(docx.oxml.shared.qn('w:val'), font_size, )

    # Join all the xml elements together add add the required text to the w:r element
    rPr.append(fontcolor)
    rPr.append(underline)
    new_run.append(rPr)
    new_run.text = url
    hyperlink.append(new_run)
    
    # <w:hyperlink>
    #     <w:r>
    #         <w:rPr>
    #             <w:color w:val="0000FF"/>
    #             <w:u w:val="single"/>
    #             <w:sz w:val="28"/>
    #         </w:rPr>
    #     </w:r>
    # </w:hyperlink>

    paragraph._p.append(hyperlink)
    return hyperlink