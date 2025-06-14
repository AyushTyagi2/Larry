import json
import os

# Path to the task file
TASK_FILE = "tasks/to_do/tasks.json"

# Initialize tasks file if not exists
def initialize_task_file():
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as file:
            json.dump({"tasks": []}, file)

# Add a task
def add_task(task_name):
    initialize_task_file()
    with open(TASK_FILE, "r") as file:
        data = json.load(file)
    data["tasks"].append({"task": task_name, "done": False})
    with open(TASK_FILE, "w") as file:
        json.dump(data, file)
    print(f"Task '{task_name}' added to your to-do list.")

# Get all tasks
def get_tasks():
    initialize_task_file()
    with open(TASK_FILE, "r") as file:
        data = json.load(file)
    tasks = data["tasks"]
    if not tasks:
        print("Your to-do list is empty.")
    else:
        print("Here’s your to-do list:")
        for i, task in enumerate(tasks, 1):
            status = "Done" if task["done"] else "Pending"
            print(f"{i}. {task['task']} - {status}")

# Mark a task as done
def mark_done(task_index):
    initialize_task_file()
    with open(TASK_FILE, "r") as file:
        data = json.load(file)
    try:
        task = data["tasks"][task_index - 1]
        task["done"] = True
        with open(TASK_FILE, "w") as file:
            json.dump(data, file)
        print(f"Task '{task['task']}' marked as done!")
    except IndexError:
        print("Task number not found.")

# Delete a task
def delete_task(task_index):
    initialize_task_file()
    with open(TASK_FILE, "r") as file:
        data = json.load(file)
    try:
        task = data["tasks"].pop(task_index - 1)
        with open(TASK_FILE, "w") as file:
            json.dump(data, file)
        print(f"Task '{task['task']}' has been deleted.")
    except IndexError:
        print("Task number not found.")
