import json

group2path = {
    0: [{"endpoint": "instruction", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": True},
        {"endpoint": "task", "task_num": 1, "theme": True},
        {"endpoint": "task", "task_num": 2, "theme": True},
        {"endpoint": "task", "task_num": 3, "theme": True},
        {"endpoint": "hold", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": True},
        {"endpoint": "task", "task_num": 1, "theme": True},
        {"endpoint": "task", "task_num": 2, "theme": True},
        {"endpoint": "task", "task_num": 3, "theme": True},
        {"endpoint": "post", "theme": True},
        ],

    1: [{"endpoint": "instruction", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": True},
        {"endpoint": "task", "task_num": 1, "theme": True},
        {"endpoint": "task", "task_num": 2, "theme": True},
        {"endpoint": "task", "task_num": 3, "theme": True},
        {"endpoint": "hold", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": False},
        {"endpoint": "task", "task_num": 1, "theme": False},
        {"endpoint": "task", "task_num": 2, "theme": False},
        {"endpoint": "task", "task_num": 3, "theme": False},
        {"endpoint": "post", "theme": False}
        ],

    2: [{"endpoint": "instruction", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": True},
        {"endpoint": "task", "task_num": 1, "theme": True},
        {"endpoint": "task", "task_num": 2, "theme": True},
        {"endpoint": "task", "task_num": 3, "theme": True},
        {"endpoint": "forget", "theme": True},
        {"endpoint": "task", "task_num": 0, "theme": False},
        {"endpoint": "task", "task_num": 1, "theme": False},
        {"endpoint": "task", "task_num": 2, "theme": False},
        {"endpoint": "task", "task_num": 3, "theme": False},
        {"endpoint": "post", "theme": True}
        ],
}

userpath_as_json = json.dumps(group2path)
userpath_as_py = json.loads(userpath_as_json)

