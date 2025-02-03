import pytest
import json
from datetime import datetime, timedelta

@pytest.fixture
def auth_headers(client):
    """Fixture que cria um usuário e retorna o header de autenticação"""
    # Registrar usuário
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
    """Fixture com dados de exemplo para uma task"""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'pending',
        'expire_date': (datetime.now() + timedelta(days=1)).isoformat()
    }

def test_create_task(client, auth_headers, sample_task):
    """Teste de criação de task"""
    response = client.post(
        '/task',
        headers=auth_headers,
        json=sample_task
    )
    assert response.status_code == 201
    assert b"Task created" in response.data

def test_get_tasks(client, auth_headers, sample_task):
    """Teste de listagem de tasks"""
    # Criar uma task primeiro
    client.post('/task', headers=auth_headers, json=sample_task)
    
    # Buscar todas as tasks
    response = client.get('/task', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['title'] == sample_task['title']

def test_get_single_task(client, auth_headers, sample_task):
    """Teste de busca de task específica"""
    # Criar uma task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']
    
    # Buscar a task criada
    response = client.get(f'/task/{task_id}', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == sample_task['title']

def test_update_task(client, auth_headers, sample_task):
    """Teste de atualização de task"""
    # Criar uma task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']
    
    # Atualizar a task
    updated_data = sample_task.copy()
    updated_data['title'] = 'Updated Title'
    response = client.put(
        f'/task/{task_id}',
        headers=auth_headers,
        json=updated_data
    )
    assert response.status_code == 204

    # Verificar se foi atualizada
    get_response = client.get(f'/task/{task_id}', headers=auth_headers)
    data = json.loads(get_response.data)
    assert data['title'] == 'Updated Title'

def test_delete_task(client, auth_headers, sample_task):
    """Teste de deleção de task"""
    # Criar uma task
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']
    
    # Deletar a task
    response = client.delete(f'/task/{task_id}', headers=auth_headers)
    assert response.status_code == 204

    # Verificar se foi deletada
    get_response = client.get(f'/task/{task_id}', headers=auth_headers)
    assert get_response.status_code == 404

def test_unauthorized_access(client, sample_task):
    """Teste de acesso não autorizado"""
    response = client.get('/task')
    assert response.status_code == 401

def test_access_other_user_task(client, auth_headers, sample_task):
    """Teste de acesso à task de outro usuário"""
    # Criar uma task com primeiro usuário
    create_response = client.post('/task', headers=auth_headers, json=sample_task)
    task_id = json.loads(create_response.data)['id']
    
    # Criar e logar com segundo usuário
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
    
    # Tentar acessar task do primeiro usuário
    response = client.get(f'/task/{task_id}', headers=other_headers)
    assert response.status_code == 403

def test_invalid_task_data(client, auth_headers):
    """Teste de criação de task com dados inválidos"""
    invalid_task = {
        'title': '',  # título vazio
        'description': 'Test Description',
        'status': 'invalid_status',  # status inválido
        'expire_date': 'invalid_date'  # data inválida
    }
    response = client.post('/task', headers=auth_headers, json=invalid_task)
    assert response.status_code == 400
