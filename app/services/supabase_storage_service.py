import typing
import uuid
from dataclasses import dataclass
from typing import List, Optional

if typing.TYPE_CHECKING:  # pragma: no cover - typing hint support
    from supabase import Client as SupabaseClient  # pragma: no cover
else:  # pragma: no cover - runtime fallback
    SupabaseClient = typing.Any  # type: ignore[assignment]

try:
    from supabase import Client, create_client
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    Client = None  # type: ignore[assignment]
    create_client = None  # type: ignore[assignment]
    _SUPABASE_IMPORT_ERROR = exc
else:
    _SUPABASE_IMPORT_ERROR = None

from app.config.settings import settings


@dataclass
class UploadedImage:
    filename: str
    data: bytes
    content_type: Optional[str] = None


class SupabaseStorageService:
    """Handles uploads to Supabase storage for patient images."""

    def __init__(self) -> None:
        if create_client is None:
            raise RuntimeError(
                "Supabase SDK is not installed. Install it with 'pip install supabase>=2.4.0'."
            ) from _SUPABASE_IMPORT_ERROR
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError("Supabase credentials are not configured.")

        self._client: SupabaseClient = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
        self._bucket_name = settings.SUPABASE_IMAGE_BUCKET

    def _build_object_path(self, profile_id: uuid.UUID, filename: str) -> str:
        safe_filename = filename.replace(" ", "_")
        return f"{profile_id}/{uuid.uuid4()}_{safe_filename}"

    def upload_patient_images(
        self, profile_id: uuid.UUID, uploads: List[UploadedImage]
    ) -> List[str]:
        if not uploads:
            raise ValueError("At least one image is required for upload.")

        storage = self._client.storage.from_(self._bucket_name)
        public_urls: List[str] = []

        for upload in uploads:
            object_path = self._build_object_path(profile_id, upload.filename)
            try:
                storage.upload(
                    path=object_path,
                    file=upload.data,
                    file_options={"content-type": upload.content_type}
                    if upload.content_type
                    else None,
                )
            except Exception as exc:  # noqa: BLE001 - propagate storage error context
                raise RuntimeError(f"Failed to upload {upload.filename}: {exc}") from exc

            public_url_result = storage.get_public_url(object_path)
            if not public_url_result or "publicUrl" not in public_url_result:
                raise RuntimeError(
                    f"Failed to generate public URL for {upload.filename}"
                )

            public_urls.append(public_url_result["publicUrl"])

        return public_urls
