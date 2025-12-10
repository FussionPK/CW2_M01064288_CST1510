import sqlite3
import hashlib
from pathlib import Path
from typing import Optional


DB_FILENAME = "platform.db"


def get_db_path() -> str:
	"""Return the database file path under the database folder."""
	base_dir = Path(__file__).resolve().parent 
	db_path = base_dir / DB_FILENAME
	return str(db_path) #eg "/path/to/database/platform.db"


class DatabaseConnection:
	"""Handles the low-level SQLite connection and setup."""

	def __init__(self, db_path: Optional[str] = None):
		if db_path is None:
			db_path = get_db_path()
		self.db_path = db_path
		self._ensure_directory()

	def _ensure_directory(self) -> None:
		# Make sure the database folder exists before creating the file
		db_parent = Path(self.db_path).parent
		if not db_parent.exists():
			db_parent.mkdir(parents=True, exist_ok=True)

	def connect(self):
		# Open a raw SQLite connection
		return sqlite3.connect(self.db_path)

	def initialize(self) -> None:
		# Create tables if they do not exist
		conn = self.connect()
		cursor = conn.cursor()

		cursor.execute(
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

		cursor.execute(
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

		cursor.execute(
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

		cursor.execute(
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

		conn.commit()
		conn.close()
		self._seed_basic_data()

	def _seed_basic_data(self) -> None:
		# Add a few starter rows the first time the tables are empty
		connection = self.connect()
		cursor = connection.cursor()

		cursor.execute("SELECT COUNT(*) FROM users")
		count_users = cursor.fetchone()[0]
		if count_users == 0:
			hashed_admin = hashlib.sha256("admin".encode("utf-8")).hexdigest()
			cursor.execute(
				"INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
				("admin", "admin@example.com", "admin", hashed_admin),
			)

		cursor.execute("SELECT COUNT(*) FROM datasets")
		count_datasets = cursor.fetchone()[0]
		if count_datasets == 0:
			cursor.execute(
				"INSERT INTO datasets (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
				("Initial Logs", "Security log extracts", "2024-01-01", "2024-01-02"),
			)

		cursor.execute("SELECT COUNT(*) FROM tickets")
		count_tickets = cursor.fetchone()[0]
		if count_tickets == 0:
			cursor.execute(
				"INSERT INTO tickets (title, description, status, priority, created_at, updated_at, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)",
				("Reset Password", "User cannot sign in", "Open", "Medium", "2024-02-10", "2024-02-10", "IT Analyst"),
			)

		cursor.execute("SELECT COUNT(*) FROM incidents")
		count_incidents = cursor.fetchone()[0]
		if count_incidents == 0:
			cursor.execute(
				"INSERT INTO incidents (title, description, severity, status, reported_by, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
				("Phishing Email", "Staff reported suspicious email", "High", "Investigating", "SOC", "Responder", "2024-03-01", "2024-03-01"),
			)

		connection.commit()
		connection.close()
