class Ticket:
    """Represents an IT service desk ticket with performance metrics."""

    def __init__(
        self,
        ticket_id: int,
        title: str,
        description: str,
        status: str,
        stage: str,
        priority: str,
        created_at: str,
        updated_at: str,
        resolved_at: str,
        assigned_to: str,
        time_to_resolve_hours: float,
        waiting_stage_hours: float,
        customer_satisfaction: int,
        channel: str,
    ):
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.status = status
        self.stage = stage
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at
        self.resolved_at = resolved_at
        self.assigned_to = assigned_to
        self.time_to_resolve_hours = time_to_resolve_hours
        self.waiting_stage_hours = waiting_stage_hours
        self.customer_satisfaction = customer_satisfaction
        self.channel = channel

    def __repr__(self):
        return (
            "Ticket(ticket_id={ticket_id}, title='{title}', stage='{stage}', assigned_to='{assignee}', "
            "time_to_resolve_hours={resolve}, waiting_stage_hours={waiting})"
        ).format(
            ticket_id=self.ticket_id,
            title=self.title,
            stage=self.stage,
            assignee=self.assigned_to,
            resolve=self.time_to_resolve_hours,
            waiting=self.waiting_stage_hours,
        )