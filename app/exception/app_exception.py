from app.enums.code import Code

class AppException(Exception):
    """Custom exception class to hold error code."""
    def __init__(self, code: Code):
        self.code = code
