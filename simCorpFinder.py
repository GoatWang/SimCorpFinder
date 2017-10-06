from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDesktopWidget, QLabel, QLineEdit, QGridLayout
from PyQt5.QtWidgets import QPushButton, QFileDialog, QMessageBox, QCheckBox, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QIcon, QFont


import numpy 
import pandas as pd
import os
from datetime import datetime
import uuid
import sys

# user information
import socket
import getpass
import subprocess
import platform

from pymongo import MongoClient
import selfPwd
conn = MongoClient(selfPwd.getMongoUrl())
db = conn.simcorpfinder

from versionControl import versionControl

if not "SimCorpFinderData" in os.listdir("C:\\"):
    os.mkdir("C:\\SimCorpFinderData")
if not "logs" in os.listdir("C:\\SimCorpFinderData"):
    os.mkdir("C:\\SimCorpFinderData\\logs")
if not "outputs" in os.listdir("C:\\SimCorpFinderData"):
    os.mkdir("C:\\SimCorpFinderData\\outputs")
if not "companyInfo_v23" in os.listdir("C:\\SimCorpFinderData"):
    os.mkdir("C:\\SimCorpFinderData\\companyInfo_v23")
    
from googleCrawler import Main
from crawlerUtl import getDistinctName, getCurrentDir
from outputReader import writeStats

# from PyQt5.QtGui import QLine
class simCorpFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Build Grid Layout
        grid = QGridLayout()
        # grid.setSpacing(20)
        
        ## preview
        preview = QLabel('')
        preview.setWordWrap(True)
        preview.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        grid.addWidget(preview, 0, 2, 7, 1)
        grid.setColumnMinimumWidth(2, 200)

        self.targetCorp = ""
        self.keywords = ""

        self.keywords_emphasize = ""
        self.keywords_filtered = ""
        
        self.outputDir = "C:\\SimCorpFinderData\\outputs"
        self.findingCorps = ""
        self.findingCorpsLi = []
        self.recarwling = False
        self.threadNum = 4


        def updatePreview():
            previewText = ""
            previewText += "Target Company: " + str(self.targetCorp) + "\n\n"
            previewText += "Keywords: " + str(self.keywords) + "\n\n"
            previewText += "Keywords(Emphasize): " + str(self.keywords_emphasize) + "\n\n"
            previewText += "Keywords(Filtered): " + str(self.keywords_filtered) + "\n\n"
            previewText += "Output Directory: " + self.outputDir + "\n\n"
            previewText += "Finding Companies: \n" + self.findingCorps + "\n\n"
            previewText += "Threads Number: " + str(self.threadNum) + "\n\n"
            previewText += "Recrawling Data: " + str(self.recarwling) + "\n\n"
            preview.setText(previewText)
            self.resize(self.sizeHint())
        updatePreview()




        # target Label and Textbox
        target = QLabel('Target Company')
        grid.addWidget(target, 0, 0)

        targetEdit = QLineEdit()
        targetEdit.setPlaceholderText("Beverage Company")
        grid.addWidget(targetEdit, 0, 1)

        def textChanged_target():
            self.targetCorp = getDistinctName(targetEdit.text().replace("\n", "").replace("_"," ")).replace(" ", "")
            updatePreview()
        targetEdit.textChanged.connect(textChanged_target)






        # keyword Label and Textbox
        keywords = QLabel('Keywords')
        grid.addWidget(keywords, 1, 0)

        keywordsEdit = QLineEdit()
        keywordsEdit.setPlaceholderText("drink tea")
        grid.addWidget(keywordsEdit, 1, 1)

        def textChanged_keywords():
            self.keywords = keywordsEdit.text().replace("\n", "").lower()
            updatePreview()
        keywordsEdit.textChanged.connect(textChanged_keywords)



        # keyword Label and Textbox
        keywords_emphasize = QLabel('Keywords(Emphasize)')
        grid.addWidget(keywords_emphasize, 2, 0)

        keywords_emphasizeEdit = QLineEdit()
        keywords_emphasizeEdit.setPlaceholderText('"beverage company" beverage')
        grid.addWidget(keywords_emphasizeEdit, 2, 1)

        def textChanged_keywords_emphasize():
            self.keywords_emphasize = keywords_emphasizeEdit.text().replace("\n", "").lower()
            updatePreview()
        keywords_emphasizeEdit.textChanged.connect(textChanged_keywords_emphasize)




        # keyword Label and Textbox
        keywords_filtered = QLabel('Keywords(Filtered)')
        grid.addWidget(keywords_filtered, 3, 0)

        keywords_filteredEdit = QLineEdit()
        keywords_filteredEdit.setPlaceholderText("juice")
        grid.addWidget(keywords_filteredEdit, 3, 1)

        def textChanged_keywords_filtered():
            self.keywords_filtered = keywords_filteredEdit.text().replace("\n", "").lower()
            updatePreview()
        keywords_filteredEdit.textChanged.connect(textChanged_keywords_filtered)










        ## threads number slider
        thread = QLabel('Threads Number')
        grid.addWidget(thread, 6, 0)

        threadSlider = QSlider(Qt.Horizontal)
        threadSlider.setMinimum(2)
        threadSlider.setMaximum(8)
        threadSlider.setValue(4)
        threadSlider.setTickPosition(QSlider.TicksBelow)
        threadSlider.setTickInterval(1)
        grid.addWidget(threadSlider, 6, 1)

        def threadChange():
            self.threadNum = threadSlider.value()
            updatePreview()
        threadSlider.valueChanged.connect(threadChange)





        ## rewrite (recrawl) checkbox
        recarwlCheckbox = QCheckBox("Recrawling Data", self)
        recarwlCheckbox.setChecked(False)
        def clickBox():
            self.recarwling = recarwlCheckbox.isChecked()
            updatePreview()
        recarwlCheckbox.stateChanged.connect(clickBox)
        grid.addWidget(recarwlCheckbox, 7, 0)




        ## output dir browser
        OutputDirPath = QLabel('Output Directory')
        grid.addWidget(OutputDirPath, 4, 0)

        btnOutputDirBrowser = QPushButton("File Browser")
        grid.addWidget(btnOutputDirBrowser, 4, 1)

        def selectOutputDir():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec_():
                self.outputDir = dialog.selectedFiles()[0]
            updatePreview()

        btnOutputDirBrowser.clicked.connect(selectOutputDir)




        # Input File browser Label and Button
        findingPath = QLabel('Finding Companies')
        grid.addWidget(findingPath, 5, 0)
        
        
        btnFileBrowser = QPushButton("File Browser")
        grid.addWidget(btnFileBrowser, 5, 1)
        
        def selectFile():
            filePath = QFileDialog.getOpenFileName(filter="*.csv")[0]
            if filePath:  ## if directly close the file chooser
                try:
                    findindCorps = pd.read_csv(filePath, header=None)[0].tolist()
                    self.findingCorpsLi = findindCorps
                    findindCorpsStr = ""
                    for num, corp in enumerate(findindCorps):
                        if num < 10:
                            findindCorpsStr += str(num+1) + ". " + corp + "\n"
                        else:
                            break
                    if len(findindCorps) > 10:
                        findindCorpsStr += "..." + "\n"
                        findindCorpsStr += "..." + "\n"
                        findindCorpsStr += str(len(findindCorps)) + ". " + findindCorps[-1]
                    self.findingCorps = findindCorpsStr
                    updatePreview()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Please select valid csv file")
                    msg.setWindowTitle("Notice")
                    msg.exec_()
                    ## https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm
        btnFileBrowser.clicked.connect(selectFile)


        ## ranking Button
        btnRanking = QPushButton("Start Ranking")
        grid.addWidget(btnRanking, 7, 2)
        
        def startRanking():
            if self.keywords != "" and self.targetCorp != "" and len(self.findingCorpsLi) != 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Please wait!")
                msg.setInformativeText("(first time only)It takes about " + str(int(len(self.findingCorpsLi) * 3.5)) + "~" + str(int(len(self.findingCorpsLi) * 3.5 * 1.4)) +" seconds to process!")
                msg.setWindowTitle("Notice")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                reply = msg.exec_()

                if reply == QMessageBox.Ok:
                    
                    data = {
                        "user":getpass.getuser(),
                        "ip":socket.gethostbyname(socket.gethostname()),
                        "hostname":socket.gethostname(),
                        "platform":platform.platform() + "_" + platform.architecture()[0],
                        "version":versionControl.version,
                        "targetCorp":self.targetCorp,
                        "findingCorps":self.findingCorpsLi,
                        "searchTime":datetime.utcnow(),
                        "keywords":self.keywords,
                        "keywords_emphasize":self.keywords_emphasize,
                        "keywords_filtered":self.keywords_filtered
                    }
                    collection = db['user_log']   
                    collection.insert_one(data)

                    print("Start crawling")
                    Main().startThread(findingCorps=self.findingCorpsLi, targetComp=self.targetCorp, forceDelete=self.recarwling, threadNum=self.threadNum)
                    
                    print("95% " + "Writing output file, please wait patiently")
                    # writeStats_word(self.targetCorp, self.keywords, self.keywords_emphasize, self.keywords_filtered, self.outputDir, self.findingCorpsLi, False)
                    writeStats(self.targetCorp, self.keywords, self.keywords_emphasize, self.keywords_filtered, self.outputDir, self.findingCorpsLi)

                    print("100% Finished!")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("The file was generated under: \n" + self.outputDir + "\n The program will be closed immediately.")
                    msg.setWindowTitle("Output Directory and Close Notice")
                    msg.exec_()
                    self.close()

                    subprocess.run(["explorer", self.outputDir])
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Please enter Taget Company or Keywords or Finding Companies!")
                msg.setWindowTitle("Notice")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        btnRanking.clicked.connect(startRanking)


        ## News Button
        btnNews = QPushButton("News")
        grid.addWidget(btnNews, 0, 3)
        def showNews():
                collection = db['news']
                res = collection.find()
                newsLi = sorted(res, key=lambda x:x['time'], reverse=True)[:5]
                newsStr = ""
                for news in newsLi:
                    newsStr += str(news['time'].date()) + " " + news['news'] + "\n"
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(newsStr)
                msg.setWindowTitle("News")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        btnNews.clicked.connect(showNews)


        ## Web Button
        btnWeb = QPushButton("Website")
        grid.addWidget(btnWeb, 1, 3)
        def goToAbout():
            subprocess.run(["explorer", "https://goatwang.github.io/SimCorpFinder/index.html"])

        btnWeb.clicked.connect(goToAbout)


        ## Documentation Button
        btnDocumentation = QPushButton("Documentation")
        grid.addWidget(btnDocumentation, 2, 3)
        def goToDocumentation():
            subprocess.run(["explorer", "https://goatwang.github.io/SimCorpFinder/index.html#Documentation"])

        btnDocumentation.clicked.connect(goToDocumentation)


        self.setLayout(grid)
        self.setFont(QFont("Times", 9))
        self.setWindowTitle("SimCorpFinder" + "(v" + versionControl.version + ")")
        self.setWindowIcon(QIcon( getCurrentDir() + "\\favicon.ico"))
        self.move(500,80)
        self.resize(self.sizeHint())
        self.show()

        collection = db['version']
        res = collection.find()
        versionInfo = sorted(res, key=lambda x:x['time'], reverse=True)[0]

        if versionControl.version < versionInfo['version']: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("The new version is available, you can go to the official website to download" )
            msg.setInformativeText("update information: \n" + versionInfo['updateInfo'])
            msg.setWindowTitle("New Version Available")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    SCF = simCorpFinder()
    sys.exit(app.exec_())
