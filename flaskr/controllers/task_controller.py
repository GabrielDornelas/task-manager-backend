from flask import jsonify, request, g
from ..utils import handle_collection_to_list
from ..models.task import get_task_by_id, get_tasks_from_user, create_task, update_task, delete_task

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
        'user_id': g.user["_id"]
    }

def get_task(id):
    task = handle_collection_to_list(get_task_by_id(id))
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return task

def get_all_tasks():
    tasks = handle_collection_to_list(get_tasks_from_user(g.user['_id']))
    return jsonify(tasks), 200

def is_the_user_task(id):
    task = get_task_by_id(id)
    if task and task['user_id'] == g.user['_id']:
        return True
    return False

def create_new_task():
    task = get_task_from_request(request)
    create_task(task)
    return jsonify({"message": "Task created"}), 201

def update_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    task = get_task_from_request(request)
    task['_id'] = id
    updated = update_task(task)
    if not updated:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task updated successfully"}), 204

def delete_existing_task(id):
    if not is_the_user_task(id):
        return jsonify({"error": "Not user's task"}), 403

    deleted = delete_task(id)
    if not deleted:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted successfully"}), 204
