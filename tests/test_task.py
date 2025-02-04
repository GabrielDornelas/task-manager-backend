import pytest
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
from flaskr.infra.db import get_db

@pytest.fixture
def auth_headers(client):
    """Fixture that creates a user and returns the authentication header"""
    # Register user
    client.post('/auth/register', json={
        'username': 'task_user',
        'password': 'task_pass',
        'email': 'task@example.com'
    })

    # Login
    response = client.post('/auth/login', json={
        'username': 'task_user',
        'password': 'task_pass'
    })
    token = json.loads(response.data)['token']

    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_task():
    """Fixture with example data for a task"""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.now() + timedelta(days=1)).isoformat()
    }


def test_create_task(client, auth_headers, sample_task):
    """Test of task creation"""
    response = client.post('/task', headers=auth_headers, json=sample_task)
    assert response.status_code == 201

    # Verify if created_at was defined
    data = response.get_json()
    task_id = data['id']

    db = get_db()
    task = db.tasks.find_one({'_id': ObjectId(task_id)})
    assert 'created_at' in task
    assert isinstance(task['created_at'], datetime)

def test_get_tasks(client, auth_headers, sample_task):
    """Test of task listing"""
    # Create a task first
    client.post('/task', headers=auth_headers, json=sample_task)

    # Search all tasks
    response = client.get('/task', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

    assert data[0]['title'] == sample_task['title']

def test_get_single_task(client, auth_headers, sample_task):
    """Test of searching a specific task"""
    # Create a task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']

    # Search the created task
    response = client.get(f'/task/{task_id}', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == sample_task['title']


def test_update_task(client, auth_headers, sample_task):
    """Test of task update"""
    # Create a task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']

    # Update the task
    updated_data = sample_task.copy()
    updated_data['title'] = 'Updated Title'

    response = client.put(
        f'/task/{task_id}',
        headers=auth_headers,
        json=updated_data
    )
    assert response.status_code == 204

    # Verify if it was updated
    get_response = client.get(f'/task/{task_id}', headers=auth_headers)
    data = json.loads(get_response.data)
    assert data['title'] == 'Updated Title'


def test_delete_task(client, auth_headers, sample_task):
    """Test of task deletion"""
    # Create a task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']

    # Delete the task
    response = client.delete(f'/task/{task_id}', headers=auth_headers)
    assert response.status_code == 204


    # Verify if it was deleted
    get_response = client.get(f'/task/{task_id}', headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_access(client, sample_task):
    """Test of unauthorized access"""
    response = client.get('/task')
    assert response.status_code == 401


def test_access_other_user_task(client, auth_headers, sample_task):
    """Test of accessing another user's task"""
    # Create a task with the first user
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']

    # Create and login with the second user
    client.post('/auth/register', json={
        'username': 'other_user',
        'password': 'other_pass',
        'email': 'other@example.com'
    })

    login_response = client.post('/auth/login', json={
        'username': 'other_user',
        'password': 'other_pass'
    })
    other_token = json.loads(login_response.data)['token']
    other_headers = {'Authorization': f'Bearer {other_token}'}

    # Try to access the first user's task
    response = client.get(f'/task/{task_id}', headers=other_headers)
    assert response.status_code == 403


def test_invalid_task_data(client, auth_headers):
    """Test of task creation with invalid data"""
    invalid_task = {
        'title': '',  # empty title
        'description': 'Test Description',
        'status': 'invalid_status',  # invalid status
        'expire_date': 'invalid_date'  # invalid date
    }

    response = client.post('/task', headers=auth_headers, json=invalid_task)
    assert response.status_code == 400
