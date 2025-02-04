from flask import jsonify, request, g
from ..models.task import Task
from datetime import datetime
from ..infra.redis_client import (
    cache_task_list,
    get_cached_task_list
)
from ..controllers.auth_controller import login_required
import sys

def check_task_owner(task):
    """Verifica se a task pertence ao usuário logado"""
    return str(task.user_id) == str(g.user._id)

@login_required
def get_task(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    if not check_task_owner(task):
        return jsonify({"error": "Forbidden"}), 403
        
    return jsonify(task.to_dict()), 200

@login_required
def get_all_tasks():
    user_id = str(g.user._id)
    
    # Tentar pegar do cache primeiro
    cached_tasks = get_cached_task_list(user_id)
    if cached_tasks:
        return jsonify(cached_tasks), 200

    tasks = Task.get_all_for_user(user_id)
    tasks_data = [task.to_dict() for task in tasks]
    
    # Armazenar em cache
    cache_task_list(user_id, tasks_data)
    return jsonify(tasks_data), 200

@login_required
def create_new_task():
    try:
        data = request.get_json()
        
        # Validar dados
        if not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        
        if data.get('status') and data.get('status') not in ['pending', 'in_progress', 'completed']:
            return jsonify({"error": "Invalid status"}), 400
        
        if data.get('expire_date'):
            try:
                datetime.fromisoformat(data['expire_date'])
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid expire_date format"}), 400

        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            expire_date=data.get('expire_date'),
            user_id=g.user._id
        )
        task_id = task.save()
        
        if not task_id:
            return jsonify({"error": "Error creating task"}), 500
        
        return jsonify({"message": "Task created", "id": str(task_id)}), 201
    except Exception as e:
        print(f"DEBUG: Erro ao criar task: {str(e)}", file=sys.stderr)
        return jsonify({"error": "Internal server error"}), 500

@login_required
def update_task(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    if not check_task_owner(task):
        return jsonify({"error": "Forbidden"}), 403
        
    data = request.get_json()
    task.update(data)
    return '', 204

@login_required
def delete_task(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    if not check_task_owner(task):
        return jsonify({"error": "Forbidden"}), 403
        
    task.delete()
    return '', 204
