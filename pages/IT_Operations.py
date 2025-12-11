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
	st.set_page_config(page_title="IT Operations Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("IT Operations Dashboard")
	st.write("View and create support tickets.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to update tickets.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Tickets")
	all_tickets = database_manager_service.list_tickets()
	if len(all_tickets) == 0:
		st.info("No tickets open.")
	else:
		st.dataframe(pd.DataFrame(all_tickets))

	st.subheader("Add Ticket")
	with st.form("ticket_form"):
		ticket_title = st.text_input("Title")
		ticket_description = st.text_area("Description")
		ticket_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
		ticket_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
		ticket_assigned_to = st.text_input("Assigned To")
		ticket_creation_date = st.text_input("Created At (YYYY-MM-DD)", value="2024-06-01")
		ticket_last_updated = st.text_input("Updated At (YYYY-MM-DD)", value="2024-06-01")
		submit_ticket_button = st.form_submit_button("Save Ticket")

		if submit_ticket_button:
			if ticket_title == "" or ticket_description == "":
				st.warning("Title and description are required.")
			else:
				database_manager_service.add_ticket(ticket_title, ticket_description, ticket_status, ticket_priority, ticket_creation_date, ticket_last_updated, ticket_assigned_to)
				st.success("Ticket saved.")

	st.subheader("CSV File Upload")
	csv_file_upload = st.file_uploader("Upload a CSV file with ticket data", type="csv", key="it_ops_csv")
	if csv_file_upload is not None:
		if st.button("Process CSV Upload", key="it_ops_csv_button"):
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
