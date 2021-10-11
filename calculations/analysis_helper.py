import sqlite3
import numpy as np
import pandas as pd


def analysis_tables():
    con = sqlite3.connect("myDB.db")
    user = pd.read_sql_query("SELECT * from user", con)
    answer = pd.read_sql_query("SELECT * from answers", con)
    con.close()

    user['time_hash'] = user['time_hash'].astype(int)
    answer['task_time'] = (pd.to_datetime(answer.end_time) - pd.to_datetime(answer.start_time)) / np.timedelta64(1, 's')

    data = pd.merge(user, answer, left_on='time_hash', right_on='user_hid', suffixes=('_user', '_answer'))
    participants_with_na_values = data[data.isna().any(axis=1)]

    numbers = data[['id_user', 'username', 'group', 'block_num', 'task_num', 'answer', 'task_time',
                    'how_helpful', 'how_comfortable']]
    words = user[['id', 'group', 'reason']]
    prior = pd.read_csv("prior.csv")
    return prior, data, numbers, words, participants_with_na_values


prior, data, numbers, words, participants_with_na_values = analysis_tables()


def table_maker(task_num_block0, task_num_block1, check_string):
    block0_task = numbers.loc[(numbers.block_num == 0) & (numbers.task_num == task_num_block0), :]
    block1_task = numbers.loc[(numbers.block_num == 1) & (numbers.task_num == task_num_block1), :]

    table_task = pd.merge(block0_task, block1_task, on=['id_user', 'username', 'group', 'how_helpful', 'how_comfortable'],
                          suffixes=('_block0', '_block1'))
    table_task['delta_time'] = table_task.task_time_block1 - table_task.task_time_block0
    table_task['change'] = (table_task.answer_block0.str.contains(check_string, regex=False) !=
                            table_task.answer_block1.str.contains(check_string, regex=False))
    table_task.loc[table_task.answer_block0.str.contains(check_string, regex=False), 'change'] = 'No_set'
    table_task = pd.merge(prior, table_task, on='username')
    table_task.loc[~(table_task.set.str.contains(check_string, regex=False)), 'change'] = 'No_preset'
    table_task = table_task.loc[:, ['id_user', 'set', 'group', 'answer_block0',
                                    'task_time_block0', 'answer_block1', 'task_time_block1',
                                    'delta_time', 'change', 'how_helpful', 'how_comfortable']].dropna()
    return table_task
