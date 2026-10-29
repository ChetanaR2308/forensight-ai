from __future__ import annotations

from datetime import datetime

from app.models.domain import Event, Observation, ObservationStatus


class TimelineService:
    def build_timeline(self, case_id: str, observations: list[Observation]) -> list[Event]:
        sortable = sorted(
            observations,
            key=lambda item: (item.source_timestamp or item.created_at or datetime.min),
        )

        events: list[Event] = []
        seen: set[tuple[str, str]] = set()
        for observation in sortable:
            timestamp = observation.source_timestamp or observation.created_at
            if timestamp is None:
                continue
            key = (timestamp.isoformat(), observation.kind)
            if key in seen:
                continue
            seen.add(key)
            events.append(
                Event(
                    case_id=case_id,
                    timestamp=timestamp,
                    description=f"{observation.kind}: {observation.value[:120]}",
                    evidence_id=observation.evidence_id,
                    observation_ids=[observation.id],
                    status=ObservationStatus.correlated,
                )
            )
        return events
