"""
Test cases for evaluator classes.
Contains test data and mock configurations for evaluation testing.
"""

from ast_roller.evaluators import EvaluatorNode
from ast_roller.results import ResultNode


class DummyEvalNode(EvaluatorNode):
    """A dummy evaluator node for testing purposes."""

    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return ResultNode(self.value, f"Dummy {self.value}")


# Test cases for DiceRollEvaluatorNode
DICE_ROLL_CASES = {
    "single_die": [
        ("d6", {"result": 6, "calls": [(1, 6)], "raw_results": [6]}),
        ("1d8", {"result": 8, "calls": [(1, 8)], "raw_results": [8]}),
        ("d20", {"result": 20, "calls": [(1, 20)], "raw_results": [20]}),
        ("1d100", {"result": 100, "calls": [(1, 100)], "raw_results": [100]}),
    ],
    "multiple_dice": [
        ("3d6", {"result": 18, "calls": [(1, 6), (1, 6), (1, 6)], "raw_results": [6, 6, 6]}),
        ("5d8", {"result": 40, "calls": [(1, 8), (1, 8), (1, 8), (1, 8), (1, 8)], "raw_results": [8, 8, 8, 8, 8]}),
        (
            "6d10",
            {
                "result": 60,
                "calls": [(1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10)],
                "raw_results": [10, 10, 10, 10, 10, 10],
            },
        ),
    ],
    "fudge_dice": [
        ("df", {"result": 1, "calls": [(-1, 1)], "raw_results": [1]}),
        ("4dF", {"result": 4, "calls": [(-1, 1), (-1, 1), (-1, 1), (-1, 1)], "raw_results": [1, 1, 1, 1]}),
    ],
    "invalid_dice": [
        "3d1",  # y = 1 (invalid die size)
        "0d6",  # x = 0 (zero dice)
        "3dx",  # y not number or F (invalid die type)
        "ad6",  # x not number (invalid count)
        "2d",  # missing die size
        "d",  # incomplete dice format
    ],
    "keep_drop": {
        "valid": [
            ("4d6", ["dl1"], {"result": 9, "calls": 4 * [(1, 6)], "raw_results": [1, 2, 3, 4]}),
            ("5d8", ["kh3"], {"result": 12, "calls": 5 * [(1, 8)], "raw_results": [1, 2, 3, 4, 5]}),
            ("6d10", ["dh2"], {"result": 10, "calls": 6 * [(1, 10)], "raw_results": [1, 2, 3, 4, 5, 6]}),
            ("4dF", ["kl2"], {"result": -2, "calls": 4 * [(-1, 1)], "raw_results": [-1, 0, 1, -1]}),
        ],
        "invalid": [
            ("3d6", ["dl4"]),  # Dropping more dice than rolled
            ("99d100", ["kh10", "kl20", "dl30", "dh40"]),  # Oversubscribed across multiple directives
        ],
    },
    "reroll": {
        "valid": [
            ("5d6", ["r2"], {"result": 19, "calls": [(1, 6)] * 7, "raw_results": [6, 1, 3, 4, 5]}),  # Two rerolls
            (
                "20d20",
                ["rh20"],
                {"result": 210 - 20 + 1, "calls": [(1, 20)] * 21, "raw_results": list(range(1, 21))},
            ),  # One reroll
            ("4d6", ["rh5"], {"result": 10, "calls": [(1, 6)] * 4, "raw_results": [1, 2, 3, 4]}),  # No rerolls
        ],
        "invalid": [
            ("2d6", ["rl6"]),  # Reroll loww needs to be less than upper bound
            ("3d8", ["rh1"]),  # Reroll high needs to be greater than lower bound
            ("5d6", ["r3", "rh4"]),  # Reroll directives overlap
            ("3d4", ["r5"]),  # Reroll directive out of range
        ],
    },
}

# Test cases for NumberEvaluatorNode
NUMBER_EVALUATOR_CASES = {
    "valid": [
        ("-42", "integer", -42),
        ("3.14", "float", 3.14),
        ("7", "natural_num", 7),
        # TBD
        ("0", "integer", 0),
    ],
    "invalid": [
        ("-3.14", "natural_num"),  # Negative float as natural number
        ("abc", "integer"),  # Non-numeric string
        ("4.5.6", "float"),  # Malformed float
        ("0", "natural_num"),  # Non-positive integer as natural number
    ],
}


# Test cases for BinaryOpEvaluatorNode
BINARY_OP_CASES = {
    "valid": {
        "addition": [
            (DummyEvalNode(5), DummyEvalNode(3.2), 8.2),
            (DummyEvalNode(-4), DummyEvalNode(4), 0),
            (DummyEvalNode(0), DummyEvalNode(10), 10),
        ],
        "subtraction": [
            (DummyEvalNode(0), DummyEvalNode(-2.0), 2.0),
            (DummyEvalNode(5), DummyEvalNode(3), 2),
            (DummyEvalNode(3), DummyEvalNode(5), -2),
        ],
        "multiplication": [
            (DummyEvalNode(5), DummyEvalNode(1), 5),
            (DummyEvalNode(-4), DummyEvalNode(0), 0),
            (DummyEvalNode(0), DummyEvalNode(10), 0),
            (DummyEvalNode(3), DummyEvalNode(2.5), 7.5),
        ],
        "division": [
            (DummyEvalNode(5), DummyEvalNode(2), 2.5),
            (DummyEvalNode(-4), DummyEvalNode(2), -2),
            (DummyEvalNode(0), DummyEvalNode(10), 0),
            (DummyEvalNode(10), DummyEvalNode(1.0), 10.0),
            (DummyEvalNode(3), DummyEvalNode(1.5), 2.0),
        ],
    },
    "invalid": [
        # divisor expr can eval to zero, but we don't want to check for the possiibility of
        # arbitrary expressions doing so. It's fine if evaluator raises ZeroDivisionError.
        # Cover in own test.
        # ('/', DummyEvalNode(5), DummyEvalNode(0)),  # Division by zero
        ("%", DummyEvalNode(5), DummyEvalNode(3.2)),  # Invalid operator
        ("+", DummyEvalNode(5), "Not an Eval Node"),  # Right operand not eval node
        ("-", "Not an Eval Node", DummyEvalNode(3.2)),  # Left operand not eval node
    ],
}


SEQUENCE_EVALUATOR_CASES = {
    "valid": [
        ([DummyEvalNode(1), DummyEvalNode(2)], [1, 2]),
        ([DummyEvalNode(3), DummyEvalNode(4), DummyEvalNode(5)], [3, 4, 5]),
    ],
    "invalid": [[DummyEvalNode(1)], []],
}

# Test cases for ListEvaluatorNode
LIST_EVALUATOR_CASES = {
    "non_looping": [
        (DummyEvalNode(7), 7),
        (DummyEvalNode(-3.5), -3),  # List exprs are top-level-ish, so they round.
        (DummyEvalNode(0), 0),
    ],
    "one_dimensional": [
        (DummyEvalNode(3), DummyEvalNode(4), [4, 4, 4]),
        (DummyEvalNode(5), DummyEvalNode(-2.5), [-2, -2, -2, -2, -2]),
        (DummyEvalNode(1), DummyEvalNode(0), [0]),
        (DummyEvalNode(0), DummyEvalNode(2.5), []),
        (DummyEvalNode(-3), DummyEvalNode(10), []),  # Special case for negative count at the moment.
    ],
    "n_dimensional": [
        (DummyEvalNode(2), DummyEvalNode(3), DummyEvalNode(4), [[4, 4, 4], [4, 4, 4]]),
        (DummyEvalNode(2), DummyEvalNode(0), DummyEvalNode(4), [[], []]),
        (DummyEvalNode(0), DummyEvalNode(5), DummyEvalNode(6), []),
    ],
}
