import smtplib
import random
import datetime

from flask import Flask, request, url_for, render_template, jsonify, session
from werkzeug.utils import redirect
from flaskext.mysql import MySQL
import bcrypt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from bs4 import BeautifulSoup
import pandas as pd
import json

app = Flask(__name__)

mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "explorer_db"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_PORT"] = 3307
mysql.init_app(app)

app.secret_key = "abc"

conn = mysql.connect()
cursor = conn.cursor()


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("final_homepage.html")


@app.route("/login", methods=["POST"])
def login():
    login_email = request.form["email"]
    login_password = request.form["password"]
    insert_stmt = "SELECT * FROM user WHERE user_email=%s "
    data = login_email
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        # print(myresult[0][1], myresult[0][2])
        if len(myresult) == 1 and bcrypt.checkpw(
            login_password.encode(), myresult[0][3].encode()
        ):
            if myresult[0][4] == 2:
                print("Got here")
                return redirect(url_for("annotate"))
            elif myresult[0][4] == 3:
                pass
            else:
                session["useremail"] = login_email
                session["username"] = myresult[0][2]
                session["genre"] = []
                return redirect(url_for("map"))
        else:
            return "fail"

    except Exception as e:
        print(e)

    return render_template("final_homepage.html", exist="wrong email or password")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/email_validation/", methods=["GET"])
def email_validation():
    recieved_email = request.args.get("email")
    insert_stmt = "SELECT * FROM user WHERE user_email=%s "
    data = recieved_email

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        res = True
        if len(myresult) == 1:
            res = False
    except Exception as e:
        print(e)

    if res == True:
        number = 0
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login("the.explorer.verify@gmail.com", "8884233310")
        number = random.randint(1000, 9999)
        message = (
            """Subject: OTP Verification, The Explorer\n\n Thank you for signing up with TheExplorer. We'd love to have you onboard!
        To proceed and finish your registration please enter the given OTP in the website. Do not share this OTP with anyone else.
        \nOTP: """
            + str(number)
            + """\n\nRegards \nTeamExplorer"""
        )
        s.sendmail("the.explorer.verify@gmail.com", recieved_email, message)
        s.quit()

        return str(number)
    else:
        return "exist"


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["h_name"]
    email = request.form["h_email"]
    password = request.form["h_pass"]
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(), salt)
    insert_stmt = "SELECT * FROM user WHERE user_email=%s "
    data = email
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        if len(myresult) == 0:
            insert_stmt = "INSERT INTO user(user_email, user_name,user_pass,role_id) VALUES (%s, %s, %s, %s)"
            data = (email, username, password, 1)
            cursor.execute(insert_stmt, data)
            conn.commit()
            session["useremail"] = email
            session["username"] = username
            session["genre"] = []
            return redirect(url_for("map"))
        else:
            print("email exists", myresult)
            return render_template("registerpage.html", exist="user exists")
    except:
        # Rolling back in case of error
        conn.rollback()


@app.route("/map")
def map():
    if "username" not in session.keys():
        return render_template("final_homepage.html")
    insert_stmt = (
        "SELECT  event_key,event_title, event_lat,event_long FROM event LIMIT 6"
    )
    keys = list()
    marker_data = list()
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt)
        myresult = cursor.fetchall()
        for rec in myresult:
            temp = dict()
            temp["id"] = rec[0]
            temp["popline"] = rec[1]
            temp["lat"] = rec[2]
            temp["long"] = rec[3]
            marker_data.append(temp)
        insert_stmt = "SELECT  event_title FROM event WHERE event_text IS NOT NULL"
        cursor.execute(insert_stmt)
        myresult = cursor.fetchall()
        for rec in myresult:
            keys.append(rec[0])
    except Exception as e:
        print(e)

    session["genre"] = []
    user = [{"name": session["username"], "email": session["useremail"]}]

    return render_template(
        "leaflet.html", marker_data=marker_data, user=user, keys=keys
    )


@app.route("/search", methods=["GET"])
def search():
    cursor.execute(
        "SELECT event_key,event_title,event_text,new_rank,htext FROM event WHERE htext IS NOT NULL AND error IS NULL"
    )
    data = pd.DataFrame(cursor.fetchall())
    heads = list()
    for row in cursor.description:
        heads.append(row[0])
    data.columns = heads
    vect = TfidfVectorizer()
    x = vect.fit_transform(data["htext"])
    knn = KNeighborsClassifier(n_neighbors=5, metric="euclidean")
    knn.fit(x, data["event_title"])
    try:
        query = request.args.get("query")
        feature = data["htext"]
        feature = feature.append(pd.Series([query]), ignore_index=True)
        url = data["event_title"]
        url = url.append(pd.Series(["query"]), ignore_index=True)
        x = vect.fit_transform(feature)
        res = knn.kneighbors(x[-1:], n_neighbors=6, return_distance=False)
        res = res[0][:]
        queries = data.loc[res, ["event_key", "event_title", "event_text", "new_rank"]]
        queries = queries.sort_values(by=["new_rank"], ascending=False)
        return jsonify({"res": queries.values.tolist()})
    except Exception as e:
        print(e)

    return u"Success"


@app.route("/_get_data/", methods=["GET"])
def _get_data():
    recieved_event_id = request.args.get("id")
    insert_stmt = (
        "SELECT   event_year,event_title,event_text,url,event_key FROM event where event_key=%s"
    )
    data = recieved_event_id
    final_data = {}
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        ss = myresult[0]
        final_data = {
            "event_key": ss[4],
            "event_name": ss[1],
            "year": ss[0],
            "description": ss[2],
            "url": ss[3],
        }
    except Exception as e:
        print(e)

    return final_data


@app.route("/_get_year_data/", methods=["GET"])
def _get_year_data():
    recieved_year = json.loads(request.args.get("main"))
    opt = recieved_year["option"]
    genre_list = session["genre"]
    select_stmt = ""
    if opt == 0:
        if len(genre_list) == 0:
            select_stmt = "SELECT event_key , event_title ,event_year, event_lat , event_long FROM event where event_year=%s"
            data = recieved_year["data"]
        else:
            select_stmt = """SELECT event.event_key , event.event_title ,event.event_year, event.event_lat , event.event_long, genre.genre_text
            FROM event JOIN genre ON event.event_genre = genre.genre_id 
            WHERE event.event_year = %s AND genre.genre_text IN %s"""
            data = (recieved_year["data"], tuple(session["genre"]))
    else:
        temp = recieved_year["data"]
        keys = tuple([temp[str(i)] for i in range(6)])
        select_stmt = "SELECT event_key,event_title ,event_year, event_lat , event_long FROM event where event_key IN %s"
        data = ((keys),)

    marker_data = []
    try:
        # Executing the SQL command
        cursor.execute(select_stmt, data)
        print(cursor._last_executed)
        if cursor.rowcount <= 0:
            return u"Fail", 200
        myresult = cursor.fetchall()
        for i in myresult:
            marker = {"id": i[0], "lat": i[3], "long": i[4], "popline": i[1]}
            marker_data.append(marker)
    except Exception as e:
        print(e)

    return jsonify(marker_data)


@app.route("/_set_genre/", methods=["GET"])
def _set_genre():
    recieved_genre = request.args.get("genre")
    genre_list = session["genre"]

    if recieved_genre in genre_list:
        genre_list.remove(recieved_genre)
    else:
        genre_list.append(recieved_genre)
    session["genre"] = genre_list
    return str(session["genre"])


@app.route("/annotate")
def annotate():
    return render_template("annotate.html")


@app.route("/runscripts")
def runscripts():
    return render_template("run_scripts.html")


@app.route("/viewdata")
def viewdata():
    return render_template("view_data.html")


@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    key = request.args.get("id")
    stmt = "SELECT event_key,event_title,url,event_text FROM event WHERE event_key = %s"
    try:
        cursor.execute(stmt, key)
        res = cursor.fetchall()
        response = {
            "event_key": res[0][0],
            "event_title": res[0][1],
            "url": res[0][2],
            "event_text": res[0][3],
        }

    except Exception as e:
        print(e)

    return response


@app.route("/getAttributes", methods=["GET"])
def getAttributes():
    key = request.args.get("table")
    columns = list()
    stmt = "SHOW COLUMNS FROM " + key
    try:
        cursor.execute(stmt)
        res = cursor.fetchall()
        for i in res:
            temp = dict()
            temp["col"] = i[0]
            columns.append(temp)
    except Exception as e:
        print(e)

    return jsonify(columns)


@app.route("/getrows", methods=["GET"])
def getrows():
    table = request.args.get("table")
    sortBy = request.args.get("sortBy")
    number = int(request.args.get("number"))

    if table == "event":
        if number > 500:
            number = 500
<<<<<<< HEAD
            stmt = "SELECT * FROM " + table + " WHERE htext IS NOT NULL AND error IS NOT NULL ORDER BY " + sortBy + " LIMIT " + str(
                number)
=======
            stmt = (
                "SELECT * FROM "
                + table
                + " WHERE htext IS NOT NULL AND error IS NOT NULL ORDER BY "
                + sortBy
                + " LIMIT "
                + str(number)
            )
>>>>>>> 38f86a2f49345cac955ce7d191815f3bdb837566
        else:
            stmt = (
                "SELECT * FROM "
                + table
                + " ORDER BY "
                + sortBy
                + " LIMIT "
                + str(number)
            )

    else:
<<<<<<< HEAD
        stmt = "SELECT * FROM " + table + " ORDER BY " + sortBy + " LIMIT " + str(number)
=======
        stmt = (
            "SELECT * FROM " + table + " ORDER BY " + sortBy + " LIMIT " + str(number)
        )
>>>>>>> 38f86a2f49345cac955ce7d191815f3bdb837566
    try:
        cursor.execute(stmt)
        res = cursor.fetchall()

    except Exception as e:
        print(e)

    return jsonify(res)


@app.route("/send_flag/", methods=["GET"])
def send_flag():
    event_key = request.args.get("event_key")
    radioflag = request.args.get("radioflag") + " " + request.args.get("flagDesc")

    request.args.get("flagDesc")
    date = datetime.date.today()
    time = datetime.datetime.now().time()
    insert_stmt = "INSERT INTO flag_log(event_key,flag_date,flag_time,flag_description, user_id,flag_approved) VALUES (%s,%s,%s,%s,%s,0)"

    userid = "SELECT user_id FROM user  WHERE user_email=\""+str(session["useremail"])+"\""
    try:
        cursor.execute(userid)
        res = cursor.fetchall()
        data = (event_key,date, time, radioflag, res[0][0])

        cursor.execute(insert_stmt,data)
        res = cursor.fetchall()


    except Exception as e:
        print(e)

    return "success"


if __name__ == "__main__":
    app.run(debug=True)
