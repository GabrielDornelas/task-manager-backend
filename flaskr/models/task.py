from bson import ObjectId
from ..db import get_db

def get_task_by_id(id):
    db = get_db()
    tasks_collection = db["tasks"]
    task = tasks_collection.find_one({"_id": ObjectId(id)})
    return task

def get_tasks_from_user(user_id):
    db = get_db()
    tasks_collection = db["tasks"]
    tasks = tasks_collection.find({"user_id": ObjectId(user_id)})
    return tasks

def create_task(task):
    db = get_db()
    tasks_collection = db["tasks"]
    result = tasks_collection.insert_one(task)
    return str(result.inserted_id)

def update_task(task):
    db = get_db()
    tasks_collection = db["tasks"]
    filter = {"_id": ObjectId(task['_id'])}
    update = {
        '$set': {
            "title": task['title'],
            "description": task['description'],
            "status": task['status'],
            "expire_date": task['expire_date'],
            "user_id": task['user_id']
        }
    }
    result = tasks_collection.update_one(filter, update)
    return result.modified_count > 0

def delete_task(id):
    db = get_db()
    tasks_collection = db["tasks"]
    filter = {"_id": ObjectId(id)}
    result = tasks_collection.delete_one(filter)
    return result.deleted_count > 0
