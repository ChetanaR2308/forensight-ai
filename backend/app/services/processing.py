from abc import ABC, abstractmethod
from pathlib import Path

from app.models.domain import Observation, ObservationStatus


class OCRAdapter(ABC):
    @abstractmethod
    def extract_text(self, path: str) -> str: ...


class DeterministicOCRAdapter(OCRAdapter):
    def extract_text(self, path: str) -> str:
        suffix = Path(path).suffix.lower()
        if suffix in {".txt", ".log", ".csv", ".json"}:
            try:
                content = Path(path).read_text(encoding="utf-8", errors="ignore").strip()
                if content:
                    return content[:500]
            except Exception:
                pass
        stem = Path(path).stem.replace("-", " ").replace("_", " ")
        return f"Placeholder OCR extract for file {stem}".strip()


class MediaMetadataExtractor:
    def extract(self, path: str) -> dict:
        metadata = {"filename": Path(path).name}
        try:
            import cv2  # type: ignore

            capture = cv2.VideoCapture(path)
            if capture.isOpened():
                metadata["frame_count"] = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata["fps"] = float(capture.get(cv2.CAP_PROP_FPS))
            capture.release()
        except Exception:
            metadata["opencv_available"] = False
        return metadata


class ProcessingPipeline:
    def __init__(self, ocr_adapter: OCRAdapter | None = None) -> None:
        self.ocr_adapter = ocr_adapter or DeterministicOCRAdapter()
        self.metadata_extractor = MediaMetadataExtractor()

    def process(self, case_id: str, evidence_id: str, storage_path: str) -> tuple[dict, list[Observation]]:
        metadata = self.metadata_extractor.extract(storage_path)
        text = self.ocr_adapter.extract_text(storage_path)
        observations = [
            Observation(
                case_id=case_id,
                evidence_id=evidence_id,
                kind="text_excerpt",
                value=text,
                source="ocr_placeholder",
                processing_stage="ocr",
                confidence=0.2,
                status=ObservationStatus.inconclusive,
            )
        ]
        return metadata, observations
