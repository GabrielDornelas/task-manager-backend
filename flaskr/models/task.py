from bson import ObjectId
from ..db import get_db

class Task:
    def __init__(self, title, description, status, expire_date, user_id, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.title = title
        self.description = description
        self.status = status
        self.expire_date = expire_date
        self.user_id = user_id

    def save(self):
        db = get_db()
        tasks_collection = db["tasks"]
        task_data = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "expire_date": self.expire_date,
            "user_id": self.user_id
        }
        if not self._id:  # If no _id, it's a new task to be inserted
            result = tasks_collection.insert_one(task_data)
            self._id = str(result.inserted_id)
        else:
            filter = {"_id": ObjectId(self._id)}
            update = {'$set': task_data}
            tasks_collection.update_one(filter, update)
        return self._id

    def delete(self):
        db = get_db()
        tasks_collection = db["tasks"]
        result = tasks_collection.delete_one({"_id": ObjectId(self._id)})
        return result.deleted_count > 0

    @staticmethod
    def get_by_id(id):
        db = get_db()
        tasks_collection = db["tasks"]
        task_data = tasks_collection.find_one({"_id": ObjectId(id)})
        if task_data:
            return Task(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                expire_date=task_data['expire_date'],
                user_id=task_data['user_id'],
                _id=str(task_data['_id'])
            )
        return None

    @staticmethod
    def get_all_for_user(user_id):
        db = get_db()
        tasks_collection = db["tasks"]
        tasks_data = tasks_collection.find({"user_id": ObjectId(user_id)})
        tasks = []
        for task_data in tasks_data:
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                expire_date=task_data['expire_date'],
                user_id=task_data['user_id'],
                _id=str(task_data['_id'])
            )
            tasks.append(task)
        return tasks
