from flask import jsonify, request, make_response
from flask import Blueprint
import jwt
import datetime


from API.project_api import token_required
from DB.user_db import UserDB
from Objects.user import User

user_api = Blueprint('user_api', __name__)
secret_key = 'secret'


@user_api.route('/api/user/<int:id>', methods=['GET'])
def get_user_by_id(id):
    with UserDB() as db:
        user = db.get_user_info(id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@user_api.route('/api/user/<int:id>', methods=['POST'])
def update_user(id):
    data = request.get_json()
    user = User.from_dict(data)
    user.id = id
    with UserDB() as db:
        result = db.update_user(user)
    if result:
        return jsonify({'result': 'Update successful'}), 200
    else:
        return jsonify({'error': 'Error during update'}), 404


@user_api.route('/api/auth', methods=['POST'])
def auth():
    """
    POST query with token
    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    with UserDB() as db:
        user_id = db.check_auth(username, password)
    if not user_id:
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }, 'secret', algorithm='HS256')

    response = make_response(jsonify({"message": "Login successful", "token": token, "user_id": user_id}))

    return response, 200


@user_api.route('/api/users', methods=['GET'])
@token_required
def get_users_list(current_user_id):

    with UserDB() as db:
        users = db.get_users_db(current_user_id)

    user_list = [{'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name} for user in users]

    return jsonify(user_list)


@user_api.route('/api/friends', methods=['GET'])
@token_required
def get_friends(current_user_id):

    with UserDB() as db:
        users = db.get_friends(current_user_id)

    user_list = [{'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name} for user in users]

    return jsonify(user_list)

@user_api.route('/api/add_friends', methods=['POST'])
@token_required
def add_friends(current_user_id):
    data = request.get_json()
    friend_ids = data.get('friend_ids', [])

    if not friend_ids:
        return jsonify({'success': False, 'error': 'No friends selected'}), 400

    with UserDB() as db:
        for friend_id in friend_ids:
            result = db.create_friendship(current_user_id, friend_id)
            if not result:
                return jsonify({'error': "Friendship is already exists"})

    return jsonify({'success': True})


@user_api.route('/api/delete_friends', methods=['POST'])
@token_required
def delete_friends(current_user_id):
    data = request.get_json()
    friend_ids = data.get('friend_ids', [])

    if not friend_ids:
        return jsonify({'success': False, 'error': 'No friends selected'}), 400

    with UserDB() as db:
        for friend_id in friend_ids:
            result = db.delete_friendship(current_user_id, friend_id)
            if not result:
                return jsonify({'error': "An error occurred"})

    return jsonify({'success': True})


@user_api.route('/api/<projectId>/add_users', methods=['POST'])
@token_required
def add_users(current_user_id, projectId):
    data = request.get_json()
    user_ids = data.get('user_ids', [])

    if not user_ids:
        return jsonify({'success': False, 'error': 'No friends selected'}), 400

    with UserDB() as db:
        for user_id in user_ids:
            result = db.add_users_to_project(user_id, projectId)
            if not result:
                return jsonify({'error': "User is already assigned to the project"})

    return jsonify({'success': True})


@user_api.route('/api/<projectId>/delete_users', methods=['POST'])
@token_required
def delete_users_from_project(current_user_id, projectId):
    data = request.get_json()
    friend_ids = data.get('friend_ids', [])

    if not friend_ids:
        return jsonify({'success': False, 'error': 'No friends selected'}), 400

    with UserDB() as db:
        for user_id in friend_ids:
            result = db.delete_users_from_project(user_id, projectId)
            if not result:
                return jsonify({'error': "An error occurred"})

    return jsonify({'success': True})