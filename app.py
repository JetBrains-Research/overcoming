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
    reason = db.Column(db.String(500), index=True, unique=False)
    answers = db.relationship('Answers', backref='user', lazy='dynamic')

    def __init__(self, username, theme, reason):
        self.username = username
        self.theme = theme
        self.reason = reason

    def set_hid(self, username):
        self.username_hash = hash(username)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hid = db.Column(db.Integer, db.ForeignKey('user.username_hash'), index=True)
    block = db.Column(db.Integer, unique=False)
    task_num = db.Column(db.Integer, unique=False)
    answer = db.Column(db.String(300), unique=False)

    def __init__(self, answer, block, task_num, user_hid):
        self.answer = answer
        self.block = block
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


class PostForm(FlaskForm):
    reason = TextAreaField("Reason", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user', methods=["GET", "POST"])
def user():
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_name = request.form.get('user_name', False)
        theme = request.form.get('theme', False)
        new = User(username=user_name, theme=theme, reason="")
        new.set_hid(form.user_name.data)
        db.session.add(new)
        db.session.commit()
        session['theme'] = theme
        session['user'] = hash(user_name)
        return redirect(url_for("instruction",
                                _external=True,
                                _scheme='http'))

    return render_template('user.html',
                           template_form=form)


@app.route('/instruction')
def instruction():
    theme = session.get('theme', None)
    return render_template('instruction.html', theme=theme)


@app.route('/task/<int:num>/<int:block_num>', methods=["GET", "POST"])
def task(num, block_num):
    form = TaskForm(csrf_enabled=False)
    new_num = int(num) + 1
    block_num = block_num
    theme = session.get('theme', None)
    if int(num) > 2 and block_num == 1:
        return redirect(url_for("forget",
                                _external=True,
                                _scheme='http'))
    if int(num) > 2 and block_num == 2:
        return redirect(url_for("post",
                                _external=True,
                                _scheme='http'))

    if form.validate_on_submit():
        if int(num) <= 2:
            user_hid = session.get('user', None)
            answer = form.answer.data
            new_answer = Answers(answer=answer, block=block_num, user_hid=user_hid, task_num=num)
            db.session.add(new_answer)
            db.session.commit()
            return redirect(url_for("task",
                                    num=new_num,
                                    block_num=block_num,
                                    _external=True,
                                    _scheme='http'))

    return render_template('task.html',
                           num=num,
                           block_num=block_num,
                           template_form=form,
                           theme=theme,
                           task_line1=tasks_list['task'][int(num)]['line1'],
                           task_line2=tasks_list['task'][int(num)]['line2'])


@app.route('/forget')
def forget():
    theme = session.get('theme', None)
    return render_template('forget.html', theme=theme)


@app.route('/post', methods=["GET", "POST"])
def post():
    theme = session.get('theme', None)
    form = PostForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(username_hash=user_hid).first()
        user_row.reason += form.reason.data
        db.session.commit()
        return redirect(url_for("fin",
                                _external=True,
                                _scheme='http'))

    return render_template('post.html', template_form=form, theme=theme)


@app.route('/fin')
def fin():
    theme = session.get('theme', None)
    return render_template('fin.html', theme=theme)


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)
