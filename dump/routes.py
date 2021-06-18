from app import app
from app import db, Tasks, Answers
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField

class TaskForm(FlaskForm):
    answer = TextAreaField("Answer")
    submit = SubmitField("Submit")

@app.route('/task', methods=["GET", "POST"])
def task():
    task_line_1 = tasks.query.get(1)
    def task_line1():
        return task_line_1.task_line1
    def task_line2():
        return task_line_1.task_line2
    return render_template('task.html',
                           template_form=TaskForm(),
                           task_line1=task_line1,
                           task_line2=task_line2)
