__author__ = 'mohaowen'

import sys
import re
import xlwt
import urllib2
import httplib
import time
import Queue
import threading
import random
from time import ctime
from lxml import etree

httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

totalQuery = int()
rankQueue = Queue.Queue()
writeQueue = Queue.Queue()





class rankThread(threading.Thread):
    def __init__(self, name, querylist):
        threading.Thread.__init__(self)
        self.threadName = name
        self.queryList = querylist


    def getFirsNatureRankUrl(self, input_list, fromThread):

        #xrankQueue = Queue.Queue(maxsize=totalQuery)

        for line in input_list:                                     #read query file per line
            newline = urllib2.quote(line)
            queryRequst='http://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=' + newline
            html_source = urllib2.urlopen(queryRequst, timeout=5).read()                                    #download pages
            #time.sleep(random.uniform(0,1))
            #html_source = urllib2.urlopen(line).read()
            queryTree = etree.HTML(html_source)                                                # change pages to a DOM tree

            firstNatureRank = queryTree.xpath('//*[@id="J-items-content"]/div[@class="f-icon m-item"][1]/div/div[2]/div[1]/a')    # firstNatureRank's Xpath
            for queryPage in firstNatureRank:                                  #get  firstNatureRank nodes

                firstNatureRank_url = queryPage.attrib['href']
                out = fromThread + ': ' + firstNatureRank_url
                rankQueue.put(firstNatureRank_url)
                print out

    # print "End of " + fromThread
    print str(rankQueue.qsize())

    def run(self):
        print "From" + self.threadName
        self.getFirsNatureRankUrl(self.queryList, self.threadName)


class termThread(threading.Thread):

    def __init__(self, name, term):
        threading.Thread.__init__(self)
        self.threadName = name
        self.termurl = term

    def getTerms(self, termurl):

        termList = list()
        select_Product_source = urllib2.urlopen(termurl, timeout=5).read()
        firstRankTree = etree.HTML(select_Product_source)

        keywords = firstRankTree.xpath('//meta[@name="keywords"]')
        producttitle = firstRankTree.xpath('//title/text()')
        breadcrumb = firstRankTree.xpath('//div[@class="ui-breadcrumb"]')
        productpic = firstRankTree.xpath('//meta[@property="og:image"]')
        for keywordsValue in keywords:
            termList.append(keywordsValue.attrib['content'])
            print "keywords:" + keywordsValue.attrib['content']

        termList.append(producttitle)
        print "producttitle:" + producttitle

        for productpicValue in productpic:
            termList.append(productpicValue.attrib['content'])
            print "productpic:" + productpicValue.attrib['content']

        for breadcrumbValue in breadcrumb:
            termList.append(breadcrumbValue.attrib['content'])
            print "breadcrumb:" + breadcrumbValue.attrib['content']
        return termList

    def run(self):
        print "From" + self.threadName
        list_tmp = self.getTerms(self.termurl)
        writeQueue.append(list_tmp)


class producer():
    def __init__(self, inputPath):
        self.queryPath = inputPath


    def opnefile(self):
        readQueryFile = open(self.queryPath, "r")
        listQuery = readQueryFile.readlines()
        totalQuery = len(listQuery)
        return listQuery

    def produce(self):
        allquery = self.opnefile()
        subList = len(allquery)/3

        thread1 = rankThread("Thread-1", allquery[:subList])
        thread2 = rankThread("Thread-2", allquery[subList:2*subList])
        thread3 = rankThread("Thread-3", allquery[2*subList:])

        try:
            thread1.start()
            thread2.start()
            thread3.start()
            time.sleep(10)

        except:
            print "Error: unable to start Producer thread"

class consumer():

    def __init__(self, conUrl):
        self.consumeUrl = conUrl

    def consume(self):

        print "Now queue size is:" + str(rankQueue.qsize())
        print "TermUrl: "+self.consumeUrl
        threadTerm = termThread("termThread-1", self.consumeUrl)
        try:
            threadTerm.start()
        except:
            print "Error: unable to start Consumer thread"
        time.sleep(3)
class writefile():

    def __init__(self, wList):
        self.writeList = wList

    def output(self):
        ISOTIMEFORMAT = '%b-%d_%H-%M'
        filename = time.strftime(ISOTIMEFORMAT, time.localtime()) + ".xls"
        ISOTIMEFORMAT = '%X'

        book = xlwt.Workbook(encoding='utf-8', style_compression=0)      # create a excel book
        sheet = book.add_sheet('Sheet1', cell_overwrite_ok=True)         # add a sheet

        dataRow = 0                                                     # sheet's Row
        count = 0                                                       # Spider Count
        sheet.write(dataRow, 0, self.writeList[0])
        sheet.write(dataRow, 1, self.writeList[1])
        sheet.write(dataRow, 2, self.writeList[2])
        sheet.write(dataRow, 3, self.writeList[3])
        count += 1
        leftnum = totalQuery - count
        print "Finish  " + str(count) + "  product query. " + str(leftnum) + " queries left. " + time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
        book.save(filename)