import smtplib
import random
from flask import Flask, request, url_for, render_template, jsonify
from werkzeug.utils import redirect
from flaskext.mysql import MySQL
import bcrypt


import json

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'explorer_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3307
mysql.init_app(app)

app.secret_key = "abc"

conn = mysql.connect()
cursor = conn.cursor()


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('final_homepage.html')


@app.route('/login', methods=['POST'])
def login():
    login_email = request.form['email']
    login_password = request.form['password']
    #print(login_email, login_password)
    # # Preparing SQL query to INSERT a record into the database.
    insert_stmt = (
        "SELECT * FROM user WHERE user_email=%s "
    )
    data = login_email

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()

        print(myresult[0][1], myresult[0][2])

        if len(myresult) == 1 and myresult[0][1] == login_email and bcrypt.checkpw(login_password.encode(),myresult[0][3].encode()):
            return redirect(url_for('map'))
        else:
            print("Fail")

        # Commit your changes in the database
        conn.commit()

    except:
        # Rolling back in case of error
        conn.rollback()

    return render_template('final_homepage.html', exist="wrong email or password")

@app.route('/logout')
def logout():
    return redirect(url_for('index'))



@app.route('/email_validation/', methods=['GET'])
def email_validation():
    #print("----------------")
    recieved_email = request.args.get('email')

    print(recieved_email)

    insert_stmt = (
        "SELECT * FROM user WHERE user_email=%s "
    )
    data = recieved_email

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        #print(myresult)
        res = True
        if len(myresult) == 1:
            res = False

        # Commit your changes in the database
        conn.commit()


    except:
        # Rolling back in case of error
        conn.rollback()

    if res == True:

        #li = [recieved_email]
        number=0
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("the.explorer.verify@gmail.com", "8884233310")
        number = random.randint(1000, 9999)
        #print(number)
        message = """Subject: OTP Verification, The Explorer\n\n Thank you for signing up with TheExplorer. We'd love to have you onboard!
        To proceed and finish your registration please enter the given OTP in the website. Do not share this OTP with anyone else.
        \nOTP: """+str(number)+"""\n\nRegards \nTeamExplorer"""
        s.sendmail("the.explorer.verify@gmail.com",recieved_email,message)
        s.quit()

        return str(number)
    else:
        return "exist"


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form["h_name"]
    email = request.form["h_email"]
    password = request.form["h_pass"]
    
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(),salt)
    insert_stmt = (
        "SELECT * FROM user WHERE user_email=%s "
    )
    data = email

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        print(myresult)
        if len(myresult) == 0:
            #print("does not exists exists", myresult)

            insert_stmt = (
                "INSERT INTO user(user_email, user_name,user_pass,role_id) VALUES (%s, %s, %s, %s)"
            )
            data = (email, username, password, 1)
            print("insert data->", username, password, email)

            cursor.execute(insert_stmt, data)
            conn.commit()

            return redirect(url_for('map'))
        else:
            print("email exists", myresult)
            return render_template('registerpage.html', exist="user exists")

        # Commit your changes in the database
        conn.commit()

    except:
        # Rolling back in case of error
        conn.rollback()

    # Preparing SQL query to INSERT a record into the database.

@app.route('/map')
def map():
    insert_stmt = (
        "SELECT  event_key,event_title, event_lat,event_long FROM event LIMIT 6"
    )
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
        # Commit your changes in the database
        #conn.commit()

    except Exception as e:
        # Rolling back in case of error
        #conn.rollback()
        print(e)

    user = [{'firstname': "fn", 'lastname': "ln", 'age': 10.2555185},
            {'firstname': "dfsfn", 'lastname': "lasdfsfn", 'age': 20}]

    return render_template('leaflet.html', marker_data=marker_data, user=user)


@app.route('/_get_data/', methods=['GET'])
def _get_data():
    recieved_event_id = request.args.get('id')
    #print(recieved_event_id)

    insert_stmt = (
        "SELECT   event_year,event_title,event_text,url FROM event where event_key=%s"
    )

    data = recieved_event_id
    final_data = {}
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        #print(myresult)
        ss = myresult[0]
        final_data = {
            'event_name': ss[1],
            'year': ss[0],
            'description': ss[2],
            'url': ss[3]
        }
        #print("a----------")

        # Commit your changes in the database
        #conn.commit()


    except Exception as e:
        # Rolling back in case of error
        #conn.rollback()
        print(e)

    return final_data


@app.route('/_get_year_data/', methods=['GET'])
def _get_year_data():
    recieved_year = request.args.get('id')
    #print(recieved_year)

    insert_stmt = (
        "SELECT  event_key , event_title ,event_year, event_lat , event_long FROM event where event_year=%s"
    )
    data = recieved_year
    marker_data = []

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        if cursor.rowcount<=0:
            return u"Fail",200
        myresult = cursor.fetchall()
        #print(myresult)
        

        for i in myresult:
            marker = {
                'id': i[0],
                'lat': i[3],
                'long': i[4],
                'popline': i[1]}

            marker_data.append(marker)

        # Commit your changes in the database
        #conn.commit()


    except Exception as e:
        # Rolling back in case of error
        #conn.rollback()
        print(e)

    #print(marker_data)
    return jsonify(marker_data)


if __name__ == '__main__':
    app.run(debug = True)
