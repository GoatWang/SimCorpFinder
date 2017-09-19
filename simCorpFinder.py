from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDesktopWidget, QLabel, QLineEdit, QGridLayout
from PyQt5.QtWidgets import QPushButton, QFileDialog, QMessageBox, QCheckBox, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QIcon, QFont


import numpy 
import pandas as pd
import os
import socket
from datetime import datetime
import uuid
import sys

if not "SimCorpFinderData" in os.listdir("C:\\"):
    os.mkdir("C:\\SimCorpFinderData")
if not "logs" in os.listdir("C:\\SimCorpFinderData"):
    os.mkdir("C:\\SimCorpFinderData\\logs")
if not "outputs" in os.listdir("C:\\SimCorpFinderData"):
    os.mkdir("C:\\SimCorpFinderData\\outputs")

from googleCrawler import Main
from crawlerUtl import getDistinctName
from elasticUtl import writeStats, esLogin, checkDateoutAndDelete, writeStats_word
# from elasticsearch import Elasticsearch
# es = Elasticsearch()
es = esLogin()

# from PyQt5.QtGui import QLine
class simCorpFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Build Grid Layout
        grid = QGridLayout()
        grid.setSpacing(20)

        ## preview
        preview = QLabel('')
        preview.setWordWrap(True)
        preview.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        grid.addWidget(preview, 0, 2, 5, 1)
        grid.setColumnMinimumWidth(2, 200)

        self.targetCorp = ""
        self.keywords = ""
        self.outputDir = "C:\\SimCorpFinderData\\outputs"
        self.findingCorps = ""
        self.findingCorpsLi = []
        self.recarwling = False
        self.threadNum = 4


        def updatePreview():
            previewText = ""
            previewText += "Target Company: " + str(self.targetCorp) + "\n\n"
            previewText += "Keywords: " + str(self.keywords) + "\n\n"
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
        targetEdit.setPlaceholderText("Coca-Cola Global")
        grid.addWidget(targetEdit, 0, 1)

        def textChanged_target():
            self.targetCorp = getDistinctName(targetEdit.text().replace("\n", "").replace("_"," ")).replace(" ", "")
            updatePreview()
        targetEdit.textChanged.connect(textChanged_target)






        # keyword Label and Textbox
        keywords = QLabel('Keywords')
        grid.addWidget(keywords, 1, 0)

        keywordsEdit = QLineEdit()
        keywordsEdit.setPlaceholderText("drink juice beverage")
        grid.addWidget(keywordsEdit, 1, 1)

        def textChanged_keywords():
            self.keywords = keywordsEdit.text().replace("\n", "")
            updatePreview()
        keywordsEdit.textChanged.connect(textChanged_keywords)



        ## threads number slider
        thread = QLabel('Threads Number')
        grid.addWidget(thread, 4, 0)

        threadSlider = QSlider(Qt.Horizontal)
        threadSlider.setMinimum(2)
        threadSlider.setMaximum(8)
        threadSlider.setValue(4)
        threadSlider.setTickPosition(QSlider.TicksBelow)
        threadSlider.setTickInterval(1)
        grid.addWidget(threadSlider, 4, 1)

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
        grid.addWidget(recarwlCheckbox, 5, 0)




        ## output dir browser
        OutputDirPath = QLabel('Output Directory')
        grid.addWidget(OutputDirPath, 2, 0)

        btnOutputDirBrowser = QPushButton("File Browser")
        grid.addWidget(btnOutputDirBrowser, 2, 1)

        def selectOutputDir():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec_():
                self.outputDir = dialog.selectedFiles()[0]
            updatePreview()

        btnOutputDirBrowser.clicked.connect(selectOutputDir)




        # Input File browser Label and Button
        findingPath = QLabel('Finding Companies')
        grid.addWidget(findingPath, 3, 0)
        
        
        btnFileBrowser = QPushButton("File Browser")
        grid.addWidget(btnFileBrowser, 3, 1)
        
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
        grid.addWidget(btnRanking, 5, 2)
        
        def startRanking():
            if not es.indices.exists('companyembedding'):
                es.indices.create('companyembedding')
            if not es.indices.exists('companyembedding_url'):
                es.indices.create('companyembedding_url')
            if not es.indices.exists('companyembedding_labeled'):
                es.indices.create('companyembedding_labeled')
            if not es.indices.exists('companyembedding_labeled_url'):
                es.indices.create('companyembedding_labeled_url')
            if not es.indices.exists('user_log'):
                es.indices.create('user_log')

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please wait!")
            msg.setInformativeText("If this is the first time the program process these companies, the program will take about " + str(int(len(self.findingCorpsLi) * 3.5)) + "~" + str(int(len(self.findingCorpsLi) * 3.5 * 1.4)) +" seconds to process!")
            msg.setWindowTitle("Notice")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            reply = msg.exec_()
            if reply == QMessageBox.Ok:
                
                data = {
                    "ip":socket.gethostbyname(socket.gethostname()),
                    "targetCorp":self.targetCorp,
                    "findingCorps":str(self.findingCorpsLi) ,
                    "searchTime":datetime.utcnow(),
                    "keywords":self.keywords
                }
                es.create(index="user_log", doc_type="search", id=uuid.uuid4(), body=data)
                Main().startThread(findingCorps=self.findingCorpsLi, targetComp=self.targetCorp, forceDelete=self.recarwling, threadNum=self.threadNum)
                
                # writeStats(self.targetCorp, self.keywords, self.outputDir, self.findingCorpsLi, False)
                writeStats_word(self.targetCorp, self.keywords, self.outputDir, self.findingCorpsLi, False)
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The file was generated under: \n" + self.outputDir + "\n The program will be closed immediately.")
                msg.setWindowTitle("Output Directory and Close Notice")
                msg.exec_()
                self.close()
            
        btnRanking.clicked.connect(startRanking)

        self.setLayout(grid)
        self.setFont(QFont("Times", 9))
        self.setWindowTitle("SimCorpFinder")
        # self.setWindowIcon(QIcon("book.png"))
        self.resize(self.sizeHint())
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    SCF = simCorpFinder()
    sys.exit(app.exec_())
