from flask import Blueprint
from ..controllers.task_controller import (
    get_task, get_all_tasks, create_task,
    update_task, delete_task
)

task_bp = Blueprint('task', __name__)

task_bp.route('/task', methods=["POST"])(create_task)
task_bp.route('/task', methods=["GET"])(get_all_tasks)
task_bp.route('/task/<task_id>', methods=["GET"])(get_task)
task_bp.route('/task/<task_id>', methods=["PUT"])(update_task)
task_bp.route('/task/<task_id>', methods=["DELETE"])(delete_task)
