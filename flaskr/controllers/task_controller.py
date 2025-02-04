from flask import jsonify, request, g
from ..models.task import Task
from ..views.task_view import task_response, tasks_list_response
from .auth_controller import get_logged_user_id
from datetime import datetime
from ..infra.redis_client import (
    cache_task, get_cached_task, cache_task_list,
    get_cached_task_list, invalidate_task_cache,
    invalidate_user_task_list
)

def get_task_from_request(request):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")
    expire_date = data.get("expire_date")

    import sys
    print(f"DEBUG: g.user._id: {g.user._id}", file=sys.stderr)
    print(f"DEBUG: tipo do g.user._id: {type(g.user._id)}", file=sys.stderr)

    return {
        'title': title,
        'description': description,
        'status': status,
        'expire_date': expire_date,
        'user_id': g.user._id
    }

def get_task(id):
    # Tentar pegar do cache primeiro
    cached_task = get_cached_task(id)
    if cached_task:
        return jsonify(cached_task), 200

    task = Task.get_by_id(id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    # Armazenar em cache
    task_data = task_response(task.__dict__)
    cache_task(id, task_data)
    return jsonify(task_data), 200

def get_all_tasks():
    user_id = str(get_logged_user_id())
    
    # Tentar pegar do cache primeiro
    cached_tasks = get_cached_task_list(user_id)
    if cached_tasks:
        return jsonify(cached_tasks), 200

    tasks = Task.get_all_for_user(get_logged_user_id())
    tasks_data = tasks_list_response([task.__dict__ for task in tasks])
    
    # Armazenar em cache
    cache_task_list(user_id, tasks_data)
    return jsonify(tasks_data), 200

def is_the_user_task(id):
    task = Task.get_by_id(id)
    if task and task.user_id == get_logged_user_id():
        return True
    return False

def create_new_task():
    task_data = get_task_from_request(request)
    
    import sys
    print(f"DEBUG: Task data antes de criar: {task_data}", file=sys.stderr)
    
    # Validar dados
    if not task_data['title']:
        return jsonify({"error": "Title is required"}), 400
    
    if task_data['status'] not in ['pending', 'in_progress', 'completed']:
        return jsonify({"error": "Invalid status"}), 400
    
    try:
        datetime.fromisoformat(task_data['expire_date'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid expire_date format"}), 400

    task = Task(
        title=task_data['title'],
        description=task_data['description'],
        status=task_data['status'],
        expire_date=task_data['expire_date'],
        user_id=task_data['user_id']
    )
    task_id = task.save()

    # Invalidar cache de lista
    invalidate_user_task_list(str(task_data['user_id']))
    
    return jsonify({"message": "Task created", "id": str(task_id)}), 201

def update_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    task_data = get_task_from_request(request)
    task = Task.get_by_id(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Validar dados
    if not task_data['title']:
        return jsonify({"error": "Title is required"}), 400
    
    if task_data['status'] not in ['pending', 'in_progress', 'completed']:
        return jsonify({"error": "Invalid status"}), 400
    
    try:
        datetime.fromisoformat(task_data['expire_date'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid expire_date format"}), 400
    
    # Atualiza os atributos da tarefa
    task.title = task_data['title']
    task.description = task_data['description']
    task.status = task_data['status']
    task.expire_date = task_data['expire_date']
    task.user_id = task_data['user_id']
    
    task.save()

    # Invalidar caches
    invalidate_task_cache(id)
    invalidate_user_task_list(str(task_data['user_id']))
    
    return jsonify({"message": "Task updated successfully"}), 204

def delete_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    task = Task.get_by_id(id)
    if task and task.delete():
        # Invalidar caches
        invalidate_task_cache(id)
        invalidate_user_task_list(str(task.user_id))
        return jsonify({"message": "Task deleted successfully"}), 204
    return jsonify({"error": "Task not found"}), 404
