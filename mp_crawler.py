# coding=utf-8
# Goal: parse house information for each district from websites
# for each district, get 「土地區段位置或建物區門牌」,「建物型態」,「建物現況格局」,「坪數」,「屋齡」,「總價元」,「資料來源」into csv file

# Procedure:
# 1. get the number of page for each district by parsing first html content
# 2. for each district put all html page together, use htmlparser to parse content and save data into file

import sys
import math
import urllib
import time
import multiprocessing
from HTMLParser import HTMLParser

cityName = ['TaipeiXinyi', 'TaipeiDaan', 'TaipeiWanhua', "HsinchuCity", "TaichungCity", "KaohsiungCity", "YilanCountry"]

cityToURL = {"TaipeiXinyi" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=1&zip=110&price_min=&price_m\
ax=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search=&page=",
             "TaipeiDaan" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=1&zip=106&price_min=&price_m\
ax=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search=&page=",
             "TaipeiWanhua" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=1&zip=108&price_min=&price_m\
ax=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search=&page=",
             "HsinchuCity" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=6&zip=300%2F300&price_min=&p\
rice_max=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search\
=&page=",
             "TaichungCity" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=10&zip=400%2F439&price_min=&price_max=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search=&page=",
             "KaohsiungCity" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=19&zip=800%2F852&price_min=&\
price_max=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search\
=&page=",
             "YilanCountry" : "https://tw.v2.house.yahoo.com/object_search_result.html?&homes_type=preowned&zone=5&zip=260%2F272&price_min=&p\
rice_max=&area_min=0&area_max=25&preowned_main_type=1&preowned_sub_type=0&preowned_keyword=&homes_search=\
&page="
}


def gethtmlcontent(cityName):
    # get page number
    url = cityToURL[cityName] + '1'
    content = urllib.urlopen(url).read()
    startIndex = content.find('共')
    endIndex = content.find('筆')
    pageNumber = int(math.ceil( float(content[startIndex + 4 : endIndex]) / 10 ))

    # get HtmlContent by concatenate all html page
    htmlContent = ''
    for number in xrange(1, pageNumber+1):
        url = cityToURL[cityName] + (str)(number)
        htmlContent += urllib.urlopen(url).read()
        sys.stdout.write("%s Progress: %d%% \r" % (cityName, number * 100 / pageNumber) )
        sys.stdout.flush()
    return htmlContent

def getvalue(attribute, line):
    startIndex = line.find(attribute) + 9;
    endIndex = line.find(',', startIndex)
    value = line[startIndex : endIndex].strip()
    return value

class parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.tmpdata = ''
        self.inData = False
        self.getData = False

    def handle_data(self, data):
        if self.getData == True and len(data.strip()) > 0:
            self.tmpdata = self.tmpdata + ',' + data.strip()

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and attrs == [('class', 'yui3-u-3-5')]:
            self.inData = True
        if tag == 'div' and attrs == [('class', 'yui3-g provider')]:
            self.inData = False
            self.data.append(self.tmpdata )
            self.tmpdata = ''
        if (tag == 'li' or tag == 'em') and (self.inData == True):
            self.getData = True
        else: self.getData = False

def parsehtmlandsavedata(htmlContent):
    # declare HtmlParser
    hp = parser()
    hp.feed(htmlContent)

    # parsing data and save into file
    for line in hp.data:
        line = line.replace('總價：,', '總價：')
        addr = getvalue('地址', line)
        buildtype = getvalue('類別', line)
        status = getvalue('格局', line)
        area = getvalue('坪數', line)[:-4]
        age = getvalue('屋齡', line)[:-4]
        if(len(age) <= 0): age = '0'
        cost = getvalue('總價', line)[:-4]+ '0000'
        obj = addr + ',' + buildtype + ',' + status + ',' + area + ',' + age + ',' + cost + ',房仲網\n'
        file.write(obj)
    hp.close()


if __name__ == "__main__":
    start_time = time.time()
    print 'Start to Get HtmlContent ... '

    # parallelly get html content
    pool = multiprocessing.Pool(5)
    htmlContents = pool.map(gethtmlcontent, cityName)
    print 'Get HtmlContent is done!!'

    # sequentially parsing and save data into file
    print 'Start to parse HtmlContent and save data into file ...'
    with open("ParseWebsite.csv", 'a') as file:
        for htmlContent in htmlContents:
            parsehtmlandsavedata(htmlContent)

    print 'Everything is done!!'
    print 'Execution time: ' + str(time.time() - start_time)
