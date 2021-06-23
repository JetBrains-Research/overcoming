from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager
from flask_login import UserMixin
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import StringField
from wtforms import RadioField
from wtforms.validators import DataRequired
from flask_login import login_required
import json
from flask_login import login_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    theme = db.Column(db.String(64), index=True, unique=False)
    answers = db.relationship('Answers', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(300), index=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, answer, user_id):
        self.answer = answer
        self.user_id = user_id


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/user', methods=["GET", "POST"])
def user():
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        new = User(username=form.user_name.data, theme=form.theme.data)
        db.session.add(new)
        db.session.commit()
        login_user(new)

        return redirect(url_for("task",
                                _external=True,
                                _scheme='http'))

    return render_template('user.html',
                           template_form=form)


@app.route('/<username>/task', methods=["GET", "POST"])
@login_required
def task(username):
    user = User.query.filter_by(username=username).first_or_404()
    task_line1 = tasks_list['task'][0]['line1']
    task_line2 = tasks_list['task'][0]['line2']

    user_id = user.id
    answer = request.form.get('answer', False)
    new_answer = Answers(answer=answer, user_id=user_id)
    db.session.add(new_answer)
    db.session.commit()

    return render_template('task.html',
                           user=user,
                           template_form=TaskForm(),
                           task_line1=task_line1,
                           task_line2=task_line2)


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)
