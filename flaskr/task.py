import datetime
from flask import Blueprint, jsonify, request, g
from bson import ObjectId
from flaskr.auth import login_required
from flaskr.db import get_db, handle_collection_to_list
from enum import Enum

class Status(Enum):
    UNTOUCHED = "Untouched"
    STARTED = "Started"
    FINISHED = "Finished"

bp = Blueprint('blog', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    """ Rota para listar todos os tasks """
    try:
        db = get_db()
        tasks_collection = db["tasks"]
        filter = {"user_id": ObjectId(g.user['_id'])}
        tasks = handle_collection_to_list(tasks_collection.find(filter))
        return jsonify(tasks)
    except Exception as error:
        return jsonify({"error": f"{error} happen."}), 400


@bp.route('/create', methods=['POST'])
@login_required
def create():
    """ Rota para criar um novo task """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    status = data.get('status')
    expire_date = data.get('expire_date')
    
    if not title:
        return jsonify({"error": "Title is required."}), 400

    if not expire_date:
        return jsonify({"error": "Expire date is required."}), 400
    
    if status not in {s.value for s in Status}:
        return jsonify({"error": "Invalid status. Allowed values: Untouched, Started, Finished"}), 400

    try:
        # Converte a string para um objeto datetime
        expire_date = datetime.datetime.fromisoformat(expire_date)

        # Verifica se a data está no futuro
        if expire_date <= datetime.datetime.now():
            return jsonify({"error": "Expire date must be in the future."}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM"}), 400

    db = get_db()
    tasks_collection = db["tasks"]  # Acessa a collection correta

    try:
        # Insere o usuário na collection
        tasks_collection.insert_one({
            "title": title,
            "description": description,
            "status": status,
            "user_id": g.user['_id'],
            "expire_date": expire_date
        })
        return jsonify({"message": "Task registered successfully!"}), 201
    except Exception as error:
        return jsonify({"error": f"{error} happen."}), 400


@bp.route('/<id>/update', methods=['PUT'])
@login_required
def update(id):
    """ Rota para atualizar um task existente """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    status = data.get('status')
    expire_date = data.get('expire_date')

    if not title:
        return jsonify({"error": "Title is required."}), 400

    if not expire_date:
        return jsonify({"error": "Expire date is required."}), 400

    if status not in {s.value for s in Status}:
        return jsonify({"error": "Invalid status. Allowed values: Untouched, Started, Finished"}), 400

    try:
        expire_date = datetime.datetime.fromisoformat(expire_date)
        if expire_date <= datetime.datetime.now():
            return jsonify({"error": "Expire date must be in the future."}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM"}), 400

    db = get_db()
    tasks_collection = db["tasks"]
    filter = {"_id": ObjectId(id)}
    update = {
        '$set': {
            "title": title,
            "description": description,
            "status": status,
            "expire_date": expire_date
        }
    }    
    tasks_collection.update_one(filter, update)
    
    return jsonify({"message": "Task updated successfully!"}), 200


@bp.route('/<id>/delete', methods=['DELETE'])
@login_required
def delete(id):
    """ Rota para excluir um task """
    db = get_db()
    tasks_collection = db["tasks"]
    filter = {"_id": ObjectId(id)}
    tasks_collection.delete_one(filter)
    return jsonify({"message": "Task deleted successfully!"}), 200
