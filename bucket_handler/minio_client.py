import os
from minio import Minio
from urllib.parse import urlparse

class BucketHandler:
    """Handles the connection to MinIO for object storage."""

    client: Minio = None
    bucket_name: str = ""

    @classmethod
    def connect(cls):
        """Initializes the MinIO client."""
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")
        endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT")
        cls.bucket_name = os.getenv("MINIO_BUCKET_NAME")

        if not all([access_key, secret_key, endpoint, cls.bucket_name]):
            raise ValueError("MinIO credentials are not fully set in the environment variables.")

        parsed_url = urlparse(endpoint)
        hostname = parsed_url.netloc if parsed_url.netloc else parsed_url.path
        is_secure = parsed_url.scheme == "https"

        cls.client = Minio(
            hostname,
            access_key=access_key,
            secret_key=secret_key,
            secure=is_secure
        )
        print("Connected to MinIO successfully.")

        # Ensure the bucket exists
        if not cls.client.bucket_exists(cls.bucket_name):
            print(f"Warning: Bucket '{cls.bucket_name}' does not exist.")
            # Depending on use case, might want to create the bucket here
        else:
            print(f"Bucket '{cls.bucket_name}' confirmed.")

    @classmethod
    def get_client(cls) -> Minio:
        """Returns the MinIO client instance."""
        if not cls.client:
             raise ConnectionError("MinIO client has not been initialized.")
        return cls.client

bucket_handler = BucketHandler
