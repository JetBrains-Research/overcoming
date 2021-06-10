from flask import Flask
from flask import request
from flask import escape
from flask import render_template
import sqlite3

con = sqlite3.connect('form_data.db')
app = Flask(__name__, template_folder='templates')
connection = 'form_data.db'
task_list = ["""Дано: print(something, type(something)). <br> Сравните типы объектов.""",
             """Дан список: names = ["a", "b", "c"]. <br> Проитерируйте объекты в нем и выведите значение элемента и 
             его порядковый номер в списке.""",
             """Дан список: list = ['a','b','c','d']. <br> Просуммируйте значения в нем."""]


def create_db(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute('''CREATE TABLE form_data
                   (answer text)''')
    con.commit()
    con.close()

#create_db(connection)

def write_to_database(new_form_data, connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute(f"INSERT INTO form_data VALUES ({new_form_data['answer']})")
    con.close()


def test_database(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM form_data'):
        print(row)
    con.close()



@app.route('/form')
def form():

    return render_template('form.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        write_to_database(form_data, connection)
        return f"thank you for participation!"


def create_db(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute('''CREATE TABLE form_data
                   (answer text)''')
    con.commit()
    con.close()


def write_to_database(new_form_data, connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute(f"INSERT INTO form_data VALUES ({new_form_data['answer']})")
    con.close()


def test_database(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM form_data'):
        print(row)
    con.close()

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)


