import sqlite3
from pathlib import Path
from typing import Dict, Optional

import bcrypt


DB_FILENAME = "platform.db"


def get_db_path() -> str:
	"""Return the database file path under the database folder."""
	base_directory = Path(__file__).resolve().parent
	database_file_path = base_directory / DB_FILENAME
	return str(database_file_path)


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
		# Create or update tables to the latest schema definition
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
				owner_department TEXT,
				data_source TEXT,
				row_count INTEGER,
				size_mb REAL,
				quality_score REAL,
				retention_policy TEXT,
				status TEXT,
				last_accessed TEXT,
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
				stage TEXT,
				priority TEXT,
				created_at TEXT,
				updated_at TEXT,
				resolved_at TEXT,
				assigned_to TEXT,
				time_to_resolve_hours REAL,
				waiting_stage_hours REAL,
				customer_satisfaction INTEGER,
				channel TEXT
			)
			"""
		)

		database_cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS incidents (
				incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				description TEXT,
				category TEXT,
				threat_vector TEXT,
				severity TEXT,
				status TEXT,
				reported_by TEXT,
				assigned_to TEXT,
				detected_at TEXT,
				first_response_at TEXT,
				resolved_at TEXT,
				time_to_first_response_hours REAL,
				time_to_resolve_hours REAL,
				business_impact TEXT
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

		self._ensure_additional_columns(database_cursor)

		database_connection.commit()
		database_connection.close()
		self.seed_initial_sample_data()

	def _ensure_additional_columns(self, cursor) -> None:
		# Ensure legacy databases are upgraded with new analytic columns
		self._ensure_columns(
			cursor,
			"datasets",
			{
				"owner_department": "TEXT",
				"data_source": "TEXT",
				"row_count": "INTEGER DEFAULT 0",
				"size_mb": "REAL DEFAULT 0.0",
				"quality_score": "REAL DEFAULT 0.0",
				"retention_policy": "TEXT",
				"status": "TEXT",
				"last_accessed": "TEXT"
			},
		)

		self._ensure_columns(
			cursor,
			"tickets",
			{
				"stage": "TEXT",
				"resolved_at": "TEXT",
				"time_to_resolve_hours": "REAL DEFAULT 0.0",
				"waiting_stage_hours": "REAL DEFAULT 0.0",
				"customer_satisfaction": "INTEGER DEFAULT 0",
				"channel": "TEXT"
			},
		)

		self._ensure_columns(
			cursor,
			"incidents",
			{
				"category": "TEXT",
				"threat_vector": "TEXT",
				"detected_at": "TEXT",
				"first_response_at": "TEXT",
				"resolved_at": "TEXT",
				"time_to_first_response_hours": "REAL DEFAULT 0.0",
				"time_to_resolve_hours": "REAL DEFAULT 0.0",
				"business_impact": "TEXT"
			},
		)

	def _ensure_columns(self, cursor, table: str, column_definition_map: Dict[str, str]) -> None:
		cursor.execute(f"PRAGMA table_info({table})")
		existing_columns = {row[1] for row in cursor.fetchall()}
		for column_name, ddl in column_definition_map.items():
			if column_name not in existing_columns:
				cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {ddl}")

	def seed_initial_sample_data(self) -> None:
		# Add seed rows the first time the tables are empty
		database_connection = self.connect()
		database_cursor = database_connection.cursor()

		database_cursor.execute("SELECT COUNT(*) FROM users")
		total_user_count = database_cursor.fetchone()[0]
		if total_user_count == 0:
			admin_password_hashed = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
			database_cursor.execute(
				"INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
				("admin", "admin@example.com", "admin", admin_password_hashed),
			)

			analyst_password_hashed = bcrypt.hashpw("analyst".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
			database_cursor.execute(
				"INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)",
				("analyst", "analyst@example.com", "analyst", analyst_password_hashed),
			)

		database_cursor.execute("SELECT COUNT(*), GROUP_CONCAT(name, '|') FROM datasets")
		total_dataset_count, dataset_names_concat = database_cursor.fetchone()
		dataset_names_concat = dataset_names_concat or ""
		if total_dataset_count == 0 or (total_dataset_count <= 1 and "Initial Logs" in dataset_names_concat):
			database_cursor.execute("DELETE FROM datasets")
			initial_datasets = [
				("Security Email Logs", "Phishing detection samples", "Security", "Exchange Gateway", 125000, 7.8, 0.82, "Archive after 12 months", "Active", "2024-06-01", "2024-01-04", "2024-05-27"),
				("Endpoint Telemetry", "EDR events aggregated hourly", "Security", "CrowdStrike", 2850000, 25.4, 0.76, "Archive after 6 months", "Active", "2024-06-10", "2024-02-12", "2024-06-09"),
				("Customer Support Tickets", "Historic IT tickets for reporting", "IT Operations", "ServiceNow", 54000, 18.3, 0.91, "Archive after 18 months", "Active", "2024-04-14", "2023-12-01", "2024-04-12"),
				("Data Science Sandbox", "Experimental ML datasets", "Data Science", "S3 Sandbox", 375000, 42.6, 0.65, "Archive after 3 months", "Inactive", "2024-01-30", "2023-07-15", "2024-01-18"),
				("Finance KPIs", "Financial dashboard extracts", "Finance", "ERP Warehouse", 8200, 4.1, 0.94, "Archive after 24 months", "Active", "2024-05-01", "2023-11-21", "2024-04-28"),
			]
			database_cursor.executemany(
				"""
				INSERT INTO datasets (
					name, description, owner_department, data_source, row_count, size_mb,
					quality_score, retention_policy, status, last_accessed, created_at, updated_at
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				initial_datasets,
			)

		database_cursor.execute("SELECT COUNT(*), GROUP_CONCAT(title, '|') FROM tickets")
		total_ticket_count, ticket_titles_concat = database_cursor.fetchone()
		ticket_titles_concat = ticket_titles_concat or ""
		if total_ticket_count == 0 or (total_ticket_count <= 1 and "Reset Password" in ticket_titles_concat):
			database_cursor.execute("DELETE FROM tickets")
			initial_tickets = [
				("VPN Access Failure", "Remote engineer cannot connect", "Open", "Waiting for User", "High", "2024-06-01", "2024-06-10", None, "Morgan Lee", 0.0, 42.0, 68, "Portal"),
				("HR Onboarding Laptop", "Provision device for new hire", "Resolved", "Fulfillment", "Medium", "2024-05-10", "2024-05-18", "2024-05-18", "Priya Patel", 52.0, 12.0, 90, "Email"),
				("Finance App Outage", "Finance cannot access ledger", "Resolved", "Major Incident", "Critical", "2024-05-28", "2024-05-29", "2024-05-29", "Morgan Lee", 16.0, 8.0, 72, "Phone"),
				("Printer Queue Delay", "Queue stuck on 1st floor", "Open", "Waiting for Vendor", "Low", "2024-05-15", "2024-06-11", None, "Adam Scott", 0.0, 96.0, 0, "Portal"),
				("Password Reset Automation", "Workflow failing nightly", "Resolved", "Investigation", "High", "2024-05-03", "2024-05-06", "2024-05-06", "Priya Patel", 32.0, 6.0, 88, "Portal"),
			]
			database_cursor.executemany(
				"""
				INSERT INTO tickets (
					title, description, status, stage, priority, created_at, updated_at, resolved_at,
					assigned_to, time_to_resolve_hours, waiting_stage_hours, customer_satisfaction, channel
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				initial_tickets,
			)

		database_cursor.execute("SELECT COUNT(*), GROUP_CONCAT(title, '|') FROM incidents")
		total_incident_count, incident_titles_concat = database_cursor.fetchone()
		incident_titles_concat = incident_titles_concat or ""
		if total_incident_count == 0 or (total_incident_count <= 1 and "Phishing Email" in incident_titles_concat):
			database_cursor.execute("DELETE FROM incidents")
			initial_incidents = [
				("Credential Harvesting Campaign", "Targeted phishing against executives", "Phishing", "Email Link", "Critical", "Investigating", "SOC Level 1", "Jamie Fox", "2024-06-05T08:24:00", "2024-06-05T09:05:00", None, 0.7, 0.0, "Executive email compromise risk"),
				("Invoice Fraud Attempt", "Finance clerk received spoofed vendor request", "Phishing", "Spoofed Domain", "High", "Contained", "Finance", "Jamie Fox", "2024-05-27T13:15:00", "2024-05-27T13:40:00", "2024-05-27T18:20:00", 0.4, 5.1, "Potential payment diversion"),
				("Credential Stuffing Alerts", "Elevated failed logins from single ASN", "Credential Abuse", "Botnet", "Medium", "Monitoring", "Security Automation", "Azra Singh", "2024-05-30T22:30:00", "2024-05-30T22:42:00", None, 0.2, 0.0, "Possible account takeover"),
				("Suspicious USB Insertions", "Multiple USB devices on finance workstations", "Insider", "Physical", "High", "Resolved", "Security Awareness", "Morgan Hale", "2024-05-12T10:05:00", "2024-05-12T10:25:00", "2024-05-12T14:55:00", 0.3, 4.8, "Malware propagation concern"),
				("Phishing Portal Clone", "Fake VPN landing page discovered", "Phishing", "Web Spoof", "Critical", "Open", "Threat Intel", "Jamie Fox", "2024-06-09T07:50:00", "2024-06-09T08:20:00", None, 0.5, 0.0, "Credentials exfiltration active"),
			]
			database_cursor.executemany(
				"""
				INSERT INTO incidents (
					title, description, category, threat_vector, severity, status, reported_by, assigned_to,
					detected_at, first_response_at, resolved_at, time_to_first_response_hours,
					time_to_resolve_hours, business_impact
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				initial_incidents,
			)

		database_connection.commit()
		database_connection.close()
