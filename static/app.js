const supportedPriorities = ['Low', 'Medium', 'High'];
const defaultPriority = 'Medium';

document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskText = document.createElement('span');
        const priority = supportedPriorities.includes(task.priority)
            ? task.priority
            : defaultPriority;
        const priorityLabel = document.createElement('span');
        const deleteButton = document.createElement('button');

        taskText.textContent = task.title;
        priorityLabel.textContent = priority;
        priorityLabel.className = `priority priority-${priority.toLowerCase()}`;
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete-btn';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        li.appendChild(taskText);
        li.appendChild(priorityLabel);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput.value || defaultPriority;

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = defaultPriority;
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
