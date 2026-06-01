"""Deterministic actionable explanations for failure groups."""

from typing import Dict, List, Optional, Tuple

from risk import RiskLevel


class FailureExplainer:
    """Generate human-readable investigation guidance from failure metadata."""

    @classmethod
    def why_this_matters(
        cls,
        risk_level: RiskLevel,
        is_recurring: bool,
        occurrence_count: int,
        affected_tests: int,
    ) -> str:
        """Return a full explanation of why this group deserves attention."""
        if risk_level == RiskLevel.HIGH:
            if is_recurring and affected_tests > 1:
                return (
                    "Recurring failure affecting multiple tests. "
                    "This issue appears repeatedly and may indicate a systemic problem."
                )
            if is_recurring:
                return (
                    "Recurring failure with elevated occurrence history. "
                    "This pattern may indicate a systemic problem."
                )
            if affected_tests > 1:
                return (
                    "High-impact failure spanning multiple tests. "
                    "Address the root cause to restore suite stability."
                )
            return (
                "High-risk failure pattern detected. "
                "Investigate immediately before impact spreads."
            )

        if risk_level == RiskLevel.MEDIUM:
            if is_recurring or affected_tests > 1:
                return (
                    "Failure impacts multiple tests but has limited recurrence history."
                )
            return (
                "Moderate-risk failure. "
                "Track recurrence and blast radius over the next runs."
            )

        if is_recurring:
            return (
                "Previously seen failure with limited current blast radius. "
                "Monitor for escalation."
            )
        if affected_tests > 1:
            return (
                "New failure affecting multiple tests. "
                "Monitor for recurrence."
            )
        return "New failure with limited impact. Monitor for recurrence."

    @classmethod
    def insight_reason(
        cls,
        is_recurring: bool,
        affected_tests: int,
    ) -> str:
        """Short reason line for TOP INSIGHTS."""
        if is_recurring and affected_tests > 1:
            return "Recurring across multiple tests."
        if is_recurring:
            return "Seen in prior runs."
        if affected_tests > 1:
            return "Affects multiple tests in this run."
        return "New failure in this run."

    @classmethod
    def investigation_focus(cls, top_signature: str, is_recurring: bool) -> str:
        """Guidance for where to start investigation."""
        if is_recurring:
            return "Start with the highest recurring group."
        return f"Start with: {top_signature}"

    @classmethod
    def build_top_insights(
        cls,
        scored_groups: List[Tuple],
        recurring_root_causes: int = 0,
        history=None,
    ) -> List[str]:
        """Build TOP INSIGHTS section lines."""
        if not scored_groups:
            return []

        top_sig, top_group, top_risk = scored_groups[0]
        if history:
            is_recurring = history.seen_before(top_sig)
            occurrence_count = history.occurrences_for_report(top_sig)
        else:
            is_recurring = False
            occurrence_count = 1

        reason = cls.insight_reason(is_recurring, top_group.count)
        why = cls.why_this_matters(
            top_risk.level, is_recurring, occurrence_count, top_group.count
        )

        lines = [
            "TOP INSIGHTS",
            "-" * 70,
            "",
            "1. Highest Risk Issue:",
            f"   {top_sig}",
            "",
            "Reason:",
            f"   {reason}",
            "",
            "2. Stability Signal:",
        ]

        if recurring_root_causes > 0:
            lines.append(
                f"   {recurring_root_causes} recurring failure group"
                f"{'s' if recurring_root_causes != 1 else ''} detected."
            )
        else:
            lines.append("   No recurring failure groups in history yet.")

        lines.extend(
            [
                "",
                "3. Investigation Focus:",
                f"   {cls.investigation_focus(top_sig, is_recurring)}",
                "",
                "Why it matters:",
                f"   {why}",
            ]
        )
        return lines


if __name__ == "__main__":
    cases = [
        ("HIGH", RiskLevel.HIGH, True, 7, 3),
        ("MEDIUM", RiskLevel.MEDIUM, True, 3, 2),
        ("LOW", RiskLevel.LOW, False, 1, 1),
    ]

    print("Actionable summary verification:")
    explanations = []
    for label, level, recurring, occ, affected in cases:
        text = FailureExplainer.why_this_matters(level, recurring, occ, affected)
        explanations.append(text)
        print(f"\n  [{label}]")
        print(f"    {text}")

    unique = len(set(explanations)) == len(explanations)
    print(f"\n  [{'OK' if unique else 'FAIL'}] Explanations differ across LOW/MEDIUM/HIGH")
