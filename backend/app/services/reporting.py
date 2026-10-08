from app.models.domain import Citation, Finding, Observation, Report, UncertaintyStatus


class ReportService:
    def build_report(self, case_id: str, observations: list[Observation]) -> Report:
        if not observations:
            findings = [
                Finding(
                    case_id=case_id,
                    summary="No observations available.",
                    status=UncertaintyStatus.inconclusive,
                    confidence=0.0,
                    citations=[],
                )
            ]
            return Report(
                case_id=case_id,
                summary="Inconclusive: insufficient evidence available.",
                findings=findings,
                conflicts=[],
                evidence_gaps=["No uploaded evidence has produced usable observations."],
                suggested_next_actions=["Upload additional relevant evidence."],
            )

        findings = []
        conflicts: list[str] = []
        for observation in observations:
            status = (
                UncertaintyStatus.conflicting
                if observation.status.value == "conflicting"
                else UncertaintyStatus.uncertain
            )
            if status == UncertaintyStatus.conflicting:
                conflicts.append(f"Conflict in observation {observation.id}")

            findings.append(
                Finding(
                    case_id=case_id,
                    summary=f"{observation.kind}: {observation.value}",
                    status=status,
                    confidence=observation.confidence,
                    citations=[
                        Citation(
                            evidence_id=observation.evidence_id,
                            observation_id=observation.id,
                            source=observation.source,
                            timestamp=observation.source_timestamp or observation.created_at,
                        )
                    ],
                )
            )

        return Report(
            case_id=case_id,
            summary="Structured evidence observations with uncertainty labels.",
            findings=findings,
            conflicts=conflicts,
            evidence_gaps=[] if observations else ["No evidence observations available"],
            suggested_next_actions=[
                "Review cited evidence manually.",
                "Collect additional corroborating evidence where uncertainty remains.",
            ],
        )
