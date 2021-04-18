

"""
TO DO:
1. Lemmatize or stem words before KNN. Use NLTK
2. Use semi supervised learning with tensorflow?
3. Replicate paper at  : https://www.aclweb.org/anthology/C00-1066.pdf
4. Try using other supervised to train model and then use here? Data distribution
    problems

"""




















from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from bs4 import BeautifulSoup
import pandas as pd
import mysql
from mysql.connector import Error

def tag_genre():

    categ = [["education","college","university","department of education","education policy","school",
    "graduate","doctorate","phd","grade","classroom","blackboard","teacher","professor","students",
    "lecturer","research","guide","scholar","examinations","exam","certificate","rank","scholarship","text books","books","notebooks"],
    ["art","creativity","creative art","visual art","architecture","ceramics","conceptual art","drawing","painting",
    "photography","sculpture","literary arts","writing","editing","dance","music","theater","performing arts",
    "applied arts","video games","multidisciplinary artistic works","song","sing","color"],
    ["biology","reproduction","flora","fauna","plants","animals","animal kingdom","cells","virus","bacteria",
    "tissues","muscles","bones","blood","fungi","human body","respiration","nervous system","brain","disease","pandemic",
    "eyes","veins","arteries","intestines","nerves","vegetative state","blood cells","immunity","AIDS","disorder","anxiety",
    "cortex","orthology"],
    ["computer","computer organization","binary","hardware","software","machine","artifical intelligence","keyboard","mouse",
    "programming","code","cryptography","operating system","technology","laptop","cpu","central processing unit","gpu","grapics processing unit",
    "language","compiler","interpreter","scheduling","process","networking","database","data strcutures","data","unix","java","linux","windows","apple",
    "google","android","science"],
    ["hospital","health","health worker","doctors","nurses","physiotherapists","psychiatrists","neurosurgeons","gyneacologists",
    "physicians","oncology","opthalmology","amputation","operation theater","surgery","operation","ultrasound","mri","x-ray","ecg","echogram",
    "blood test","urine test","tissue culture","stem cells","cancer","orthopaedic","paediatrician","injections","syringes","menstrual cycles",
    "puberty","hygiene"],
    ["literature","reading","writing","poetry","short stories","stories","novels","poems","book series","author","publishing house",
    "publish","alliteration","anecdote","quote","pulitzer","poet","audience","biography","charatcer","drama","play","theater",
    "epilogue","essay","irony","imagery","lyric","plot","shakespeare","longfellow","maya angelou","prose","narrative","autobiography","fiction","non fiction",
    "literary criticism","literature review","speech","review","fable","psychology"],
    ["politics","government","democracy","republic","monarchy","anarchy","dictatorship","laws","king","queen","president","minister",
    "governor","member","legislation","council","assembly","boards","amendment","act","bill","judiciary","rule","party","term","sentence","judgement","protest",
    "oppression","right wing","left wing","judge","laywer","court","trial","hearing","section","constitution","right","prison sentence","election","vote","lobbying",
    "unions","public","jurisdiction"],
    ["religion","beliefs","traditions","culture","prayer","hindu","muslim","jain","buddhism","jews","zoroastrians","christian","gathering","chant","temple","mosque",
    "church","monastery","monk","priest","father","prophet","god","caste","practices","rituals","superstitions","myths","satan","legends","testament","magic",
    "people","faith","followers","digambara","svetambara","mahaveera","vatican","pope","kashi","tirupathi","cathedral","saint"],
    ["sport","ball","bowling","cricket","football","soccer","rugby","badminton","racquet","bat","play","score","match","qualifiers",
    "teams","tennis","wimbledon","kabaddi","commentator","field","stadium","points","score board","points table",
    "trophy","world cup","race","sportsmanship","shuttle"]]

    g_map = {1:"Education",2:"Art",3:"Biology",4:"Computer Science",5:"Health",6:"Literature",
    7:"Politics",8:"Religion",9:"Sports"}
    try:
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        cur = conn.cursor()
        cur.execute('''SELECT event_key,url,htext FROM event WHERE html IS NOT NULL AND error IS NULL AND event_genre IS NULL''')
        data = pd.DataFrame(cur.fetchall())
        heads = list()
        for row in cur.description:
            heads.append(row[0])
        data.columns = heads
        data.index = data["event_key"]
        #print(data)
        categ = [" ".join(i) for i in categ]
        catego = pd.DataFrame(zip(categ),columns = ["text"])
        vect = TfidfVectorizer()
        count = 0
        for i in range(len(data.index)):
            print(data.iloc[i]["event_key"],data.iloc[i]["url"]," - ",end = " ")
            cop = catego.append({"text":data.iloc[i]["htext"]},ignore_index = True)
            x= vect.fit_transform(cop["text"])
            #print(x[10].shape)
            #print(cop)
            knn = KNeighborsClassifier(n_neighbors=5, metric='minkowski')
            knn.fit(x,cop.index)
            #print(x[10])
            res = knn.kneighbors(x[-1:],n_neighbors = 2,return_distance = False)
            #print(res)
            print(g_map[(res[0][1]+1)])
            #print(type(res[0][1]+1))
            #print(type(data.iloc[i]["event_key"]))
            cur.execute("UPDATE event SET event_genre = %s WHERE event_key = %s",(int(res[0][1]+1),int(data.iloc[i]["event_key"])))
            count+=1
            if count%100==0 :
                conn.commit
        conn.commit()
        cur.close()
        conn.close()
        print(count,"rows")
        print("Done! Check database")
    except Error as e:
        print("Error while connecting to MySQL", e)





