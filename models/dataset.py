class DataSet:
    """Represents a managed dataset."""

    def __init__(self, dataset_id: int, name: str, description: str, created_at: str, updated_at: str):
        self.dataset_id = dataset_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return (
            f"DataSet(dataset_id={self.dataset_id}, name='{self.name}', description='{self.description}', "
            f"created_at='{self.created_at}', updated_at='{self.updated_at}')"
        )