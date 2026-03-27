from __future__ import annotations

import boto3

from app.core.config import get_settings


class ObjectStorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    def upload_bytes(self, object_key: str, content: bytes, content_type: str) -> None:
        self.client.put_object(Bucket=self.bucket, Key=object_key, Body=content, ContentType=content_type)

    def presign_upload(self, object_key: str, expires_in: int = 900) -> str:
        return self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": object_key},
            ExpiresIn=expires_in,
        )

