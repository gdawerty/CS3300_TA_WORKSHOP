import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return all tasks with a default priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


def test_get_tasks_returns_existing_priority(client):
    """Preserve and return priority values already stored on tasks."""
    tasks[0]['priority'] = 'High'

    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['priority'] == 'High'
    assert data[1]['priority'] == 'Medium'


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_accepts_supported_priorities(client, priority):
    """Create a task for each supported priority value."""
    response = client.post(
        '/api/tasks',
        json={"title": "Prioritized task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


def test_add_task_defaults_missing_priority_to_medium(client):
    """Default a task's priority to Medium when it is omitted."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['priority'] == 'Medium'

    get_response = client.get('/api/tasks')
    returned_task = get_response.get_json()[-1]
    assert returned_task['priority'] == 'Medium'


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities that are not supported values."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "Urgent"}
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_add_task_success(client):
    """Create a task without changing existing title behavior."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    assert response.get_json()['title'] == "Test new task"
    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_missing_title(client):
    """Reject task requests without a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()
    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
