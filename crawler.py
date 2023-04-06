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
    def __init__(self, pub):
        self.pub = pub
        self.url = None
        self.priority = 0
        self.text = None
        self.keywords = None
        self.year = None
        self.domain = None
        self.period = None
        self.citations = None
        self.minim_citations = None

    def read(self):
        """Read contents of a web page and closes the browser"""
        wd = webdriver.Chrome()
        wd.get(self.url)
        text = BeautifulSoup(wd.page_source,"lxml").get_text()
        wd.close()
        self.text = text

    def get_url(self):
        self.url = self.pub["pub_url"] 
    
    def get_year(self):
        """Get publication year from the copyright"""
        self.year = int(self.pub["bib"]["pub_year"])

    def in_period(self, period):
        """Filter Paper by time period"""
        if "-" in period:
            period = period.split("-")
        else:
            period = period.split()

        if self.year:
            self.period = ((self.year > int(period[0])) and (self.year < int(period[1])))
        
    def get_keywords(self):
        """Get keywords from the publication text"""
        for line in self.text.split("\n"):
            if "keywords" in line.lower():
                self.keywords = line
    
    def keywords_filter(self, filter_words):
        if self.keywords:
            for word in filter_words:
                if re.findall(word.lower(), self.keywords):
                    self.priority = int(self.priority) + 1
    
    def filter_domains(self, domains):
        """Filter Paper by domain"""
        print(domains.split())
        for domain in domains.split():
            print(domain)
            print(re.findall(domain.lower(), self.url))
            if re.findall(domain.lower(), self.url):
                self.domain = re.findall(domain.lower(), self.url)[0]

    def get_citations(self):
        """get the number of citations from scholarly data"""
        if self.pub["num_citations"]:
            self.citations = int(self.pub["num_citations"])

    def filter_citations(self, citations):
        """Return if the number of the citations is igual or grater than the minimum"""
        self.minim_citations = (self.citations >= int(citations))

    def norm_priority(self):
        self.priority = int(self.priority) % 10


def get_first_n_pubs(query, n):
    """Create a list of dictionaries with the first n publications data"""
    ## Must be done with next() since query is an iterator and 
    ## isn't subscriptable 
    return [next(query) for i in tqdm(range(0, n))]


def get_arguments():
    """Return the filename and interest group from flags"""
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--query", help="The query you want to search")
    parser.add_argument("-kw", "--keywords", help="The key words of interest")
    parser.add_argument("-n", "--number", help="Maximum number of papers in the output")
    parser.add_argument("-p", "--period", help="The time period to filter for (optional)")
    parser.add_argument("-d", "--domains", help="Filter by domain name (optional)")
    parser.add_argument("-c", "--citations", help="number of citations(optional)")
    parser.add_argument("-o", "--output", help="Output file name")

    return parser.parse_args()

def make_url_score_output(lst):

    string = ""

    for paper in lst:

        string += f"{paper.url},  {paper.priority}\n\n"

    string = "#url, #score\n" + string

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
    if args.citations:
        citations = args.citations

    search = scholarly.search_pubs(query)
    
    pubs = get_first_n_pubs(search, n)

    papers = []

    print(pubs[0]["pub_url"])

    for pub in tqdm(pubs):
        try:
             papers.append(Paper(pub))
        except Exception as e:
            raise e 
        finally:
            pass
    
    for paper in papers:
        
        try:
            paper.get_url()
            paper.read()
            paper.get_keywords()
            paper.keywords_filter(keywords)

        except Exception as e:
            raise e
        finally:
            pass

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
                print(domains)
                paper.filter_domains(domains)
            except Exception as e:
                raise e
            finally:
                pass

        papers = list(filter(lambda x: True if x.domain else False, papers))

    if citations:

        for paper in papers:
            try:
                paper.get_citations()
                paper.filter_citations(citations)
            except Exception as e:
                raise e
            finally:
                pass

        papers = list(filter(lambda x: True if x.minim_citations else False, papers))

    papers.sort(key=lambda x: x.priority)

    string = make_url_score_output(papers)

    write_output(string, filename)

if __name__ == '__main__':
    main()