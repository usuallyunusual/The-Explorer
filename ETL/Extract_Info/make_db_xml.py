
import mysql
from mysql.connector import Error
import xml.etree.ElementTree as ET
import os 

text = open("explorer_db.xml","r",encoding = "utf-8").read() 
try:
    conn = mysql.connector.connect(host = "127.0.0.1",port = 3307,database = "explorer_db",user = "root",password = "")
    if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
    cur = conn.cursor()
    tree = ET.fromstring(text)
    genre = tree.findall("./genre/rec")
    for i in range(len(genre)):
        cur.execute("INSERT INTO genre( genre_id , genre_text ) VALUES ( %s , %s )",
            (int(genre[i][0].text),genre[i][1].text))
    print("Done with genre")
    events = tree.findall("./event/rec")
    for i in range(len(events)):
        for j in range(14):
            events[i][j].text = events[i][j].text if events[i][j].text!='None' else None
        #print(events[i][0].text,flush = True)
        cur.execute("""
            INSERT INTO event
            (event_key, event_title, event_text, event_year, event_genre, event_lat, event_long, event_location, url, html, error, old_rank, new_rank, htext)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (int(events[i][0].text),events[i][1].text,events[i][2].text,events[i][3].text,events[i][4].text,events[i][5].text,events[i][6].text,
                events[i][7].text,events[i][8].text,events[i][9].text,events[i][10].text,events[i][11].text,events[i][12].text,events[i][13].text))
    print("Done with event")
    links = tree.findall("./links/rec")
    for i in range(len(links)):
        cur.execute("INSERT INTO links( from_id , to_id ) VALUES ( %s , %s )",
            (int(links[i][0].text),int(links[i][1].text)))
    print("Done with Links")
    conn.commit()
    print("Done with commit. Check database")
    cur.close()
    conn.close()
except Error as e:
        print("Error while connecting to MySQL", e)