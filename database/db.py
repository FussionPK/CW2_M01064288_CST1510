import sqlite3
import hashlib
from pathlib import Path
from typing import Optional


DB_FILENAME = "platform.db"


def get_db_path() -> str:
	"""Return the database file path under the database folder."""
	base_directory = Path(__file__).resolve().parent 
	database_file_path = base_directory / DB_FILENAME
	return str(database_file_path) #eg "/path/to/database/platform.db"


class DatabaseConnection:
	"""Handles the low-level SQLite connection and setup."""

	def __init__(self, db_path: Optional[str] = None):
		if db_path is None:
			db_path = get_db_path()
		self.database_file_path = db_path
		self.create_directory_if_missing()

	def create_directory_if_missing(self) -> None:
		# Make sure the database folder exists before creating the file
		database_folder = Path(self.database_file_path).parent
		if not database_folder.exists():
			database_folder.mkdir(parents=True, exist_ok=True)

	def connect(self):
		# Open a raw SQLite connection
		return sqlite3.connect(self.database_file_path)

	def initialize(self) -> None:
		# Create tables if they do not exist
		database_connection = self.connect()
		database_cursor = database_connection.cursor()

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS users (
				user_id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT UNIQUE,
				email TEXT,
				role TEXT,
				password_hash TEXT
			)
			"""
		)

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS datasets (
				dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT,
				description TEXT,
				created_at TEXT,
				updated_at TEXT
			)
			"""
		)

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS tickets (
				ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				description TEXT,
				status TEXT,
				priority TEXT,
				created_at TEXT,
				updated_at TEXT,
				assigned_to TEXT
			)
			"""
		)

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS incidents (
				incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				description TEXT,
				severity TEXT,
				status TEXT,
				reported_by TEXT,
				assigned_to TEXT,
				created_at TEXT,
				updated_at TEXT
			)
			"""
		)

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS csv_data (
				csv_id INTEGER PRIMARY KEY AUTOINCREMENT,
				filename TEXT,
				row_count INTEGER,
				columns TEXT,
				upload_date TEXT,
				data_json TEXT
			)
			"""
		)

		database_connection.commit()
		database_connection.close()
		self.seed_initial_sample_data()

	def seed_initial_sample_data(self) -> None:
		# Add a few starter rows the first time the tables are empty
		database_connection = self.connect()
		database_cursor = database_connection.cursor()

		database_cursor.execute("SELECT COUNT(*) FROM users")
		total_user_count = database_cursor.fetchone()[0]
		if total_user_count == 0:
			admin_password_hashed = hashlib.sha256("admin".encode("utf-8")).hexdigest()
			database_cursor.execute(
				"INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
				("admin", "admin@example.com", "admin", admin_password_hashed),
			)

		database_cursor.execute("SELECT COUNT(*) FROM datasets")
		total_dataset_count = database_cursor.fetchone()[0]
		if total_dataset_count == 0:
			database_cursor.execute(
				"INSERT INTO datasets (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
				("Initial Logs", "Security log extracts", "2024-01-01", "2024-01-02"),
			)

		database_cursor.execute("SELECT COUNT(*) FROM tickets")
		total_ticket_count = database_cursor.fetchone()[0]
		if total_ticket_count == 0:
			database_cursor.execute(
				"INSERT INTO tickets (title, description, status, priority, created_at, updated_at, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)",
				("Reset Password", "User cannot sign in", "Open", "Medium", "2024-02-10", "2024-02-10", "IT Analyst"),
			)

		database_cursor.execute("SELECT COUNT(*) FROM incidents")
		total_incident_count = database_cursor.fetchone()[0]
		if total_incident_count == 0:
			database_cursor.execute(
				"INSERT INTO incidents (title, description, severity, status, reported_by, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
				("Phishing Email", "Staff reported suspicious email", "High", "Investigating", "SOC", "Responder", "2024-03-01", "2024-03-01"),
			)

		database_connection.commit()
		database_connection.close()
