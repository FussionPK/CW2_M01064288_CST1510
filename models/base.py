class BaseRecord:
    """Simple base class for shared helpers across records."""

    def to_dict(self) -> dict:
        # Convert the instance dictionary into a plain dict for display or storage
        return dict(self.__dict__)
