import hashlib
from typing import Optional, Dict

from services.base_service import BaseService


class AuthManagerService(BaseService):
    """Handles simple username and password checks."""

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def _hash_password(self, password: str) -> str:
        # Basic sha256 hashing to avoid plain text storage
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username: str, email: str, role: str, password: str) -> bool:
        if username == "" or password == "":
            return False
        password_hash = self._hash_password(password)
        created = self.db_manager.add_user(username, email, role, password_hash)
        return created

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        # Check if the hashed password matches the stored one
        user_rows = self.db_manager.get_user_by_username(username)
        if len(user_rows) == 0:
            return None
        stored_user = user_rows[0]
        hashed_input = self._hash_password(password)
        if stored_user["password_hash"] == hashed_input:
            return stored_user
        return None