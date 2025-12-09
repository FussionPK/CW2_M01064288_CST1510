import streamlit as st
import pandas as pd

from database.db import DatabaseConnection
from services.database_manager import DbManagerService


def get_db_manager():
	connection = DatabaseConnection()
	connection.initialize()
	return DbManagerService(connection)


def main():
	st.title("IT Operations Dashboard")
	st.write("View and create support tickets.")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	db_manager = get_db_manager()

	if st.session_state["user"] is None:
		st.info("Sign in on the Login page to update tickets.")
	else:
		st.success(f"Signed in as {st.session_state['user']['username']}")

	st.subheader("Tickets")
	tickets = db_manager.list_tickets()
	if len(tickets) == 0:
		st.info("No tickets open.")
	else:
		st.dataframe(pd.DataFrame(tickets))

	st.subheader("Add Ticket")
	with st.form("ticket_form"):
		title = st.text_input("Title")
		description = st.text_area("Description")
		status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
		priority = st.selectbox("Priority", ["Low", "Medium", "High"])
		assigned_to = st.text_input("Assigned To")
		created_at = st.text_input("Created At (YYYY-MM-DD)", value="2024-06-01")
		updated_at = st.text_input("Updated At (YYYY-MM-DD)", value="2024-06-01")
		submit_ticket = st.form_submit_button("Save Ticket")

		if submit_ticket:
			if title == "" or description == "":
				st.warning("Title and description are required.")
			else:
				db_manager.add_ticket(title, description, status, priority, created_at, updated_at, assigned_to)
				st.success("Ticket saved.")


if __name__ == "__main__":
	main()
