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
	st.set_page_config(page_title="Data Science Dashboard", page_icon=":bar_chart:", initial_sidebar_state="expanded")
	st.title("Data Science Dashboard")
	st.write("Manage datasets and keep simple notes.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	database_manager_service = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to add data.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Datasets")
	all_datasets = database_manager_service.list_datasets()
	if len(all_datasets) == 0:
		st.info("No datasets recorded.")
	else:
		st.dataframe(pd.DataFrame(all_datasets))

	st.subheader("Add Dataset")
	with st.form("dataset_form"):
		dataset_name = st.text_input("Name")
		dataset_description = st.text_area("Description")
		dataset_creation_date = st.text_input("Created At (YYYY-MM-DD)", value="2024-05-01")
		dataset_last_updated = st.text_input("Updated At (YYYY-MM-DD)", value="2024-05-01")
		add_dataset_button = st.form_submit_button("Save Dataset")

		if add_dataset_button:
			if dataset_name == "":
				st.warning("Name is required.")
			else:
				database_manager_service.add_dataset(dataset_name, dataset_description, dataset_creation_date, dataset_last_updated)
				st.success("Dataset saved.")

	st.subheader("CSV File Upload")
	csv_file_upload = st.file_uploader("Upload a CSV file", type="csv")
	if csv_file_upload is not None:
		if st.button("Process CSV Upload"):
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
