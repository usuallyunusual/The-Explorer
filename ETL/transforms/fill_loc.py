




"""
To DO:
1.Location accuracy is horrible
2.Need State lookup data to narrow down the search
3.Observe and correct process is required.
4. fuzzywuzzy.process is not doing a great job with country classification
5. Use the heirarchcal structure of the data

"""














#!/usr/bin/env python
# coding: utf-8



import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz,process
import geolocation
import mysql
from mysql.connector import Error




def tag_loc():
    id = list()
    name = list()
    lat = list()
    long = list()
    pop = list()
    code = list()
    fh = open("../lookup/cities15000.txt", "r", encoding ="utf-8")
    count = 0
    for line in fh:
        t = line.split("\t")
        id.append(t[0])
        name.append(t[2])
        lat.append(t[4])
        long.append(t[5])
        pop.append(t[14])
        code.append(t[8])
    assert len(id)==len(name)== len(lat) ==len(long) ==len(pop) ==len(code)
    cities = pd.DataFrame(list(zip(id,name,lat,long,pop,code)),columns = ["id",
        "name","lat","long","pop","code"])
    len(cities)
    def lname(x):
        return len(x)
    cities["len"] = cities["name"].apply(lname)
    cities["len"].min()
    cities = cities.drop((cities.loc[cities["len"]==0].index.tolist()))
    cities = cities.drop((cities.loc[cities["len"]==2].index.tolist()))
    Countries = pd.read_csv("../lookup/allCountries.csv")
    Countries.head()
    #pre_words = ["at","of","in","the","University","College"]
    #post_words = ["campaign"]
    try:
        conn = mysql.connector.connect(host = "127.0.0.1",port = 3307,database = "explorer_db",user = "root",password = "")
        cur = conn.cursor(buffered = True)
        cur1 = conn.cursor()
        maincount = 0
        cur.execute("SELECT event_key,url,htext FROM event WHERE htext IS NOT NULL AND error IS NULL AND event_location IS NULL")
        for row in cur:
            print(row[0],row[1],end = ' ')
            main_text = row[2]
            main_text = re.sub(r"British\s","Britain",main_text)
            main_text = re.sub(r"United\sStates","America",main_text)
            main_text = re.sub(r"\s[U][S]\s","United States of America",main_text)
            main_text = re.sub(r"\s[U][K]\s","United Kingdom",main_text)
            split_pos = row[2].split()
            loc = None
            sims = 0
            count = 0
            for word in range(len(split_pos)):
                if len(split_pos[word])<4:continue
                temp = process.extractOne(split_pos[word],Countries["Country"])
                j = word
                possible = split_pos[j]
                while j+1<len(split_pos) and temp[1] < process.extractOne((possible+" "+split_pos[j+1]),Countries["Country"])[1]:
                    temp = process.extractOne(possible+" "+split_pos[j+1],Countries["Country"])
                    possible+=" "+split_pos[j+1]
                    j+=1 if (j+2)<len(split_pos) else 0
                if temp[1]>= 90:
                    #print("Pos:",possible)
                    if temp[1] > sims:
                        loc = Countries.loc[temp[2]]["Country"]
                        lat = Countries.loc[temp[2]]["lat"]
                        long = Countries.loc[temp[2]]["long"]
                        con = Countries.loc[temp[2]]["code"]
                        sims = temp[1]
                    if count>4:
                        break
                    count+=1
            if loc != None:
                temp = cities[cities["code"]==con]
                #print(loc)
            else:
                temp = cities
            for word in range(len(split_pos)):
                if len(split_pos[word])<=2:continue
                if temp.loc[temp["name"] == split_pos[word]].index.tolist():
                    #if re.match("\d\d\d\d",split_pos[word+1]):continue
                    #if split_pos[word-1] not in pre_words:continue
                    #if split_pos[word+1] in post_words:continue
                    location = split_pos[word]
                    if(temp.loc[cities["name"] == (split_pos[word]+" "+split_pos[word+1])].index.tolist()):
                                  location = split_pos[word]+" "+split_pos(word+1)
                    #print(" ".join(split_pos[word-2:word+2]))
                    loc = temp.loc[cities["name"] == location].sort_values(by = ["pop"],ascending = False).iloc[0]["name"]
                    lat = temp.loc[cities["name"] == location].sort_values(by = ["pop"],ascending = False).iloc[0]["lat"]
                    long = temp.loc[cities["name"] == location].sort_values(by = ["pop"],ascending = False).iloc[0]["long"]
                    break
            print(loc)
            cur1.execute("UPDATE event SET event_lat = %s, event_long = %s, event_location = %s WHERE event_key = %s",(str(lat),str(long),loc,row[0]))
            maincount+=1
            if maincount%100==0:
                conn.commit()
        conn.commit()
        cur.close()
        cur1.close()
        conn.close()
        print(maincount,"rows")
        print("Done!. Check database")
    except Error as e:
        print("error",e)

            

