# Overcoming the mental set effect in programming
This is the code for an experiment that is held to find an ecologically valid tool to get rid of habitual code smells.  
We adapted the Luchins' ([Luchins, 1942](https://psycnet.apa.org/record/2011-21639-001)) paradigm to see if induction of cognitive control and increased awareness, provided by task-irrelevand change and by cue to intentionally forget prior solutions, would help to overcome the mental set effect, in other words to use less habitual but more direct solutions in simle programing tasks.

We think that cognitove deiven development is an important direction of research and work, so we would like to concider this project as a contribution to the field.

The project contains a Flask app to gather data and a Jupyter notebook to make calculations.

## Getting Started
The app for an experiment is situated in the [«app» folder](../tree/calculation/app).<br/>
Prerequisites might be found there in the [requirements.txt](../blob/calculation/app/requirements.txt).<br/>
`pip install -r requirements.txt`

[app.py](../blob/calculation/app/app.py) is the main file which should be run to get access to a
local website with the experiment.<br/>
`python3 app.py`

## App architecture
The main part of the experiment is the Flask app with a linear multipage structure. Page change happens when the «Next» button is pressed by a participant.

The first page, **`index` route**, contains initial instructions.

Next, the **`user` route** is presented. On the front end of this page, participant fills in their email and choose their habitual IDE theme. On the back end quite a few processes took place:
1. All data from the form goes to the `User` model, along with its timestamp. The model might be found in the [models.py](../blob/calculation/app/models.py) file. 
2. The timestamp is hashed and logged to the user model for further usage as a foreign key in another model.
3. In the user model the group is assigned according to the preset «codenames» `name2group = {"control": 0, "change": 1, "all": 2}` for testing purposes, or according to the index of the newly-formed row.
4. We needed the theme to be changed from habitual to the opposite one in the second phase of the experiment. In order to do that we made a `Theme` class to transform the theme to boolean.

```python
class Theme:
    themes = {0: 'Dark', 1: 'Light'}
    def __init__(self, color):
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
```
5. The order and characteristics of further page-presentation is set from the [userpath.json](../blob/calculation/app/userpath.json) file according to the assighned group and chosen theme. 
```python
def set_path(self):
    theme = Theme(self.theme)
    group = self.group    
    with open('userpath.json') as userpath_json:
        userpath_load = json.load(userpath_json)
        userpath_dumps = json.dumps(userpath_load)
        userpath_py = json.loads(userpath_dumps)
    path = userpath_py[str(group)]
    for point_id in range(len(path)):
        path[point_id]['theme'] = theme.true if path[point_id]['theme'] else theme.neg
    self.path = path
```

Next page is **`instruction` route**, where main instructions are given. Here the ['tasks.json'](../blob/calculation/app/tasks.json) file is parced in order to save `tasks_list` in session for futher usage. From here to redirect to the next page the self-writen content_processor is used:
```python
def page_managment():
    def get_next_page(page_id):
        path = session['path']
        next_page = path[page_id+1]
        return url_for(**next_page, _external=True, _scheme='http')
    return {'get_next_page': get_next_page}
```

After that **`task` route** is presented. This is a cycle of 4 pages each with a task and code editor. The text for the tasks gets from the `tasks_list` and the code editor is a block of js code. On the back end of this page several things happen:
1. solutions from the code editor are processed with the [process_code.js](../blob/calculation/app/static/process_code.js) and the connected `process_code` function.
2. then the solution itself and timestamps of the beginning and end of page presentation are logged into the `Answers` model.

When the cycle is done participant is redirected to the **`forget`** or **`hold` routes** depending on the experimental group they are in.

Onwards another cycle of **`task` routes** is presented. In this phase wording and order of the tasks, presentation is changed. Additionally, for two experimental groups theme is changed to the opposite one this time. And for the control group, there is no change of theme. 

Following that, the **`post` route** page is presented, where a participant is asked to fill in the reasons to change or not to change solutions of the tasks on the second phase. Data from that form adds to the `User` model. 

If a participant was presented with the change of the theme they were redirected to the **`follow` route** with the follow-up questions. Answers to them also go to the `User` model.

And the last page for all participants is **`fin` route** with valedictions and permission to close the tab.

## Data
All data will go to the newly formed «database» folder into myDB.db file.  
In the database two tables may be found: «user» and «answers».  

One can find our aproach to data analysis in the [«calculations» folder](..tree/calculation/calculations)
in the [over_cal.ipynb file](../blob/calculation/calculations/over_cal.ipynb).

*We use this app online and our data is stored on the server, also we use data from a pre-experimental questionnaire,
and so one always places myDB.db and prior.csv files to the «calculations» folder manually.
Note that the prior.csv file should contain two columns: username and set.
Where username is participant's email and set is the name(s) of function(s) which are habitually used by a participant.*

## Credits
This project was made during a summer internship in [Machine Learning for 
Software Engineering Research Group in JetBrains Research](https://research.jetbrains.org/groups/ml_methods/). <br/>
Supervisor and contributor of this project is [Sergey Titov](https://github.com/TitovSergey). <br/>
Author: [Agniya Serheyuk](https://github.com/hugnia)
