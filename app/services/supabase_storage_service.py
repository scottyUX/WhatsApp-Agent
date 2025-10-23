from __future__ import annotations

import typing as t
import uuid
from dataclasses import dataclass

try:
    from supabase import Client as SbClient, create_client
    from supabase.lib.client_options import ClientOptions  # <-- important
except Exception as _exc:  # pragma: no cover
    SbClient = t.Any  # type: ignore
    create_client = None  # type: ignore
    ClientOptions = None  # type: ignore
    _SUPABASE_IMPORT_ERROR = _exc

from app.config.settings import settings


@dataclass
class UploadedImage:
    filename: str
    data: bytes
    content_type: str | None = None


class SupabaseStorageService:
    """
    Handles uploads to Supabase Storage for patient images.

    - PUBLIC bucket: returns deterministic public URLs
    - PRIVATE bucket: returns signed URLs; normalizes SDK return shapes
    """

    def __init__(self) -> None:
        if create_client is None:
            raise RuntimeError(
                "Supabase SDK is not installed. Install it with 'pip install supabase>=2.4.0'."
            ) from _SUPABASE_IMPORT_ERROR

        # Required config
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError("Supabase credentials are not configured.")
        if not settings.SUPABASE_IMAGE_BUCKET:
            raise RuntimeError("Supabase image bucket is not configured (SUPABASE_IMAGE_BUCKET).")

        # Optional toggles
        self._bucket_is_public: bool = bool(getattr(settings, "SUPABASE_BUCKET_IS_PUBLIC", True))
        self._signed_url_ttl: int = int(getattr(settings, "SUPABASE_SIGNED_URL_TTL", 3600))

        # ✅ Use ClientOptions (NOT a dict)
        if ClientOptions is not None:
            options = ClientOptions(
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                },
                auto_refresh_token=False,
                persist_session=False,
            )
        else:
            options = None 

        self._client: SbClient = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY, 
            options=options,
        )
        self._bucket_name = settings.SUPABASE_IMAGE_BUCKET

    def upload_patient_images(self, profile_id: uuid.UUID, uploads: list[UploadedImage]) -> list[str]:
        if not uploads:
            raise ValueError("At least one image is required for upload.")

        storage = self._client.storage.from_(self._bucket_name)
        out_urls: list[str] = []

        for up in uploads:
            object_path = self._build_object_path(profile_id, up.filename)

            # 1) upload
            file_opts = {"content-type": (up.content_type or self._guess_content_type(up.filename))}
            res = storage.upload(path=object_path, file=up.data, file_options=file_opts)
            self._raise_if_error("upload", res)

            # 2) URL
            if self._bucket_is_public:
                # Try SDK first (normalize), then deterministic builder
                public_res = storage.get_public_url(object_path)
                url = self._extract_public_url(public_res) or self._build_public_url(object_path)
            else:
                signed_res = storage.create_signed_url(object_path, self._signed_url_ttl)
                self._raise_if_error("create_signed_url", signed_res)
                url = self._extract_signed_url(signed_res, object_path)

            if not url:
                raise RuntimeError(f"Failed to generate public URL for {up.filename}")

            out_urls.append(url)

        return out_urls

    def _build_object_path(self, profile_id: uuid.UUID, filename: str) -> str:
        safe_filename = (filename or "image").replace(" ", "_")
        return f"{profile_id}/{uuid.uuid4()}_{safe_filename}".lstrip("/")

    def _build_public_url(self, path: str) -> str:
        base = settings.SUPABASE_URL.rstrip("/")
        return f"{base}/storage/v1/object/public/{self._bucket_name}/{path.lstrip('/')}"

    def _extract_public_url(self, result: t.Any) -> str | None:
        """
        Accept shapes:
          - "https://.../public/<bucket>/<path>"
          - {"publicUrl": "..."} / {"publicURL": "..."}
          - {"data": {"publicUrl": "..."}} / {"data": {"publicURL": "..."}}
        """
        if isinstance(result, str) and result:
            return result
        if isinstance(result, dict):
            for k in ("publicUrl", "publicURL"):
                v = result.get(k)
                if isinstance(v, str) and v:
                    return v
            data = result.get("data")
            if isinstance(data, dict):
                for k in ("publicUrl", "publicURL"):
                    v = data.get(k)
                    if isinstance(v, str) and v:
                        return v
        return None

    def _extract_signed_url(self, result: t.Any, path: str) -> str | None:
        """
        Accept shapes:
          - {"data": {"signedUrl": "https://.../storage/v1/object/sign/<bucket>/<path>?token=..."}}
          - {"signedUrl": "..."} / {"signedURL": "..."}
          - relative "/storage/v1/object/sign/<bucket>/<path>?token=..."
          - token-only: {"data": {"token": "<...>"}} → build absolute URL with token
        """
        # direct string
        if isinstance(result, str) and result:
            return self._abs(result) if result.startswith("/") else result

        if isinstance(result, dict):
            for key in ("signedUrl", "signedURL"):
                v = result.get(key)
                if isinstance(v, str) and v:
                    return self._abs(v) if v.startswith("/") else v
            data = result.get("data")
            if isinstance(data, dict):
                for key in ("signedUrl", "signedURL"):
                    v = data.get(key)
                    if isinstance(v, str) and v:
                        return self._abs(v) if v.startswith("/") else v
                token = data.get("token")
                if isinstance(token, str) and token:
                    rel = f"/storage/v1/object/sign/{self._bucket_name}/{path.lstrip('/')}?token={token}"
                    return self._abs(rel)

        return None

    def _abs(self, maybe_relative: str) -> str:
        if maybe_relative.startswith("/"):
            return f"{settings.SUPABASE_URL.rstrip('/')}{maybe_relative}"
        return maybe_relative

    @staticmethod
    def _guess_content_type(name: str) -> str:
        n = (name or "").lower()
        if n.endswith(".png"):
            return "image/png"
        if n.endswith(".jpg") or n.endswith(".jpeg"):
            return "image/jpeg"
        if n.endswith(".webp"):
            return "image/webp"
        if n.endswith(".gif"):
            return "image/gif"
        return "application/octet-stream"

    @staticmethod
    def _raise_if_error(op: str, result: t.Any) -> None:
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            msg = err if isinstance(err, str) else err.get("message", str(err))
            raise RuntimeError(f"Supabase {op} error: {msg}")