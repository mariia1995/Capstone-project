from DB.database_queries import DBBase
from Objects.project import Project


class ProjectDB(DBBase):
    def create_project(self, project):
        query = "INSERT INTO projects (name, description) VALUES (?, ?)"
        query2 = "INSERT INTO users_projects (user_id, project_id, role_id) VALUES (?, ?, ?)"
        try:
            cursor = self.execute_query(query, (project.name, project.description))
            project_id = cursor.lastrowid
        except Exception:
            raise
            return
        try:
            self.execute_query(query2, (project.user_id, project_id, 1))
            return project_id
        except Exception:
            raise

    def get_project_info(self, id):
        query = """
        SELECT p.id, p.name, p.description, p.creation_date, u.username
        FROM projects p 
        JOIN users_projects up ON p.id = up.project_id 
        JOIN users u ON u.id = up.user_id 
        WHERE p.id = ? and up.role_id = 1
        """
        cursor = self.execute_query(query, (id,))
        result = cursor.fetchone()
        if result:
            columns = ['id', 'name', 'description', 'creation_date', 'user_id']
            result_dict = dict(zip(columns, result))
            project = Project(**result_dict)
            return project
        else:
            return None

    def get_projects(self, user_id):
        query = """
        SELECT p.id, p.name, manager.username AS manager_name
        FROM projects p
        JOIN users_projects up ON p.id = up.project_id
        JOIN users current_user ON current_user.id = up.user_id
        JOIN users_projects mup ON mup.project_id = p.id AND mup.role_id = 1
        JOIN users manager ON manager.id = mup.user_id
        WHERE up.user_id = ?
        """
        cursor = self.execute_query(query, (user_id,))
        projects_list = []
        results = cursor.fetchall()
        if results:
            for result in results:
                columns = ['id', 'project', 'project_manager']
                result_dict = dict(zip(columns, result))
                projects_list.append(result_dict)
        return projects_list

    def update_project(self, project):
        query = """
                SELECT u.id
                FROM projects p 
                JOIN users_projects up ON p.id = up.project_id 
                JOIN users u ON u.id = up.user_id 
                WHERE p.id = ? 
                AND up.role_id = 1
                """
        cursor = self.execute_query(query, (project.id,))
        creator_id = cursor.fetchone()
        if project.user_id != creator_id[0]:
            return "Error"
        query = (f"UPDATE projects SET name = '{project.name}', description = '{project.description}' "
                 f" WHERE id = {project.id}")
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

    def delete_project(self, project_id, user_id):
        query = """
                        SELECT u.id
                        FROM projects p 
                        JOIN users_projects up ON p.id = up.project_id 
                        JOIN users u ON u.id = up.user_id 
                        WHERE p.id = ? 
                        AND up.role_id = 1
                        """
        cursor = self.execute_query(query, (project_id,))
        creator_id = cursor.fetchone()[0]
        if user_id != creator_id:
            return "Error"
        query = (f"DELETE from projects WHERE id = {project_id}")
        try:
            cursor = self.execute_query(query)
            result = cursor.rowcount
            if result:
                return True
            else:
                return False
        except Exception:
            print("Exception during delete project sql execution" + Exception)
            return False

    def get_project_users(self, project_id):
        query = """
        SELECT u.username, r.name, u.id
        FROM projects p 
        JOIN users_projects up ON p.id = up.project_id 
        JOIN users u ON u.id = up.user_id 
		JOIN roles r ON r.id = up.role_id
        WHERE p.id = ?
        """
        cursor = self.execute_query(query, (project_id,))
        users = cursor.fetchall()
        if users:
            return users
        else:
            return False
