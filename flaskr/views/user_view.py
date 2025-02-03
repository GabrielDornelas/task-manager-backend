def user_response(user):
    """Formata um usuário para resposta"""
    return {
        "id": str(user._id),
        "username": user.username,
        "email": user.email
    }
