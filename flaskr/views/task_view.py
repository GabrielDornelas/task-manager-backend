def task_response(task):
    """Formata uma única task"""
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "expire_date": task["expire_date"],
        "user_id": str(task["user_id"])
    }

def tasks_list_response(tasks):
    """Formata uma lista de tasks"""
    return [{
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "expire_date": task["expire_date"],
        "user_id": str(task["user_id"])
    } for task in tasks]
