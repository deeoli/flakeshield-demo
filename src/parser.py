"""Parse JUnit XML test results."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TestResult:
    """Single test result."""

    name: str
    classname: str
    status: str  # 'pass' or 'fail'
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    error_stack: Optional[str] = None

    def __repr__(self):
        return f"<Test {self.classname}.{self.name} status={self.status}>"


class JUnitParser:
    """Parse JUnit XML files."""

    @staticmethod
    def parse(xml_file: str) -> List[TestResult]:
        """Parse JUnit XML and extract test results.

        Args:
            xml_file: Path to JUnit XML file

        Returns:
            List of TestResult objects
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()

        results = []

        # Handle both testsuites (multiple suites) and testsuite (single suite)
        suites = root.findall(".//testsuite")
        if not suites:
            suites = [root]

        for suite in suites:
            suite_name = suite.get("name", "unknown")

            for testcase in suite.findall("testcase"):
                test_name = testcase.get("name")
                class_name = testcase.get("classname", suite_name)
                time = testcase.get("time", "0")

                # Check for failure
                failure = testcase.find("failure")
                if failure is not None:
                    error_msg = failure.get("message", "")
                    error_type = failure.get("type", "Error")
                    error_stack = failure.text or ""

                    result = TestResult(
                        name=test_name,
                        classname=class_name,
                        status="fail",
                        error_message=error_msg,
                        error_type=error_type,
                        error_stack=error_stack,
                    )
                else:
                    result = TestResult(
                        name=test_name,
                        classname=class_name,
                        status="pass",
                    )

                results.append(result)

        return results


if __name__ == "__main__":
    # Demo
    results = JUnitParser.parse("sample-results/junit.xml")
    print(f"Parsed {len(results)} tests")
    for r in results:
        print(f"  {r}")
