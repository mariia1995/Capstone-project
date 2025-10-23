import sqlite3

from flask import Blueprint
from flask import jsonify, request

from DB.task_db import TaskDB
from API.project_api import token_required
from Objects.task import Task

task_api = Blueprint('task_api', __name__)
secret_key = 'secret'


@task_api.route('/api/project/<int:project_id>/task', methods=['POST'])
@token_required
def create_task(project_id, current_user_id):
    data = request.get_json()
    data["creator_id"] = current_user_id
    data["assignee"] = current_user_id
    data["project_id"] = project_id
    task = Task.from_dict(data)
    try:
        with TaskDB() as db:
            result = db.create_task(task)
        if result:
            return jsonify({'result': 'Creation successful', "task_id": result}), 200
        else:
            return jsonify({'error': 'Error during creation'}), 404
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Error during creation', "message": "Task with the same name already exists"}), 409
    except Exception as e:
        return jsonify({'error': 'Error during creation', "message": str(e)}), 404


@task_api.route('/api/task/<int:id>', methods=['GET'])
@token_required
def get_task_by_id(id, current_user_id):
    with TaskDB() as db:
        task = db.get_task_info(id)
    if task:
        return jsonify(task), 200
    else:
        return jsonify({'error': 'Task not found'}), 404


@task_api.route('/api/project/<int:project_id>/task', methods=['GET'])
@token_required
def get_tasks(project_id, current_user_id):
    with TaskDB() as db:
        task = db.get_tasks_by_project(project_id)
    if task:
        return jsonify(task), 200
    else:
        return jsonify({'error': 'Tasks not found'}), 404


@task_api.route('/api/user/task', methods=['GET'])
@token_required
def get_tasks_by_user(current_user_id):
    with TaskDB() as db:
        task = db.get_tasks_by_user(current_user_id)
    if task:
        return jsonify(task), 200
    else:
        return jsonify({'error': 'Tasks not found'}), 404


@task_api.route('/api/project/task/<int:task_id>', methods=['POST'])
@token_required
def update_task(current_user_id, task_id):
    data = request.get_json()
    #task = Task.from_dict(data)
    data['id'] = task_id

    with TaskDB() as db:
        result = db.update_task(data)
    if result != "Error":
        return jsonify({'result': 'Update successful'}), 200
    elif result == "Error":
        return jsonify({'error': 'You do not have permissions to modify the task!'}), 400
    else:
        return jsonify({'error': 'Error during update'}), 404

@task_api.route('/api/task/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id, current_user_id):
    with TaskDB() as db:
        task = db.delete_task(task_id)
    if task:
        return jsonify({'message': 'Task was deleted'}), 200
    else:
        return jsonify({'error': 'Tasks not found'}), 404

@task_api.route('/api/project/task/<int:task_id>', methods=['GET'])
@token_required
def get_project_by_task(task_id, current_user_id):
    with TaskDB() as db:
        project_id = db.get_project_by_task(task_id)
    if project_id:
        return jsonify({'project_id': project_id}), 200
    else:
        return jsonify({'error': 'Project not found'}), 404