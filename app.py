from flasgger import Swagger
from flask import Flask
from flask_login import LoginManager

from DB.user_db import UserDB
from dotenv import load_dotenv
import os

login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app():
    app = Flask(__name__)

    app.secret_key = 'secret'
    load_dotenv()
    from Render.auth import auth
    from Render.project_render import project
    from Render.task_render import task
    from Render.friends_render import friends
    from API.user_api import user_api
    from API.project_api import project_api

    from API.task_api import task_api

    login_manager.init_app(app)


    app.register_blueprint(auth)
    app.register_blueprint(project)
    app.register_blueprint(task)
    app.register_blueprint(friends)
    app.register_blueprint(user_api)
    app.register_blueprint(project_api)
    app.register_blueprint(task_api)


    return app


@login_manager.user_loader
def load_user(user_id):
    with UserDB() as db:
        user = db.get_user_info(id=user_id)
    if user:
        return user
    return None
