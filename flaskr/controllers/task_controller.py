from flask import jsonify, request, g
from ..models.task import Task
from ..views.task_view import task_response, tasks_list_response
from .auth_controller import get_logged_user_id

def get_task_from_request(request):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")
    expire_date = data.get("expire_date")

    return {
        'title': title,
        'description': description,
        'status': status,
        'expire_date': expire_date,
        'user_id': g.user._id
    }

def get_task(id):
    task = Task.get_by_id(id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_response(task.__dict__)), 200

def get_all_tasks():
    tasks = Task.get_all_for_user(get_logged_user_id())
    return jsonify(tasks_list_response([task.__dict__ for task in tasks])), 200

def is_the_user_task(id):
    task = Task.get_by_id(id)
    if task and task.user_id == get_logged_user_id():
        return True
    return False

def create_new_task():
    task_data = get_task_from_request(request)
    task = Task(
        title=task_data['title'],
        description=task_data['description'],
        status=task_data['status'],
        expire_date=task_data['expire_date'],
        user_id=task_data['user_id']
    )
    task.save()  # Cria ou atualiza a tarefa
    return jsonify({"message": "Task created"}), 201

def update_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    task_data = get_task_from_request(request)
    task = Task.get_by_id(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Atualiza os atributos da tarefa
    task.title = task_data['title']
    task.description = task_data['description']
    task.status = task_data['status']
    task.expire_date = task_data['expire_date']
    task.user_id = task_data['user_id']
    
    task.save()  # Atualiza a tarefa no banco
    return jsonify({"message": "Task updated successfully"}), 204

def delete_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    task = Task.get_by_id(id)
    if task and task.delete():
        return jsonify({"message": "Task deleted successfully"}), 204
    return jsonify({"error": "Task not found"}), 404
