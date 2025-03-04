import mysql.connector
from mysql.connector import Error
from datetime import datetime

class BudgetDatabase:
    def __init__(self, host, user, password, database):
        """Inicjalizacja połączenia z bazą danych"""
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql!",
                database="budget_tracker"
            )
            print("Pomyślnie połączono z bazą danych")
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Błąd podczas łączenia z bazą danych: {e}")
            raise

    def is_connected(self):
        """Check if the database connection is open"""
        return self.connection.is_connected()

    def get_all_transactions(self):
        """Pobiera wszystkie transakcje z bazy danych"""
        try:
            query = """
                SELECT
                    t.transaction_id,
                    t.amount,
                    t.transaction_date,
                    c.name as category_name,
                    tt.name as transaction_type,
                    a.name as account_name,
                    t.description
                FROM Transactions t
                JOIN Categories c ON t.category_id = c.category_id
                JOIN TransactionTypes tt ON t.transaction_type_id = tt.transaction_type_id
                JOIN Accounts a ON t.account_id = a.account_id
                ORDER BY t.transaction_date DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Błąd podczas pobierania transakcji: {e}")
            return []

    def add_transaction(self, account_id, category_id, transaction_type_id,
                       amount, description):
        """Dodaje nową transakcję do bazy danych"""
        try:
            query = """
                INSERT INTO Transactions
                (account_id, category_id, transaction_type_id, amount,
                 transaction_date, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (account_id, category_id, transaction_type_id, amount,
                     datetime.now().date(), description)

            self.cursor.execute(query, values)
            self.connection.commit()
            print("Transakcja została dodana pomyślnie")
            return True
        except Error as e:
            print(f"Błąd podczas dodawania transakcji: {e}")
            self.connection.rollback()
            return False

    def get_account_balance(self, account_id):
        """Pobiera saldo konta"""
        try:
            query = "SELECT current_balance FROM Accounts WHERE account_id = %s"
            self.cursor.execute(query, (account_id,))
            result = self.cursor.fetchone()
            return result['current_balance'] if result else None
        except Error as e:
            print(f"Błąd podczas pobierania salda: {e}")
            return None

    def search_transactions(self, start_date=None, end_date=None, category_id=None, search_query=None, min_amount=None):
        """Search transactions based on filters."""
        try:
            conditions = []
            values = []

            query = """
                SELECT t.*, c.name as category_name, a.name as account_name
                FROM Transactions t
                JOIN Categories c ON t.category_id = c.category_id
                JOIN Accounts a ON t.account_id = a.account_id
                WHERE 1=1
            """

            if search_query:
                conditions.append("t.description LIKE %s")
                values.append(f"%{search_query}%")  # Partial match search

            if start_date:
                conditions.append("t.transaction_date >= %s")
                values.append(start_date)

            if end_date:
                conditions.append("t.transaction_date <= %s")
                values.append(end_date)

            if category_id:
                conditions.append("t.category_id = %s")
                values.append(category_id)

            if min_amount:
                conditions.append("t.amount >= %s")
                values.append(min_amount)

            if conditions:
                query += " AND " + " AND ".join(conditions)

            query += " ORDER BY t.transaction_date DESC"

            self.cursor.execute(query, tuple(values))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error during transaction search: {e}")
            return []

    def get_recent_transactions(self, user_id, limit=10):
        """Fetch the most recent transactions for a user's accounts"""
        try:
            query = """
                SELECT t.transaction_date, t.amount, t.description, c.name AS category_name
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.account_id IN (
                    SELECT account_id FROM accounts
                )
                ORDER BY t.transaction_date DESC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching recent transactions: {e}")
            return []



    def get_all_accounts(self):
        """Fetch all accounts with their balances"""
        try:
            query = """
                SELECT account_id, name, current_balance FROM Accounts
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Błąd podczas pobierania kont: {e}")
            return []

    def get_all_categories(self):
        """Fetch all categories"""
        try:
            query = """
                SELECT category_id, name FROM Categories
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Błąd podczas pobierania kategorii: {e}")
            return []

    def add_savings(self, goal_name, goal_amount, target_date, user_id):
        query = """
            INSERT INTO savings_goals (goal_name, goal_amount, target_date, user_id)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (goal_name, goal_amount, target_date, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding savings goal: {e}")
            self.connection.rollback()
            return False

    def get_savings_goal(self, user_id):
        query = """
            SELECT id, goal_name, goal_amount, saved_amount
            FROM savings_goals
            WHERE user_id = %s
        """
        try:
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Błąd przy pobieraniu danych: {e}")
            return []

    def add_contribution(self, goal_id, amount):
        try:
            self.cursor.execute(
                "INSERT INTO contributions (goal_id, amount) VALUES (%s, %s)",
                (goal_id, amount),
            )
            self.cursor.execute(
                "UPDATE savings_goals SET saved_amount = saved_amount + %s WHERE goal_id = %s",
                (amount, goal_id),
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding contribution: {e}")
            self.connection.rollback()
            return False


    def update_saved_amount(self, id, new_saved_amount):
        """Update the saved_amount for a specific goal."""
        query = """
            UPDATE savings_goals
            SET saved_amount = %s
            WHERE id = %s
        """
        try:
            self.cursor.execute(query, (new_saved_amount, id))
            self.connection.commit()
        except Exception as e:
            print(f"Error updating saved_amount: {e}")
            self.connection.rollback()


    def get_savings_goal_by_id(self, id, user_id):
        """Fetch a savings goal by its id and user_id."""
        query = """
            SELECT * FROM savings_goals
            WHERE id = %s AND user_id = %s
        """
        self.cursor.execute(query, (id, user_id))
        result = self.cursor.fetchone()
        return result


    def update_savings_goal(self, id, goal_name, goal_amount, target_date):
        """Update the savings goal."""
        query = """
        UPDATE savings_goals
        SET goal_name = %s, goal_amount = %s, target_date = %s
        WHERE id = %s
        """
        try:
            self.cursor.execute(query, (goal_name, goal_amount, target_date, id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating savings goal: {e}")
            self.connection.rollback()
            return False


    def close(self):
        """Zamyka połączenie z bazą danych"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Połączenie z bazą danych zostało zamknięte")
