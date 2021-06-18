from app import db, Tasks

first = Tasks(task_line1="""Дано: print(something, type(something))""",
              task_line2="""Сравните типы объектов""")
db.session.add(first)

second = Tasks(task_line1="""Дан список: names = ['a', 'b', 'c']""",
               task_line2="""Проитерируйте объекты в нем и выведите значение элемента и 
             его порядковый номер в списке""")
db.session.add(second)

third = Tasks(task_line1="""Дан список: list = ['a','b','c','d']""",
              task_line2="""Просуммируйте значения в нем""")
db.session.add(third)

db.session.commit()
