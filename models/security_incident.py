class Incident:
    """Represents a simple security incident record."""

    def __init__(self, incident_id: int, title: str, description: str, severity: str, status: str, reported_by: str, assigned_to: str, created_at: str, updated_at: str):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.severity = severity
        self.status = status
        self.reported_by = reported_by
        self.assigned_to = assigned_to
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return (
            f"Incident(incident_id={self.incident_id}, title='{self.title}', description='{self.description}', "
            f"severity='{self.severity}', status='{self.status}', reported_by='{self.reported_by}', "
            f"assigned_to='{self.assigned_to}', created_at='{self.created_at}', updated_at='{self.updated_at}')"
        )