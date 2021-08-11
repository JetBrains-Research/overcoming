import json
from datetime import datetime
from flask import request, render_template, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, RadioField
from wtforms.validators import DataRequired
from models import create_app, db, User, Answers

app = create_app()
app.app_context().push()
db.create_all()


class UserForm(FlaskForm):
    theme_categories = [("Light", "Светлая"), ("Dark", "Темная")]
    username = StringField("User name", validators=[DataRequired()])
    theme = RadioField("Your usual theme", choices=theme_categories)
    submit = SubmitField("Дальше")


class PostForm(FlaskForm):
    reason = TextAreaField("Reason", validators=[DataRequired()])
    submit = SubmitField("Дальше")


class FollowupForm(FlaskForm):
    scale_points = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    how_helpful = RadioField("Helpfulness", choices=scale_points, validators=[DataRequired()])
    how_comfortable = RadioField("Comfort", choices=scale_points, validators=[DataRequired()])
    submit = SubmitField("Дальше")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user', methods=["GET", "POST"])
def user():
    form = UserForm(meta={'csrf': False})
    if form.validate_on_submit():
        username = request.form.get('username', False)
        theme = request.form.get('theme', False)

        new_user = User(username=username, theme=theme, reason="", how_helpful="", how_comfortable="", time=datetime.now())

        user_row = User.query.count()
        name2group = {"control": 0, "change": 1, "all": 2}
        if new_user.username in name2group.keys():
            group = name2group[new_user.username]
        else:
            group = user_row % 3

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


@app.context_processor
def page_managment():
    def get_next_page(page_id):
        path = session['path']
        next_page = path[page_id+1]
        return url_for(**next_page, _external=True, _scheme='http')
    return {'get_next_page': get_next_page}


@app.route('/instruction')
def instruction():
    session['step_id'] = 0
    theme = session.get('theme', None)

    with open('tasks.json') as tasks_json:
        tasks_list = json.load(tasks_json)
        session['tasks_list'] = tasks_list

    return render_template('instruction.html', theme=theme, page_id=session['step_id'])


@app.route('/task/<int:task_num>/<string:theme>', methods=["GET", "POST"])
def task(task_num, theme):
    session['step_id'] += 1
    tasks_list = session.get('tasks_list', None)
    session['start_time'] = datetime.now()
    session['task_num'] = task_num

    if session['step_id'] <= 4:
        block_num = 0
    else:
        block_num = 1
    session['block_num'] = block_num

    return render_template('task.html',
                           task_num=task_num,
                           theme=theme,
                           task_line1=tasks_list['task'][block_num][task_num]['line1'],
                           task_line2=tasks_list['task'][block_num][task_num]['line2'])


@app.route('/process_code', methods=['POST', 'GET'])
def process_code():
    if request.method == "POST":
        code = request.get_json()
        user_hid = session.get('user', None)
        task_num = session.get('task_num', None)
        block_num = session.get('block_num', 0)

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


@app.route('/forget/<string:theme>')
def forget(theme):
    session['step_id'] += 1
    return render_template('forget.html', theme=theme, page_id=session['step_id'])


@app.route('/hold/<string:theme>')
def hold(theme):
    session['step_id'] += 1
    return render_template('hold.html', theme=theme, page_id=session['step_id'])


@app.route('/post', methods=["GET", "POST"])
def post():
    form = PostForm(meta={'csrf': False})
    if form.validate_on_submit():
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        user_row.reason += form.reason.data
        db.session.commit()
        if user_row.group == 0:
            return redirect(url_for("fin", _external=True, _scheme='http'))
        else:
            return redirect(url_for("follow", _external=True, _scheme='http'))

    return render_template('post.html', template_form=form)


@app.route('/follow', methods=["GET", "POST"])
def follow():
    session['step_id'] += 1
    form = FollowupForm(meta={'csrf': False})
    if form.validate_on_submit():
        user_hid = session.get('user', None)
        user_row = User.query.filter_by(time_hash=user_hid).first()
        user_row.how_helpful += form.how_helpful.data
        user_row.how_comfortable += form.how_comfortable.data
        db.session.commit()
        return redirect(url_for("fin", _external=True, _scheme='http'))
    return render_template('followup.html', template_form=form)


@app.route('/fin')
def fin():
    return render_template('fin.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

# docker build -t test:test .
# docker run -d -p 80:8080 -v /Users/sergey.titov/Documents/work/jbr/overcoming/app/database/:/app/database/
# --name pyapp test:test
