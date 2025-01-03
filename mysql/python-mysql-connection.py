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
                password="PracaProjekt00#",
                database="budget_tracker"
            )
            print("Pomyślnie połączono z bazą danych")
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Błąd podczas łączenia z bazą danych: {e}")
            raise

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

    def search_transactions(self, start_date=None, end_date=None, 
                          category_id=None, min_amount=None):
        """Wyszukuje transakcje według określonych kryteriów"""
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
            
            self.cursor.execute(query, tuple(values))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Błąd podczas wyszukiwania transakcji: {e}")
            return []

    def close(self):
        """Zamyka połączenie z bazą danych"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Połączenie z bazą danych zostało zamknięte")
