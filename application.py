from flask import Flask
from flask import request, escape
from flask import render_template
import pickle
import sqlite3

con = sqlite3.connect('example.db')

app = Flask(__name__, template_folder='templates')
connection = 'example.db'

def create_db(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute('''CREATE TABLE form_data
                   (Name text, City text, Country text)''')
    con.commit()
    con.close()


def write_to_database(new_from_data, connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute(f"INSERT INTO form_data VALUES ({new_from_data['Name'], new_from_data['City'], new_from_data['Country']})")
    con.close()


def test_database(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM form_data'):
        print(row)
    con.close()

#create_db(connection)
@app.route('/form')
def form():

    return render_template('form.html')


@app.route('/data/', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        print(request)
        form_data = request.form
        write_to_database(form_data, connection)
        test_database(connection)
        return f"thank you for participation!"
        #return render_template('data.html', form_data=form_data)


def create_db(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute('''CREATE TABLE form_data
                   (Name text, City text, Country text)''')
    con.commit()
    con.close()


def write_to_database(new_from_data, connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    print(f"INSERT INTO form_data VALUES ({new_from_data['Name']}, {new_from_data['City']}, {new_from_data['Country']})")
    cur.execute(f"INSERT INTO form_data VALUES ({new_from_data['Name']}, {new_from_data['City']}, {new_from_data['Country']})")
    con.commit()
    con.close()


def test_database(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM form_data'):
        print(row)
    con.close()


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)


