import json
from datetime import datetime
from flask import request, render_template, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, RadioField
from wtforms.validators import DataRequired
from models import create_app, db, User, Answers

app = create_app()
app.app_context().push()


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

        new_user = User(username=username, theme=theme, reason="", time=datetime.now())

        user_row = User.query.count()
        name2group = {"control": 0, "forget": 1, "change": 2, "all": 3}
        if new_user.username in name2group.keys():
            group = name2group[new_user.username]
        else:
            group = user_row % 4

        new_user.set_group(group)
        new_user.set_path()

        db.session.add(new_user)
        db.session.commit()

        session['user'] = new_user.time_hash
        session['group'] = new_user.group
        session['theme'] = new_user.theme
        session['path'] = new_user.path

        return redirect(url_for("instruction", _external=True, _scheme='http'))
    return render_template('user.html',
                           template_form=form)


@app.route('/instruction')
def instruction():
    session['step_id'] = 0
    theme = session.get('theme', None)

    with open('tasks.json') as tasks_json:
        tasks_list = json.load(tasks_json)
        session['tasks_list'] = tasks_list

    return render_template('instruction.html', theme=theme, page_id=session['step_id'])


@app.route('/process_code', methods=['POST', 'GET'])
def process_code():
    if request.method == "POST":
        code = request.get_json()
        user_hid = session.get('user', None)
        task_num = session.get('task_num', None)

        if session['step_id'] <= 3:
            block_num = 1
        else:
            block_num = 2

        answer = Answers(answer=code[0]['code'], block_num=block_num, user_hid=user_hid,
                         task_num=task_num, start_time=session.pop('start_time', None),
                         end_time=datetime.now())
        db.session.add(answer)
        db.session.commit()

        m = page_managment()
        url = m['get_next_page'](session['step_id'])
        print(url)
        results = {'code_uploaded': 'True',
                   'redirect': url}
        return jsonify(results)


@app.context_processor
def page_managment():
    def get_next_page(page_id):
        path = session['path']
        next_page = path[page_id+1]
        if next_page['endpoint'] is None:
            session['step_id'] += 1
            next_page = path[session['step_id'] + 1]
        return url_for(**next_page, _external=True, _scheme='http')
    return {'get_next_page': get_next_page}


@app.route('/task/<int:task_num>/<string:theme>', methods=["GET", "POST"])
def task(task_num, theme):
    session['step_id'] += 1
    tasks_list = session.get('tasks_list', None)
    session['start_time'] = datetime.now()
    session['task_num'] = task_num
    return render_template('task.html',
                           task_num=task_num,
                           theme=theme,
                           task_line1=tasks_list['task'][task_num]['line1'],
                           task_line2=tasks_list['task'][task_num]['line2'])


@app.route('/forget/<string:theme>')
def forget(theme):
    session['step_id'] += 1
    return render_template('forget.html', theme=theme, page_id=session['step_id'])


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
    db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)

# docker build -t test:test .
# docker run -d -p 80:8080 -v /Users/sergey.titov/Documents/work/jbr/overcoming/app/database/:/app/database/
# --name pyapp test:test
