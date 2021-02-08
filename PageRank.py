# homework 3
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated cs525.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import cs525
import re
import requests
import numpy as np
from urllib.parse import urljoin
from collections import defaultdict

import bs4 as BeautifulSoup  # you will want this for parsing html documents


# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

class PageRankIndex(object):
    def __init__(self):
        # you'll want to create something here to hold your index, and other
        # necessary data members
        self.index_url_dict = {}
        self._documents = []
        self._inverted_index = {}

    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at
    def index_url(self, url):
        # ADD CODE HERE
        req = requests.get(url)
        data = BeautifulSoup.BeautifulSoup(req.text, "lxml")
            
        children = data.find_all("a")
        self.all_url = [ child.get("href") for child in children]
        i = 0
        n = len(self.all_url)
        self._inverted_index = defaultdict(list)
        while(i < n):
            if self.all_url[i] not in self.index_url_dict:
                
                
                url_i = urljoin(url, children[i].string)
                                
                req_i = requests.get(url_i)
                data_i = BeautifulSoup.BeautifulSoup(req_i.text, "lxml")
                children_i = data_i.find_all("a")
                
                text_i = str(data_i.find_all(text=True)[-1])
                
                text_i = re.split('[^a-zA-Z0-9]', text_i)    
                
                

                token_s = []                
                for j in range(len(text_i)): 
                    tokens = self.tokenize(text_i[j])
                    token_s.append(tokens)
               
                for idx, text in enumerate(token_s):
                    self._inverted_index[text[0]].append(i)
                
                for Key in (self._inverted_index):
                    self._inverted_index[Key] = list(set(self._inverted_index[Key]))
            
            
                self.index_url_dict[self.all_url[i]] = [child.get("href") for child in children_i]
                
            i += 1
            
        self.mapped_url = {}
        
        for i, url in enumerate(self.all_url):          
            self.mapped_url[url] = i 
    
        n = len(self.mapped_url)
        transition_matrix = np.zeros((n,n))
        teleporting_matrix = np.full((n, n), 1/n)
        
        for key in self.index_url_dict:
            for value in self.index_url_dict[key]:
                transition_matrix[self.mapped_url[key]][self.mapped_url[value]] = 1
        
        transition_matrix = transition_matrix/ np.sum(transition_matrix, axis = 1, keepdims = True)
        
        alpha = 0.9      
        self.P = (alpha * transition_matrix) + ((1 - alpha) * teleporting_matrix)      
        self.x = np.full((1,n), 1/n)
        
        while(True):
            a = np.dot(self.x, self.P)
            if np.linalg.norm(a-self.x) < 1e-8:
                break
            else:
                self.x = a
        
        num_files_indexed = len(self._documents)
                
        return  num_files_indexed                
        
    
    
    # tokenize( text )
    # purpose: convert a string of terms into a list of terms 
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        # ADD CODE HERE
        text = text.lower()
        tokens = re.split('[^a-zA-Z0-9]', text)   
        return tokens

    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        # ADD CODE HERE
        query_tokens = self.tokenize(text)
        token_url = set(range(len(self.all_url)))
        
        for token in query_tokens:
#            print(self._inverted_index[token])
            if token in self._inverted_index:
                token_url = token_url & set(self._inverted_index[token])
                
        token_url = list(token_url)
#        print(token_url)
        
        page_name = []
        score = []
        
        for url in token_url:
            score.append(self.x[:, url])      
            page_name.append(self.all_url[url])
#        print('\n')
        top_10 = sorted(list(zip(page_name, score)), reverse=True)[:10]
        top_10_pages = list(map(lambda x : (x[0], x[1][0]), top_10))
        
        return top_10_pages
        

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    index = PageRankIndex()
    url = 'http://web.cs.wpi.edu/~kmlee/cs525/new10/index.html'
    num_files = index.index_url(url)
    search_queries = (
       'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        )
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

I = PageRankIndex()
r = I.index_url('http://web.cs.wpi.edu/~kmlee/cs525/new10/index.html')
