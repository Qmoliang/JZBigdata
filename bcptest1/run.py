 #coding=utf-8

import scrapy
from scrapy.crawler import CrawlerProcess
import sys
import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import csv
import os
from scrapy.utils.project import get_project_settings
import codecs
import re, htmlentitydefs

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        pages = []
        f = open("input.txt", "r")
        line = f.readline().replace('\n', '')
        print line
        print '\n'
        for filename in os.listdir(line):
            url = "file:///" + line.replace("%5C",'\\') + filename + "/GAB_ZIP_INDEX.xml"
            print "--------------"
            print url
            print "--------------"
            page = scrapy.Request(url)
            pages.append(page)

            g = open("output.txt", "r")
            rout = g.readline().replace('\n', '')
            os.mkdir(rout+filename)
            print rout+filename
            
            print '\n\n\n\n\n'
            g.close()
        f.close()
        print pages
        print '\n\n\n\n\n'
        return pages



    #chn中文信息#
    def unescape(self,text):
        def convert(matchobj):
            text = matchobj.group(0)
            if text[:2] == "&#":
                # Numeric Character Reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # Character entities references
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # Return Unicode characters
        return re.sub("&#?\w+;", convert, text)
    #------------------#

    def parse(self, response):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        main = response.xpath("//DATASET/DATA/DATASET")[0]
        dataset = main.xpath('./DATA')
        for data in dataset:
            item = data.xpath('./ITEM')
            col = self.valFind(item[0].extract())
            col = self.transfer(col)
            row = self.valFind(item[1].extract())
            row = self.transfer(row)
            nameData = data.xpath('./DATASET')[0]
            name = self.valFind(nameData.xpath('./DATA/ITEM')[1].extract())
            listData = data.xpath('./DATASET')[1]
            listItem = listData.xpath('./DATA/ITEM').extract()
            colList = []
            for item in listItem:
                colList.append(self.nameFind(item))
            #print name, row, col ,colList
            self.stripFile(name, row, col ,colList,response)


    def valFind(self,itemTmp):
        indexF = itemTmp.find('val') + 5
        indexE = itemTmp[indexF:-1].find('"')+indexF
        return itemTmp[indexF:indexE]

    def nameFind(self,itemTmp):
        indexF = itemTmp.find('chn') + 5
        indexE = itemTmp[indexF:-1].find('"')+indexF
        chin = itemTmp[indexF:indexE]
        chins = self.unescape(chin)
        return chins


 
       

    
    def stripFile(self,oldFName,row,col,listed,response):
        '''''remove the space or Tab or enter in a file,and output to a new file in the same folder'''
        f = open("output.txt", "r")
        route = f.readline().replace('\n', '')
        f.close()
        
        #print response.url
        #print '\n\n\n\n\n\n\n'
        g = open("input.txt", "r")
        rout = g.readline().replace('\n', '')
        print "--------------"
        print rout
        print "--------------"
        g.close()
        newres = response.url.replace("%5C",'\\')
        print "--------------"
        print newres
        print "--------------"
        stri = newres[len(rout)+8:len(newres)]
        print "--------------"
        print stri
        print "--------------"
        end = stri.find('GAB_ZIP_INDEX.xml')
        outputFileName = stri[0:end-1]
        print "--------------"
        print outputFileName
        print "--------------"
        na = rout + outputFileName + '/' + oldFName
        na = na.replace("%5C",'/')
        fp = open(na,"r+")
        newFp = file(route+'/' + outputFileName + '/' +oldFName[0:-4]+r'.csv',"a+")
        print route
        print '\n\n\n\n\n\n\n'
        newFp.write(codecs.BOM_UTF8)
        for i in range(0, len(listed)-1):
            newFp.write(listed[i]+',')
        newFp.write(listed[-1]+'\n')

        for eachline in fp.readlines():
            newStr = eachline.replace(col,",").replace(row,"\n").strip()
            #print "Write:",newStr
            newFp.write(newStr+'\n')
        
        newFp.close()
        fp.close()
    def transfer(self,a):
        b=''
        for i in a.split('\\'):
            if(len(i) == 0):
                continue
            if(i[0] == 't'):
                b += '\t'
                if(len(i)>1):
                    b += i[1:]
                continue
            if(i[0] =='n'):
                b += '\n'
                if(len(i)>1):
                    b += i[1:]
                continue
            if(i[0] == 'r'):
                b += '\r'
                if(len(i)>1):
                    b += i[1:]
                continue
            b += i
        return b
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


reload(sys)
sys.setdefaultencoding( "utf-8" )

print "abcde\n\n\n\n\n\n\n\n\n\n\n\n\n"
process.crawl(QuotesSpider)
process.start() # the script will block here until the crawling is finished
