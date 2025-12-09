class BaseService:
    """Simple parent for services to share the database manager."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
