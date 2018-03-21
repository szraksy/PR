# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 08:51:05 2018

@author: Sezer
"""

import xmltodict
import csv
import httplib as httpclient
import urllib
import requests
import threading as t

# global result variable
OUTPUT = {"ID":[],"TYPE":[],"VALUE":[]}

Devices = {
    '0' : "Temperature",
    '1' : "Humidity",
    '2' : "Motion",
    '3' : "Alien Presence", 
    '4' : "Dark Matter",}
    
def deserialize(response, type):
    if (type == "Application/json"):
        return response.json()

    elif (type == "Application/xml"):
        return xmltodict.parse(response.text)["device"]

    elif (type == "text/csv"):
        d = {'device_id':[],
             'sensor_type':[],
             'value':[]}
        reader = csv.DictReader(response.text.splitlines())        
        for row in reader:
            for key in row:
                d[key].append(row[key])        
        return d
    
    return "not relevant"
    
def save_data(data,type):
    if (type == "Application/xml"):
        for key in data:
            if key == "@id":
                OUTPUT["ID"].append([data.get(key)])  
            if key == "type":
                OUTPUT["TYPE"].append([data.get(key)])   
            if key == "value":
                OUTPUT["VALUE"].append([data.get(key)])  

    elif (type == "Application/json"):
        for key in data:
            if key == "device_id":
                OUTPUT["ID"].append([data.get(key)])  
            if key == "sensor_type":
                OUTPUT["TYPE"].append([data.get(key)]) 
            if key == "value":
                OUTPUT["VALUE"].append([data.get(key)])  
                
    elif (type == "text/csv"):
        for key in data:
            if key == "device_id":
                OUTPUT["ID"].append(data.get(key))  
            if key == "sensor_type":
                OUTPUT["TYPE"].append(data.get(key)) 
            if key == "value":
                OUTPUT["VALUE"].append(data.get(key)) 
                
    
def format_and_reorder_output():
    #Collecting raw data (list with lists)
    L1 = [item for sublist in OUTPUT["ID"] for item in sublist]
    L2 = [item for sublist in OUTPUT["TYPE"] for item in sublist]
    L3 = [item for sublist in OUTPUT["VALUE"] for item in sublist]
    
    #Storing collected data into a dict
    FINAL = {"ID":L1,"TYPE":L2,"VALUE":L3}
    
    print("\n~~~~ RESULTS ~~~~")
    for i in range(len(Devices)):
        t=0;
        print"\n",Devices[str(i)],": " #device name
        for j in FINAL["TYPE"]:
            if j == str(i) or j==i: #ordering data by device type
                print"Device ",FINAL["ID"][t],"-",FINAL["VALUE"][t]
            t+=1 
            
        
def parallel_t_requests(urls):
    threads = [t.Thread(target=fetch_url, args=(url,)) for url in urls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()        
        
def main_request():
    main_response = requests.post(URL)
    urls_body = main_response.json() 
    urls_header = main_response.headers        
    urls_count = len(urls_body)
    secret_key = urls_header['Session']
   
    secret_key_header = { "Session" : secret_key }
    return urls_body,secret_key_header,urls_count


def refactor_urls(urls_count,urls_body,URL):
    return [(URL+urls_body[i]["path"]) for i in range(urls_count)]    
    
def fetch_url(url):
    print"HTTP request sent!"
    try:
     
        result = requests.get(url, headers=secret_key_header)        
        process_result(result)
     
      

    
    except urllib.error.HTTPError as e:
        print("\n!!! SERVER KEY TIMED OUT!!!")
        print("Or perhaps:",e)      
        retrying = True
    

def process_result(result):

    value_format = result.headers['Content-Type']
    device_body = deserialize(result,value_format)
    save_data(device_body, value_format)
    
    print"\nHTTP Response status:"
    print result.status_code
   


URL_RAW = "desolate-ravine-43301.herokuapp.com"
conn = httpclient.HTTPConnection(URL_RAW)
URL = "http://" + URL_RAW

retrying = True # only once
while(retrying):
    
  
    urls_body,secret_key_header,urls_count = main_request()
    urls = refactor_urls(urls_count,urls_body,URL)
    retrying = False #job considered complete...
    parallel_t_requests(urls)
    if(retrying): #...unless an error requests a retry
        print"\n!!! RETRYING !!!"

        
format_and_reorder_output()    
conn.close()
