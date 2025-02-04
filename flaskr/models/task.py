from bson import ObjectId
from ..infra.db import get_db
from datetime import datetime, timedelta

class Task:
    def __init__(self, title, description, status, expire_date, user_id, _id=None):
        self._id = str(_id) if _id else None
        self.title = title
        self.description = description
        self.status = status
        self.expire_date = expire_date
        self.user_id = str(user_id) if user_id else None

    def save(self):
        db = get_db()
        tasks_collection = db["tasks"]
        
        task_data = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "expire_date": self.expire_date,
            "user_id": ObjectId(self.user_id),
            "created_at": datetime.utcnow()
        }
        
        try:
            if self._id:  # Update
                task_id = ObjectId(self._id)
                result = tasks_collection.replace_one(
                    {"_id": task_id},
                    task_data
                )
            else:  # Insert
                result = tasks_collection.insert_one(task_data)
                self._id = str(result.inserted_id)
            
            return self._id
        except Exception as e:
            return None

    def delete(self):
        db = get_db()
        tasks_collection = db["tasks"]
        result = tasks_collection.delete_one({"_id": ObjectId(self._id)})
        return result.deleted_count > 0

    @classmethod
    def get_by_id(cls, id):
        """Search for a task by ID"""
        db = get_db()
        try:
            task_data = db['tasks'].find_one({'_id': ObjectId(id)})
            if task_data:
                return cls(
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    expire_date=task_data['expire_date'],
                    user_id=str(task_data['user_id']),
                    _id=str(task_data['_id'])
                )
        except Exception as e:
            return None

    @staticmethod
    def get_all_for_user(user_id):
        db = get_db()
        tasks_collection = db["tasks"]
        
        # Convert to ObjectId in the search since we saved it as ObjectId
        tasks_cursor = tasks_collection.find({"user_id": ObjectId(user_id)})
        tasks = []
        for task_data in tasks_cursor:
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                expire_date=task_data['expire_date'],
                user_id=str(task_data['user_id']),
                _id=str(task_data['_id'])
            )
            tasks.append(task)
        return tasks

    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': str(self._id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'expire_date': self.expire_date,

            'user_id': str(self.user_id),
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None
        }

    def update(self, data):
        """Update task data"""
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'status' in data:
            self.status = data['status']
        if 'expire_date' in data:
            self.expire_date = data['expire_date']
        
        return self.save()

    @classmethod
    def count_by_status(cls):
        """Count tasks by status"""
        db = get_db()
        pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        
        result = db.tasks.aggregate(pipeline)
        counts = {doc['_id']: doc['count'] for doc in result}
        
        # Ensure all statuses appear
        all_status = {'pending': 0, 'in_progress': 0, 'completed': 0}
        all_status.update(counts)
        return all_status


    @classmethod
    def get_error_rate(cls, hours=24):
        """Calculate error rate in the last X hours"""
        db = get_db()
        since = datetime.utcnow() - timedelta(hours=hours)
        

        # Here you can implement your specific error logic
        # For example, tasks that failed or were canceled
        total = db.tasks.count_documents({'created_at': {'$gte': since}})
        errors = db.tasks.count_documents({
            'created_at': {'$gte': since},
            'status': 'error'  # or other error criteria
        })

        
        return round(errors / total * 100, 2) if total > 0 else 0
