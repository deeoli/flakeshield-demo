"""Generate failure summary report."""

import os
from typing import Dict, List, Optional, Tuple
from parser import JUnitParser, TestResult
from grouper import FailureGrouper, FailureGroup
from history import FailureHistory
from risk import RiskScorer, RiskAssessment
from explain import FailureExplainer


class ReportGenerator:
    """Generate human-readable failure reports."""

    @staticmethod
    def _score_groups(
        groups: Dict[str, FailureGroup],
        history: Optional[FailureHistory],
    ) -> List[Tuple[str, FailureGroup, RiskAssessment]]:
        """Score and sort failure groups by risk (highest first)."""
        scored = []
        for sig, group in groups.items():
            if history:
                occurrence_count = history.occurrences_for_report(sig)
                is_recurring = history.seen_before(sig)
            else:
                occurrence_count = 1
                is_recurring = False
            risk = RiskScorer.calculate(
                occurrence_count, group.count, is_recurring
            )
            scored.append((sig, group, risk))
        return RiskScorer.sort_groups(scored)

    @staticmethod
    def _history_lines(sig: str, history: FailureHistory) -> List[str]:
        lines = []
        if history.seen_before(sig):
            lines.append("Seen Before:")
            lines.append("YES")
            lines.append("")
            lines.append("Occurrences:")
            lines.append(str(history.occurrences_for_report(sig)))
            lines.append("")
            lines.append("Status:")
            lines.append("RECURRING")
        else:
            lines.append("Seen Before:")
            lines.append("NO")
            lines.append("")
            lines.append("Occurrences:")
            lines.append("1")
            lines.append("")
            lines.append("Status:")
            lines.append("NEW")
        return lines

    @staticmethod
    def generate_text_report(
        results: List[TestResult],
        groups: Dict[str, FailureGroup],
        history: Optional[FailureHistory] = None,
    ) -> str:
        """Generate plain-text failure summary report."""
        total_tests = len(results)
        failed_tests = sum(1 for r in results if r.status == "fail")
        num_groups = len(groups)
        scored_groups = ReportGenerator._score_groups(groups, history)

        lines = []

        lines.append("=" * 70)
        lines.append("FLAKESHIELD FAILURE GROUPING REPORT")
        lines.append("=" * 70)
        lines.append("")

        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Tests:        {total_tests}")
        lines.append(f"Failed Tests:       {failed_tests}")
        lines.append(f"Failure Groups:     {num_groups}")
        lines.append(f"Unique Root Causes: {num_groups}")

        if history:
            current_sigs = list(groups.keys())
            summary = history.get_summary(current_sigs)
            lines.append("")
            lines.append("RECURRING FAILURE ANALYSIS")
            lines.append("-" * 70)
            lines.append(f"New root causes:       {summary['new_root_causes']}")
            lines.append(f"Recurring root causes: {summary['recurring_root_causes']}")
            lines.append("")
            lines.append("Signal compression:")
            lines.append(f"  {failed_tests} failures -> {num_groups} root causes")

        recurring_count = 0
        if history:
            recurring_count = history.get_summary(list(groups.keys()))[
                "recurring_root_causes"
            ]

        if scored_groups:
            top_sig, top_group, top_risk = scored_groups[0]
            if history:
                top_recurring = history.seen_before(top_sig)
                top_occ = history.occurrences_for_report(top_sig)
            else:
                top_recurring = False
                top_occ = 1
            top_why = FailureExplainer.why_this_matters(
                top_risk.level, top_recurring, top_occ, top_group.count
            )
            lines.append("")
            lines.append("Top Priority Group:")
            lines.append(top_sig)
            lines.append("")
            lines.append("Risk:")
            lines.append(top_risk.level.value)
            lines.append("")
            lines.append("Why it matters:")
            lines.append(top_why)
            lines.extend(
                FailureExplainer.build_top_insights(
                    scored_groups, recurring_count, history
                )
            )

        lines.append("")

        if scored_groups:
            lines.append("RISK ANALYSIS")
            lines.append("-" * 70)
            lines.append("")

            for idx, (sig, group, risk) in enumerate(scored_groups, 1):
                if history:
                    is_recurring = history.seen_before(sig)
                    occurrence_count = history.occurrences_for_report(sig)
                else:
                    is_recurring = False
                    occurrence_count = 1

                lines.append(f"Group {idx}")
                lines.append("-" * 70)
                lines.append("")
                lines.append(f"Risk: {risk.formatted()}")
                lines.append("")
                lines.append("Why This Matters:")
                lines.append(
                    FailureExplainer.why_this_matters(
                        risk.level, is_recurring, occurrence_count, group.count
                    )
                )
                lines.append("")

                if history:
                    lines.extend(ReportGenerator._history_lines(sig, history))
                    lines.append("")

                lines.append("Signature:")
                lines.append(sig)
                lines.append("")
                lines.append("Affected Tests:")
                for test in sorted(group.affected_tests):
                    lines.append(f"  - {test}")
                lines.append("")
        else:
            lines.append("NO FAILURES DETECTED")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def save_report(report_text: str, output_file: str) -> None:
        """Save report to file."""
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_text)


if __name__ == "__main__":
    print("Parsing JUnit XML...")
    results = JUnitParser.parse("sample-results/junit.xml")
    print(f"  [OK] Parsed {len(results)} tests")

    print("\nGrouping failures...")
    groups = FailureGrouper.group_failures(results)
    print(f"  [OK] Detected {len(groups)} failure groups")

    print("\nLoading failure history...")
    history = FailureHistory()
    print(f"  [OK] Loaded {len(history.records)} historical signatures")

    current_sigs = list(groups.keys())
    summary = history.get_summary(current_sigs)
    print(f"\nDetected {len(groups)} failure groups")
    print(f"  New root causes: {summary['new_root_causes']}")
    print(f"  Recurring root causes: {summary['recurring_root_causes']}")

    scored = ReportGenerator._score_groups(groups, history)
    if scored:
        top_sig, _, top_risk = scored[0]
        print(f"\nTop priority: {top_sig}")
        print(f"  Risk: {top_risk.formatted()}")
        print("\nRisk order:")
        for sig, _, risk in scored:
            print(f"  {risk.level.value:6} ({risk.score:.2f})  {sig[:50]}")

    print("\nGenerating report...")
    report = ReportGenerator.generate_text_report(results, groups, history)

    print("\nSaving to reports/failure-summary.txt...")
    ReportGenerator.save_report(report, "reports/failure-summary.txt")
    print("  [OK] Report saved")

    print("\nPersisting failure history...")
    for sig in current_sigs:
        history.record_failure(sig)
    print("  [OK] History updated")

    print("\n" + report)
