from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, RadioField
from wtforms.validators import DataRequired
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.Integer, unique=False)
    username = db.Column(db.String(64), index=True, unique=False)
    time = db.Column(db.DateTime(), default=datetime.now(), index=True, unique=True)
    time_hash = db.Column(db.String(128), unique=True)
    theme = db.Column(db.String(64), unique=False)
    reason = db.Column(db.String(500), index=True, unique=False)
    answers = db.relationship('Answers', backref='user', lazy='dynamic')

    def __init__(self, username, theme, reason, time):
        self.username = username
        self.theme = theme
        self.reason = reason
        self.time = time
        self.time_hash = hash(time)

    def set_group(self, id):
        self.group = id % 4 if (id % 4 >= 1) & (id % 4 < 4) else 0
        # 0 - control, 1 - forget, 2 - change, 3 - forget+change


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hid = db.Column(db.Integer, db.ForeignKey('user.time_hash'), index=True)
    block_num = db.Column(db.Integer, unique=False)
    task_num = db.Column(db.Integer, unique=False)
    answer = db.Column(db.String(300), unique=False)
    start_time = db.Column(db.DateTime(), index=True, unique=True)
    end_time = db.Column(db.DateTime(), index=True, unique=True)

    def __init__(self, answer, block_num, task_num, user_hid, end_time, start_time):
        self.answer = answer
        self.block_num = block_num
        self.task_num = task_num
        self.user_hid = user_hid
        self.start_time = start_time
        self.end_time = end_time


db.create_all()


class SubmitForm(FlaskForm):
    submit = SubmitField("Submit")


with open('tasks.json') as tasks_json:
    tasks_list = json.load(tasks_json)


class UserForm(FlaskForm):
    theme_categories = [("Light", "Light"), ("Dark", "Dark")]
    username = StringField("User name", validators=[DataRequired()])
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
    form = UserForm(meta={'csrf': False})
    if form.validate_on_submit():
        username = request.form.get('username', False)
        theme = request.form.get('theme', False)
        time = datetime.now()
        new_user = User(username=username, theme=theme, reason="", time=time)
        db.session.add(new_user)

        session['user'] = hash(time)
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        name2group = {"control": 0, "forget": 1, "change": 2, "all": 3}

        if user_row.username in name2group.keys():
            group = name2group[user_row.username]
        else:
            group = user_row.id

        db.session.refresh(new_user)
        new_user.set_group(group)
        db.session.commit()

        session['group'] = user_row.group
        session['theme'] = theme

        return redirect(url_for("instruction", _external=True, _scheme='http'))

    return render_template('user.html',
                           template_form=form)


@app.route('/instruction')
def instruction():
    theme = session.get('theme', None)
    return render_template('instruction.html', theme=theme)


@app.route('/process_code', methods=['POST', 'GET'])
def process_code():
    if request.method == "POST":
        code = request.get_json()
        user_hid = session.get('user', None)
        block_num = session.get('block_num', None)
        task_num = session.get('task_num', None)
        answer = Answers(answer=code[0]['code'], block_num=block_num, user_hid=user_hid,
                         task_num=task_num, start_time=session.pop('start_time', None),
                         end_time=datetime.now())
        db.session.add(answer)
        db.session.commit()
        results = {'code_uploaded': 'True'}
        return jsonify(results)


@app.route('/task/<int:task_num>/<int:block_num>/<string:theme>', methods=["GET", "POST"])
def task(task_num, block_num, theme):
    form = SubmitForm(meta={'csrf': False})
    next_task_num = task_num + 1
    group = session.get('group', None)
    session['block_num'] = block_num
    session['task_num'] = task_num

    if form.validate_on_submit() and task_num <= 2:
        return redirect(url_for("task", task_num=next_task_num, block_num=block_num, theme=theme,
                                _external=True, _scheme='http'))

    if task_num > 2 and block_num == 1 and (group == 1 or group == 3):
        return redirect(url_for("forget", _external=True, _scheme='http'))

    if task_num > 2 and block_num == 1 and group == 2 and theme == 'Dark':
        return redirect(url_for("task", task_num=0, block_num=2, theme="Light",
                                _external=True, _scheme='http'))

    if task_num > 2 and block_num == 1 and group == 2 and theme == 'Light':
        return redirect(url_for("task", task_num=0, block_num=2, theme='Dark',
                                _external=True, _scheme='http'))

    if task_num > 2 and block_num == 1 and group == 0:
        return redirect(url_for("task", task_num=0, block_num=2, theme=theme,
                                _external=True, _scheme='http'))

    if task_num > 2 and block_num == 2:
        return redirect(url_for("post", _external=True, _scheme='http'))

    session['start_time'] = datetime.now()
    return render_template('task.html',
                           task_num=task_num,
                           block_num=block_num,
                           template_form=form,
                           theme=theme,
                           task_line1=tasks_list['task'][task_num]['line1'],
                           task_line2=tasks_list['task'][task_num]['line2'])


@app.route('/forget')
def forget():
    theme = session.get('theme', None)
    group = session.get('group', None)
    return render_template('forget.html', theme=theme, group=group, task_num=0, block_num=2)


@app.route('/post', methods=["GET", "POST"])
def post():
    form = PostForm(meta={'csrf': False})
    if form.validate_on_submit():
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        user_row.reason += form.reason.data
        db.session.commit()
        return redirect(url_for("fin", _external=True, _scheme='http'))

    return render_template('post.html', template_form=form)


@app.route('/fin')
def fin():
    return render_template('fin.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
