import bcrypt
from typing import Optional, Dict


class AuthManagerService:
    """Handles username and password authentication with bcrypt salting."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def hash_password_securely(self, password: str) -> str:
        # Use bcrypt with automatic salt generation (default: 12 rounds)
        # Returns bytes, decode to string for database storage
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed_password.decode("utf-8")

    def register_user(self, username: str, email: str, role: str, password: str) -> bool:
        if username == "" or password == "":
            return False
        hashed_password = self.hash_password_securely(password)
        user_created = self.db_manager.add_user(username, email, role, hashed_password)
        return user_created

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        # Check if the input password matches the stored bcrypt hash
        matching_users = self.db_manager.get_user_by_username(username)
        if len(matching_users) == 0:
            return None
        stored_user_data = matching_users[0]
        stored_password_hash = stored_user_data["password_hash"].encode("utf-8")
        input_password_bytes = password.encode("utf-8")
        # bcrypt.checkpw compares password with its hash, returns True if match
        if bcrypt.checkpw(input_password_bytes, stored_password_hash):
            return stored_user_data
        return None