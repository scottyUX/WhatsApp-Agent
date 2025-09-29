from fastapi import Request
from typing import Optional


class RequestUtils:
    @staticmethod
    def get_device_id_from_headers(request: Request) -> Optional[str]:
        return request.headers.get("X-Device-ID", None)

    @staticmethod
    def get_ip_address_from_headers(request: Request) -> Optional[str]:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else None
