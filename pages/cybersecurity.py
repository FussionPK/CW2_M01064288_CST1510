import streamlit as st
import pandas as pd
import json
from datetime import datetime

from database.db import DatabaseConnection
from services.database_manager import DbManagerService


def get_db_manager():
	database_connection = DatabaseConnection()
	database_connection.initialize()
	return DbManagerService(database_connection)


def main():
	st.set_page_config(page_title="Cybersecurity Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("Cybersecurity Dashboard")
	st.write("Track incidents and add new reports.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.warning("Please sign in on the Login page to make changes.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Current Incidents")
	all_incidents = database_manager_service.list_incidents()
	if len(all_incidents) == 0:
		st.info("No incidents recorded yet.")
	else:
		st.dataframe(pd.DataFrame(all_incidents))

	st.subheader("Add Incident")
	with st.form("incident_form"):
		incident_title = st.text_input("Title")
		incident_description = st.text_area("Description")
		incident_severity = st.selectbox("Severity", ["Low", "Medium", "High"])
		incident_status = st.selectbox("Status", ["New", "Investigating", "Closed"])
		incident_reported_by = st.text_input("Reported By")
		incident_assigned_to = st.text_input("Assigned To")
		incident_creation_date = st.text_input("Created At (YYYY-MM-DD)", value="2024-04-01")
		incident_last_updated = st.text_input("Updated At (YYYY-MM-DD)", value="2024-04-01")
		submit_incident_button = st.form_submit_button("Save Incident")

		if submit_incident_button:
			if incident_title == "" or incident_description == "":
				st.warning("Please enter a title and description.")
			else:
				database_manager_service.add_incident(incident_title, incident_description, incident_severity, incident_status, incident_reported_by, incident_assigned_to, incident_creation_date, incident_last_updated)
				st.success("Incident saved.")

	st.subheader("CSV File Upload")
	csv_file_upload = st.file_uploader("Upload a CSV file with incident data", type="csv", key="cybersecurity_csv")
	if csv_file_upload is not None:
		if st.button("Process CSV Upload", key="cybersecurity_csv_button"):
			try:
				csv_dataframe = pd.read_csv(csv_file_upload)
				filename_text = csv_file_upload.name
				row_count_number = len(csv_dataframe)
				column_names_text = ",".join(csv_dataframe.columns.tolist())
				upload_date_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				data_json_text = csv_dataframe.to_json(orient="records")
				
				database_manager_service.add_csv_data(filename_text, row_count_number, column_names_text, upload_date_text, data_json_text)
				st.success(f"CSV file '{filename_text}' uploaded successfully with {row_count_number} rows.")
				st.subheader("Preview")
				st.dataframe(csv_dataframe.head(10))
			except Exception as error:
				st.error(f"Error processing CSV: {str(error)}")

	st.subheader("Uploaded CSV Files")
	all_csv_uploads = database_manager_service.list_csv_data()
	if len(all_csv_uploads) == 0:
		st.info("No CSV files uploaded yet.")
	else:
		st.dataframe(pd.DataFrame(all_csv_uploads))


if __name__ == "__main__":
	main()
