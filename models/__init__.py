from .user import User
from .security_incident import Incident
from .it_ticket import Tickets
from .dataset import Data_Set

__all__ = [
    "User",
    "Incident",
    "Tickets",
    "Data_set",
]

#the above code will ensure importing from models package will have access to all the defined classes.
#also it will look neater when importing from models package.