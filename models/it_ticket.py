class Tickets:
    def __init__(self, ticket_id: int, title: str, description: str, status: str, priority: str, created_at: str, updated_at: str, assigned_to: int):
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"Tickets(ticket_id={self.ticket_id}, title='{self.title}', description='{self.description}', status='{self.status}', priority='{self.priority}', created_at='{self.created_at}', updated_at='{self.updated_at}')"