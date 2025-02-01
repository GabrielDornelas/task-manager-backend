from flask import Blueprint
from ..controllers.task_controller import get_task, get_all_tasks, create_new_task, update_existing_task, delete_existing_task

task_bp = Blueprint('task', __name__)

task_bp.route('/task', methods=["POST"])(create_new_task)
task_bp.route('/task', methods=["GET"])(get_all_tasks)
task_bp.route('/task/<id>', methods=["GET"])(get_task)
task_bp.route('/task/<id>', methods=["PUT"])(update_existing_task)
task_bp.route('/task/<id>', methods=["DELETE"])(delete_existing_task)
