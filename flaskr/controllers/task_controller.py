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
def create_task():
    """Criar uma nova task"""
    data = request.get_json()
    
    # Validar dados
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    # Validar campos obrigatórios
    if not all(k in data for k in ['title', 'description', 'status']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Validar título não vazio
    if not data['title'].strip():
        return jsonify({'error': 'Title cannot be empty'}), 400
        
    # Validar status
    valid_status = ['pending', 'in_progress', 'completed']
    if data['status'] not in valid_status:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_status)}'}), 400
        
    # Validar data de expiração
    if data.get('expire_date'):
        try:
            datetime.fromisoformat(data['expire_date'])
        except ValueError:
            return jsonify({'error': 'Invalid expire_date format'}), 400
    
    # Criar task
    task = Task(
        title=data['title'],
        description=data['description'],
        status=data['status'],
        expire_date=data.get('expire_date'),
        user_id=g.user._id
    )
    
    # Salvar
    task_id = task.save()
    if task_id:
        return jsonify({
            'message': 'Task created',
            'id': str(task_id),
            'task': task.to_dict()
        }), 201
    
    return jsonify({'error': 'Failed to create task'}), 400

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
