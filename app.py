import smtplib
import random
from flask import Flask, request, url_for, render_template, jsonify
from werkzeug.utils import redirect
from flaskext.mysql import MySQL

import json

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'explorer_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

app.secret_key = "abc"

conn = mysql.connect()
cursor = conn.cursor()


@app.route('/')
def test():
    return render_template('final_homepage.html')


@app.route('/login', methods=['POST'])
def login():
    login_email = request.form['email']
    login_password = request.form['password']
    print(login_email, login_password)
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

        if len(myresult) == 1 and myresult[0][1] == login_email and myresult[0][3] == login_password:
            return redirect(url_for('map'))

        # Commit your changes in the database
        conn.commit()

    except:
        # Rolling back in case of error
        conn.rollback()

    return render_template('final_homepage.html', exist="wrong email or password")


@app.route('/email_validation/', methods=['GET'])
def email_validation():
    print("----------------")
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
        print(myresult)
        res = True
        if len(myresult) == 1:
            res = False

        # Commit your changes in the database
        conn.commit()


    except:
        # Rolling back in case of error
        conn.rollback()

    if res == True:

        li = [recieved_email]
        number=0
        for dest in li:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login("the.explorer.verify@gmail.com", "8884233310")
            number = random.randint(1000, 9999)
            print(number)
            message = "Your otp "+str(number)
            s.sendmail("sender_email_id", dest, message)
            s.quit()

        return str(number)
    else:
        return "exist"


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
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
            print("does not exists exists", myresult)

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
        "SELECT  event_key , event_title ,event_year, event_lat , event_long FROM event ORDER BY event_year DESC"
    )

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt)
        myresult = cursor.fetchall()
        yearint = 0
        for i in myresult:
            li = []
            if i[2][0] == "[":
                li = i[2].strip('][').split(', ')
                print(type(li))

            else:
                yearint = int(i[2])

            # print(yearint)

        # Commit your changes in the database
        conn.commit()

    except:
        # Rolling back in case of error
        conn.rollback()

    marker_data = [{
        'id': 0,
        'lat': 13.00715,
        'long': 76.0962,
        'popline': 'this is pop line 0'
    },
        {
            'id': 1,
            'lat': 13.120000,
            'long': 73.680000,
            'popline': 'this is pop line 1'
        }
        ,
        {
            'id': 2,
            'lat': 43.120000,
            'long': 73.680000,
            'popline': 'this is pop line 2'
        },
        {
            'id': 3,
            'lat': 13.120000,
            'long': 43.680000,
            'popline': 'this is pop line 3'
        }

    ]

    user = [{'firstname': "fn", 'lastname': "ln", 'age': 10.2555185},
            {'firstname': "dfsfn", 'lastname': "lasdfsfn", 'age': 20}]

    return render_template('leaflet.html', marker_data=marker_data, user=user)


@app.route('/_get_data/', methods=['GET'])
def _get_data():
    recieved_event_id = request.args.get('id')
    print(recieved_event_id)

    insert_stmt = (
        "SELECT   event_year, event_title , event_text FROM event where event_key=%s"
    )

    data = recieved_event_id
    final_data = {}
    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()
        print(myresult)
        ss = myresult[0]
        final_data = {
            'event_name': ss[1],
            'year': ss[0],
            'description': ss[2]
        }
        print("a----------")

        # Commit your changes in the database
        conn.commit()


    except:
        # Rolling back in case of error
        conn.rollback()

    return final_data


@app.route('/_get_year_data/', methods=['GET'])
def _get_year_data():
    recieved_year = request.args.get('id')
    print(recieved_year)

    insert_stmt = (
        "SELECT  event_key , event_title ,event_year, event_lat , event_long FROM event where event_year=%s"
    )
    data = recieved_year
    marker_data = []

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)
        myresult = cursor.fetchall()

        for i in myresult:
            marker = {
                'id': i[0],
                'lat': i[3],
                'long': i[4],
                'popline': i[1]}

            marker_data.append(marker)

        # Commit your changes in the database
        conn.commit()


    except:
        # Rolling back in case of error
        conn.rollback()

    print(marker_data)
    return jsonify(marker_data)


if __name__ == '__main__':
    app.run(debug=True)
