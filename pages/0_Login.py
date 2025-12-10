import streamlit as st

from database.db import DatabaseConnection
from services.database_manager import DbManagerService
from services.auth_manager import AuthManagerService


def get_services():
	# Build shared services for the page
	db_connection = DatabaseConnection()
	db_connection.initialize()
	db_manager = DbManagerService(db_connection)
	auth_manager = AuthManagerService(db_manager)
	return auth_manager, db_manager


def main():
	st.set_page_config(page_title="Login", page_icon=":bar_chart:", initial_sidebar_state="collapsed")
	st.title("Login")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	auth_manager, db_manager = get_services()

	st.write("Use this page to sign in or create a basic account.")

	login_placeholder = st.empty()
	register_placeholder = st.empty()

	with login_placeholder.form("login_form"):
		st.subheader("Sign In")
		username = st.text_input("Username")
		password = st.text_input("Password", type="password")
		login_button = st.form_submit_button("Login")
		if login_button:
			user = auth_manager.authenticate_user(username, password)
			if user is None:
				st.warning("Invalid username or password.")
			else:
				st.session_state["user"] = user
				st.success(f"Welcome {user['username']}! Redirecting...")
				st.switch_page("Home.py")

	with register_placeholder.form("register_form"):
		st.subheader("Register")
		new_username = st.text_input("New Username")
		new_email = st.text_input("Email")
		new_role = st.selectbox("Role", ["analyst", "viewer"])
		new_password = st.text_input("New Password", type="password")
		register_button = st.form_submit_button("Create Account")
		if register_button:
			created = auth_manager.register_user(new_username, new_email, new_role, new_password)
			if created:
				st.success("Account created. You can sign in now.")
			else:
				st.warning("User already exists or missing details.")

	st.subheader("Current Session")
	if st.session_state["user"] is None:
		st.info("No user is signed in.")
	else:
		user_info = st.session_state["user"]
		st.write("Username:", user_info["username"])
		st.write("Role:", user_info["role"])
		st.write("Email:", user_info["email"])
		logout_button = st.button("Logout")
		if logout_button:
			st.session_state["user"] = None
			st.success("You have logged out.")


if __name__ == "__main__":
	main()
