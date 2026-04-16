const apiUrl = "/api/tasks/";

document.addEventListener("DOMContentLoaded", fetchTasks);

document.getElementById("taskForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const taskData = {
    nurse: document.getElementById("nurse").value,
    patient_name: document.getElementById("patient_name").value,
    task_description: document.getElementById("task_description").value,
    schedule: document.getElementById("schedule").value,
    status: document.getElementById("status").value
  };

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(taskData)
  });

  if (response.ok) {
    document.getElementById("taskForm").reset();
    fetchTasks();
  } else {
    const error = await response.json();
    alert("Error adding task: " + JSON.stringify(error));
  }
});

async function fetchTasks() {
  const response = await fetch(apiUrl);
  const tasks = await response.json();

  const taskList = document.getElementById("taskList");
  taskList.innerHTML = "";

  tasks.forEach(task => {
    const taskCard = document.createElement("div");
    taskCard.className = "border rounded-lg p-4 shadow-sm bg-gray-50";

    taskCard.innerHTML = `
      <h3 class="text-lg font-bold">${task.patient_name}</h3>
      <p><strong>Description:</strong> ${task.task_description}</p>
      <p><strong>Status:</strong> ${task.status}</p>
      <p><strong>Schedule:</strong> ${new Date(task.schedule).toLocaleString()}</p>
      <div class="mt-3 flex gap-2">
        <button onclick="markCompleted(${task.id})" class="bg-green-600 text-white px-3 py-1 rounded">Complete</button>
        <button onclick="deleteTask(${task.id})" class="bg-red-600 text-white px-3 py-1 rounded">Delete</button>
      </div>
    `;

    taskList.appendChild(taskCard);
  });
}

async function markCompleted(taskId) {
  const getResponse = await fetch(`${apiUrl}${taskId}/`);
  const task = await getResponse.json();

  task.status = "completed";

  const response = await fetch(`${apiUrl}${taskId}/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(task)
  });

  if (response.ok) {
    fetchTasks();
  } else {
    alert("Failed to update task.");
  }
}

async function deleteTask(taskId) {
  const response = await fetch(`${apiUrl}${taskId}/`, {
    method: "DELETE"
  });

  if (response.ok) {
    fetchTasks();
  } else {
    alert("Failed to delete task.");
  }
}