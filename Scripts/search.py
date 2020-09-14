



"""

TO DO:
1) STEMM THE HTEXT BEFORE VECTORIZING FOR BETTER ACCURACY?
2) TRY USING %LIKE% IN DATABASE QUERY (USEFUL FOR LARGE DATA IN MEMORY) AND 
    OPTIMIZE
3) TRY LOOKING IN URLS TO FIND UN-FETHCED BUT MORE RELEVANT PAGES AND FETCH 
    AND PROCESS AND SERVE
4) THRESHOLD THE KMEANS RESULT TO ONLY INCLUDE UNDER A CERTAIN MEASURE. 
   (MORE ACCURATE RESULTS ALBEIT LESS)
5) FETCH ONLY RELEVANT DATA FROM DB NOT *. INCREASES EFFICIENCY
6) DISPLAY THE TITLE AND THE MESSAGE BEFORE LINK LIKE GOOGLE
7) MAKE CODE MORE ROBUST TO EDGE CASES AND EXCEPTIONS
8) DISPLAY TIME PER QUERY


"""

















from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from bs4 import BeautifulSoup
import pandas as pd
import mysql
from mysql.connector import Error

try:
    conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
    if conn.is_connected():
        print("Connection successful: ",conn.get_server_info())
    cur = conn.cursor()
    cur.execute('''SELECT * FROM event WHERE html IS NOT NULL AND error IS NULL''')
    data = pd.DataFrame(cur.fetchall())
    heads = list()
    for row in cur.description:
        heads.append(row[0])
    data.columns = heads
    vect = TfidfVectorizer()
    x = vect.fit_transform(data['htext'])
    knn = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
    knn.fit(x,data['url'])
    while True:
        try:
            query = input('Search query: ')
            feature = data['htext']
            feature = feature.append(pd.DataFrame({query}),ignore_index = True)
            url = data['url']
            url = url.append(pd.DataFrame({'query'}),ignore_index = True)
            x = vect.fit_transform(feature[0])
            res = knn.kneighbors(x[-1:],n_neighbors = 6,return_distance = False)
            res = res[0][1:]
            def result(x):
                for i in x:
                    print(queries['url'][i]) 
            queries = data.loc[res,['event_key','url','new_rank']]
            queries = queries.sort_values(by=['new_rank'],ascending = False)
            #print(queries)
            result(res)
        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break
        except:
            print('Unknown error')
            break
except Error as e:
    print("Error while connecting to MySQL", e)




