from app.config.settings import settings
from fastapi import HTTPException, status


class ErrorUtils:
    @staticmethod
    def toHTTPException(exception: Exception) -> HTTPException:
        if isinstance(exception, HTTPException):
            return exception
        if settings.DEBUG:
            return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exception))
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
