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
app.config["MYSQL_DATABASE_PORT"] = 3306
mysql.init_app(app)

app.secret_key = "abc"


def get_connection():
    conn = mysql.connect()
    cursor = conn.cursor()
    return conn, cursor


def close_connection(conn, cursor):
    conn.close()
    cursor.close()


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("final_homepage.html")


@app.route("/login", methods=["POST"])
def login():
    conn, cursor = get_connection()
    login_email = request.form["email"]
    login_password = request.form["password"]
    date = request.form["date"]
    time = request.form["time"]
    # print(date, time)
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
            stmt = """SELECT activity_id FROM activity WHERE activity_text = 'Login'"""
            cursor.execute(stmt)
            act_id = cursor.fetchall()[0][0]
            # print(act_id)
            stmt = """INSERT INTO activity_log (user_id,activity_id,activity_date,activity_time,event_key,activity_rating) values
            (%s,%s,%s,%s,%s,-1)"""
            data = (myresult[0][0], act_id, date, time, None)
            cursor.execute(stmt, data)
            # print(myresult[0][4])
            conn.commit()
            if myresult[0][4] == 3:
                session["username"] = "Backend"
                session["id"] = myresult[0][0]
                session["useremail"] = login_email
                close_connection(conn, cursor)
                return redirect(url_for("annotate"))
            elif myresult[0][4] == 2:
                print("Here")
                session["username"] = "Admin"
                session["id"] = myresult[0][0]
                session["useremail"] = login_email
                close_connection(conn, cursor)
                return redirect(url_for("log_activity"))
            else:
                session["useremail"] = login_email
                session["id"] = myresult[0][0]
                session["username"] = myresult[0][2]
                session["genre"] = []
                close_connection(conn, cursor)
                return redirect(url_for("map"))
        else:
            return redirect(url_for("index"))

    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)
        return redirect(url_for("index.html"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    conn, cursor = get_connection()
    date = request.form["date"]
    time = request.form["time"]
    print(date, time)
    stmt = """SELECT activity_id FROM activity WHERE activity_text = 'Logout'"""
    cursor.execute(stmt)
    act_id = cursor.fetchall()[0][0]
    stmt = """INSERT INTO activity_log (user_id,activity_id,activity_date,activity_time,event_key,activity_rating) values
    (%s,%s,%s,%s,%s,-1)"""
    data = (session["id"], act_id, date, time, None)
    cursor.execute(stmt, data)
    conn.commit()
    close_connection(conn, cursor)
    session.clear()
    return redirect(url_for("index"))


@app.route("/email_validation/", methods=["GET"])
def email_validation():
    conn, cursor = get_connection()
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
        close_connection(conn, cursor)
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "Fail"

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
    conn, cursor = get_connection()
    date = request.form["date"]
    time = request.form["time"]
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
            stmt = """SELECT user_id FROM user WHERE user_email  = %s"""
            cursor.execute(stmt, (email,))
            user_id = cursor.fetchall()[0][0]
            stmt = """SELECT activity_id FROM activity WHERE activity_text  = 'LOGIN'"""
            cursor.execute(stmt)
            act_id = cursor.fetchall()[0][0]
            stmt = """INSERT INTO activity_log (user_id,activity_id,activity_date,activity_time,event_key,activity_rating) values
            (%s,%s,%s,%s,%s,-1)"""
            data = (user_id, act_id, date, time, None)
            cursor.execute(stmt, data)
            conn.commit()
            session["useremail"] = email
            session["id"] = user_id
            session["username"] = username
            session["genre"] = []
            close_connection(conn, cursor)
            return redirect(url_for("map"))
        else:
            print("email exists", myresult)
            close_connection(conn, cursor)
            return render_template("registerpage.html", exist="user exists")
    except:
        # Rolling back in case of error
        conn.rollback()
        close_connection(conn, cursor)
        return "Fail"


@app.route("/map")
def map():
    if "username" not in session.keys():
        return render_template("final_homepage.html")
    insert_stmt = (
        "SELECT  event_key,event_title, event_lat,event_long FROM event LIMIT 6"
    )
    conn, cursor = get_connection()
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
        close_connection(conn, cursor)
        session["genre"] = []
        user = [{"name": session["username"], "email": session["useremail"]}]
        return render_template(
            "leaflet.html", marker_data=marker_data, user=user, keys=keys
        )
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "Couldn't fetch data"


@app.route("/search", methods=["GET"])
def search():
    conn, cursor = get_connection()
    date = request.args["date"]
    time = request.args["time"]
    try:
        cursor.execute(
            "SELECT event_key,event_title,event_text,new_rank,htext FROM event WHERE htext IS NOT NULL AND error IS NULL"
        )
    except Exception as e:
        print(e)
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
        cursor.execute(
            """SELECT activity_id FROM activity WHERE activity_text = 'Search'"""
        )
        act_id = cursor.fetchall()[0][0]
        stmt = """INSERT INTO activity_log (user_id,activity_id,activity_date,activity_time,event_key,activity_rating,search_text) values
        (%s,%s,%s,%s,%s,-1,%s)"""
        subs = (session["id"], act_id, date, time, None, query)
        cursor.execute(stmt, subs)
        conn.commit()
        feature = data["htext"]
        feature = feature.append(pd.Series([query]), ignore_index=True)
        url = data["event_title"]
        url = url.append(pd.Series(["query"]), ignore_index=True)
        x = vect.fit_transform(feature)
        res = knn.kneighbors(x[-1:], n_neighbors=6, return_distance=False)
        res = res[0][:]
        queries = data.loc[res, ["event_key", "event_title", "event_text", "new_rank"]]
        queries = queries.sort_values(by=["new_rank"], ascending=False)
        close_connection(conn, cursor)
        return jsonify({"res": queries.values.tolist()})
    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)
        return "Fail"


@app.route("/_get_data/", methods=["GET"])
def _get_data():
    conn, cursor = get_connection()
    recieved_event_id = request.args.get("id")
    insert_stmt = "SELECT   event_year,event_title,event_text,url,event_key FROM event where event_key=%s"
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
        close_connection(conn, cursor)
        return final_data
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "Fail"


@app.route("/_get_year_data/", methods=["GET"])
def _get_year_data():
    conn, cursor = get_connection()
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
        close_connection(conn, cursor)
    except Exception as e:
        print(e)
        close_connection(conn, cursor)

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


@app.route("/viewdata")
def viewdata():
    if session["username"] == "Admin":
        return render_template("view_data.html", layout_variable="layout_admin.html")
    elif session["username"] == "Backend":
        return render_template("view_data.html", layout_variable="layout.html")
    else:
        return redirect(url_for("map"))


@app.route("/annot")
def annot():
    conn, cursor = get_connection()
    id = request.args.get("id")
    genre = request.args.get("genre")
    stmt = "SELECT genre_id FROM genre WHERE genre_text = %s"
    try:
        cursor.execute(stmt, genre)
        res = cursor.fetchall()[0][0]
        stmt = "UPDATE event SET event_genre = %s WHERE event_key = %s"
        cursor.execute(stmt, (res, id))
        print(cursor._last_executed)
        conn.commit()
        close_connection(conn, cursor)
        return "Success"
    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)
        return "Fail"


@app.route("/accept_reject")
def accpet_reject():
    conn, cursor = get_connection()
    key = request.args.get("id")
    val = request.args.get("val")
    stmt = """UPDATE flag_log SET flag_approved = %s WHERE flag_key = %s"""
    try:
        cursor.execute(stmt, (val, key))
        conn.commit()
        close_connection(conn, cursor)
        return "Success"
    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)
        return "Fail"


@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    conn, cursor = get_connection()
    key = request.args.get("id")
    opt = int(request.args.get("opt"))
    if opt == 0:
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
            close_connection(conn, cursor)
            return response
        except Exception as e:
            print(e)
            close_connection(conn, cursor)
            return "Fail"
    else:
        stmt = "SELECT event_key,event_title,event_year,genre.genre_text,url,event_location,event_text FROM event JOIN genre ON event.event_genre = genre.genre_id WHERE event.event_key = %s"
        try:
            cursor.execute(stmt, key)
            res = cursor.fetchall()
            response = {
                "event_key": res[0][0],
                "event_title": res[0][1],
                "event_year": res[0][2],
                "event_genre": res[0][3],
                "url": res[0][4],
                "event_location": res[0][5],
                "event_text": res[0][6],
            }
            close_connection(conn, cursor)
            return response
        except Exception as e:
            print(e)
            close_connection(conn, cursor)
            return "Fail"


@app.route("/log_activity")
def log_activity():
    return render_template("log_activity.html")


@app.route("/vis")
def vis():
    conn, cursor = get_connection()
    stmt = """SELECT COUNT(*) FROM  event WHERE html IS NOT NULL AND error IS NULL"""
    try:
        cursor.execute(stmt)
        records = cursor.fetchall()[0][0]
        stmt = """SELECT COUNT(*) FROM genre"""
        cursor.execute(stmt)
        genres_count = cursor.fetchall()[0][0]
        stmt = """SELECT COUNT(*) FROM user"""
        cursor.execute(stmt)
        users = cursor.fetchall()[0][0]
        stmt = """SELECT event_genre FROM event WHERE event_genre IS NOT NULL"""
        cursor.execute(stmt)
        temp = cursor.fetchall()
        temp = [i[0] for i in temp]
        genres = list()
        for i in range(1, 10):
            genres.append(temp.count(i))
        stmt = (
            """SELECT event_title,new_rank FROM event ORDER BY NEW_RANK DESC LIMIT 5"""
        )
        cursor.execute(stmt)
        res = cursor.fetchall()
        ranks = list()
        titles = list()
        for row in res:
            ranks.append(row[1])
            titles.append(row[0])
        stmt = """SELECT activity_date FROM activity_log WHERE activity_date >= DATE_ADD(CURDATE(), INTERVAL -3 DAY) AND activity_id = 1 ORDER BY activity_date DESC"""
        cursor.execute(stmt)
        res = cursor.fetchall()
        res = [i[0] for i in res]
        dates = list()
        counts = list()
        for i in res:
            if i in dates:
                continue
            if len(dates) > 0 and (dates[len(dates) - 1] - i).days > 1:
                for k in range(0, dates[len(dates) - 1].days - i):
                    dates.append(0)
                    counts.append(0)
            dates.append(i)
            count = 0
            for j in res:
                if j == i:
                    count += 1
            counts.append(count)
        counts.reverse()
        if len(counts) < 7:
            counts = [0] * (7 - len(counts)) + counts
        print(dates, counts)
        stmt = """SELECT search_text FROM activity_log WHERE search_text IS NOT NULL"""
        cursor.execute(stmt)
        res = cursor.fetchall()
        raw_words = list()
        for row in res:
            for i in row[0].lower().split():
                raw_words.append(i)
        words = list()
        w_count = list()
        for word in raw_words:
            if word in words:
                continue
            words.append(word)
            count = 0
            for j in raw_words:
                if word == j:
                    count += 1
            w_count.append(count)
        word_df = pd.DataFrame(
            [i for i in zip(words, w_count)], columns=["Words", "Counts"]
        )
        word_df = word_df.sort_values(by=["Counts"], ascending=False)
        if word_df.shape[0] > 4:
            word_df = word_df.iloc[0:5]
        words = word_df["Words"].values.tolist()
        w_count = word_df["Counts"].values.tolist()
        print(words, w_count)

        data = {
            "records": records,
            "genres_count": genres_count,
            "genres": genres,
            "users": users,
            "titles": titles,
            "ranks": ranks,
            "counts": counts,
            "words": words,
            "w_count": w_count,
        }
        close_connection(conn, cursor)
        return render_template("vis.html", data=data)
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "fail"


@app.route("/getAttributes", methods=["GET"])
def getAttributes():
    conn, cursor = get_connection()
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
        close_connection(conn, cursor)
    except Exception as e:
        print(e)
        close_connection(conn, cursor)

    return jsonify(columns)


@app.route("/getrows", methods=["GET"])
def getrows():
    conn, cursor = get_connection()
    table = request.args.get("table")
    sortBy = request.args.get("sortBy")
    number = int(request.args.get("number"))
    # print(table, sortBy, number)
    if table == "event":
        if number > 500:
            number = 500
        stmt = (
                "SELECT * FROM "
                + table
                + " WHERE htext IS NOT NULL AND error IS NULL ORDER BY "
                + sortBy
                + " LIMIT "
                + str(number)
        )
    else:
        stmt = (
                "SELECT * FROM " + table + " ORDER BY " + sortBy + " LIMIT " + str(number)
        )
    try:
        cursor.execute(stmt)
        print(cursor._last_executed)
        res = cursor.fetchall()
        data = list()
        for row in res:
            data.append([str(i) for i in row])
        close_connection(conn, cursor)
        return {"data": data}
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "Fail"
    # print(data)


@app.route("/send_flag/", methods=["GET"])
def send_flag():
    conn, cursor = get_connection()
    event_key = request.args.get("event_key")
    radioflag = request.args.get("radioflag") + " " + request.args.get("flagDesc")
    date = request.args.get("date")
    time = request.args.get("time")
    insert_stmt = "INSERT INTO flag_log(event_key,flag_date,flag_time,flag_description, user_id,flag_approved) VALUES (%s,%s,%s,%s,%s,0)"

    userid = (
            'SELECT user_id FROM user  WHERE user_email="' + str(session["useremail"]) + '"'
    )
    try:
        cursor.execute(userid)
        res = cursor.fetchall()
        data = (event_key, date, time, radioflag, res[0][0])
        print(data)
        cursor.execute(insert_stmt, data)
        res = cursor.fetchall()
        conn.commit()
        close_connection(conn, cursor)
        return "success"
    except Exception as e:
        print(e)
        close_connection(conn, cursor)
        return "Fail"


@app.route("/forgotmail")
def forgotmail():
    conn, cursor = get_connection()
    mail = request.args.get("mail")
    res = False

    insert_stmt = "SELECT * FROM user WHERE user_email=%s "
    data = mail
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()

        if len(myresult) == 1:
            res = True

        if res == True:
            number = 0
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.starttls()
            s.login("the.explorer.verify@gmail.com", "8884233310")
            number = random.randint(1000, 9999)
            message = (
                    """Subject: OTP Verification, The Explorer\n\n 
            To proceed and finish your password reset please enter the given OTP in the website. Do not share this OTP with anyone else.
            \nOTP: """
                    + str(number)
                    + """\n\nRegards \nTeamExplorer"""
            )
            s.sendmail("the.explorer.verify@gmail.com", mail, message)
            s.quit()
            return str(number)
        else:
            return "fail"


    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)


@app.route("/resetpass")
def resetpass():
    conn, cursor = get_connection()
    newpassword = request.args.get("newpassword")
    mail = request.args.get("resetmail")

    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(newpassword.encode(), salt)

    update_stmt = "UPDATE user SET user_pass = %s WHERE user_email = %s"
    data = (password.decode(), mail)
    print(update_stmt)
    try:
        # Executing the SQL command
        cursor.execute(update_stmt, data)
        result = cursor.fetchall()


    except Exception as e:
        print(e)
        conn.rollback()
        close_connection(conn, cursor)

    print(mail, password.decode())

    return "pass"


if __name__ == "__main__":
    app.run(debug=True)
