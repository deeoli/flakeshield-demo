"""Group failures by normalized signature."""

import re
from dataclasses import dataclass
from typing import Dict, List
from parser import TestResult


@dataclass
class FailureGroup:
    """Group of failures with same root cause."""

    signature: str
    affected_tests: List[str]
    count: int
    sample_error: str

    def __repr__(self):
        return f"<Group signature={self.signature!r} count={self.count}>"


class FailureGrouper:
    """Group failures by normalized root cause signature."""

    @staticmethod
    def normalize_signature(error_message: str, error_stack: str) -> str:
        """Normalize error signature by removing variable parts.

        Args:
            error_message: Error message text
            error_stack: Full stack trace

        Returns:
            Normalized signature
        """
        # Use error message as primary signal
        sig = error_message or error_stack or "Unknown"

        # Remove line numbers (e.g., ":142" -> "")
        sig = re.sub(r":\d+\)", ")", sig)
        sig = re.sub(r":\d+:", ":", sig)

        # Remove timestamps (e.g., "2026-05-31T14:22:10.421Z" -> "")
        sig = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?", "", sig)

        # Remove file paths (e.g., "/home/runner/work/app/src/" -> "")
        sig = re.sub(r"/[a-z0-9_\-\.\/]+/", "", sig)
        sig = re.sub(r"[a-z0-9_\-\.]+/(work|app|src)/", "", sig)

        # Remove millisecond precision
        sig = re.sub(r"\d+ms", "Xms", sig)

        # Extract primary error type if it's an Exception
        # "Cannot read property 'validate' of null" -> keep as-is
        # "TimeoutError: Request timeout" -> keep "TimeoutError"

        # Collapse multiple spaces
        sig = re.sub(r"\s+", " ", sig).strip()

        return sig

    @staticmethod
    def group_failures(results: List[TestResult]) -> Dict[str, FailureGroup]:
        """Group test failures by normalized signature.

        Args:
            results: List of test results

        Returns:
            Dict mapping signature -> FailureGroup
        """
        groups: Dict[str, FailureGroup] = {}

        for result in results:
            if result.status == "fail":
                # Normalize the failure signature
                sig = FailureGrouper.normalize_signature(
                    result.error_message,
                    result.error_stack,
                )

                # Add to group or create new
                if sig not in groups:
                    groups[sig] = FailureGroup(
                        signature=sig,
                        affected_tests=[],
                        count=0,
                        sample_error=result.error_message or result.error_type,
                    )

                test_id = f"{result.classname}.{result.name}"
                groups[sig].affected_tests.append(test_id)
                groups[sig].count += 1

        return groups


if __name__ == "__main__":
    from parser import JUnitParser

    # Demo
    results = JUnitParser.parse("sample-results/junit.xml")
    groups = FailureGrouper.group_failures(results)

    print(f"Detected {len(groups)} failure groups:")
    for sig, group in groups.items():
        print(f"\n  Group: {group.signature}")
        print(f"  Count: {group.count}")
        print(f"  Tests: {', '.join(group.affected_tests)}")
