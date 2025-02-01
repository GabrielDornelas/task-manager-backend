def format_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "expire_date": task["expire_date"]
    }
