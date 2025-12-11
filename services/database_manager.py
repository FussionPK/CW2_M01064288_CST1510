import sqlite3
from typing import List, Dict, Tuple

from database.db import DatabaseConnection


class DbManagerService:
    """Handles CRUD calls against the SQLite database."""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def execute_select_query(self, sql_query: str, query_parameters: Tuple = ()) -> List[Dict]:
        # Execute a select and return rows as dictionaries
        all_rows: List[Dict] = []
        database_connection = self.connection.connect()
        database_cursor = database_connection.cursor()
        database_cursor.execute(sql_query, query_parameters)
        fetched_results = database_cursor.fetchall()
        column_names_list = []
        for column_description in database_cursor.description:
            column_names_list.append(column_description[0])
        for single_row in fetched_results:
            row_as_dictionary = {}
            # Use zip to pair column names with their corresponding values
            for column_name, column_value in zip(column_names_list, single_row):
                row_as_dictionary[column_name] = column_value
            all_rows.append(row_as_dictionary)
        database_connection.close()
        return all_rows

    def execute_insert_or_update_query(self, sql_query: str, query_parameters: Tuple = ()) -> None:
        # Execute an insert or update statement
        database_connection = self.connection.connect()
        database_cursor = database_connection.cursor()
        database_cursor.execute(sql_query, query_parameters)
        database_connection.commit()
        database_connection.close()

    def add_user(self, username: str, email: str, role: str, password_hash: str) -> bool:
        # Add a user if the username does not already exist
        existing_users = self.get_user_by_username(username)
        if len(existing_users) > 0:
            return False
        self.execute_insert_or_update_query(
            "INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
            (username, email, role, password_hash),
        )
        return True

    def get_user_by_username(self, username: str) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM users WHERE username = ?", (username,))

    def list_users(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM users", ())

    def add_dataset(self, name: str, description: str, created_at: str, updated_at: str) -> None:
        self.execute_insert_or_update_query(
            "INSERT INTO datasets (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (name, description, created_at, updated_at),
        )

    def list_datasets(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM datasets", ())

    def add_ticket(self, title: str, description: str, status: str, priority: str, created_at: str, updated_at: str, assigned_to: str) -> None:
        self.execute_insert_or_update_query(
            "INSERT INTO tickets (title, description, status, priority, created_at, updated_at, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, status, priority, created_at, updated_at, assigned_to),
        )

    def list_tickets(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM tickets", ())

    def add_incident(self, title: str, description: str, severity: str, status: str, reported_by: str, assigned_to: str, created_at: str, updated_at: str) -> None:
        self.execute_insert_or_update_query(
            "INSERT INTO incidents (title, description, severity, status, reported_by, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, description, severity, status, reported_by, assigned_to, created_at, updated_at),
        )

    def list_incidents(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM incidents", ())

    def add_csv_data(self, filename: str, row_count: int, columns: str, upload_date: str, data_json: str) -> None:
        self.execute_insert_or_update_query(
            "INSERT INTO csv_data (filename, row_count, columns, upload_date, data_json) VALUES (?, ?, ?, ?, ?)",
            (filename, row_count, columns, upload_date, data_json),
        )

    def list_csv_data(self) -> List[Dict]:
        return self.execute_select_query("SELECT csv_id, filename, row_count, columns, upload_date FROM csv_data", ())