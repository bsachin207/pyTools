# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 00:35:39 2017
@author: Sachin Badgujar

Objective: Scrap the career web pages and find out matching jobs with the 
provided resume.

Description:
This is program is made for learning and demo purpose. Currently, the program 
supports only Citadel career page. This script is made for python 2.7 only. 
The script is neither optomized nor intelligent in terms of finding matches.

Please note this is just for a demo purpose.

Credits:
BeautifulSoup, NTLK  and of course ME !

Please feel free to provide any suggestion or modifications.
"""

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk, string
from collections import defaultdict

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

#remove punctuation, lowercase, stem
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


#Main function for the processing of resume
def main():    
    #URL of Career page of CITADEL
    req = requests.get("https://www.citadel.com/careers/open-positions/")

    #scapping the web pages - Strictly for Citadel    
    soup = BeautifulSoup(req.content,"lxml")
    the_article = soup.findAll("article")
    if the_article:
       postings = the_article[0].findAll("a",href=True)
       position_links = [(x.text, "http:" + x['href']) for x in postings]
    
    #path for the resume
    resume_path = "Resume.txt"
    while(True):
        f = open(resume_path)
        resume = ''
        for line in f:
            resume += line.decode('unicode_escape').encode('ascii','ignore')
        
        #Job matching based on cosine similarity
        job_matching = defaultdict(list)
        for k,v in position_links:
           req = requests.get(v)
           soup = BeautifulSoup(req.content,"lxml")
           the_article = soup.findAll("article")[0].text
           job_matching[int(cosine_sim(resume,the_article)*100)].append(k)
        
        #print the matching positions. You can change this
        print "The top positions matched for current resume: "
        
        for items in sorted(job_matching,reverse=True)[:2]:
            for job in job_matching[items]:
                print " > ",job.encode('ascii','ignore')
        
        user_input = raw_input("Please enter loaction of another text resume "\
        "without quotes or 0 to exit:")
        if user_input == '0':
            break;
        else:
            resume_path = user_input

if __name__ == "__main__":
    main()