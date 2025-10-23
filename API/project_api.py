import sqlite3
from functools import wraps

from flasgger import Swagger, swag_from
from flask import jsonify, request, make_response
from flask import Blueprint
import jwt

from DB.project_db import ProjectDB
from DB.user_db import UserDB
from Objects.project import Project

project_api = Blueprint('project_api', __name__)
secret_key = 'secret'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # Проверка наличия токена в заголовках
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Расшифровка токена
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user_id=current_user_id, *args, **kwargs)

    return decorated


@project_api.route('/api/project/<int:id>', methods=['GET'])
@token_required
def get_project_by_id(id, current_user_id):
    with ProjectDB() as db:
        project = db.get_project_info(id)
    if project:
        return jsonify(project.to_dict()), 200
    else:
        return jsonify({'error': 'Project not found'}), 404


@project_api.route('/api/projects', methods=['GET'])
@token_required
def get_projects(current_user_id):
    with ProjectDB() as db:
        list_projects = db.get_projects(current_user_id)
    if list_projects:
        return jsonify(list_projects), 200
    else:
        return jsonify({'message': 'No projects found'}), 200


# /apidocs/ to open swagger
@project_api.route('/api/project', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': '',
            'examples': {
                'application/json': {'result': 'Creation successful', "project_id": 'id'}
            }
        }
    }
})
@token_required
def create_project(current_user_id):
    """
       Project creation
       ---
       tags:
         - Project creation
       parameters:
         - name: name
           in: query
           type: string
           required: true
           description: name of the project
         - name: user_id
           in: query
           type: int
           required: true
           description: id of the creator
         - name: description
           in: query
           type: string
           required: false
           description: project description
       responses:
         200:
           description: Successful creation
           schema:
             type: object
             properties:
               message:
                 type: string
                 example: Creation successful
       """
    data = request.get_json()
    data["user_id"] = current_user_id
    project = Project.from_dict(data)
    try:
        with ProjectDB() as db:
            result = db.create_project(project)
        if result:
            return jsonify({'result': 'Creation successful', "project_id": result}), 200
        else:
            return jsonify({'error': 'Error during creation'}), 404
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Error during creation', "message": "Project with the same name already exists"}), 409
    except Exception as e:
        return jsonify({'error': 'Error during creation', "message": str(e)}), 404


@project_api.route('/api/project/<int:id>', methods=['POST'])
@token_required
def update_project(id, current_user_id):
    data = request.get_json()
    data["user_id"] = current_user_id
    project = Project.from_dict(data)
    project.id = id
    with ProjectDB() as db:
        result = db.update_project(project)
    if result != "Error":
        return jsonify({'result': 'Update successful'}), 200
    elif result == "Error":
        return jsonify({'error': 'You do not have permissions to modify the project!'}), 400
    else:
        return jsonify({'error': 'Error during update'}), 404


@project_api.route('/api/project/<int:id>', methods=['DELETE'])
@token_required
def delete_project(id, current_user_id):
    with ProjectDB() as db:
        result = db.delete_project(id, current_user_id)
    if result != "Error":
        return jsonify({'result': 'Project was deleted'}), 200
    elif result == "Error":
        return jsonify({'error': 'You do not have permissions to delete the project!'}), 400
    else:
        return jsonify({'error': 'Error during delete'}), 404


@project_api.route('/api/project_users/<int:project_id>', methods=['GET'])
@token_required
def get_users(project_id, current_user_id):
    with ProjectDB() as db:
        result = db.get_project_users(project_id)
    response = []
    if result:
        for row in result:
            response.append({'username': row[0],
                             'role': row[1],
                             'user_id': row[2]})
        return jsonify(response), 200
    else:
        return jsonify({'error': 'There was an error in request execution'}), 400


@project_api.route('/api/project_users/delete', methods=['DELETE']) # not ready
def delete_users():
    data = request.get_json()
    user_ids = data.get('user_ids', [])

    if not user_ids:
        return jsonify({'success': False, 'error': 'No users selected'}), 400

    # Логика удаления пользователей из проекта
    # Пример:
    for user_id in user_ids:
        # Удаление пользователя из базы данных
        pass

    return jsonify({'success': True})