import pytest

import app as app_module

app = app_module.app
tasks = app_module.tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task store before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return existing tasks with a default priority."""
    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_with_priority(client, priority):
    """Create a task with each supported priority."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority}
    )

    assert response.status_code == 201
    task = response.get_json()
    assert task['title'] == f"{priority} task"
    assert task['priority'] == priority


def test_add_task_missing_priority_defaults_to_medium(client):
    """Default a task's priority to Medium when it is omitted."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'

    tasks_response = client.get('/api/tasks')
    created_task = tasks_response.get_json()[-1]
    assert created_task['priority'] == 'Medium'


def test_add_task_invalid_priority_defaults_to_medium(client):
    """Default unsupported priorities to Medium instead of storing them."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid priority task", "priority": "Urgent"}
    )

    assert response.status_code == 201
    task = response.get_json()
    assert task['priority'] == 'Medium'
    assert all(
        stored_task.get('priority', 'Medium') != 'Urgent'
        for stored_task in tasks
    )


def test_get_tasks_normalizes_missing_and_invalid_priorities(client):
    """Normalize missing and invalid priorities in GET responses."""
    tasks.append({"id": 3, "title": "High task", "priority": "High"})
    tasks.append({"id": 4, "title": "Invalid task", "priority": "Urgent"})
    tasks.append({"id": 5, "title": "Missing task"})

    response = client.get('/api/tasks')

    assert response.status_code == 200
    priorities = {
        task['title']: task['priority'] for task in response.get_json()
    }
    assert priorities['Project-1 Report'] == 'Medium'
    assert priorities['Project-2 MMFs'] == 'Medium'
    assert priorities['High task'] == 'High'
    assert priorities['Invalid task'] == 'Medium'
    assert priorities['Missing task'] == 'Medium'


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response = client.post('/api/tasks', json={})
    assert response.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200

    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
