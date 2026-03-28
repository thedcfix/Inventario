import uuid
import os
from datetime import datetime, timedelta, timezone

from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
    BlobSasPermissions,
)


class StorageService:
    def __init__(self, connection_string, container_name):
        self._blob_service = BlobServiceClient.from_connection_string(connection_string)
        self._container_name = container_name
        self._account_name = self._blob_service.account_name
        self._account_key = self._blob_service.credential.account_key
        # Ensure the container exists (private access)
        try:
            self._blob_service.create_container(container_name)
        except Exception:
            pass
        self._container_client = self._blob_service.get_container_client(
            container_name
        )

    def upload_photo(self, file_stream, original_filename):
        """Upload a photo and return (blob_name, sas_url)."""
        ext = os.path.splitext(original_filename)[1].lower() or ".jpg"
        blob_name = f"{uuid.uuid4().hex}{ext}"

        content_settings = ContentSettings(
            content_type=self._mime_type(ext)
        )

        blob_client = self._container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            file_stream,
            overwrite=True,
            content_settings=content_settings,
        )
        return blob_name, self._generate_sas_url(blob_name)

    def get_photo_url(self, blob_name):
        """Generate a fresh SAS URL for an existing blob."""
        return self._generate_sas_url(blob_name)

    def _generate_sas_url(self, blob_name):
        """Generate a SAS URL valid for 100 years."""
        sas_token = generate_blob_sas(
            account_name=self._account_name,
            container_name=self._container_name,
            blob_name=blob_name,
            account_key=self._account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(days=36500),
        )
        return f"https://{self._account_name}.blob.core.windows.net/{self._container_name}/{blob_name}?{sas_token}"

    def delete_photo(self, blob_name):
        """Delete a photo from blob storage."""
        if not blob_name:
            return
        try:
            blob_client = self._container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
        except Exception:
            pass

    @staticmethod
    def _mime_type(ext):
        mapping = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mapping.get(ext, "application/octet-stream")
