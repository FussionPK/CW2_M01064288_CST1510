from .ai_assistant import AIService
from .auth_manager import AuthManagerService
from .database_manager import DBmanagerService

__all__ = [
    "AIService",
    "AuthManagerService",
    "DBmanagerService",
]

#the above code will ensure importing from services package will have access to all the defined classes.
#also it will look neater when importing from services package.