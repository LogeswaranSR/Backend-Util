class MsgException(BaseException):
    def __init__(self, title: str, message: str, httpStatus: int):
        super().__init__(message)
        self.title = title
        self.message = message
        self.httpStatus = httpStatus
    
    def __init__(self, title: str, message: str):
        super().__init__(message)
        self.title = title
        self.message = message
        self.httpStatus = 500
    

class ExceptionUtil:
    @staticmethod
    def bad_request_exception(message: str):
        return MsgException("BadRequest", message, 400)
    
    @staticmethod
    def unauthorized_exception(message: str):
        return MsgException("AuthError", message, 401)