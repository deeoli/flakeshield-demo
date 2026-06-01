"""Deterministic risk scoring for failure groups."""

from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class RiskAssessment:
    """Risk score and classification for a failure group."""

    level: RiskLevel
    score: float
    raw_score: float
    why: str

    def formatted(self) -> str:
        """Return display string e.g. HIGH (0.92)."""
        return f"{self.level.value} ({self.score:.2f})"


class RiskScorer:
    """Calculate deterministic risk scores per failure group."""

    OCCURRENCE_WEIGHT = 0.4
    AFFECTED_WEIGHT = 0.3
    RECURRING_BONUS = 0.5
    MAX_RAW_SCORE = 4.5

    HIGH_THRESHOLD = 0.70
    MEDIUM_THRESHOLD = 0.35

    @classmethod
    def calculate(
        cls,
        occurrence_count: int,
        affected_tests: int,
        is_recurring: bool,
    ) -> RiskAssessment:
        """Score a failure group.

        risk = (occurrence_count * 0.4) + (affected_tests * 0.3) + recurring_bonus
        """
        recurring_bonus = cls.RECURRING_BONUS if is_recurring else 0.0
        raw_score = (
            occurrence_count * cls.OCCURRENCE_WEIGHT
            + affected_tests * cls.AFFECTED_WEIGHT
            + recurring_bonus
        )
        score = min(1.0, raw_score / cls.MAX_RAW_SCORE)
        level = cls._classify(score)
        why = cls._explain(is_recurring, affected_tests, occurrence_count)
        return RiskAssessment(level=level, score=score, raw_score=raw_score, why=why)

    @classmethod
    def _classify(cls, score: float) -> RiskLevel:
        if score >= cls.HIGH_THRESHOLD:
            return RiskLevel.HIGH
        if score >= cls.MEDIUM_THRESHOLD:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @classmethod
    def _explain(
        cls, is_recurring: bool, affected_tests: int, occurrence_count: int
    ) -> str:
        if is_recurring and affected_tests > 1:
            return "Recurring failure affecting multiple tests."
        if is_recurring:
            return "Recurring failure detected in prior runs."
        if affected_tests > 1:
            return "Multiple tests share the same root cause."
        if occurrence_count > 1:
            return "Repeated occurrence within this run."
        return "New failure with limited blast radius."

    @classmethod
    def sort_groups(cls, scored_groups: list) -> list:
        """Sort scored entries by risk score descending (risk is last element)."""
        return sorted(scored_groups, key=lambda item: item[-1].score, reverse=True)


if __name__ == "__main__":
    cases = [
        ("HIGH", 7, 3, True, RiskLevel.HIGH),
        ("MEDIUM", 3, 2, True, RiskLevel.MEDIUM),
        ("LOW", 1, 1, False, RiskLevel.LOW),
    ]

    print("Risk scoring verification:")
    scored = []
    for label, occ, affected, recurring, expected in cases:
        risk = RiskScorer.calculate(occ, affected, recurring)
        ok = risk.level == expected
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {label}: {risk.formatted()} (expected {expected.value})")
        scored.append((label, risk))

    order = [item[1].level.value for item in RiskScorer.sort_groups(scored)]
    expected_order = ["HIGH", "MEDIUM", "LOW"]
    order_ok = order == expected_order
    print(f"\nSort order: {' -> '.join(order)}")
    print(f"  [{'OK' if order_ok else 'FAIL'}] Expected HIGH -> MEDIUM -> LOW")
