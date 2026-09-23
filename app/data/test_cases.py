"""
MASTER TEST DATASET: Categorized Test Cases
Used by: app/gui/pages/test_cases_page.py and tests/integration/
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    __test__ = False
    id: str
    input_str: str
    expected_accepted: bool
    category: str
    expected_reason: str


MASTER_TEST_SUITE: list[TestCase] = [
    # --- VALID TEST CASES (10 minimum) ---
    TestCase("TC-VAL-01", "EMP-2026-0001", True, "Valid Standard", "Standard valid ID"),
    TestCase("TC-VAL-02", "EMP-2026-0042", True, "Valid Standard", "Standard valid ID"),
    TestCase("TC-VAL-03", "EMP-2026-9999", True, "Valid Standard", "Maximum sequence number"),
    TestCase("TC-VAL-04", "EMP-2000-0000", True, "Valid Boundary", "Boundary year 2000"),
    TestCase("TC-VAL-05", "EMP-2099-1234", True, "Valid Boundary", "Boundary year 2099"),
    TestCase("TC-VAL-06", "EMP-1999-5555", True, "Valid Standard", "Historical year 1999"),
    TestCase("TC-VAL-07", "EMP-2024-8765", True, "Valid Standard", "Recent year 2024"),
    TestCase("TC-VAL-08", "EMP-2025-0101", True, "Valid Standard", "Valid sequence"),
    TestCase("TC-VAL-09", "EMP-2027-3333", True, "Valid Future", "Future year 2027"),
    TestCase("TC-VAL-10", "EMP-2030-7777", True, "Valid Future", "Future year 2030"),

    # --- INVALID PREFIX ---
    TestCase("TC-INV-01", "AXP-2026-0001", False, "Invalid Prefix", "Prefix is not 'EMP'"),
    TestCase("TC-INV-02", "emp-2026-0001", False, "Invalid Prefix", "Prefix must be uppercase"),
    TestCase("TC-INV-03", "EM-2026-0001", False, "Invalid Prefix", "Prefix too short"),
    TestCase("TC-INV-04", "EMPP-2026-0001", False, "Invalid Prefix", "Prefix too long"),

    # --- INVALID SEPARATORS ---
    TestCase("TC-INV-05", "EMP2026-0001", False, "Missing Separator", "Missing first hyphen"),
    TestCase("TC-INV-06", "EMP-20260001", False, "Missing Separator", "Missing second hyphen"),
    TestCase("TC-INV-07", "EMP_2026_0001", False, "Wrong Separator", "Underscore instead of hyphen"),
    TestCase("TC-INV-08", "EMP--2026-0001", False, "Extra Separator", "Consecutive hyphens"),

    # --- INVALID YEAR ---
    TestCase("TC-INV-09", "EMP-26-0001", False, "Invalid Year", "Year too short (2 digits)"),
    TestCase("TC-INV-10", "EMP-20261-0001", False, "Invalid Year", "Year too long (5 digits)"),
    TestCase("TC-INV-11", "EMP-202A-0001", False, "Invalid Year", "Non-numeric character in year"),

    # --- INVALID SEQUENCE NUMBER ---
    TestCase("TC-INV-12", "EMP-2026-1", False, "Invalid Sequence", "Sequence too short"),
    TestCase("TC-INV-13", "EMP-2026-00001", False, "Invalid Sequence", "Sequence too long"),
    TestCase("TC-INV-14", "EMP-2026-12B4", False, "Invalid Sequence", "Letter inside numeric sequence"),

    # --- SPECIAL & EMPTY STRINGS ---
    TestCase("TC-INV-15", "", False, "Empty Input", "Empty input string"),
    TestCase("TC-INV-16", "EMP-2026-0001 ", False, "Trailing Whitespace", "Trailing space character"),
    TestCase("TC-INV-17", " EMP-2026-0001", False, "Leading Whitespace", "Leading space character"),
    TestCase("TC-INV-18", "EMP-2026-00!1", False, "Invalid Symbol", "Symbol '!' outside alphabet Sigma"),
]
