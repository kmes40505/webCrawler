from crawler import *
import os
import urllib.request
import subprocess
import re
import json
from functools import partial

rootPath = "file:" + urllib.request.pathname2url(os.getcwd() + "/sampleHtml/")

homeHtml = rootPath + "home.html"
dir1Html = rootPath + "dir1/dir1.html"
dir2Html = rootPath + "dir2/dir2.html"

def terminalResultIntoDict(input:str)-> dict:
	jsonStr = re.sub("([^\n\t ]+)", r'"\1"', input)
	jsonStr = re.sub("((\n\t.+)+)", r":[\1]", jsonStr)
	jsonStr = re.sub("\n\t*", "", jsonStr)
	jsonStr = re.sub('""', '","', jsonStr)
	jsonStr = re.sub(r']"', '],"', jsonStr)
	retDict = json.loads("{" + jsonStr + "}")
	return retDict



allPageDict = \
	{
		homeHtml: {dir1Html, dir2Html},
		dir1Html: {homeHtml, dir2Html},
		dir2Html: {homeHtml, dir1Html}
	}

def checkPageContent(checkDict:dict, testName: str, targetPages: set):
	checkParent = set(checkDict.keys())
	assert len(checkParent.difference(targetPages)) == 0, testName + ": incorrect pages crawled. Should be: " + str(targetPages) + " but has: " + str(checkParent) \
		+ "\nResult value: " + str(checkDict)

	for targetPage in targetPages:
		ansChildPagePaths = allPageDict[targetPage]
		checkChild = set(checkDict[targetPage])
		assert len(checkChild.difference(ansChildPagePaths)) == 0, testName + ": " + targetPage + " has wrong urls. Should be: " + str(ansChildPagePaths) + " but has: " + str(checkChild) \
			+ "\nResult value: " + str(checkDict)


def crawlAll():
	funcCallResultDict = crawlUrl(homeHtml)
	terminalResult = subprocess.run(["python", "crawler.py", homeHtml], stdout=subprocess.PIPE,text=True).stdout
	terminalResultDict = terminalResultIntoDict(terminalResult)
	crawlAllTestName = "crawAll"
	terminalTestName = crawlAllTestName + " terminal Test"
	functionTestName = crawlAllTestName + " function call Test"
	ansPages = [homeHtml, dir1Html, dir2Html]
	checkPageContent(terminalResultDict, terminalTestName, ansPages)
	checkPageContent(funcCallResultDict, functionTestName, ansPages)

def maxOneUrl():
	funcCallResultDict = crawlUrl(homeHtml, maxUrlNum = 1)
	terminalResult = subprocess.run(["python", "crawler.py", "-n", "1", homeHtml], stdout=subprocess.PIPE,text=True).stdout
	terminalResultDict = terminalResultIntoDict(terminalResult)
	crawlAllTestName = "maxOneUrl"
	terminalTestName = crawlAllTestName + " terminal Test"
	functionTestName = crawlAllTestName + " function call Test"
	ansPages = [homeHtml]
	checkPageContent(terminalResultDict, terminalTestName, ansPages)
	checkPageContent(funcCallResultDict, functionTestName, ansPages)

def maxTwoUrl():
	crawlAllTestName = "maxTwoUrl"
	terminalTestName = crawlAllTestName + " terminal Test"
	functionTestName = crawlAllTestName + " function call Test"

	def check(testName: str, checkDict: dict):
		checkDictPages = checkDict.keys()
		assert len(checkDictPages) == 2 and homeHtml in checkDictPages, testName +": incorrect pages crawled. Should have 2 pages and contains " + homeHtml + ". Value: " + str(checkDict)
		checkPageContent(checkDict, testName, checkDictPages)

	funcCallResultDict = crawlUrl(homeHtml, maxUrlNum = 2)
	check(functionTestName, funcCallResultDict)

	terminalResult = subprocess.run(["python", "crawler.py", "-n", "2", homeHtml], stdout=subprocess.PIPE,text=True).stdout
	terminalResultDict = terminalResultIntoDict(terminalResult)
	check(terminalTestName, terminalResultDict)

crawlAll()
maxOneUrl()
maxTwoUrl()
print("All Test Passed")