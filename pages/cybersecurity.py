import streamlit as st
import pandas as pd

from database.db import DatabaseConnection
from services.database_manager import DbManagerService


def get_db_manager():
	connection = DatabaseConnection()
	connection.initialize()
	return DbManagerService(connection)


def main():
	st.title("Cybersecurity Dashboard")
	st.write("Track incidents and add new reports.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	db_manager = get_db_manager()

	if st.session_state["user"] is None:
		st.warning("Please sign in on the Login page to make changes.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Current Incidents")
	incidents = db_manager.list_incidents()
	if len(incidents) == 0:
		st.info("No incidents recorded yet.")
	else:
		st.dataframe(pd.DataFrame(incidents))

	st.subheader("Add Incident")
	with st.form("incident_form"):
		title = st.text_input("Title")
		description = st.text_area("Description")
		severity = st.selectbox("Severity", ["Low", "Medium", "High"])
		status = st.selectbox("Status", ["New", "Investigating", "Closed"])
		reported_by = st.text_input("Reported By")
		assigned_to = st.text_input("Assigned To")
		created_at = st.text_input("Created At (YYYY-MM-DD)", value="2024-04-01")
		updated_at = st.text_input("Updated At (YYYY-MM-DD)", value="2024-04-01")
		submit_button = st.form_submit_button("Save Incident")

		if submit_button:
			if title == "" or description == "":
				st.warning("Please enter a title and description.")
			else:
				db_manager.add_incident(title, description, severity, status, reported_by, assigned_to, created_at, updated_at)
				st.success("Incident saved.")


if __name__ == "__main__":
	main()
