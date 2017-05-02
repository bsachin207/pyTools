# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 17:03:50 2017
This program is made for only THINX
This creates 2 output files in the working directory

Objective: Searches for 'Tampon' products on amazon and analyze reviews of 20 products
for past one year.

Resources: It uses 'Amazon Product Advertising API' You need Access keys and Secret keys.

Output: CSV files containing number of reviews for past 1 year
 
@author: Sachin
"""
from amazonproduct import API
from selenium import webdriver
from ProductInfo import ProductInfo
from datetime import datetime
import time
import socket
from selenium.common.exceptions import NoSuchElementException
import csv
import pandas as pd
socket.setdefaulttimeout(50)


ACCESS_KEY='Enter your Access Key'
SECRET_KEY = 'Enter your key'
TAG = 'Enter your tag'

#To get All reviews
def set_filter_all_review(t):
    for product in t:
        filter_loc = product.all_review_url.find('sortBy=')
        new_url = product.all_review_url[:filter_loc] + 'reviewerType=all_reviews&' + product.all_review_url[filter_loc:]
        product.set_all_review_url(new_url)
    
    return t

#Write a complete file for reviews
def write_all_reviews_CSV(top_20_tampons):
    o = open('AmazonReviewsVerifiedPurchaser.csv','w')
    writer = csv.writer(o)
    writer.writerow(['ASIN','BestSellerRank','Name','ReviewDate'])
    for p in top_20_tampons:
        itr = []
        for date in p.review_dates:
           itr.append([p.ASIN, p.best_seller_rank, p.name, date])

        writer.writerows(itr)

    o.close()


def write_reviews_per_month(top_20_tampons):
    df = pd.read_csv('AmazonReviewsVerifiedPurchaser.csv',usecols=[0,1,2,3],parse_dates=[3])
    df['ReviewDate'] = df.ReviewDate.apply(lambda x: str(x)[:7])
    df['Name'] = df.Name.apply(lambda x: str(x)[:30])
    df['ASIN'] = df.ASIN + ' - ' + df.BestSellerRank.astype(str)+' - ' + df.Name
    del df['Name']
    del df['BestSellerRank']
    
    per_month = df.groupby(['ASIN',df.ReviewDate]).size().unstack('ASIN').fillna(0)
    
    #for last 12 months
    per_month = per_month[-12:]
    per_month.to_csv('PerMonthReviews.csv')
    

def main():
    api = API(locale='us',access_key_id=ACCESS_KEY,secret_access_key=SECRET_KEY,associate_tag=TAG)
    #Create List of Tampon Products from Amazon
    tampon_items = []
    response = api.item_search('HealthPersonalCare', Keywords='Tampons',ResponseGroup="Large, Reviews")
    for i in response:
        if hasattr(i,'SalesRank'):
            product = ProductInfo()
            product.set_ASIN(i.ASIN)
            product.set_best_seller_rank(int(i.SalesRank))
            product.set_name(i.ItemAttributes.Title.text)
            product.set_review_iframe_url(i.CustomerReviews.IFrameURL)
            tampon_items.append(product)
    
    #Take top 22 products for fetching reviews        
    top_20_tampons = tampon_items[:22]
    
    #Open a Browser to get all the reviews (Dynamic Page Loading Amazon)
    browser=webdriver.Chrome()
    
    #Get link for all reciews from review Iframe
    for product in top_20_tampons:
        browser.get(product.review_iframe_url)
        x = browser.find_elements_by_class_name('small')
        if x:
            x = x[0].find_element_by_tag_name('a').get_attribute('href')
            product.set_all_review_url(str(x))
    
    browser.close()
   
    #filter out the product whose reviews are not present
    top_20_tampons = [product for product in top_20_tampons if product.all_review_url]
    
    '''
    Filter to reviews by "all reviews" otherwise scrap only 'Verified Purchaser Reviews'
    #top_20_tampons = set_filter_all_review(top_20_tampons)
    '''
    
    #Scan for all reviews
    socket.setdefaulttimeout(50)
    brow = webdriver.Chrome()
    brow.set_page_load_timeout(30)
    for product in top_20_tampons:
        time.sleep(5)
        brow.get(str(product.all_review_url))
        valid = True
        #Do it till all the previous 1 year reviews are scraped
        while valid:
            while True:
                try:
                    x = brow.find_element_by_id('cm_cr-review_list')
                    break
                except NoSuchElementException:
                    print 'Excpetion'
            
            #get all reviews for the product from that page        
            dt = [str(i.text)[3:] for i in x.find_elements_by_class_name('review-date')]
            dt = map(lambda x: datetime.strptime(x.replace(',', ''), '%B %d %Y'), dt)
            
            # setting review dates into product and Checking
            product.review_dates.extend(dt)    
            
            #Check of last reiew on the page is 1 year old        
            if (datetime.now()-dt[-1]).days > 365:
                valid = False
            # Goto next page to get more reviews
            else:
                if len(dt)==10:
                    last_button = brow.find_element_by_class_name("a-last")
                    next_page_url = last_button.find_element_by_tag_name('a').get_attribute('href')
                    print next_page_url            
                    brow.get(str(next_page_url))
                else:
                    valid = False
    
    brow.close()
    
    #Write a complete file for reviews
    write_all_reviews_CSV(top_20_tampons)
    
    #Write reviews per month per product for plottring and analysis
    write_reviews_per_month(top_20_tampons)
    



if __name__ == "__main__": 
    main()
    