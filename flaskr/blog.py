from flask import Blueprint, jsonify, request, g
from werkzeug.exceptions import abort

from flaskr.auth import login_required, get_user_from_jwt
from flaskr.db import get_db


bp = Blueprint('blog', __name__)

@bp.route('/', methods=['GET'])
@login_required
def index():
    """ Rota para listar todos os posts """
    token = request.headers.get('Authorization')
    if token:
        try:
            user = get_user_from_jwt(token)
            db = get_db()
            posts_collection = db["posts"]
            posts = posts_collection.find({"username": user['username']})
            posts_list = [
                {
                    "id": post["id"],
                    "title": post["title"],
                    "body": post["body"],
                    "created": post["created"],
                    "author_id": post["author_id"],
                    "username": post["username"]
                }
                for post in posts
            ]
            return jsonify(posts_list)
        except Exception as error:
            print(error)    
    
    return None


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
    db.execute(
        'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
        (title, body, g.user['id'])
    )
    db.commit()
    return jsonify({"message": "Post created successfully!"}), 201


def get_post(id, check_author=True):
    """ Função para buscar um post específico """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=['PUT'])
@login_required
def update(id):
    """ Rota para atualizar um post existente """
    post = get_post(id)

    data = request.get_json()
    title = data.get('title')
    body = data.get('body')

    if not title:
        return jsonify({"error": "Title is required."}), 400

    db = get_db()
    db.execute(
        'UPDATE post SET title = ?, body = ? WHERE id = ?',
        (title, body, id)
    )
    db.commit()
    
    return jsonify({"message": "Post updated successfully!"}), 200


@bp.route('/<int:id>/delete', methods=['DELETE'])
@login_required
def delete(id):
    """ Rota para excluir um post """
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    
    return jsonify({"message": "Post deleted successfully!"}), 200
