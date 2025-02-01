from flask import Blueprint
from ..controllers.auth_controller import login_required
from ..controllers.task_controller import get_task, get_all_tasks, create_new_task, update_existing_task, delete_existing_task

task_bp = Blueprint('task', __name__)

task_bp.route('/task', methods=["POST"])(login_required(create_new_task))
task_bp.route('/task', methods=["GET"])(login_required(get_all_tasks))
task_bp.route('/task/<id>', methods=["GET"])(login_required(get_task))
task_bp.route('/task/<id>', methods=["PUT"])(login_required(update_existing_task))
task_bp.route('/task/<id>', methods=["DELETE"])(login_required(delete_existing_task))
