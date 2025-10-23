import os

import requests
from flask import Blueprint
from flask import render_template, request, url_for, redirect, flash, session
from flask_login import login_required, current_user

import API.project_api

project = Blueprint('project', __name__)

@project.route('/create_project')
@login_required
def create_project():
    token = request.cookies.get('token')
    return render_template('create_project.html', token=token)

@project.route('/projects')
@login_required
def projects():
    token = request.cookies.get('token')
    return render_template('projects.html', token=token)


@project.route('/project/<int:id>')
@login_required
def project_information(id):
    token = request.cookies.get('token')
    headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
    project_data = requests.get(os.getenv('BASE_URL') + f'api/project/{id}', headers=headers).json()
    if project_data:
        return render_template('project.html', project=project_data, token=token)
    else:
        flash('Project not found', 'error')
        return redirect(url_for('project.projects'))

@project.route('/update_project', methods=['POST'])
@login_required
def update_project():
    name = request.form.get('name')
    description = request.form.get('description')
    project_id = request.form.get('project-id')
    json = {'name': name, 'description': description}
    token = request.cookies.get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(os.getenv('BASE_URL') + f'api/project/{project_id}', json=json, headers=headers)
    if response.status_code == 200:
        flash('Project updated successfully!', 'success')
    return redirect(url_for('project.project_information', id=project_id))

@project.route('/project/<projectId>/manage_users')
@login_required
def manage_users(projectId):
    token = request.cookies.get('token')
    return render_template('manage_users.html', token=token, projectId=projectId)