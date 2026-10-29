from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.domain import Observation, ObservationStatus


class OCRAdapter(ABC):
    @abstractmethod
    def extract_text(self, path: str) -> str: ...


class DeterministicOCRAdapter(OCRAdapter):
    @staticmethod
    def _read_text_file(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            return ""

    @staticmethod
    def _document_notice(path: Path) -> str:
        return (
            f"Document file {path.name} was captured for review. "
            "The MVP performs deterministic source-preserving extraction and requires a human investigator to validate the underlying original artifact."
        )

    def extract_text(self, path: str) -> str:
        file_path = Path(path)
        suffix = file_path.suffix.lower()

        if suffix in {".txt", ".log", ".csv", ".json"}:
            text = self._read_text_file(file_path)
            if text:
                return text[:2000]

        if suffix in {".pdf", ".doc", ".docx"}:
            return self._document_notice(file_path)

        if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
            return (
                f"Image file {file_path.name} was uploaded for manual review. "
                "The system preserves source provenance and does not claim content beyond the original evidence file."
            )

        if suffix in {".mp4", ".avi", ".mov", ".mkv"}:
            return (
                f"Video file {file_path.name} was uploaded for manual review. "
                "Frame-level analysis may be added when OpenCV or model weights are available; no autonomous verdict is generated."
            )

        stem = file_path.stem.replace("-", " ").replace("_", " ")
        return f"Placeholder OCR extract for file {stem}.".strip()


class MediaMetadataExtractor:
    def extract(self, path: str) -> dict[str, Any]:
        file_path = Path(path)
        metadata: dict[str, Any] = {
            "filename": file_path.name,
            "file_type": file_path.suffix.lower().lstrip("."),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        }

        try:
            import cv2  # type: ignore

            capture = cv2.VideoCapture(path)
            if capture.isOpened():
                metadata["frame_count"] = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata["fps"] = float(capture.get(cv2.CAP_PROP_FPS))
                metadata["opencv_available"] = True
            capture.release()
        except Exception:
            metadata["opencv_available"] = False

        return metadata


class ProcessingPipeline:
    def __init__(self, ocr_adapter: OCRAdapter | None = None) -> None:
        self.ocr_adapter = ocr_adapter or DeterministicOCRAdapter()
        self.metadata_extractor = MediaMetadataExtractor()

    @staticmethod
    def _extract_time_mentions(text: str) -> list[datetime]:
        timestamps: list[datetime] = []
        patterns = [
            r"\b\d{1,2}:\d{2}(?:\s?[APap][Mm])?\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
        ]
        for pattern in patterns:
            for match in re.findall(pattern, text):
                cleaned = match.strip()
                try:
                    if ":" in cleaned:
                        main = cleaned.upper().replace("AM", " AM").replace("PM", " PM")
                        if "AM" in main or "PM" in main:
                            timestamps.append(datetime.strptime(f"2024-01-01 {main}", "%Y-%m-%d %I:%M %p"))
                        else:
                            timestamps.append(datetime.strptime(f"2024-01-01 {main}", "%Y-%m-%d %H:%M"))
                    elif "-" in cleaned:
                        timestamps.append(datetime.strptime(cleaned, "%Y-%m-%d"))
                    elif "/" in cleaned:
                        timestamps.append(datetime.strptime(cleaned, "%m/%d/%Y"))
                except ValueError:
                    continue
        return timestamps

    @staticmethod
    def _extract_locations(text: str) -> list[str]:
        location_candidates: list[str] = []
        pattern = (
            r"(?:at|near|inside|outside|warehouse|station|road|entrance|building|parking|room|hall|lane|street|office)\s+"
            r"[A-Za-z0-9 .'-]+"
        )
        for token in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = re.sub(r"^(?:at|near|inside|outside)\s+", "", token, flags=re.IGNORECASE).strip()
            if cleaned and len(cleaned) > 2:
                location_candidates.append(cleaned)
        return list(dict.fromkeys(location_candidates))[:5]

    @staticmethod
    def _extract_entities(text: str) -> list[str]:
        candidates = []
        for token in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text):
            if token.lower() not in {"the", "and", "for", "with", "from", "into", "this"}:
                candidates.append(token)
        return list(dict.fromkeys(candidates))[:10]

    def process(self, case_id: str, evidence_id: str, storage_path: str) -> tuple[dict[str, Any], list[Observation]]:
        metadata = self.metadata_extractor.extract(storage_path)
        text = self.ocr_adapter.extract_text(storage_path)
        observations: list[Observation] = []

        if text:
            observations.append(
                Observation(
                    case_id=case_id,
                    evidence_id=evidence_id,
                    kind="text_excerpt",
                    value=text[:2000],
                    source="ocr_adapter",
                    processing_stage="ocr",
                    confidence=0.75,
                    status=ObservationStatus.observed,
                )
            )

            for entity in self._extract_entities(text):
                observations.append(
                    Observation(
                        case_id=case_id,
                        evidence_id=evidence_id,
                        kind="entity",
                        value=entity,
                        source="text_parser",
                        processing_stage="entity_extraction",
                        confidence=0.62,
                        status=ObservationStatus.observed,
                    )
                )

            for location in self._extract_locations(text):
                observations.append(
                    Observation(
                        case_id=case_id,
                        evidence_id=evidence_id,
                        kind="location",
                        value=location,
                        source="text_parser",
                        processing_stage="location_extraction",
                        confidence=0.55,
                        status=ObservationStatus.uncertain,
                    )
                )

            for timestamp in self._extract_time_mentions(text)[:5]:
                observations.append(
                    Observation(
                        case_id=case_id,
                        evidence_id=evidence_id,
                        kind="time_reference",
                        value=f"Detected time reference: {timestamp.isoformat()}",
                        source="deterministic_parser",
                        source_timestamp=timestamp,
                        processing_stage="timeline",
                        confidence=0.68,
                        status=ObservationStatus.uncertain,
                    )
                )

        if not observations:
            observations.append(
                Observation(
                    case_id=case_id,
                    evidence_id=evidence_id,
                    kind="metadata_only",
                    value=f"No readable text extracted from {metadata.get('filename', 'unknown file')}.",
                    source="deterministic_pipeline",
                    processing_stage="metadata",
                    confidence=0.2,
                    status=ObservationStatus.inconclusive,
                )
            )

        metadata["detected_time_mentions"] = [item.isoformat() for item in self._extract_time_mentions(text)[:5]]
        metadata["extracted_entities"] = self._extract_entities(text)
        metadata["extracted_locations"] = self._extract_locations(text)
        metadata["text_excerpt_length"] = len(text)
        metadata["processing_note"] = (
            "Best-effort deterministic extraction performed; final forensic interpretation remains human-in-the-loop."
        )
        return metadata, observations


class EvidenceAnalyzer:
    def __init__(self, pipeline: ProcessingPipeline | None = None) -> None:
        self.pipeline = pipeline or ProcessingPipeline()

    def analyze(self, case_id: str, evidence_id: str, storage_path: str) -> tuple[dict[str, Any], list[Observation]]:
        return self.pipeline.process(case_id, evidence_id, storage_path)


def extract_observations(case_id: str, evidence_id: str, storage_path: str) -> tuple[dict[str, Any], list[Observation]]:
    return ProcessingPipeline().process(case_id, evidence_id, storage_path)


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return json.dumps(value, default=str)


def build_extraction_payload(case_id: str, evidence_id: str, storage_path: str) -> dict[str, Any]:
    metadata, observations = extract_observations(case_id, evidence_id, storage_path)
    return {
        "case_id": case_id,
        "evidence_id": evidence_id,
        "metadata": _json_safe(metadata),
        "observations": [
            {
                "id": obs.id,
                "kind": obs.kind,
                "value": obs.value,
                "source": obs.source,
                "status": obs.status.value,
                "confidence": obs.confidence,
            }
            for obs in observations
        ],
    }


__all__ = [
    "DeterministicOCRAdapter",
    "EvidenceAnalyzer",
    "MediaMetadataExtractor",
    "OCRAdapter",
    "ProcessingPipeline",
    "build_extraction_payload",
]
