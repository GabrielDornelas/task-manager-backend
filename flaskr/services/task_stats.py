from datetime import datetime
from ..models.task import Task
from ..infra.metrics import update_task_status_metrics
from typing import Dict

def calculate_task_stats(user_id: str) -> Dict:
    """Calcula estatísticas das tasks do usuário"""
    tasks = Task.get_all_for_user(user_id)
    
    status_counts = {
        'pending': 0,
        'in_progress': 0,
        'completed': 0
    }
    
    overdue_count = 0
    total_age = 0
    
    now = datetime.now()
    
    for task in tasks:
        # Contagem por status
        status_counts[task.status] += 1
        
        # Verificar tasks atrasadas
        if task.expire_date < now and task.status != 'completed':
            overdue_count += 1
        
        # Calcular idade
        age = (now - task.created_at).days if hasattr(task, 'created_at') else 0
        total_age += age
    
    # Atualizar métricas
    update_task_status_metrics(status_counts)
    
    avg_age = total_age / len(tasks) if tasks else 0
    
    return {
        'total_tasks': len(tasks),
        'status_counts': status_counts,
        'overdue_tasks': overdue_count,
        'average_age': avg_age
    } 