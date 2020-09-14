import xml
import mysql
from mysql.connector import Error
from xml.dom import minidom 
import os 
root = minidom.Document()  
xml = root.createElement("All_records")  
root.appendChild(xml)
try:
    conn = mysql.connector.connect(host = "127.0.0.1",port = 3307,database = "explorer_db",user = "root",password = "")
    if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
    cur = conn.cursor()
    table = root.createElement("genre")
    xml.appendChild(table)
    cur.execute("SELECT * FROM genre")
    fields = [i[0] for i in cur.description ]
    #print(fields)
    for row in cur:
        recs = root.createElement("rec")
        table.appendChild(recs)
        for idx,i in enumerate(fields):
            child = root.createElement(i) 
            text = root.createTextNode(str(row[idx]))
            child.appendChild(text)
            recs.appendChild(child)
        recs.appendChild(child)
    #xml_str = root.toprettyxml(indent ="\t")  
    #print(xml_str)
    table = root.createElement("event")
    xml.appendChild(table)    
    cur.execute("SELECT * FROM event")
    fields = [i[0] for i in cur.description ]
    #print(fields)
    for row in cur:
        recs = root.createElement("rec")
        table.appendChild(recs)
        for idx,i in enumerate(fields):
            child = root.createElement(i) 
            text = root.createTextNode(str(row[idx]))
            child.appendChild(text)
            recs.appendChild(child)
        recs.appendChild(child)
    table = root.createElement("links")
    xml.appendChild(table)    
    cur.execute("SELECT * FROM links")
    fields = [i[0] for i in cur.description ]
    #print(fields)
    for row in cur:
        recs = root.createElement("rec")
        table.appendChild(recs)
        for idx,i in enumerate(fields):
            child = root.createElement(i)
            text = root.createTextNode(str(row[idx]))
            child.appendChild(text)
            recs.appendChild(child)
        recs.appendChild(child)
    xml_str = root.toprettyxml(indent ="\t")  
    #print(xml_str) 
    save_path_file = "explorer_db.xml"
  
    with open(save_path_file, "w",encoding = "utf-8") as f: 
        f.write(xml_str) 
    cur.close()
    conn.close()


except Error as e:
        print("Error while connecting to MySQL", e)
