import functools
from flask import jsonify, g

def login_required(view):
    """ Decorador para exigir autenticação via JWT """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"error": "Authentication required"}), 401
        return view(**kwargs)

    return wrapped_view

def get_logged_user_id():
    id = g.user['_id'] if g.user else None
    return id
