from __future__ import annotations

from app.models.domain import Citation, Finding, Observation, Report, UncertaintyStatus


class ReportService:
    def build_report(self, case_id: str, observations: list[Observation]) -> Report:
        if not observations:
            return Report(
                case_id=case_id,
                summary="Inconclusive: insufficient evidence available.",
                findings=[
                    Finding(
                        case_id=case_id,
                        summary="No observations available.",
                        status=UncertaintyStatus.inconclusive,
                        confidence=0.0,
                        citations=[],
                    )
                ],
                conflicts=[],
                evidence_gaps=["No uploaded evidence has produced usable observations."],
                suggested_next_actions=[
                    "Upload additional relevant evidence.",
                    "Confirm the source chain of custody and relevant timestamps.",
                ],
            )

        findings: list[Finding] = []
        conflicts: list[str] = []
        evidence_gaps: list[str] = []
        kind_groups: dict[str, list[Observation]] = {}

        for observation in observations:
            kind_groups.setdefault(observation.kind, []).append(observation)
            if observation.status == observation.status.conflicting:
                conflicts.append(f"Conflict noted in {observation.kind}: {observation.value[:150]}")

        for kind, items in kind_groups.items():
            best = max(items, key=lambda item: item.confidence)
            status = UncertaintyStatus.uncertain
            if any(item.status == item.status.conflicting for item in items):
                status = UncertaintyStatus.conflicting
            findings.append(
                Finding(
                    case_id=case_id,
                    summary=f"{kind}: {best.value[:200]}",
                    status=status,
                    confidence=best.confidence,
                    citations=[
                        Citation(
                            evidence_id=item.evidence_id,
                            observation_id=item.id,
                            source=item.source,
                            timestamp=item.source_timestamp or item.created_at,
                        )
                        for item in items[:3]
                    ],
                )
            )

        if not conflicts:
            conflicts = ["No material conflicts were identified in the currently available evidence."]

        if len(observations) < 3:
            evidence_gaps.append("Few observations are available for a high-confidence analytic conclusion.")
        if not any(observation.kind in {"location", "time_reference"} for observation in observations):
            evidence_gaps.append("No explicit time or location references were extracted from the current evidence set.")

        return Report(
            case_id=case_id,
            summary="Structured evidence was reviewed with uncertainty and provenance preserved.",
            findings=findings,
            conflicts=conflicts,
            evidence_gaps=evidence_gaps,
            suggested_next_actions=[
                "Review the cited evidence manually.",
                "Collect corroborating evidence for uncertain or conflicting findings.",
                "Document any missing timeline or location details before drawing conclusions.",
            ],
        )
