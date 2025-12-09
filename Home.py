import streamlit as st

from database.db import DatabaseConnection


def prepare_database():
	# Ensure tables exist before pages run
	db = DatabaseConnection()
	db.initialize()


def main():
	st.set_page_config(page_title="Multi-Domain Platform", page_icon=":bar_chart:")
	st.title("Multi-Domain Intelligence Platform")
	st.write("Use the sidebar to open each dashboard page.")

	prepare_database()

	st.subheader("Pages")
	st.write("- Login: create or use a simple account")
	st.write("- Cybersecurity: track incidents")
	st.write("- Data Science: manage datasets")
	st.write("- IT Operations: manage service tickets")
	st.write("- AI Assistant: separate page (unchanged)")

	st.subheader("How to start")
	st.write("1. Open the Login page and sign in.")
	st.write("2. Add sample records in each area.")
	st.write("3. Refresh data tables to see updates.")


if __name__ == "__main__":
	main()
