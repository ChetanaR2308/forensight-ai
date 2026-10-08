import hashlib
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class LocalObjectStorage:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.uploads_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe_filename(filename: str) -> str:
        name = Path(filename).name.replace("..", "_")
        return "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_", ".")) or "upload.bin"

    async def save_upload(self, case_id: str, evidence_id: str, upload: UploadFile) -> tuple[str, int, str]:
        target_dir = (self.base_dir / case_id).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self.safe_filename(upload.filename or "upload.bin")
        target_path = (target_dir / f"{evidence_id}-{safe_name}").resolve()

        if not str(target_path).startswith(str(self.base_dir)):
            raise ValueError("Invalid upload path")

        digest = hashlib.sha256()
        size = 0

        with target_path.open("wb") as out:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_bytes:
                    target_path.unlink(missing_ok=True)
                    raise ValueError("File exceeds configured max upload size")
                digest.update(chunk)
                out.write(chunk)

        await upload.seek(0)
        return str(target_path), size, digest.hexdigest()

    def compute_sha256(self, storage_path: str) -> str:
        digest = hashlib.sha256()
        with Path(storage_path).open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
