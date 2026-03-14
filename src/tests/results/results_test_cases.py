"""
Test cases for output formatting and pretty-printing.
Contains test data for snapshot testing and output verification.
"""

SNAPSHOT_CASES = {
    "basic_dice": [
        "3d6",
        "d20",
        "4dF",
        "4d6 dl1",
        "2d20 kh1",
        "10d10 dh2 kl2",
    ],
    "arithmetic_operations": [
        "3 * 4",
        "4+2",
        "0 - 10",
        "20 / 5",
        "29",
    ],
    "list_expressions": [
        "1d6",
        "6 3d6",
        "4 0 d8",
        "5 5 d5",
        "5 5",  # Forcing NumberResult.pretty_print, mostly.
    ],
    "complex_expressions": [
        "3 * (4 + 5)",
        "1d4 + 2 6 2d6+6",
        "2 (1d4 + 2) * 3",
        "2 2 1.5*(d8 + 4 + 2d6)",
        "(d8 + 4 + 2d6) / 2",
        "d20 kh1 + 5",
    ],
    "sequence_expressions": [
        "1d20+10+d6, d6+5+2d6",
        "4df + 2, 4dF",
        "6 2d6+6, 6 3d6, 6 4 d6",
    ],
}
