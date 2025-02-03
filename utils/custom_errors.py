
class URLError(Exception):
    """Custom exception for URL errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)