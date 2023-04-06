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
        self.key_words = None
        self.year = None
    
    def get_year(self):
        start = self.text.lower().find("copyright")
        end = start + 20
        self.year = re.findall(r'\d+', text[start:end])[0]
        
    def get_key_words(self):
        for line in clean.split("\n"):
            if "keywords" in line.lower():
                self.key_words = line
    
    def key_words_filter(self, filter_words):
        for word in filter_words:
            if word in self.key_words:
                self.priority += 1
    
    def norm_priority(self):
        self.priority = self.priority % 10

def get_first_n_pubs(query, n):
    """Create a list of dictionaries with the first n publications data"""
    ## Must be done with next() since query is an iterator and 
    ## isn't subscriptable 
    return [next(query) for i in tqdm(range(0, n))]

def get_urls(papers):
    return [paper["pub_url"] for paper in papers]

def read(url):
    wd = webdriver.Chrome()
    wd.get(url)
    text = BeautifulSoup(dr.page_source,"lxml").get_text()
    wd.close()
    return text

## -> lst.sort(key=lambda x: x.priority)

def main():
    
    query = "Antimicrobial Peptide Molecular Dinamics"
    n = 20
    
    search = scholarly.search_pubs("Antimicrobial Peptide Molecular Dinamics")
    
    pubs = get_first_n_pubs(search, n)
    
    urls = get_urls(pubs)
      
    papers = [Paper(url) for url in urls]
    
    for paper in papers:
        paper.text = read(paper.url)


