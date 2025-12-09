from models.base import BaseRecord


class Ticket(BaseRecord):
    """Represents a simple IT service desk ticket."""

    def __init__(self, ticket_id: int, title: str, description: str, status: str, priority: str, created_at: str, updated_at: str, assigned_to: str):
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at
        self.assigned_to = assigned_to

    def __repr__(self):
        return (
            f"Ticket(ticket_id={self.ticket_id}, title='{self.title}', description='{self.description}', "
            f"status='{self.status}', priority='{self.priority}', created_at='{self.created_at}', "
            f"updated_at='{self.updated_at}', assigned_to='{self.assigned_to}')"
        )