import pytest
from datetime import datetime, timedelta

def test_metrics_endpoint(client, auth_headers):
    """Teste do endpoint de métricas"""
    # Criar algumas tasks para testar
    sample_task = {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    
    # Criar 3 tasks com status diferentes
    client.post('/task', headers=auth_headers, json=sample_task)
    sample_task['status'] = 'in_progress'
    client.post('/task', headers=auth_headers, json=sample_task)
    sample_task['status'] = 'completed'
    client.post('/task', headers=auth_headers, json=sample_task)
    
    # Testar endpoint de métricas
    response = client.get('/metrics')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'active_users' in data
    assert 'tasks_by_status' in data
    assert 'avg_response_time' in data
    assert 'error_rate' in data
    assert 'timestamp' in data
    
    # Verificar contagem de tasks
    assert data['tasks_by_status']['pending'] == 1
    assert data['tasks_by_status']['in_progress'] == 1
    assert data['tasks_by_status']['completed'] == 1 