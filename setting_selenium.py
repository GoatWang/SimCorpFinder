from selenium import webdriver
import platform, os
import sys

def getCurrentDir():
    if getattr(sys, 'frozen', False):
        # frozen
        dir_ = os.path.dirname(sys.executable)
    else:
        # unfrozen
        dir_ = os.path.dirname(os.path.realpath(__file__))    
    return dir_

def cross_selenium(chrome=False):
	sysName = platform.system()
	if sysName == "Windows":
		if chrome:
			driver = webdriver.Chrome(executable_path = getCurrentDir() + '\\chromedriver.exe')
		else:
			driver = webdriver.PhantomJS(executable_path = getCurrentDir() + '\\phantomjs.exe', service_log_path='C:\SimCorpFinderData\ghostdriver.log')
	else:
		if chrome:
			driver = webdriver.Chrome(executable_path = getCurrentDir() + '\\chromedriver')
		else:
			# driver = webdriver.PhantomJS(executable_path = getCurrentDir() + '\\phantomjs')
			# driver = webdriver.PhantomJS(executable_path=os.path.join('.', 'phantomjs'))
			driver = webdriver.PhantomJS()
	return driver 


if __name__ == "__main__":
	print(getCurrentDir())
	print(os.path.join(getCurrentDir(), 'phantomjs.exe'))

