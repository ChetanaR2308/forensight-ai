from app.models.domain import Citation, InvestigationAnswer, Observation, UncertaintyStatus


class LLMProvider:
    def answer(self, _question: str, _context: list[Observation]) -> InvestigationAnswer:
        raise NotImplementedError


class DeterministicQueryService:
    def answer(self, question: str, observations: list[Observation]) -> InvestigationAnswer:
        tokens = [
            "".join(ch for ch in token.lower() if ch.isalnum())
            for token in question.split()
            if len(token) > 2
        ]
        tokens = [token for token in tokens if token]
        matched = [obs for obs in observations if any(token in obs.value.lower() for token in tokens)]

        if not matched:
            return InvestigationAnswer(
                answer="Insufficient evidence: no stored observations support this query.",
                mode="deterministic",
                status=UncertaintyStatus.inconclusive,
                citations=[],
            )

        citations = [
            Citation(
                evidence_id=obs.evidence_id,
                observation_id=obs.id,
                source=obs.source,
                timestamp=obs.source_timestamp or obs.created_at,
            )
            for obs in matched[:5]
        ]

        statement = " ".join(obs.value for obs in matched[:2])
        return InvestigationAnswer(
            answer=f"Observed evidence indicates: {statement}",
            mode="deterministic",
            status=UncertaintyStatus.uncertain,
            citations=citations,
        )
