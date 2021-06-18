from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_line1 = db.Column(db.String(300), index=True, unique=False)
    task_line2 = db.Column(db.String(300), index=True, unique=False)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(300), index=True, unique=False)

    def __init__(self, answer):
        self.answer = answer


db.create_all()


class TaskForm(FlaskForm):
    answer = TextAreaField("Answer")
    submit = SubmitField("Submit")


@app.route('/task', methods=["GET", "POST"])
def task():
    task_line_1 = Tasks.query.get(2)

    def task_line1():
        return task_line_1.task_line1

    def task_line2():
        return task_line_1.task_line2

    answer = request.form.get('answer', False)
    new_answer = Answers(answer)
    db.session.add(new_answer)
    db.session.commit()

    return render_template('task.html',
                           template_form=TaskForm(),
                           task_line1=task_line1(),
                           task_line2=task_line2())


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)
