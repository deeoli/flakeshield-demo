"""Generate failure summary report."""

from typing import Dict, List
from parser import JUnitParser, TestResult
from grouper import FailureGrouper, FailureGroup


class ReportGenerator:
    """Generate human-readable failure reports."""

    @staticmethod
    def generate_text_report(
        results: List[TestResult],
        groups: Dict[str, FailureGroup],
    ) -> str:
        """Generate plain-text failure summary report.

        Args:
            results: List of test results
            groups: Dict of failure groups

        Returns:
            Formatted report string
        """
        total_tests = len(results)
        failed_tests = sum(1 for r in results if r.status == 'fail')
        num_groups = len(groups)

        lines = []

        # Header
        lines.append('=' * 70)
        lines.append('FLAKESHIELD FAILURE GROUPING REPORT')
        lines.append('=' * 70)
        lines.append('')

        # Summary
        lines.append('SUMMARY')
        lines.append('-' * 70)
        lines.append(f'Total Tests:        {total_tests}')
        lines.append(f'Failed Tests:       {failed_tests}')
        lines.append(f'Failure Groups:     {num_groups}')
        lines.append(f'Unique Root Causes: {num_groups}')
        lines.append('')

        # Failure groups
        if groups:
            lines.append('FAILURE GROUPS')
            lines.append('-' * 70)
            lines.append('')

            for idx, (sig, group) in enumerate(sorted(groups.items(),
                                                       key=lambda x: x[1].count,
                                                       reverse=True), 1):
                lines.append(f'Group {idx}')
                lines.append('-' * 70)
                lines.append(f'Signature:')
                lines.append(f'  {sig}')
                lines.append('')
                lines.append(f'Affected Tests: ({group.count})')
                for test in sorted(group.affected_tests):
                    lines.append(f'  • {test}')
                lines.append('')
        else:
            lines.append('NO FAILURES DETECTED')
            lines.append('')

        lines.append('=' * 70)

        return '\n'.join(lines)

    @staticmethod
    def save_report(report_text: str, output_file: str) -> None:
        """Save report to file.

        Args:
            report_text: Report content
            output_file: Output file path
        """
        with open(output_file, 'w') as f:
            f.write(report_text)


if __name__ == '__main__':
    # Demo pipeline
    print('Parsing JUnit XML...')
    results = JUnitParser.parse('sample-results/junit.xml')
    print(f'  [OK] Parsed {len(results)} tests')

    print('\nGrouping failures...')
    groups = FailureGrouper.group_failures(results)
    print(f'  [OK] Detected {len(groups)} failure groups')

    print('\nGenerating report...')
    report = ReportGenerator.generate_text_report(results, groups)

    print('\nSaving to reports/failure-summary.txt...')
    ReportGenerator.save_report(report, 'reports/failure-summary.txt')
    print('  [OK] Report saved')

    print('\n' + report)
