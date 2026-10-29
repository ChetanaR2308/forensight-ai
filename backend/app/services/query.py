from __future__ import annotations

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

        matched: list[Observation] = []
        for obs in observations:
            text = (obs.value + " " + obs.source + " " + obs.kind).lower()
            if any(token in text for token in tokens):
                matched.append(obs)

        if not matched:
            return InvestigationAnswer(
                answer="Insufficient evidence: no stored observations support this question.",
                mode="deterministic",
                status=UncertaintyStatus.inconclusive,
                citations=[],
            )

        unique: list[Observation] = []
        seen_ids: set[str] = set()
        for obs in matched:
            if obs.id in seen_ids:
                continue
            seen_ids.add(obs.id)
            unique.append(obs)

        citations = [
            Citation(
                evidence_id=obs.evidence_id,
                observation_id=obs.id,
                source=obs.source,
                timestamp=obs.source_timestamp or obs.created_at,
            )
            for obs in unique[:5]
        ]

        summary = " ; ".join(obs.value[:180] for obs in unique[:3])
        if not summary:
            summary = "The available observations mention relevant facts but contain no directly answerable text."

        return InvestigationAnswer(
            answer=f"Observed evidence indicates: {summary}",
            mode="deterministic",
            status=UncertaintyStatus.uncertain,
            citations=citations,
        )
