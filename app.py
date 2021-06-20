from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import StringField
from wtforms import RadioField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(300), index=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, answer):
        self.answer = answer


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    theme = db.Column(db.String(64), index=True, unique=False)
    answer = db.relationship('Answers', backref='user', lazy='dynamic')

    def __init__(self, username, theme):
        self.username = username
        self.theme = theme


db.create_all()


class TaskForm(FlaskForm):
    answer = TextAreaField("Answer")
    submit = SubmitField("Submit")


with open('tasks.json') as tasks_json:
    tasks_list = json.load(tasks_json)


class UserForm(FlaskForm):
    theme_categories = [("Light", "Light"), ("Dark", "Dark")]
    user_name = StringField("User name", validators=[DataRequired()])
    theme = RadioField("Your usual theme", choices=theme_categories)
    submit = SubmitField("Submit")


@app.route('/user', methods=["GET", "POST"])
def user():
    user_form = UserForm(csrf_enabled=False)
    if user_form.validate_on_submit():
        user_name = request.form.get('user_name', False)
        new_user_name = User(username=user_name)
        db.session.add(new_user_name)
        db.session.commit()

        theme = request.form.get('theme', False)
        u_theme = User(theme=theme)
        db.session.add(u_theme)
        db.session.commit()

    return render_template('user.html',
                           template_form=user_form)


@app.route('/task', methods=["GET", "POST"])
def task():
    task_line1 = tasks_list['task'][0]['line1']
    task_line2 = tasks_list['task'][0]['line2']

    answer = request.form.get('answer', False)
    new_answer = Answers(answer=answer)
    db.session.add(new_answer)
    db.session.commit()

    return render_template('task.html',
                           template_form=TaskForm(),
                           task_line1=task_line1,
                           task_line2=task_line2)


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)
