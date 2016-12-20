from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import datetime
import glob, os
import argparse
import sys
import pdb

""" This utility scans finwiz.com for the list of stocks of best industries """

class ListGenerator():
    def __init__(self, perf):
        self.pages = set()
        self.internal_pages = set()
        self.start_perf = perf

    def getTitle(self, url):
        try:
            html = urlopen(url)
        except HTTPError as e:
            return None
        try:
            bsObj = BeautifulSoup(html.read(), "html.parser")
            title = bsObj.body.h1
        except AttributeError as e:
            return title

    def getBSoapObj(self, url):
        html = urlopen(url)
        bsObj = BeautifulSoup(html, "html.parser")
        return bsObj

    def getSpyPerfQuarter(self):
        bsObj = self.getBSoapObj(
                "http://finviz.com/quote.ashx?t=SPY")
        td = bsObj.find("td",text=re.compile("Perf Quarter"))
        if td.next_sibling:
            return float(td.next_sibling.get_text()[0:-1])
        else:
            return None

    def getGroupLinkList(self):
        spy_perf = self.getSpyPerfQuarter()
        print("SPY quarter performance is :{0}%".format(spy_perf))
        bsObj = self.getBSoapObj(
                "http://finviz.com/groups.ashx?g=industry&v=140&o=-perf1w")
        for table in  bsObj.findAll("table"):
            #trObj = table.findAll("tr",{"class":"table-light-row-cp"})
            trObj = table.findAll("tr", {"class":re.compile("(row-cp)")})
            for tr in trObj:
                tdObj = tr.findAll("span")
                if tdObj:
                    perf = tdObj[0].get_text()
                    float_perf =  perf.split("%", 1)

                    # All the groups that outperform SPY by certain amount
                    if float(float_perf[0]) > self.start_perf:
                        str_url = (tr.attrs['onclick']).split("=", 1)
                        full_url = "http://finviz.com/" + str(str_url[1][1:-1])
                        self.pages.add(full_url)
    
    def scanInternalLinks(self ,url):
        """ Goes through current url and gets next linked url """
        bsObj = getBSoapObj(url)
        objLinks = bsObj.findAll("a",
                {"href":re.compile("^(screener.ashx)"), "class":"screener-pages"})
        for link in objLinks:
            if link.parent:
                current_page = link.parent.find("b", text=re.compile("^[0-9]+$"))
                page_str = current_page.getText()
                link_str = link.getText()
                current_body = int(page_str)
                link_body = int(link_str)
                if link_body > current_body:
                    return "http://finviz.com/" + link.attrs['href']
            else:
                return None

    def scanInternalRecLinks(self, url):
        """ Goes through current url and gets next linked url """
        bsObj = self.getBSoapObj(url)
        objLinks = bsObj.findAll("a",
                {"href":re.compile("^(screener.ashx)"), "class":"screener-pages"})
        for link in objLinks:
            if link.parent:
                current_body = int(link.parent.find("b",
                    text=re.compile("^[0-9]+$")).getText())
                link_body = int(link.getText())
                print("current_body :", current_body)
                print("link_body :", link_body)
                if link_body > current_body:
                    print("current_body :", current_body)
                    print("link_body :", link_body)
                    url_found = "http://finviz.com/" + link.attrs['href']
                    print("Url found:" + url_found)
                    if url_found not in self.internal_pages:
                        self.internal_pages.add(url_found)
                        self.scanInternalRecLinks(url_found)

    def generateStockList(self):
        self.getGroupLinkList()
        for link in self.pages:
            self.scanInternalRecLinks(link)
        self.pages.update(self.internal_pages)

    def saveStockList(self):
        now = datetime.datetime.now()
        file_path = "../../../TradingData/" + "scan_{:d}{:d}{:d}.tls".format(now.year, now.month, now.day)
        files = glob.glob("../../../TradingData/*.tls")

        for f in files:
            os.remove(f)

        print("Start writing to a file")
        with open(file_path, 'w') as f_obj:
            for url in self.pages:
                bsObj = self.getBSoapObj(url)
                objLinks = bsObj.findAll("a",{"class":"screener-link-primary"})
                for ticker in objLinks:
                    f_obj.write(ticker.getText() + "\n")
            f_obj.write("SPY\n")
        print("End writing to a file")


    def run(self):
        self.generateStockList()
        self.saveStockList()


def check_arg(args=None):
     parser = argparse.ArgumentParser(description=
             'Screening Tasks.')

     parser.add_argument('-l', '--limit',
             nargs=1,
             help='Create list of stocks of strongest weekly industries -l limit_percentage')

     results = parser.parse_args(args)

     return results.limit

def main():
    screen = check_arg(sys.argv[1:])
    if screen:
        generator = ListGenerator(int(screen[0]))
        generator.run()

if __name__ == '__main__':
    main()
