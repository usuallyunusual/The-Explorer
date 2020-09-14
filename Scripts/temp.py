



"""
TO DO:
1. Lot of edge cases not accounted for
2. Could use some unit testing scripts for sanity check
3. What are the bounds for years?

"""


















import mysql
from mysql.connector import Error
import re
import numpy as np
import 


def reject_outliers(data, m = 6.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]


def tag_year():

    try:
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        cur = conn.cursor(buffered = True)
        cur1 = conn.cursor()
        cur.execute("SELECT event_key,htext FROM event WHERE htext IS NOT NULL AND event_year IS NULL")
        count = 0
        cent = {"first":"1st","second":"2nd","third":"3rd","fourth":"4th","fifth":"5th","sixth":"6th","seventh":"7th","eighth":"8th","ninth":"9th","tenth":"10th",
        "eleventh":"11th","twelfth":"12th","thirteenth":"13th","fourteenth":"14th","fifteenth":"15th",
        "sixteenth":"16th","seventeenth":"17th","eighteenth":"18th","nineteenth":"19th","twentieth":"20th","twentyfirst":"21st"}
        mylist = list()
        for row in cur:
            text = row[1].lower()
            pos = text.find("references[edit]")
            pos2 = text.find("further reading[edit]")
            if pos!=0:
                sub1 = text[:pos]
                sub2 = text[pos2:]
                text = sub1+sub2
            #print(text,"\n\n")
            if "century" in text:
                #print("YES\n\n")
                mylist = re.findall("\d+[a-z][a-z]\s*-*century",text)
                #print(mylist)
                sec_list = re.findall("[f,s,t,e,n][a-z][a-z]+\s*-*century",text)
                #print(sec_list)
                sec_list = [i.replace(i[:i.find(" century")],cent[i[:i.find(" century")]]) for i in sec_list if (i[:i.find(" century")]) in cent]
                mylist = mylist+sec_list
                #print(mylist)
                mylist = [re.sub(r"[a-z][a-z]\s*-*century","00",i) for i in mylist]
                #print(mylist)
            
            years = re.findall('([1][0-9][0-9][0-9])',row[1])
            years2 = re.findall('([2][0-1][0-2][0-9])',row[1])
            years = years+years2 + mylist
            if not years:
                allyear = "NULL"
            else:
                allyear = np.array([int(i) for i in years])
                allyear = reject_outliers(allyear)
            cur1.execute('''UPDATE event set event_year = %s WHERE event_key = %s''',(str(allyear[0]),row[0]))
            #print(allyear)
            print(len(allyear),count)
            count+=1

        conn.commit()
        cur.close()
        cur1.close()
        conn.close()
        print(count,"rows")
        print("Done check database!")
    except Error as e:
            print("Error while connecting to MySQL", e)
