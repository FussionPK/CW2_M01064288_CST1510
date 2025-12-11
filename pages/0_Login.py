import streamlit as st

from database.db import DatabaseConnection
from services.database_manager import DbManagerService
from services.auth_manager import AuthManagerService


def get_services():
	# Build shared services for the page
	database_connection = DatabaseConnection()
	database_connection.initialize()
	database_manager_service = DbManagerService(database_connection)
	authentication_service = AuthManagerService(database_manager_service)
	return authentication_service, database_manager_service


def main():
	st.set_page_config(page_title="Login/Register", page_icon=":bar_chart:", initial_sidebar_state="collapsed")
	
	# Hide sidebar navigation on login page
	st.markdown(
		"""
		<style>
		[data-testid="stSidebar"] {
			display: none;
		}
		</style>
		""",
		unsafe_allow_html=True
	)
	
	st.title("Login")

	if "user" not in st.session_state:
		st.session_state["user"] = None

	authentication_service, database_manager_service = get_services()

	st.write("Use this page to sign in or create a basic account.")

	login_form_placeholder = st.empty()
	registration_form_placeholder = st.empty()

	with login_form_placeholder.form("login_form"):
		st.subheader("Sign In")
		entered_username = st.text_input("Username")
		entered_password = st.text_input("Password", type="password")
		login_button_clicked = st.form_submit_button("Login")
		if login_button_clicked:
			authenticated_user = authentication_service.authenticate_user(entered_username, entered_password)
			if authenticated_user is None:
				st.warning("Invalid username or password.")
			else:
				st.session_state["user"] = authenticated_user
				st.success(f"Welcome {authenticated_user['username']}! Redirecting...")
				st.switch_page("Home.py")

	with registration_form_placeholder.form("register_form"):
		st.subheader("Register")
		new_account_username = st.text_input("New Username")
		new_account_email = st.text_input("Email")
		new_account_role = st.selectbox("Role", ["analyst", "viewer"])
		new_account_password = st.text_input("New Password", type="password")
		account_creation_button = st.form_submit_button("Create Account")
		if account_creation_button:
			account_was_created = authentication_service.register_user(new_account_username, new_account_email, new_account_role, new_account_password)
			if account_was_created:
				st.success("Account created. You can sign in now.")
			else:
				st.warning("User already exists or missing details.")

	st.subheader("Current Session")
	if st.session_state["user"] is None:
		st.info("No user is signed in.")
	else:
		logged_in_user_info = st.session_state["user"]
		st.write("Username:", logged_in_user_info["username"])
		st.write("Role:", logged_in_user_info["role"])
		st.write("Email:", logged_in_user_info["email"])
		logout_button_clicked = st.button("Logout")
		if logout_button_clicked:
			st.session_state["user"] = None
			st.success("You have logged out.")


if __name__ == "__main__":
	main()
