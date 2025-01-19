from flask_bcrypt import Bcrypt
from datetime import datetime
import logging

bcrypt = Bcrypt()
logging.basicConfig(level=logging.DEBUG)

class User:
    def __init__(self, db):
        self.db = db
        # Check if database connection is open
        if not self.db.is_connected():
            raise Exception("Database connection is not open.")
        logging.debug("User model initialized successfully.")

    def add_user(self, username, email, password):
        """Add a new user to the database"""
        try:
            cursor = self.db.cursor  # Access the cursor from the BudgetDatabase instance

            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                logging.debug("Username or email already exists.")
                return None  # Username or email already exists

            # Hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Get current timestamp for created_at and updated_at
            current_time = datetime.now()

            # Insert new user with created_at and updated_at
            cursor.execute("""
                INSERT INTO users (username, email, password, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, hashed_password, current_time, current_time))

            self.db.connection.commit()
            logging.debug("User added successfully.")
            return cursor.lastrowid  # Return the ID of the new user

        except Exception as e:
            logging.error(f"Error in add_user method: {e}")
            return None

    def authenticate_user(self, username, password):
        """Authenticate a user by checking username and password"""
        try:
            cursor = self.db.cursor

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.check_password_hash(user['password'], password):
                logging.debug("User authenticated successfully.")
                return user
            else:
                logging.debug("Authentication failed. Invalid username or password.")
                return None  

        except Exception as e:
            logging.error(f"Error in authenticate_user method: {e}")
            return None
