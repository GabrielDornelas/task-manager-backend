from bson import ObjectId
from ..infra.db import get_db

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
        
        import sys
        print(f"DEBUG: Salvando task com user_id: {self.user_id}", file=sys.stderr)
        print(f"DEBUG: Tipo do user_id: {type(self.user_id)}", file=sys.stderr)
        
        # Primeiro, vamos verificar se o _id já existe
        if hasattr(self, '_id') and self._id:
            task_id = ObjectId(self._id)
        else:
            task_id = ObjectId()
            self._id = str(task_id)
        
        task_data = {
            "_id": task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "expire_date": self.expire_date,
            "user_id": ObjectId(self.user_id)  # Converter para ObjectId ao salvar
        }
        
        print(f"DEBUG: Task data para salvar: {task_data}", file=sys.stderr)
        
        try:
            if not hasattr(self, '_id') or not self._id:  # Se não tiver _id, é uma nova task
                result = tasks_collection.insert_one(task_data)
                print(f"DEBUG: Nova task criada com ID: {result.inserted_id}", file=sys.stderr)
            else:
                filter = {"_id": task_id}
                # Remover o _id do update para evitar erro
                update_data = task_data.copy()
                del update_data["_id"]
                result = tasks_collection.replace_one(filter, update_data, upsert=True)
                print(f"DEBUG: Task atualizada: {self._id} (matched: {result.matched_count}, modified: {result.modified_count}, upserted: {result.upserted_id})", file=sys.stderr)
            
            return self._id
        except Exception as e:
            print(f"DEBUG: Erro ao salvar task: {str(e)}", file=sys.stderr)
            raise

    def delete(self):
        db = get_db()
        tasks_collection = db["tasks"]
        result = tasks_collection.delete_one({"_id": ObjectId(self._id)})
        return result.deleted_count > 0

    @staticmethod
    def get_by_id(id):
        db = get_db()
        tasks_collection = db["tasks"]
        
        import sys
        print(f"DEBUG: Buscando task por ID: {id}", file=sys.stderr)
        
        task_data = tasks_collection.find_one({"_id": ObjectId(id)})
        
        print(f"DEBUG: Task encontrada: {task_data}", file=sys.stderr)
        
        if task_data:
            return Task(
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                expire_date=task_data['expire_date'],
                user_id=str(task_data['user_id']),  # Converter para string ao retornar
                _id=str(task_data['_id'])  # Converter para string ao retornar
            )
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
