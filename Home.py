import streamlit as st

from database.db import DatabaseConnection


def prepare_database():
	# Ensure tables exist before pages run
	db = DatabaseConnection()
	db.initialize()


def main():
	st.set_page_config(page_title="Multi-Domain Platform", page_icon=":bar_chart:", initial_sidebar_state="expanded")

	prepare_database()

	# Initialize session state for user
	if "user" not in st.session_state:
		st.session_state["user"] = None

	# If user is not logged in, redirect to login page
	if st.session_state["user"] is None:
		st.switch_page("pages/0_Login.py")
		return

	# If user is logged in, show welcome page with sidebar
	st.title(f"Welcome, {st.session_state['user']['username']}!")
	st.write("You can navigate using the sidebar to access all dashboards.")
	st.subheader("Available Pages")
	st.write("- Cybersecurity: track and manage security incidents")
	st.write("- Data Science: manage and track datasets")
	st.write("- IT Operations: manage service desk tickets")
	st.write("- AI Assistant: separate page (unchanged)")


if __name__ == "__main__":
	main()

