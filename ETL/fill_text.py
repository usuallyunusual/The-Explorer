





"""
TO DO:
2) STORE AS STEMMED VERSION VS NORMAL TEXT (DRAWBACKS AND ADVANTAGES)

"""














import mysql
from mysql.connector import Error
from bs4 import BeautifulSoup

def filltext():
    try:
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        cur = conn.cursor(buffered = True)
        cur2 = conn.cursor(buffered = True) 
        cur.execute('''SELECT event_key,html FROM event WHERE html IS NOT NULL AND error IS NULL AND htext IS NULL''')
        totcount = 0
        for row in cur:
            soup = BeautifulSoup(row[1],'html.parser')
            text = soup.get_text().splitlines()
            text = "\n".join([i for i in text if i!=''])
            pos = text.find("Jump to search")
            pos = pos + len("Jump to search")
            text = text[pos:]
            pos = text.find("Navigation menu")
            text = text[:pos]
            body = ""
            count = 2
            for i in soup('p'):
                if count>=0:
                    body = body+i.get_text().strip()
                    count =  count-1
            title = soup.title.string
            title = title[:-11]
            cur2.execute('''UPDATE event SET event_title = %s,event_text = %s,htext = %s WHERE event_key=%s''',(title,body,text,row[0]))
            totcount+=1
            #print(text)
        conn.commit()
        cur2.close()
        cur.close()
        conn.close()
        print(totcount,'rows.')
        print("Done. Check database")
    except Error as e:
        print("Error while connecting to MySQL", e)


