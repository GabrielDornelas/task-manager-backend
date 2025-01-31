import datetime
from flask import Blueprint, jsonify, request, g
from werkzeug.exceptions import abort
from bson import ObjectId
from flaskr.auth import login_required
from flaskr.db import get_db, handle_collection_to_list


bp = Blueprint('blog', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    """ Rota para listar todos os posts """
    try:
        db = get_db()
        posts_collection = db["posts"]
        filter = {"author_id": ObjectId(g.user['_id'])}
        posts = handle_collection_to_list(posts_collection.find(filter))
        return jsonify(posts)
    except Exception as error:
        return jsonify({"error": f"{error} happen."}), 400


@bp.route('/create', methods=['POST'])
@login_required
def create():
    """ Rota para criar um novo post """
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    if not title:
        return jsonify({"error": "Title is required."}), 400

    db = get_db()
    posts_collection = db["posts"]  # Acessa a collection correta

    try:
        # Insere o usuário na collection
        posts_collection.insert_one({
            "title": title,
            "body": body,
            "author_id": g.user['_id'],
            "created": datetime.datetime.now()
        })
        return jsonify({"message": "Post registered successfully!"}), 201
    except Exception as error:
        return jsonify({"error": f"{error} happen."}), 400


@bp.route('/<id>/update', methods=['PUT'])
@login_required
def update(id):
    """ Rota para atualizar um post existente """
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')

    if not title:
        return jsonify({"error": "Title is required."}), 400

    db = get_db()
    posts_collection = db["posts"]
    filter = {"_id": ObjectId(id)}
    update = {
        '$set': {
            "title": title,
            "body": body,
            "created": datetime.datetime.now()
        }
    }    
    posts_collection.update_one(filter, update)
    
    return jsonify({"message": "Post updated successfully!"}), 200


@bp.route('/<id>/delete', methods=['DELETE'])
@login_required
def delete(id):
    """ Rota para excluir um post """
    db = get_db()
    posts_collection = db["posts"]
    filter = {"_id": ObjectId(id)}
    posts_collection.delete_one(filter)
    return jsonify({"message": "Post deleted successfully!"}), 200
