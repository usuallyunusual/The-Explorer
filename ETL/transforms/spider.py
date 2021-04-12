import ssl
import time
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen

import mysql
from bs4 import BeautifulSoup
from mysql.connector import Error

import fill_genre
import fill_loc
# Custom imports.
import fill_text
import fill_year
import sprank

# from MySQLdb import _mysql
# import pymysql

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    conn = mysql.connector.connect(host='127.0.0.1', port=3307, database='explorer_db', user='root', password='')
    if conn.is_connected():
        print("Connection successful: ", conn.get_server_info())
    cur = conn.cursor()

    # Check to see if we are already in progress...
    cur.execute('SELECT event_key,url FROM event WHERE html is NULL and error is NULL LIMIT 1')
    row = cur.fetchone()
    if row is not None:
        print("Restarting existing crawl.  Remove data from database to start a fresh crawl.")
    else:
        starturl = input('Enter web url or enter: ')
        if (len(starturl) < 1): starturl = 'https://en.wikipedia.org/'
        if (starturl.endswith('/')): starturl = starturl[:-1]
        web = starturl
        if (starturl.endswith('.htm') or starturl.endswith('.html')):
            pos = starturl.rfind('/')
            web = starturl[:pos]

        if (len(web) > 1):
            cur.execute('INSERT IGNORE INTO webs (url) VALUES ( %s )', (web,))
            cur.execute \
                    (
                    'INSERT IGNORE INTO event (event_text,event_year,event_genre,event_lat,event_long,event_location,url, html,error,old_rank,new_rank,htext) VALUES ( NULL,NULL,NULL,NULL,NULL,NULL,%s, NULL,NULL,NULL, 1.0,NULL )',
                    (starturl,))
            conn.commit()

    # Get the current webs
    cur.execute('''SELECT url FROM webs''')
    webs = list()
    for row in cur:
        webs.append(str(row[0]))

    print(webs)
    many = 0
    counts = list()
    while True:
        if (many < 1):
            sval = input('How many pages:')
            if (len(sval) < 1): break
            many = int(sval)
        many = many - 1

        tic = time.perf_counter()
        cur.execute('SELECT event_key,url FROM event WHERE html is NULL and error is NULL LIMIT 1')
        try:
            row = cur.fetchone()
            # print row
            fromid = row[0]
            url = row[1]
        except:
            print('No unretrieved HTML pages found')
            many = 0
            break

        print(fromid, url, end=' ')

        # If we are retrieving this page, there should be no links from it
        cur.execute('DELETE from links WHERE from_id=%s', (fromid,))
        try:
            document = urlopen(url, context=ctx)

            html = document.read()
            if document.getcode() != 200:
                print("Error on page: ", document.getcode())
                cur.execute('UPDATE event SET error=%s WHERE url=%s', (document.getcode(), url))

            if 'text/html' != document.info().get_content_type():
                print("Ignore non text/html page")
                cur.execute('DELETE FROM event WHERE url=%s', (url,))
                conn.commit()
                continue

            print('( ' + str(len(html)) + ')', end=' ')

            soup = BeautifulSoup(html, "html.parser")
        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break
        except:
            print("Unable to retrieve or parse page")
            cur.execute('UPDATE event SET error=-1 WHERE url=%s', (url,))
            conn.commit()
            continue

        cur.execute('INSERT IGNORE INTO event (url, html, new_rank) VALUES ( %s, NULL, 1.0 )', (url,))
        # print("\n",cur.lastrowid)
        cur.execute('UPDATE event SET html=%s WHERE url=%s', (html, url))
        # conn.commit()

        # Retrieve all of the anchor tags
        tags = soup('a')
        count = 0
        for tag in tags:
            href = tag.get('href', None)
            if href is None: continue
            if (href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif')): continue
            # Resolve relative references like href="/contact"
            up = urlparse(href)
            if (len(up.scheme) < 1):
                href = urljoin(url, href)
            ipos = href.find('#')
            if (ipos > 1): href = href[:ipos]
            if "php?" in href: continue
            if href.count(":") > 1: continue
            if (href.endswith('/')): href = href[:-1]
            # print(href)
            if (len(href) < 1): continue

            # Check if the URL is in any of the webs
            found = False
            for web in webs:
                if (href.startswith(web)):
                    found = True
                    break
            if not found: continue

            cur.execute('INSERT IGNORE INTO event (url, html, new_rank) VALUES ( %s, NULL, 1.0 )', (href,))
            count = count + 1
            # conn.commit()

            try:
                if cur.lastrowi d! =0:
                    toid = cur.lastrowid
                else:
                    cur.execute('SELECT event_key FROM event WHERE url=%s LIMIT 1', (href,))
                    row = cur.fetchone()
                    # print(toid)
                    toid = row[0]
            except:
                print('Could not retrieve id')
                continue
            # print fromid, toid
            cur.execute('INSERT IGNORE INTO links (from_id, to_id) VALUES ( %s, %s )', (fromid, toid))
        print(count)
        counts.append(count)
        if man y % 10 == 0:
            toc = time.perf_counter()
            perf = ((to c -tic)) / sum(counts)
            print(many, "remaining. Time per link :", perf)
            counts = list()
            conn.commit()

    conn.commit()
    cur.close()
    conn.close()
    time.sleep(2)
    print("Executing textfill.py to maintain info in database. Please don't quit.")
    fill_text.filltext()
    time.sleep(2)
    print("Executing sprank.py to calculate pageranks for newer pages. Please don't quit")
    sprank.rank()
    time.sleep(2)
    print("Executing fill_year.py to tag events with years. Please don't quit")
    fill_year.tag_year()
    time.sleep(2)
    print("Executing fill_loc.py to tag events with their location. Please don't quit")
    fill_loc.tag_loc()
    time.sleep(2)
    print("Executing fill_genre.py to tag events with their genre. Please don't quit")
    fill_genre.tag_genre()
    print("All done")
except Error as e:
    print("\nError while connecting to MySQL\n", e)
    # print(traceback.format_exc())
