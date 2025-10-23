import os

from DB import create_db

#current_directory = os.path.dirname(os.path.abspath(__file__))

# Import the create_app function from the app module.
# This function is responsible for creating the application instance.
from app import create_app

# Initialize the application using the create_app function.
app = create_app()

# Check if the database file 'database.db' does not exist.
# If it doesn't exist, call the db_connect function from create_db to establish the database connection.
if not os.path.exists('database.db'):
    create_db.db_connect()

if __name__ == '__main__':
    # Run the application in debug mode, allowing for real-time code changes and debugging
    app.run(debug=True)




