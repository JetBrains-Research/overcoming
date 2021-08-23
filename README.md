


# Overcoming the mental set effect in programming
This is the code for an experiment that is held to find an ecologically valid tool to get rid of habitual code smells.  
The project contains a Flask app to gather data and an analysis Jupyter notebook.

## Getting Started
The app for an experiment is situated in the [«app» folder](../tree/calculation/app).<br/>
Prerequisites might be found there in the [requirements.txt](../blob/calculation/app/requirements.txt).<br/>
`pip install -r requirements.txt`

[app.py](../blob/calculation/app/app.py) is the main file which should be run to get access to a
local website with the experiment.<br/>
`python3 app.py`

Also, it is possible to run app using docker. Dockerfile provided in the root.

## Data
All data will go to the newly formed «database» folder into myDB.db file.  
In the database two tables may be found: «user» and «answers».  

One can find our aproach to data analysis in the [«calculations» folder](..tree/calculation/calculations)
in the [over_cal.ipynb file](../blob/calculation/calculations/over_cal.ipynb).

*We use this app online, and our data is stored on the server, also we use data from a pre-experimental questionnaire,
and so on always places myDB.db and prior.csv files to the «calculations» folder manually.
Note that the prior.csv file should contain two columns: username and set.
Where username is participant's email and set is the name(s) of function(s) which are habitually used by a participant.*


## Credits
This project was made during a summer internship in [Machine Learning for 
Software Engineering Research Group in JetBrains Research](https://research.jetbrains.org/groups/ml_methods/). <br/>
The supervisor and contributor of this project is [Sergey Titov](https://github.com/TitovSergey). <br/>
Author: [Agniya Serheyuk](https://github.com/hugnia), St. Petersburg State University.