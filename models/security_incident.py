class Incident:
    """Represents a cybersecurity incident enriched with response metrics."""

    def __init__(
        self,
        incident_id: int,
        title: str,
        description: str,
        category: str,
        threat_vector: str,
        severity: str,
        status: str,
        reported_by: str,
        assigned_to: str,
        detected_at: str,
        first_response_at: str,
        resolved_at: str,
        time_to_first_response_hours: float,
        time_to_resolve_hours: float,
        business_impact: str,
    ):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.category = category
        self.threat_vector = threat_vector
        self.severity = severity
        self.status = status
        self.reported_by = reported_by
        self.assigned_to = assigned_to
        self.detected_at = detected_at
        self.first_response_at = first_response_at
        self.resolved_at = resolved_at
        self.time_to_first_response_hours = time_to_first_response_hours
        self.time_to_resolve_hours = time_to_resolve_hours
        self.business_impact = business_impact

    def __repr__(self):
        return (
            "Incident(incident_id={incident_id}, category='{category}', severity='{severity}', "
            "status='{status}', assigned_to='{assignee}', time_to_resolve_hours={resolve})"
        ).format(
            incident_id=self.incident_id,
            category=self.category,
            severity=self.severity,
            status=self.status,
            assignee=self.assigned_to,
            resolve=self.time_to_resolve_hours,
        )