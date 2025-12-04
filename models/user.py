class User:
    def __init__(self, user_id: int, username: str, email: str, role: str, password_hash: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = password_hash

    def __repr__(self):
        return f"User(user_id={self.user_id}, username='{self.username}', email='{self.email}', role='{self.role}', password_hash='{self.password_hash}')"