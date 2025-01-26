from http import HTTPStatus
from enum import Enum

class Code(Enum):
    # 1xx: Authentication & Authorization Errors
    UNAUTHENTICATED = (100, "Không được xác thực", HTTPStatus.UNAUTHORIZED)
    ACCESS_DENIED = (101, "Truy cập bị từ chối", HTTPStatus.FORBIDDEN)
    ROLE_NOT_EXISTED = (102, "Role không tồn tại", HTTPStatus.NOT_FOUND)

    # 2xx: User Errors
    USER_EXISTED = (200, "Người dùng đã tồn tại", HTTPStatus.BAD_REQUEST)
    USER_NOT_EXISTED = (201, "Người dùng không tồn tại", HTTPStatus.NOT_FOUND)
    USER_NOT_FOUND = (202, "Không tìm thấy người dùng", HTTPStatus.NOT_FOUND)
    USER_PASSWORD_UPDATE_FAILED = (203, "Cập nhật mật khẩu thất bại", HTTPStatus.BAD_REQUEST)
    USERNAME_OR_EMAIL_ALREADY_EXISTS = (204, "Tên người dùng hoặc email đã tồn tại", HTTPStatus.BAD_REQUEST)

    # 3xx: Project Errors
    PROJECT_NOT_EXISTED = (300, "Project không tồn tại", HTTPStatus.NOT_FOUND)
    PROJECT_NOT_FOUND = (301, "Không tìm thấy Project", HTTPStatus.NOT_FOUND)

    # 4xx: Fresher Errors
    FRESHER_EXISTED = (400, "Fresher đã tồn tại", HTTPStatus.BAD_REQUEST)
    FRESHER_NOT_EXISTED = (401, "Fresher không tồn tại", HTTPStatus.NOT_FOUND)
    FRESHER_NOT_FOUND = (402, "Không tìm thấy Fresher", HTTPStatus.NOT_FOUND)

    # 5xx: FresherProject Errors
    FRESHERPROJECT_NOT_EXISTED = (500, "FresherProject không tồn tại", HTTPStatus.NOT_FOUND)
    FRESHERPROJECT_NOT_FOUND = (501, "Không tìm thấy FresherProject", HTTPStatus.NOT_FOUND)

    # 6xx: Center Errors
    CENTER_NOT_EXISTED = (600, "Center không tồn tại", HTTPStatus.NOT_FOUND)
    CENTER_NOT_FOUND = (601, "Không tìm thấy Center", HTTPStatus.NOT_FOUND)

    # 7xx: Assignment Errors
    ASSIGNMENT_NOT_EXISTED = (700, "Assignment không tồn tại", HTTPStatus.NOT_FOUND)
    ASSIGNMENT_NOT_FOUND = (701, "Không tìm thấy Assignment", HTTPStatus.NOT_FOUND)

    # 8xx: Notification Errors
    NOTIFICATION_NOT_EXISTED = (800, "Notification không tồn tại", HTTPStatus.NOT_FOUND)
    NOTIFICATION_NOT_FOUND = (801, "Không tìm thấy Notification", HTTPStatus.NOT_FOUND)

    # 9xx: Input & Email Errors
    ENTER_MISS_INFO = (900, "Nhập thiếu thông tin", HTTPStatus.BAD_REQUEST)
    ERROR_SEND_EMAIL = (901, "Lỗi gửi email", HTTPStatus.INTERNAL_SERVER_ERROR)
    ENTER_WRONG_INFO = (902, "Nhập sai thông tin", HTTPStatus.BAD_REQUEST)

    # 0xx: Uncategorized/Internal Errors
    INTERNAL_SERVER_ERROR = (0, "Lỗi hệ thống", HTTPStatus.INTERNAL_SERVER_ERROR)
    RUNTIME_EXCEPTION = (1, "Runtime Exception xảy ra", HTTPStatus.INTERNAL_SERVER_ERROR)
    UNCATEGORIZED_EXCEPTION = (2, "Lỗi chưa được phân loại", HTTPStatus.INTERNAL_SERVER_ERROR)

    # 10xx: Okay Responses
    OK = (1000, "OK", HTTPStatus.OK)
    LOGIN_SUCCESSFULLY = (1001, "Đăng nhập thành công", HTTPStatus.OK)
    LOGGED_IN = (1002, "Bạn đã đăng nhập", HTTPStatus.OK)

    def __init__(self, code, message, status_code):
        self._value_ = code
        self.message = message
        self.status_code = status_code
