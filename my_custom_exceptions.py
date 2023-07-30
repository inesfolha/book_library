class APICallError(Exception):
    """Custom exception class to represent errors related to API calls."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)