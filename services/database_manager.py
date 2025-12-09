import sqlite3
from typing import List, Dict, Tuple

from database.db import DatabaseConnection


class DbManagerService:
    """Handles CRUD calls against the SQLite database."""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def _run_select(self, query: str, params: Tuple = ()) -> List[Dict]:
        # Execute a select and return rows as dictionaries
        rows: List[Dict] = []
        conn = self.connection.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        column_names = []
        for column in cursor.description:
            column_names.append(column[0])
        for row in result:
            row_dict = {}
            index = 0
            for name in column_names:
                row_dict[name] = row[index]
                index = index + 1
            rows.append(row_dict)
        conn.close()
        return rows

    def _run_write(self, query: str, params: Tuple = ()) -> None:
        # Execute an insert or update statement
        conn = self.connection.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def add_user(self, username: str, email: str, role: str, password_hash: str) -> bool:
        # Add a user if the username does not already exist
        existing = self.get_user_by_username(username)
        if len(existing) > 0:
            return False
        self._run_write(
            "INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
            (username, email, role, password_hash),
        )
        return True

    def get_user_by_username(self, username: str) -> List[Dict]:
        return self._run_select("SELECT * FROM users WHERE username = ?", (username,))

    def list_users(self) -> List[Dict]:
        return self._run_select("SELECT * FROM users", ())

    def add_dataset(self, name: str, description: str, created_at: str, updated_at: str) -> None:
        self._run_write(
            "INSERT INTO datasets (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (name, description, created_at, updated_at),
        )

    def list_datasets(self) -> List[Dict]:
        return self._run_select("SELECT * FROM datasets", ())

    def add_ticket(self, title: str, description: str, status: str, priority: str, created_at: str, updated_at: str, assigned_to: str) -> None:
        self._run_write(
            "INSERT INTO tickets (title, description, status, priority, created_at, updated_at, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, status, priority, created_at, updated_at, assigned_to),
        )

    def list_tickets(self) -> List[Dict]:
        return self._run_select("SELECT * FROM tickets", ())

    def add_incident(self, title: str, description: str, severity: str, status: str, reported_by: str, assigned_to: str, created_at: str, updated_at: str) -> None:
        self._run_write(
            "INSERT INTO incidents (title, description, severity, status, reported_by, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, description, severity, status, reported_by, assigned_to, created_at, updated_at),
        )

    def list_incidents(self) -> List[Dict]:
        return self._run_select("SELECT * FROM incidents", ())