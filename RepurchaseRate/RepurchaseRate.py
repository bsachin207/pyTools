# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:45:36 2017

@author: Sachin
"""
import pandas as pd
from pandas.tseries.offsets import *
from dateutil.relativedelta import relativedelta, MO
import matplotlib.pyplot as plt
import os


REPURCHASE_WINDOW = 20

#Function to calculate Repurchase Rate
def calculate_repurchase(order,s_date, e_date):
    temp = order[(order.Paidat >= s_date) & (order.Paidat < e_date)]
    returning_cust = temp[order.repurchase == 1]["Email"].nunique()
    rate = returning_cust/float(temp["Email"].nunique())
    del temp
    return rate*100

def create_data(dir_path):
    csv_files = [f for f in os.listdir(dir_path) if f[-3:] == 'csv']
    data_list = []
    for data_file in csv_files:
        ordr1 = pd.read_csv(os.path.join(dir_path,data_file),
                           usecols=[1,2,3,4,16,20],
                            names=["Email","Finance","Paidat","Status", "quantity","sku"]
                            ,low_memory=False)

        data_list.append(ordr1[(ordr1.Status=="fulfilled") & (ordr1.Finance=="paid")])

    order_data = pd.concat(data_list)
    return order_data    

if __name__ == '__main__':
        
    input_path = raw_input("Please enter data directory path:")
    #Conbine all the data
    order = create_data(input_path)
    #Cleaning the date (Assumption - PaidAt is purchase date)
    order = order[order.Paidat.notnull()]
    order.Paidat=pd.to_datetime(pd.Series(order.Paidat))
    #reformatting columns
    order=order.sort_values(["Email","Paidat"]).reset_index(drop=True)
    #calculating difference between the purchases made by each user 
    order["difference"]=order.groupby("Email")["Paidat"].diff(-1).fillna(0).dt.days
    
    #calculating start week from Monday and end week as next to max date
    start_date = min(order.Paidat) + relativedelta(weekday=MO(-1))
    end_date = max(order.Paidat) + relativedelta(days=-20)
    week_range = pd.date_range(start=start_date,end=end_date,freq='7D',normalize=True)
    order["repurchase"]=order.difference.apply(lambda x: 0 if x==0 else 1 if abs(x)-REPURCHASE_WINDOW <= 0 else 0)
    
    #calculate repurchase rate
    repurchase_rate = []
    for i in range(len(week_range)-1):
        repurchase_rate.append(calculate_repurchase(order,week_range[i],week_range[i+1]))
     
    #plot a required graph   
    plt.plot(week_range[:-1],repurchase_rate)
    plt.ylabel('Repurchase Rate')
    plt.xlabel('Week Starting date')
    plt.show()




