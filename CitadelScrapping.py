# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 00:35:39 2017

@author: Sachin
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

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


f = open("Resume.txt")
resume = ''
for line in f:
    #resume += line.decode('unicode_escape').encode('ascii','ignore')
    resume += line



req = requests.get("https://www.citadel.com/careers/open-positions/")
soup = BeautifulSoup(req.content)
the_article = soup.findAll("article")
if the_article:
   postings = the_article[0].findAll("a",href=True)
   position_links = [(x.text, "http:" + x['href']) for x in postings]

job_matching = defaultdict(list)
for k,v in position_links:
   #print k+'*******************'
   req = requests.get(v)
   soup = BeautifulSoup(req.content)
   the_article = soup.findAll("article")[0].text
   job_matching[int(cosine_sim(resume,the_article)*100)].append(k)

print job_matching