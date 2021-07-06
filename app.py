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

    def set_hid(self, time):
        self.time_hash = hash(time)

    def set_group(self, id):
        if id % 4 == 0:
            self.group = 4
        elif id % 4 == 1:
            self.group = 1
        elif id % 4 == 2:
            self.group = 2
        elif id % 4 == 3:
            self.group = 3
# 1 - forget, 2 - change, 3 - forget+change, 4 - control


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hid = db.Column(db.Integer, db.ForeignKey('user.time_hash'), index=True)
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
    #answer = TextAreaField("Answer", validators=[DataRequired()])
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
    form = UserForm(meta={'csrf': False})
    if form.validate_on_submit():
        user_name = request.form.get('user_name', False)
        theme = request.form.get('theme', False)
        time = datetime.now()
        new = User(username=user_name, theme=theme, reason="", time=time)
        new.set_hid(time)
        db.session.add(new)
        db.session.commit()
        session['theme'] = theme
        session['user'] = hash(time)

        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        if user_row.username == "forget":
            new.set_group(1)
            db.session.add(new)
            db.session.commit()

        elif user_row.username == "change":
            new.set_group(2)
            db.session.add(new)
            db.session.commit()

        elif user_row.username == "all":
            new.set_group(3)
            db.session.add(new)
            db.session.commit()

        elif user_row.username == "control":
            new.set_group(4)
            db.session.add(new)
            db.session.commit()

        else:
            new.set_group(user_row.id)
            db.session.add(new)
            db.session.commit()

        session['group'] = user_row.group

        return redirect(url_for("instruction",
                                _external=True,
                                _scheme='http'))

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
        # theme = session['theme']
        user = session['user']
        # num=2
        # block_num=0

        answer = Answers(answer=code[0]['code'], block=2, user_hid=user, task_num=2)
        db.session.add(answer)
        db.session.commit()
        #rows = db.session.query(answer).count()
        results = {'code_uploaded': 'True'}

        return jsonify(results)


# @app.route('/task/<int:num>/<int:block_num>/<string:theme>', methods=["GET", "POST"])
# def task(num, block_num, theme):
#     form = TaskForm(meta={'csrf': False})
#     new_num = int(num) + 1
#     block_num = block_num
#     theme = theme
#     group = session.get('group', None)
#
#     return render_template('task.html',
#                            num=new_num,
#                            block_num=block_num,
#                            template_form=form,
#                            theme=theme,
#                            task_line1=tasks_list['task'][int(num)]['line1'],
#                            task_line2=tasks_list['task'][int(num)]['line2'])
#

@app.route('/task/<int:num>/<int:block_num>/<string:theme>', methods=["GET", "POST"])
def task(num, block_num, theme):
    form = TaskForm(meta={'csrf': False})
    new_num = int(num) + 1
    block_num = block_num
    theme = theme
    group = session.get('group', None)

    if int(num) > 2 and block_num == 1 and group == 1:
        return redirect(url_for("forget",
                                _external=True,
                                _scheme='http'))

    if int(num) > 2 and block_num == 1 and group == 2 and theme == 'Dark':
        return redirect(url_for("task",
                                num=0,
                                block_num=2,
                                theme='Light',
                                _external=True,
                                _scheme='http'))

    if int(num) > 2 and block_num == 1 and group == 2 and theme == 'Light':
        return redirect(url_for("task",
                                num=0,
                                block_num=2,
                                theme='Dark',
                                _external=True,
                                _scheme='http'))

    if int(num) > 2 and block_num == 1 and group == 3:
        return redirect(url_for("forget",
                                _external=True,
                                _scheme='http'))

    if int(num) > 2 and block_num == 1 and group == 4:
        return redirect(url_for("task",
                                num=0,
                                block_num=2,
                                theme=theme,
                                _external=True,
                                _scheme='http'))

    if int(num) > 2 and block_num == 2:
        return redirect(url_for("post",
                                _external=True,
                                _scheme='http'))

    if form.validate_on_submit():
        if int(num) <= 2:
            user_hid = session.get('user', None)
            #answer = form.answer.data
            #new_answer = Answers(answer=answer, block=block_num, user_hid=user_hid, task_num=num)
            #db.session.add(new_answer)
            #db.session.commit()
            return redirect(url_for("task",
                                    num=new_num,
                                    block_num=block_num,
                                    theme=theme,
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
    group = session.get('group', None)
    return render_template('forget.html', theme=theme, group=group, num=0, block_num=2)


@app.route('/post', methods=["GET", "POST"])
def post():
    form = PostForm(meta={'csrf': False})
    if form.validate_on_submit():
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        user_row.reason += form.reason.data
        db.session.commit()
        return redirect(url_for("fin",
                                _external=True,
                                _scheme='http'))

    return render_template('post.html', template_form=form)


@app.route('/fin')
def fin():
    return render_template('fin.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
