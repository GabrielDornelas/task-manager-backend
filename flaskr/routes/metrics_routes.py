from ..controllers.metrics_controller import get_metrics, metrics_bp
from ..controllers.auth_controller import login_required


# Registering Blueprint routes
metrics_bp.route('/metrics', methods=['GET'])(login_required(get_metrics))
