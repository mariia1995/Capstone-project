from DB.database_queries import DBBase


def db_connect():
    with DBBase() as db:
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT,
            birthdate DATE,
            availability INTEGER CHECK (availability >= 0),
            password TEXT NOT NULL
        )
        ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE CHECK(name != ''),
            description TEXT,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        db.execute_query('''
                INSERT INTO roles (name) VALUES ("Project Manager"), ("Project Member")
                ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS users_projects (
            user_id INTEGER,
            project_id INTEGER,
            role_id INTEGER,
            PRIMARY KEY (user_id, project_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
       ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        db.execute_query('''
                        INSERT INTO statuses (name) VALUES ("Not Started"), ("In Progress"), ("Completed")
                        ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            assignee INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            status_id INTEGER,
            due_date DATE,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id),
            FOREIGN KEY (assignee) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (status_id) REFERENCES statuses(id)
        )
        ''')
        db.execute_query('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id_1 INTEGER,
            user_id_2 INTEGER,
            PRIMARY KEY (user_id_1, user_id_2),
            FOREIGN KEY (user_id_1) REFERENCES users(id),
            FOREIGN KEY (user_id_2) REFERENCES users(id),
            CHECK (user_id_1 <> user_id_2)
        )       
        ''')

        db.execute_query("""
        CREATE TRIGGER before_task_insert
        BEFORE INSERT ON tasks
        FOR EACH ROW
        BEGIN
            UPDATE users
            SET availability = availability - 20
            WHERE id = NEW.creator_id;
        END;
        """)
        db.execute_query("""
            CREATE TRIGGER after_task_update
            AFTER UPDATE ON tasks
            FOR EACH ROW
            BEGIN
                UPDATE users
                SET availability = availability + 20
                WHERE id = OLD.assignee AND OLD.assignee != NEW.assignee;

                UPDATE users
                SET availability = availability - 20
                WHERE id = NEW.assignee AND OLD.assignee != NEW.assignee;
            END;
                """)
        db.execute_query("""
             CREATE TRIGGER after_task_status_complete
             AFTER UPDATE ON tasks
             FOR EACH ROW
             BEGIN
                UPDATE users
                SET availability = availability + 20
                WHERE id = NEW.assignee AND OLD.status != NEW.status AND NEW.status = 'Completed';
             END;
                 """)
        db.execute_query("""
             CREATE TRIGGER after_task_status_update
             AFTER UPDATE ON tasks
             FOR EACH ROW
             BEGIN
                UPDATE users
                SET availability = availability - 20
                WHERE id = NEW.assignee AND OLD.status != NEW.status AND OLD.status = 'Completed';
             END;
             """)
        db.execute_query("""
             CREATE TRIGGER after_task_delete
             AFTER DELETE ON tasks
             FOR EACH ROW
             BEGIN
                     UPDATE users
                     SET availability = availability + 20
                     WHERE id = OLD.assignee;
             END;
             """)

