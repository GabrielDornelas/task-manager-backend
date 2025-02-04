import pytest
from datetime import datetime, timedelta
from bson import ObjectId

def test_metrics_endpoint_requires_auth(client):
    """Test of unauthorized access to metrics"""
    response = client.get('/metrics')
    assert response.status_code == 401


def test_metrics_endpoint(client, auth_headers):
    """Test of metrics endpoint"""
    # Create some tasks to test
    sample_task = {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    }

    # Create 3 tasks with different statuses
    client.post('/task', headers=auth_headers, json=sample_task)
    sample_task['status'] = 'in_progress'
    client.post('/task', headers=auth_headers, json=sample_task)
    sample_task['status'] = 'completed'
    client.post('/task', headers=auth_headers, json=sample_task)

    # Test metrics endpoint
    response = client.get('/metrics', headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert 'active_users' in data
    assert 'tasks_by_status' in data
    assert 'avg_response_time' in data
    assert 'error_rate' in data
    assert 'timestamp' in data

    # Verify task count
    assert data['tasks_by_status']['pending'] == 1
    assert data['tasks_by_status']['in_progress'] == 1
    assert data['tasks_by_status']['completed'] == 1

    # Verify active users
    assert data['active_users'] >= 1  # At least the test user 