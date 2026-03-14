"""
Tests for output formatting and pretty-printing functionality.
Includes snapshot testing for consistent output verification.
"""

import random

import pytest
from results_test_cases import SNAPSHOT_CASES

from ast_roller.grammar import parser, transformer


class TestPrettyPrinting:
    def run_test(self, roll_string, seed, sort_level=0):
        import ast_roller.config as config

        config.sort_level = sort_level
        random.seed(seed)
        result = transformer.transform(parser.parse(roll_string)).evaluate()
        return result.pretty_print(depth=0, indent=0)

    def validate_output(self, roll_string, snapshot, result):
        try:
            snapshot.assert_match(result, "output.txt")
        except AssertionError as e:
            error_str = f"Snapshot mismatch for roll string: {roll_string}"
            error_str += f"\tGenerated Output:\n{result}"
            error_str += f"\tSnapshot: {snapshot}"
            raise AssertionError(error_str) from e

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["basic_dice"])
    def test_basic_dice_outputs(self, roll_string, snapshot):
        suite_seed = 42
        output = self.run_test(roll_string, suite_seed)
        snapshot.assert_match(output, "output.txt")

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["arithmetic_operations"])
    def test_arithmetic_operations_outputs(self, roll_string, snapshot):
        suite_seed = 24752
        output = self.run_test(roll_string, suite_seed)
        snapshot.assert_match(output, "output.txt")

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["sequence_expressions"])
    def test_sequence_expression_outputs(self, roll_string, snapshot):
        suite_seed = 90210
        output = self.run_test(roll_string, suite_seed)
        snapshot.assert_match(output, "output.txt")

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["list_expressions"])
    def test_list_expressions_outputs(self, roll_string, snapshot):
        suite_seed = 13579
        output = self.run_test(roll_string, suite_seed)
        snapshot.assert_match(output, "output.txt")

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["list_expressions"])
    def test_sorted_list_expressions_outputs(self, roll_string, snapshot):
        suite_seed = 13579
        output = self.run_test(roll_string, suite_seed, sort_level=1)
        snapshot.assert_match(output, "output.txt")

    @pytest.mark.parametrize("roll_string", SNAPSHOT_CASES["complex_expressions"])
    def test_complex_expressions_outputs(self, roll_string, snapshot):
        suite_seed = 24886
        output = self.run_test(roll_string, suite_seed)
        snapshot.assert_match(output, "output.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
