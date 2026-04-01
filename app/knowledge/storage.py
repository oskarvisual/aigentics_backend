from __future__ import annotations

import boto3
from botocore.config import Config

from app.core.config import get_settings


class ObjectStorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )

    def qualify_key(self, object_key: str) -> str:
        prefix = self.settings.s3_key_prefix.strip("/")
        key = object_key.lstrip("/")
        if not prefix:
            return key
        if key.startswith(f"{prefix}/"):
            return key
        return f"{prefix}/{key}"

    def upload_bytes(self, object_key: str, content: bytes, content_type: str) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=self.qualify_key(object_key),
            Body=content,
            ContentType=content_type,
        )

    def presign_upload(self, object_key: str, expires_in: int = 900) -> str:
        return self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": self.qualify_key(object_key)},
            ExpiresIn=expires_in,
        )
