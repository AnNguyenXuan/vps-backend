class DuplicateDataError(Exception):
    """Exception khi có lỗi trùng dữ liệu (ví dụ: username hoặc email đã tồn tại)."""
    def __init__(self, message: str = "Dữ liệu đã tồn tại"):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    """Exception khi dữ liệu không tồn tại."""
    def __init__(self, message: str = "Dữ liệu không tồn tại"):
        self.message = message
        super().__init__(self.message)
