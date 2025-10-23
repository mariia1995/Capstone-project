from datetime import date

from DB.database_queries import DBBase
from Objects.task import Task


class TaskDB(DBBase):
    def create_task(self, task):
        if task.due_date <= date.today().isoformat():
            raise ValueError("Due date cannot be in the past.")
        query = ("INSERT INTO tasks (name, creator_id, assignee, status_id, project_id, due_date, description) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)")
        try:
            cursor = self.execute_query(query,
                                        (task.name, task.creator_id, task.assignee, 1, task.project_id,
                                         task.due_date or '', task.description or ''))
            task_id = cursor.lastrowid
            return task_id
        except Exception:
            print(Exception)
            raise

    def get_task_info(self, id):
        query = """ select t.id, t.name, t.description, s.name, u.username as assignee, u2.username, 
        t.due_date, p.name, t.creation_date as creator, u.id as assignee_id from tasks t
            join statuses s on t.status_id = s.id
            join users u on u.id = t.assignee
            join users u2 on u2.id = t.creator_id
            join projects p on p.id = t.project_id
            where project_id = ? """
        try:
            cursor = self.execute_query(query,
                                        (id,))
            result = cursor.fetchone()
            if result:
                columns = ['id', 'task_name', 'description', 'status', 'assignee', 'creator', 'due_date',
                           'project', 'creation_date', 'assignee_id']
                result_dict = dict(zip(columns, result))
                return result_dict
        except Exception:
            raise

    def get_tasks_by_project(self, project_id):
        query = """
        select t.id, t.name, s.name, u.username, u.id from tasks t 
            join statuses s on t.status_id = s.id 
            join users u on u.id = t.assignee
            where project_id = ? 
            """
        try:
            cursor = self.execute_query(query,
                                        (project_id,))
            tasks_list = []
            results = cursor.fetchall()
            if results:
                for result in results:
                    columns = ['id', 'task_name', 'status', 'username', 'user_id']
                    result_dict = dict(zip(columns, result))
                    tasks_list.append(result_dict)
            return tasks_list
        except Exception:
            raise

    def get_tasks_by_user(self, user_id):
        query = """
        select t.name, p.name, s.name, t.due_date, t.id, p.id from tasks t
            JOIN projects p on t.project_id = p.id
            JOIN statuses s on t.status_id = s.id
            where assignee = ?
            """
        try:
            cursor = self.execute_query(query,
                                        (user_id,))
            tasks_list = []
            results = cursor.fetchall()
            if results:
                for result in results:
                    columns = ['task_name', 'project_name', 'status', 'due_date', 'task_id', 'project_id']
                    result_dict = dict(zip(columns, result))
                    tasks_list.append(result_dict)
            return tasks_list
        except Exception:
            raise

    def update_task(self, task):
        #if task.due_date <= date.today().isoformat():
        #    raise ValueError("Due date cannot be in the past.")
        query = (f"UPDATE tasks SET name = {task.name}, assignee = {task.assignee}, "
                 f"status_id = {task.status_id}, due_date = {task.due_date}, description = {task.description} "
                 f"where id = {task.id}")
        try:
            cursor = self.execute_query(query)
            result = cursor.rowcount
            if result:
                return True
            else:
                return False
        except Exception:
            print("Exception during update task sql execution" + Exception)
            return False

    def delete_task(self, task_id):
        query = "DELETE from TASKS where id = ?"
        try:
            cursor = self.execute_query(query,
                                        (task_id,))
            result = cursor.rowcount
            if result:
                return True
            else:
                return False
        except Exception:
            raise

    def get_project_by_task(self, task_id):
        query = "SELECT project_id from TASKS where id = ?"
        try:
            cursor = self.execute_query(query,
                                        (task_id,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return False
        except Exception:
            raise
