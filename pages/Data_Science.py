import streamlit as st
import pandas as pd

from database.db import DatabaseConnection
from services.database_manager import DbManagerService


def get_db_manager():
	connection = DatabaseConnection()
	connection.initialize()
	return DbManagerService(connection)


def main():
	st.title("Data Science Dashboard")
	st.write("Manage datasets and keep simple notes.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	db_manager = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to add data.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Datasets")
	datasets = db_manager.list_datasets()
	if len(datasets) == 0:
		st.info("No datasets recorded.")
	else:
		st.dataframe(pd.DataFrame(datasets))

	st.subheader("Add Dataset")
	with st.form("dataset_form"):
		name = st.text_input("Name")
		description = st.text_area("Description")
		created_at = st.text_input("Created At (YYYY-MM-DD)", value="2024-05-01")
		updated_at = st.text_input("Updated At (YYYY-MM-DD)", value="2024-05-01")
		add_button = st.form_submit_button("Save Dataset")

		if add_button:
			if name == "":
				st.warning("Name is required.")
			else:
				db_manager.add_dataset(name, description, created_at, updated_at)
				st.success("Dataset saved.")


if __name__ == "__main__":
	main()
