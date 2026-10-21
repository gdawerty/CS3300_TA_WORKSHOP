from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

VALID_PRIORITIES = {"Low", "Medium", "High"}
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"}
]
next_id = 3


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with a normalized priority."""
    response_tasks = []
    for task in tasks:
        response_task = dict(task)
        response_task["priority"] = normalize_priority(
            response_task.get("priority")
        )
        response_tasks.append(response_task)
    return jsonify(response_tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with a validated priority."""
    global next_id
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    new_task = {
        "id": next_id,
        "title": data['title'],
        "priority": normalize_priority(data.get("priority"))
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete the task matching the supplied ID."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


def normalize_priority(priority):
    """Return a supported priority or the default priority."""
    if priority in VALID_PRIORITIES:
        return priority
    return DEFAULT_PRIORITY


if __name__ == '__main__':
    app.run(debug=True, port=5000)
