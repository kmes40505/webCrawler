import threading
import queue
import urllib.request
import urllib.parse
import re
import argparse
import inspect

def crawlUrl(rootUrl : str, *, maxUrlNum : int = None, printData : bool = False) -> dict:
	urlDict = {rootUrl : set()}
	urlDictLock = threading.Lock()
	urlThreads = queue.Queue();
	printLock = threading.Lock()
	def childCrawUrl(url):
		def postProcess():
			if printData:
				printLock.acquire()
				print(url)
				for childUrl in urlDict[url]:
					print("\t" + childUrl)
				printLock.release()
			urlThreads.task_done()

		try:
			html = urllib.request.urlopen(url)
		except Exception as e:
			urlDict[url].add(str(e))
			postProcess()
			return
		
		content = str(html.read())
		for childUrl in re.findall('href="([^"]*)"', content):
			childUrl = urllib.parse.urljoin(url, childUrl)
			urlDict[url].add(childUrl)
			#Extra if statement to avoid throttle at urlDictLock
			if childUrl in urlDict or (maxUrlNum is not None and len(urlDict) >= maxUrlNum):
				continue

			urlDictLock.acquire()
			if childUrl in urlDict or (maxUrlNum is not None and len(urlDict) >= maxUrlNum):
				urlDictLock.release()
				continue
			urlDict[childUrl] = set()
			urlDictLock.release()

			childThread = threading.Thread(target = childCrawUrl, args = {childUrl})
			urlThreads.put(childThread)
			childThread.start()

		postProcess()

	rootThread = threading.Thread(target = childCrawUrl, args = {rootUrl})
	urlThreads.put(rootThread)
	rootThread.start()
	urlThreads.join()
	return urlDict

if __name__ == "__main__":
	argParser = argparse.ArgumentParser()
	argParser.add_argument("rootUrl", metavar="rootUrl", help="The root url to start crawling", type=str, nargs=1)
	argParser.add_argument("-n", "--maxUrlNum", help="Maximum number of url iterated", type=int)
	args = argParser.parse_args()
	maxUrlNum = inspect.signature(crawlUrl).parameters['maxUrlNum'].default
	if args.maxUrlNum is not None:
		maxUrlNum = args.maxUrlNum

	crawlUrl(args.rootUrl[0], maxUrlNum = maxUrlNum, printData = True)