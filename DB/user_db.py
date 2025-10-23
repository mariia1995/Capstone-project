import sqlite3
from datetime import date

from werkzeug.security import check_password_hash

from DB.database_queries import DBBase
from Objects.user import User


class UserDB(DBBase):
    def create_user(self, username, email, hashed_password):
        query = "INSERT INTO users (username, email, availability, password) VALUES (?, ?, ?, ?)"
        try:
            self.execute_query(query, (username, email, 100, hashed_password))
        except Exception:
            raise

    def get_users_db(self, current_user_id):
        query = "SELECT user_id_1 from friends where user_id_2 = ?"
        cursor = self.execute_query(query, (current_user_id,))
        ids = cursor.fetchall()
        id_list = [id[0] for id in ids]
        id_list.append(current_user_id)
        placeholders = ', '.join(['?'] * len(id_list))
        query = f"SELECT id, username, first_name, last_name from users where id not in ({placeholders})"

        try:
            cursor = self.execute_query(query, id_list)
            result = cursor.fetchall()
            users = []
            if result:
                for row in result:
                    columns = ['id', 'username', 'first_name', 'last_name']
                    result_dict = dict(zip(columns, row))
                    user = User(**result_dict)
                    users.append(user)
                return users
            else:
                return []
        except Exception:
            raise

    def get_friends(self, current_user_id):
        query = "SELECT user_id_1 from friends where user_id_2 = ?"
        cursor = self.execute_query(query, (current_user_id,))
        ids = cursor.fetchall()
        id_list = [id[0] for id in ids]
        if id_list:
            placeholders = ', '.join(['?'] * len(id_list))
            query = f"SELECT id, username, first_name, last_name FROM users WHERE id IN ({placeholders})"
            cursor.execute(query, id_list)
        else:
            return []
        result = cursor.fetchall()
        users = []
        if result:
            for row in result:
                columns = ['id', 'username', 'first_name', 'last_name']
                result_dict = dict(zip(columns, row))
                user = User(**result_dict)
                users.append(user)
            return users
        else:
            return None

    def update_password(self, username, hashed_password):
        query = "UPDATE users SET password = ? WHERE username = ?"
        try:
            self.execute_query(query, (hashed_password, username))
        except Exception:
            raise

    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        try:
            result = self.execute_query(query, (username,))
            return result.fetchone()
        except Exception:
            raise

    def get_user_info(self, id):
        query = "SELECT id, username, first_name, last_name, email, phone_number, birthdate, availability FROM users WHERE id = ?"
        cursor = self.execute_query(query, (id,))
        result = cursor.fetchone()
        if result:
            columns = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'birthdate', 'availability']
            result_dict = dict(zip(columns, result))
            user = User(**result_dict)
            return user
        else:
            return None

    def check_auth(self, username, password):
        query = 'SELECT username, password, id FROM users WHERE username = ?'
        cursor = self.execute_query(query, (username,))
        result = cursor.fetchone()
        if result is None or not check_password_hash(result[1], password):
            return None
        else:
            return result[2]

    def update_user(self, user):

        query = (f"UPDATE users SET first_name = '{user.first_name}', "
                 f"last_name = '{user.last_name}', email = '{user.email}', phone_number = '{user.phone_number}', "
                 f"birthdate = '{user.birthdate}' WHERE id = {user.id}")
        try:
            cursor = self.execute_query(query)
            result = cursor.rowcount
            if result:
                return True
            else:
                return False
        except Exception:
            print("Exception during update user sql execution" + Exception)
            return False

    def create_friendship(self, current_user_id, friend_id):
        query = 'SELECT * from friends where user_id_1 = ? and user_id_2 = ?'
        cursor = self.execute_query(query, (current_user_id, friend_id))
        if cursor.rowcount <= 0:
            query2 = ("INSERT INTO friends (user_id_1, user_id_2) "
                      f"VALUES ({current_user_id}, {friend_id}), ({friend_id}, {current_user_id})")
            try:
                self.execute_query(query2)
                return True
            except Exception:
                print("Exception during update user sql execution", Exception)
                return False
        else:
            return False

    def delete_friendship(self, current_user_id, friend_id):
        query = 'DELETE from friends where user_id_1 = ? and user_id_2 = ?'
        try:
            self.execute_query(query, (current_user_id, friend_id))
            self.execute_query(query, (friend_id, current_user_id))
            return True
        except Exception:
            print("Exception during update user sql execution", Exception)
            return False

    def add_users_to_project(self, user_id, project_id):
        query = 'INSERT into users_projects (user_id, project_id, role_id) values (?, ?, 2)'
        try:
            self.execute_query(query, (user_id, project_id))
            return True
        except Exception:
            print("Exception during update user sql execution", Exception)
            return False
    def delete_users_from_project(self, user_id, project_id):
        query = 'DELETE from users_projects where user_id = ? and project_id = ?'
        try:
            self.execute_query(query, (user_id, project_id))
            return True
        except Exception:
            print("Exception during update user sql execution", Exception)
            return False



