from flask import Blueprint
from flask import render_template, request, url_for, redirect, flash, session
from flask_login import login_required

friends = Blueprint('friends', __name__)

@friends.route('/make_friend')
@login_required
def make_friend():
    token = request.cookies.get('token')
    return render_template('make_friend.html', token=token)

@friends.route('/friends')
@login_required
def friend():
    token = request.cookies.get('token')
    return render_template('friends.html', token=token)


