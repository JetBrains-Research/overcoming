from flask import Flask, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, RadioField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=False)
    username_hash = db.Column(db.String(128), unique=True)
    theme = db.Column(db.String(64), unique=False)
    answers = db.relationship('Answers', backref='user', lazy='dynamic')

    def __init__(self, username, theme):
        self.username = username
        self.theme = theme

    def set_hid(self, username):
        self.username_hash = hash(username)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(300), unique=False)
    task_num = db.Column(db.Integer, unique=False)
    user_hid = db.Column(db.Integer, db.ForeignKey('user.username_hash'), index=True)

    def __init__(self, answer, task_num, user_hid):
        self.answer = answer
        self.task_num = task_num
        self.user_hid = user_hid


db.create_all()


class TaskForm(FlaskForm):
    answer = TextAreaField("Answer", validators=[DataRequired()])
    submit = SubmitField("Submit")


with open('tasks.json') as tasks_json:
    tasks_list = json.load(tasks_json)


class UserForm(FlaskForm):
    theme_categories = [("Light", "Light"), ("Dark", "Dark")]
    user_name = StringField("User name", validators=[DataRequired()])
    theme = RadioField("Your usual theme", choices=theme_categories)
    submit = SubmitField("Submit")


@app.route('/')
@app.route('/user', methods=["GET", "POST"])
def user():
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_name = request.form.get('user_name', False)
        theme = request.form.get('theme', False)
        new = User(username=user_name, theme=theme)
        new.set_hid(form.user_name.data)
        db.session.add(new)
        db.session.commit()
        session['user'] = hash(user_name)
        return redirect(url_for("task",
                                num=0,
                                _external=True,
                                _scheme='http'))

    return render_template('user.html',
                           template_form=form)


@app.route('/task/<int:num>', methods=["GET", "POST"])
def task(num):
    form = TaskForm(csrf_enabled=False)
    task_line1 = tasks_list['task'][int(num)]['line1']
    task_line2 = tasks_list['task'][int(num)]['line2']
    new_num = int(num) + 1
    if form.validate_on_submit():
        if int(num) <= 2:
            user_hid = session.get('user', None)
            answer = form.answer.data
            new_answer = Answers(answer=answer, user_hid=user_hid, task_num=num)
            db.session.add(new_answer)
            db.session.commit()
            return redirect(url_for("task",
                                    num=new_num,
                                    _external=True,
                                    _scheme='http'))

    return render_template('task.html',
                           num=num,
                           template_form=form,
                           task_line1=task_line1,
                           task_line2=task_line2)


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)
