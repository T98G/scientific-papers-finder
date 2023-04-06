#!/usr/bin/env python3

import argparse
from scholarly import scholarly
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm   

## Going to use object orientation to keep publications data organized
## Not going to make the whole script object oriented though

class Paper:
    def __init__(self, url):
        self.url = url
        self.priority = 0
        self.text = None
        self.keywords = None
        self.year = None
        self.domain = None
        self.period = None

    def read(self):
        """Read contents of a web page and closes the browser"""
        wd = webdriver.Chrome()
        wd.get(self.url)
        text = BeautifulSoup(wd.page_source,"lxml").get_text()
        wd.close()
        self.text = text
    
    def get_year(self):
        start = self.text.lower().find("copyright")
        end = start + 20
        if len(re.findall(r'\d+', self.text[start:end])):
            self.year = int(re.findall(r'\d+', self.text[start:end])[0])

    def in_period(self, period):
        """Filter Paper by time period"""
        if "-" in period:
            period = period.split("-")
        else:
            period = period.split()

        if self.year:
            self.period = ((self.year > int(period[0])) and (self.year < int(period[1])))
        
    def get_keywords(self):
        for line in self.text.split("\n"):
            if "keywords" in line.lower():
                self.keywords = line
    
    def keywords_filter(self, filter_words):
        if self.keywords:
            for word in filter_words:
                if word in self.keywords:
                    self.priority = int(self.priority) + 1
    
    def filter_domains(self, domains):
        """Filter Paper by domain"""
        for domain in domains.split():
            if domain.lower() in self.url:
                self.domain = True

    def norm_priority(self):
        self.priority = int(self.priority) % 10


def get_first_n_pubs(query, n):
    """Create a list of dictionaries with the first n publications data"""
    ## Must be done with next() since query is an iterator and 
    ## isn't subscriptable 
    return [next(query) for i in tqdm(range(0, n))]

def get_urls(papers):
    return [paper["pub_url"] for paper in papers]

def get_arguments():
    """Return the filename and interest group from flags"""
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--query", help="The query you want to search")
    parser.add_argument("-kw", "--keywords", help="The key words of interest")
    parser.add_argument("-n", "--number", help="Maximum number of papers in the output")
    parser.add_argument("-p", "--period", help="The time period to filter for (optional)")
    parser.add_argument("-d", "--domains", help="Filter by domain name (optional)")
    parser.add_argument("-o", "--output", help="Output file name")

    return parser.parse_args()

def make_url_score_output(lst):

    string = ""

    for paper in lst:

        string += f"{paper.url},  {paper.priority}\n\n"

    string = "#url, #score" + string

    return string

def write_output(string, filename):
    """"""
    with open(filename, "w") as f:
        f.write(string)

def main():

    args = get_arguments()

    query = args.query
    keywords = args.keywords
    n = int(args.number)
    filename = args.output

    if args.period:
        period = args.period 
    if args.domains:
        domains = args.domains

    search = scholarly.search_pubs(query)
    
    pubs = get_first_n_pubs(search, n)
    
    urls = get_urls(pubs)

    papers = []

    for url in tqdm(urls):
        try:
             papers.append(Paper(url))
        except Exception as e:
            raise e 
        finally:
            pass
    
    for paper in papers:
        
        try:
            paper.read()
            paper.get_keywords()
            paper.keywords_filter(keywords)

        except Exception as e:
            raise e
        finally:
            pass

    for paper in papers:
        print(paper.url)

    papers = list(filter(lambda x: True if x.text else False, papers))
    papers = list(filter(lambda x: True if x.keywords else False, papers))

    if period:
        for paper in papers:
            try:
                paper.get_year()
                paper.in_period(period)
            except Exception as e:
                raise e
            finally:
                pass

        papers = list(filter(lambda x: True if x.period else False, papers))

    if domains:
        
        for paper in papers:
            try:
                paper.filter_domains(domains)
            except Exception as e:
                raise e
            finally:
                pass

        papers = list(filter(lambda x: True if x.domain else False, papers))

    print(papers)

    papers.sort(key=lambda x: x.priority)

    string = make_url_score_output(papers)

    write_output(string, filename)

if __name__ == '__main__':
    main()