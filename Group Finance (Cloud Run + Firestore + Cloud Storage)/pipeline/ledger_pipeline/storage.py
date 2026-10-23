"""Output storage: GCS in production, a local folder for tests/preview."""
from __future__ import annotations

import os
from typing import Optional, Protocol


class Storage(Protocol):
    def put(self, path: str, data: bytes, content_type: str, cache_control: str) -> None: ...
    def exists(self, path: str) -> bool: ...
    def read(self, path: str) -> bytes: ...


class LocalStorage:
    def __init__(self, root: str):
        self.root = root

    def _p(self, path: str) -> str:
        root_real = os.path.realpath(self.root)
        full = os.path.realpath(os.path.join(root_real, path))
        if full != root_real and not full.startswith(root_real + os.sep):
            raise ValueError("path escapes storage root")
        return full

    def put(self, path, data, content_type="text/plain", cache_control=""):
        full = self._p(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)

    def exists(self, path):
        return os.path.exists(self._p(path))

    def read(self, path):
        with open(self._p(path), "rb") as f:
            return f.read()


class GcsStorage:
    def __init__(self, bucket: str, client=None):
        from google.cloud import storage
        self.bucket = (client or storage.Client()).bucket(bucket)

    def put(self, path, data, content_type="text/plain", cache_control=""):
        blob = self.bucket.blob(path)
        blob.cache_control = cache_control or None
        blob.upload_from_string(data, content_type=content_type)

    def exists(self, path):
        return self.bucket.blob(path).exists()

    def read(self, path):
        return self.bucket.blob(path).download_as_bytes()
