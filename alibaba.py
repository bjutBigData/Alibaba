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

ISOTIMEFORMAT = '%b-%d_%H-%M'
filename = time.strftime(ISOTIMEFORMAT, time.localtime()) + ".xls"

ISOTIMEFORMAT = '%X'

#queryFile=sys.argv[1]             #queryfile dictory
queryFile = "/home/mohaowen/list.txt"
#excelFile=sys.argv[2]             #finally excel file save dictory

readQueryFile = open(queryFile, "r")                           #  open qureyfile
#readQueryFile = open("G:\\kws.txt", "r")

#totalQuery = len(open(r"G:\\kws.txt",'rU').readlines())
listQuery = readQueryFile.readlines()
subList = len(listQuery)/3

print str(subList)
print listQuery
#print listQuery[:len(listQuery)/3]

totalQuery = len(open(queryFile, 'rU').readlines())

rankQueue = Queue.Queue(maxsize=totalQuery)

# rankQueue.put('Thread-2: http://www.alibaba.com/product-detail/empty-plastic-water-bottles-wholesale-Plastic_60199507214.html')
# rankQueue.put('Thread-1: http://www.alibaba.com/product-detail/24-410-screw-plastic-bottle-top_1652054636.html')


print "Total num is " + str(totalQuery)
aaa = '''book = xlwt.Workbook(encoding='utf-8',style_compression=0)      # create a excel book
sheet = book.add_sheet('Sheet1',cell_overwrite_ok=True)         # add a sheet

dataRow = 0                                                     # sheet's Row
count = 0                                                       # Spider Count
  '''
def getFirsNatureRankUrl(input_list, fromThread):

    #rankQueue = Queue.Queue(maxsize=totalQuery)

    for line in input_list:                                     #read query file per line
        newline = urllib2.quote(line)
        queryRequst='http://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=' + newline
        html_source = urllib2.urlopen(queryRequst, timeout=10).read()                                    #download pages
    #time.sleep(random.uniform(0,1))
    #html_source = urllib2.urlopen(line).read()
        queryTree = etree.HTML(html_source)                                                # change pages to a DOM tree

        firstNatureRank = queryTree.xpath('//*[@id="J-items-content"]/div[@class="f-icon m-item"][1]/div/div[2]/div[1]/a')    # firstNatureRank's Xpath
        for queryPage in firstNatureRank:                                  #get  firstNatureRank nodes

            firstNatureRank_url = queryPage.attrib['href']
            out = fromThread + ': ' + firstNatureRank_url
            rankQueue.put(firstNatureRank_url)
            print out

    print "End of " + fromThread
    print str(rankQueue.qsize())

class myThread(threading.Thread):
    def __init__(self, name, querylist):
        threading.Thread.__init__(self)
        self.threadName = name
        self.queryList = querylist

    def run(self):
        print "From" + self.threadName
        getFirsNatureRankUrl(self.queryList, self.threadName)

class termThread(threading.Thread):
    def __init__(self, name, term):
        threading.Thread.__init__(self)
        self.threadName = name
        self.termurl = term

    def run(self):
        print "From" + self.threadName
        getTerms(self.termurl)


thread1 = myThread("Thread-1", listQuery[:subList])
thread2 = myThread("Thread-2", listQuery[subList:2*subList])
thread3 = myThread("Thread-3", listQuery[2*subList:])


def getTerms(termurl):

    nnn='''req_header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Connection':'keep-alive',
        'Referer':'www.alibaba.com'
    }

    req = urllib2.Request(termurl, None, req_header)'''


    select_Product_source_html = urllib2.urlopen(termurl, None, timeout=10)

    time.sleep(2)
    select_Product_source = select_Product_source_html.read()

    # print  select_Product_source
    firstRankTree = etree.HTML(select_Product_source)

    keywords = firstRankTree.xpath('//meta[@name="keywords"]')
    producttitle = firstRankTree.xpath('//title/text()')
    breadcrumb = firstRankTree.xpath('//div[@class="ui-breadcrumb"]')
    productpic = firstRankTree.xpath('//meta[@property="og:image"]')
    for keywordsValue in keywords:
        print "keywords:" + keywordsValue.attrib['content']

    print producttitle[0]

    for productpicValue in productpic:
            print "productpic:" + productpicValue.attrib['content']

    for breadcrumbValue in breadcrumb:
        print "breadcrumb:" + breadcrumbValue.attrib['content']
    vvv=''' print "keywords:" + keywords
    print "producttitle:" + producttitle
    print "breadcrumb:" + breadcrumb
    print "productpic:" + productpic
    '''

try:
    thread1.start()
    thread2.start()
    thread3.start()

    time.sleep(10)
    print "Now queue size is:" + str(rankQueue.qsize())
    while not rankQueue.empty():
        url_Term = rankQueue.get()
        print "TermUrl: "+url_Term
        threadTerm = termThread("termThread-1", url_Term)
        threadTerm.start()
        time.sleep(3)


except:
    print "Error: unable to start thread"






