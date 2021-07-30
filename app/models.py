from flask import Flask
from userpath import group2path
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from copy import deepcopy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    db.init_app(app)
    app.config['SECRET_KEY'] = 'mysecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/myDB.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


class Theme:
    themes = {0: 'Dark', 1: 'Light'}

    def __init__(self, color):
        # self.theme_id = themes[color]
        self.color = color
        for i in self.themes.items():
            if color in i:
                self.theme_id = i[0]
            else:
                continue

    @property
    def true(self):
        return self.color

    @property
    def neg(self):
        return self.themes[not self.theme_id]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.Integer, unique=False)
    username = db.Column(db.String(64), index=True, unique=False)
    time = db.Column(db.DateTime(), default=datetime.now(), index=True, unique=True)
    time_hash = db.Column(db.String(128), unique=True)
    theme = db.Column(db.String(64), unique=False)
    reason = db.Column(db.String(500), index=True, unique=False)
    how_helpful = db.Column(db.Integer, unique=False)
    how_comfortable = db.Column(db.Integer, unique=False)
    answers = db.relationship('Answers', backref='user', lazy='dynamic')

    def __init__(self, username, theme, reason, how_helpful, how_comfortable, time):
        self.username = username
        self.theme = theme
        self.reason = reason
        self.time = time
        self.how_comfortable = how_comfortable
        self.how_helpful = how_helpful
        self.time_hash = hash(time)

    def set_group(self, group_id):
        # 0 - control, 1 - forget, 2 - change, 3 - forget+change
        self.group = group_id % 4 if (group_id % 4 >= 1) & (group_id % 4 < 4) else 0

    def set_path(self):
        theme = Theme(self.theme)
        group = self.group
        path = deepcopy(group2path[group])

        for point_id in range(len(path)):
            path[point_id]['theme'] = theme.true if path[point_id]['theme'] else theme.neg

        self.path = path


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
