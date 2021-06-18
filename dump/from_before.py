
@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        new_form_data = request.form['answer']
        write_to_database(connection)
        return f"thank you for participation!"


def write_to_database(connection):
    new_form_data = request.form['answer']
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute(f"INSERT INTO form_data VALUES (new_form_data)")
    con.close()


def test_database(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM form_data'):
        print(row)
    con.close()

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)



con = sqlite3.connect('../form_data.db')
connection = 'form_data.db'


def create_db(connection):
    con = sqlite3.connect(connection)
    cur = con.cursor()
    cur.execute('''CREATE TABLE form_data
                   (answer text)''')
    con.commit()
    con.close()

#create_db(connection)
