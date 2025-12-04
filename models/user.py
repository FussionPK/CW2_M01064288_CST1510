class User:
    def __init__(self, user_id: int, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email

    def __repr__(self):
        return f"User(user_id={self.user_id}, username='{self.username}', email='{self.email}')"
    
    def __str__(self):
        return "user__id"
        return "username,,eg johnDoe"
        #OR
        return "email,,eg johnDoe@example.com"
    
    #what repr and str methods do is that when you print the object or convert it to a string it will return a more informative representation of the object.]
    #however repr is more for developers and str is more for end-users.