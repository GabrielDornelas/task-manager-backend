from bson import ObjectId
from ..infra.db import get_db

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
        
        import sys
        print(f"DEBUG: Salvando task com user_id: {self.user_id}", file=sys.stderr)
        print(f"DEBUG: Tipo do user_id: {type(self.user_id)}", file=sys.stderr)
        
        task_data = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "expire_date": self.expire_date,
            "user_id": ObjectId(self.user_id)
        }
        
        print(f"DEBUG: Task data para salvar: {task_data}", file=sys.stderr)
        
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
            print(f"DEBUG: Erro ao salvar task: {str(e)}", file=sys.stderr)
            return None

    def delete(self):
        db = get_db()
        tasks_collection = db["tasks"]
        result = tasks_collection.delete_one({"_id": ObjectId(self._id)})
        return result.deleted_count > 0

    @classmethod
    def get_by_id(cls, id):
        """Busca uma task pelo ID"""
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
            print(f"DEBUG: Erro ao buscar task: {str(e)}", file=sys.stderr)
        return None

    @staticmethod
    def get_all_for_user(user_id):
        db = get_db()
        tasks_collection = db["tasks"]
        
        import sys
        print("DEBUG: Iniciando busca de tasks", file=sys.stderr)
        print(f"DEBUG: user_id recebido: {user_id}", file=sys.stderr)
        print(f"DEBUG: tipo do user_id: {type(user_id)}", file=sys.stderr)
        
        # Converter para ObjectId na busca já que salvamos como ObjectId
        tasks_cursor = tasks_collection.find({"user_id": ObjectId(user_id)})
        tasks = []
        
        print("DEBUG: Tasks encontradas:", file=sys.stderr)
        for task_data in tasks_cursor:
            print(f"DEBUG: Task encontrada: {task_data}", file=sys.stderr)
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                expire_date=task_data['expire_date'],
                user_id=str(task_data['user_id']),
                _id=str(task_data['_id'])
            )
            tasks.append(task)
        
        print(f"DEBUG: Total de tasks encontradas: {len(tasks)}", file=sys.stderr)
        return tasks

    def to_dict(self):
        """Converte a task para dicionário"""
        return {
            'id': str(self._id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'expire_date': self.expire_date,
            'user_id': str(self.user_id)
        }

    def update(self, data):
        """Atualiza os dados da task"""
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'status' in data:
            self.status = data['status']
        if 'expire_date' in data:
            self.expire_date = data['expire_date']
        
        return self.save()
