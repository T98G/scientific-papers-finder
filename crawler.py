#!/usr/bin/env python3

##The scholar crawler v 1.0
# It's as elegant as a drunk elephant 

import argparse
from scholarly import scholarly
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
        """Get publication url from publication data"""
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
            if "keywords" in line.lower(): ##Find line with "Keywords in it" yes super junkie
                self.keywords = line
    
    def keywords_filter(self, filter_words):
        """Assign a score to publication based on the presence of keywords"""
        if self.keywords:
            for word in filter_words:
                if re.findall(word.lower(), self.keywords):
                    self.priority = int(self.priority) + 1
    
    def filter_domains(self, domains):
        """Filter Paper by domain"""
        for domain in domains.split():
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
        """Makes sure publication score is within 0 to 10 range"""
        self.priority = int(self.priority) % 10


def get_first_n_pubs(query, n):
    """Create a list of dictionaries with the first n publications data"""
    ## Must be done with next() since query is an iterator and 
    ## isn't subscriptable 
    return [next(query) for i in tqdm(range(0, n))]


def get_arguments():
    """Return the query filter parameters and output name from comandline arguments"""
    
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

    """Converts the publications urls and scores into a string that can be written in the output file"""

    string = ""

    for paper in lst:

        string += f"{paper.url},  {paper.priority}\n\n"

    string = "#url, #score\n" + string

    return string

def write_output(string, filename):
    """Writes data into a file"""
    with open(filename, "w") as f:
        f.write(string)

def main():

    args = get_arguments()

    query = args.query #the query string
    keywords = args.keywords # keywords to refine the search
    n = int(args.number) #maximum number of publications to search
    filename = args.output #output file name

    if args.period: ##Check if the -p flag was use
        period = args.period 
    if args.domains: ##Check if the -d flag was used 
        domains = args.domains
    if args.citations: ##Check if the -c flag was used
        citations = args.citations

    ## Init a query object from scholarly
    search = scholarly.search_pubs(query) 
    
    ## Iterates getting the first n publications data
    pubs = get_first_n_pubs(search, n)

    papers = [] ## Publications which were treated will be from now on regarded as papers


    for pub in tqdm(pubs):
        try:
             papers.append(Paper(pub)) ## Initialize a Paper type object for every publication
        except Exception as e:
            raise e 
        finally:
            pass
    
    for paper in papers:
        
        try:
            paper.get_url() ## Get the publication url for a Paper object
            paper.read() ## Read the webpage content
            paper.get_keywords() ## Get the key words from the web page content
            paper.keywords_filter(keywords) ##Assign a score to the publication 

        except Exception as e:
            raise e
        finally:
            pass

    ##Filters the publications making sure there is a text conten
    papers = list(filter(lambda x: True if x.text else False, papers))
    ##Filters the publications making sure they have the correct keywords
    papers = list(filter(lambda x: True if x.keywords else False, papers))

    if period:    ## If flag -p was used
        for paper in papers:
            try:
                paper.get_year() #get publication year
                paper.in_period(period) # check if the publication year is within the time interval
            except Exception as e:
                raise e
            finally:
                pass

        #Filter the publications that are in the time interval set by the user 
        papers = list(filter(lambda x: True if x.period else False, papers))

    if domains: ## If Domains is not None filter publications by domains
        
        for paper in papers:
            try:
                paper.filter_domains(domains) ##Checks if the publication url is a domain specified by the user
            except Exception as e:
                raise e
            finally:
                pass
        ## Filters the Papers based by if their url domain is in the user suplied input
        papers = list(filter(lambda x: True if x.domain else False, papers))

    if citations: ## if -c flag was used

        for paper in papers:
            try:
                paper.get_citations() #Get citations from publication data
                paper.filter_citations(citations) ## Checks if publication has minimum number of citations
            except Exception as e:
                raise e
            finally:
                pass
        ## Filters the publications by if they have the minimum number of citations
        papers = list(filter(lambda x: True if x.minim_citations else False, papers))

    #Sort the papers by their score
    papers.sort(key=lambda x: x.priority)

    #Make data into a string that can be written to the output file
    string = make_url_score_output(papers)

    #writes data to an output file
    write_output(string, filename)

if __name__ == '__main__':
    main()