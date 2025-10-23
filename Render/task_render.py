import os
from datetime import date

import requests
from flask import Blueprint, jsonify
from flask import render_template, request, url_for, redirect, flash, session
from flask_login import login_required

task = Blueprint('task', __name__)

@task.route('/project/<int:project_id>/create_task')
@login_required
def create_task(project_id):
    token = request.cookies.get('token')
    return render_template('create_task.html', token=token, project_id=project_id)

@task.route('/project/<int:project_id>/task/<int:task_id>')
@login_required
def task_information(project_id, task_id):
    token = request.cookies.get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    task_data = requests.get(os.getenv('BASE_URL') + f'api/task/{task_id}', headers=headers).json()
    return render_template('task.html', task=task_data, token=token)

@task.route('/tasks')
@login_required
def tasks():
    token = request.cookies.get('token')
    return render_template('tasks.html', token=token)

@task.route('/remove-tasks', methods=['DELETE'])
def remove_tasks():
    data = request.get_json()

    task_ids = data.get('task_ids', [])
    token = request.cookies.get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    project_id = requests.get(os.getenv('BASE_URL') + f"/api/project/task/{task_ids[0]}", headers=headers).json()["project_id"][0]
    for task in task_ids:
        requests.delete(os.getenv('BASE_URL') + f'/api/task/{task}', headers=headers).json()
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'})
    tasks = requests.get(os.getenv('BASE_URL') + f'/api/project/{project_id}/task', headers=headers).json()
    if tasks is None:
        tasks = []
    return jsonify({'success': True, 'tasks': tasks})

#@task.route('/update_task', methods=['POST'])
#@login_required
#def update_task(current_user_id):
#    token = request.cookies.get('token')
#    task_name = request.form.get('task_name')
#    description = request.form.get('description')
#    status = request.form.get('status')
#    due_date = request.form.get('tas_due_date')
#    if due_date < date.today().isoformat():
#        flash("Due date cannot be in the past.", "error")
#        return redirect(url_for('task.update_task', token=token))
#    json = {'id': current_user_id, 'task_name': task_name, 'username': username, 'first_name': first_name,
#            'last_name': last_name, 'birthdate': birthdate, 'phone_number': phone}
#    response = requests.post(os.getenv('BASE_URL') + f'api/user/{current_user.id}', json=json)
#    if response.status_code == 200:
#        flash('Profile updated successfully!', 'success')
#    return redirect(url_for('auth.profile', id=current_user.id))