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

    def add_dataset(
        self,
        name: str,
        description: str,
        owner_department: str,
        data_source: str,
        row_count: int,
        size_mb: float,
        quality_score: float,
        retention_policy: str,
        status: str,
        last_accessed: str,
        created_at: str,
        updated_at: str,
    ) -> None:
        self.execute_insert_or_update_query(
            """
            INSERT INTO datasets (
                name, description, owner_department, data_source, row_count, size_mb, quality_score,
                retention_policy, status, last_accessed, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                owner_department,
                data_source,
                row_count,
                size_mb,
                quality_score,
                retention_policy,
                status,
                last_accessed,
                created_at,
                updated_at,
            ),
        )

    def list_datasets(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM datasets", ())

    def add_ticket(
        self,
        title: str,
        description: str,
        status: str,
        stage: str,
        priority: str,
        created_at: str,
        updated_at: str,
        resolved_at: str,
        assigned_to: str,
        time_to_resolve_hours: float,
        waiting_stage_hours: float,
        customer_satisfaction: int,
        channel: str,
    ) -> None:
        self.execute_insert_or_update_query(
            """
            INSERT INTO tickets (
                title, description, status, stage, priority, created_at, updated_at, resolved_at,
                assigned_to, time_to_resolve_hours, waiting_stage_hours, customer_satisfaction, channel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                status,
                stage,
                priority,
                created_at,
                updated_at,
                resolved_at,
                assigned_to,
                time_to_resolve_hours,
                waiting_stage_hours,
                customer_satisfaction,
                channel,
            ),
        )

    def list_tickets(self) -> List[Dict]:
        return self.execute_select_query("SELECT * FROM tickets", ())

    def add_incident(
        self,
        title: str,
        description: str,
        category: str,
        threat_vector: str,
        severity: str,
        status: str,
        reported_by: str,
        assigned_to: str,
        detected_at: str,
        first_response_at: str,
        resolved_at: str,
        time_to_first_response_hours: float,
        time_to_resolve_hours: float,
        business_impact: str,
    ) -> None:
        self.execute_insert_or_update_query(
            """
            INSERT INTO incidents (
                title, description, category, threat_vector, severity, status, reported_by, assigned_to,
                detected_at, first_response_at, resolved_at, time_to_first_response_hours,
                time_to_resolve_hours, business_impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                category,
                threat_vector,
                severity,
                status,
                reported_by,
                assigned_to,
                detected_at,
                first_response_at,
                resolved_at,
                time_to_first_response_hours,
                time_to_resolve_hours,
                business_impact,
            ),
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

    def incident_counts_by_category(self) -> List[Dict]:
        return self.execute_select_query(
            "SELECT category, COUNT(*) AS total FROM incidents GROUP BY category ORDER BY total DESC",
            (),
        )

    def incident_resolution_metrics(self) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT
                severity,
                AVG(time_to_first_response_hours) AS avg_first_response,
                AVG(time_to_resolve_hours) AS avg_resolve,
                SUM(CASE WHEN status NOT IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS backlog
            FROM incidents
            GROUP BY severity
            ORDER BY backlog DESC
            """,
            (),
        )

    def open_incidents_by_category(self) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT category, COUNT(*) AS open_incidents
            FROM incidents
            WHERE status NOT IN ('Resolved','Closed','Contained')
            GROUP BY category
            ORDER BY open_incidents DESC
            """,
            (),
        )

    def ticket_metrics_by_assignee(self) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT
                assigned_to,
                AVG(CASE WHEN time_to_resolve_hours > 0 THEN time_to_resolve_hours END) AS avg_resolution_hours,
                AVG(waiting_stage_hours) AS avg_waiting_hours,
                AVG(customer_satisfaction) AS avg_csat,
                SUM(CASE WHEN status NOT IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS active_tickets
            FROM tickets
            GROUP BY assigned_to
            ORDER BY (avg_resolution_hours IS NULL), avg_resolution_hours DESC
            """,
            (),
        )

    def ticket_wait_times_by_stage(self) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT stage, AVG(waiting_stage_hours) AS avg_waiting_hours, COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY stage
            ORDER BY avg_waiting_hours DESC
            """,
            (),
        )

    def dataset_summary_by_department(self) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT
                owner_department,
                COUNT(*) AS dataset_count,
                SUM(row_count) AS total_rows,
                SUM(size_mb) AS total_size_mb,
                AVG(quality_score) AS avg_quality
            FROM datasets
            GROUP BY owner_department
            ORDER BY total_size_mb DESC
            """,
            (),
        )

    def datasets_requiring_archival(self, size_threshold: float, months_inactive_threshold: float) -> List[Dict]:
        return self.execute_select_query(
            """
            SELECT * FROM datasets
            WHERE size_mb >= ? OR status = 'Inactive'
            ORDER BY size_mb DESC
            """,
            (size_threshold,),
        )