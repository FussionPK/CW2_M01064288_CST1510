class DataSet:
    """Represents a governed enterprise dataset."""

    def __init__(
        self,
        dataset_id: int,
        name: str,
        description: str,
        owner_department: str,
        data_source: str,
        row_count: int,
        size_mb: float,
        quality_score: float,
        retention_policy: str,
        status: str,
        last_accessed: str,
        created_at: str,
        updated_at: str,
    ):
        self.dataset_id = dataset_id
        self.name = name
        self.description = description
        self.owner_department = owner_department
        self.data_source = data_source
        self.row_count = row_count
        self.size_mb = size_mb
        self.quality_score = quality_score
        self.retention_policy = retention_policy
        self.status = status
        self.last_accessed = last_accessed
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return (
            "DataSet(dataset_id={dataset_id}, name='{name}', owner_department='{department}', "
            "row_count={rows}, size_mb={size}, status='{status}')"
        ).format(
            dataset_id=self.dataset_id,
            name=self.name,
            department=self.owner_department,
            rows=self.row_count,
            size=self.size_mb,
            status=self.status,
        )