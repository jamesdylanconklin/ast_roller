"""
Tests for the dice rolling grammar parser.
"""

import pytest
from grammar_test_cases import (
    BASIC_PARSING_CASES,
    COMPLEX_CASES,
    EDGE_CASES,
    LIST_EXPRESSION_CASES,
    PRECEDENCE_CASES,
    SEQUENCE_EXPRESSION_CASES,
    SHOULD_FAIL_CASES,
)
from lark.exceptions import LarkError

from ast_roller.grammar import parser


def assert_trees_equal(actual, expected, input_str, message=""):
    if actual != expected:
        print(expected)
        pytest.fail(f"{message}\nInput: {input_str}\nExpected:\n{expected.pretty()}\nActual:\n{actual.pretty()}")


class TestBasicParsing:
    """Test basic parsing of individual expression types."""

    @pytest.mark.parametrize("input_str,expected_tree", BASIC_PARSING_CASES["numbers"])
    def test_simple_integer(self, input_str, expected_tree):
        """Test parsing a simple integer."""

        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse simple integer")

    @pytest.mark.parametrize("input_str,expected_tree", BASIC_PARSING_CASES["dice_rolls"])
    def test_simple_dice_roll(self, input_str, expected_tree):
        """Test parsing a simple dice roll."""
        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse simple dice roll")

    @pytest.mark.parametrize("input_str,expected_tree", BASIC_PARSING_CASES["parentheses"])
    def test_simple_parentheses(self, input_str, expected_tree):
        """Test parsing expressions with parentheses."""
        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse parentheses expression")


class TestSequenceExpressions:
    """Test parsing of comma-separated sequences."""

    @pytest.mark.parametrize("input_str,expected_tree", SEQUENCE_EXPRESSION_CASES)
    def test_sequence_expression(self, input_str, expected_tree):
        """Test parsing a sequence expression."""
        actual = parser.parse(input_str)
        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse sequence expression")


class TestListExpressions:
    """Test parsing of space-separated lists."""

    @pytest.mark.parametrize("input_str,expected_tree", LIST_EXPRESSION_CASES)
    def test_simple_list_expression(self, input_str, expected_tree):
        """Test parsing a simple list expression."""
        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse list expression")


class TestOperatorPrecedence:
    """Test that operators follow correct precedence rules."""

    @pytest.mark.parametrize("input_str,expected_tree", PRECEDENCE_CASES)
    def test_operator_precedence(self, input_str, expected_tree):
        """Test that operators follow correct precedence rules."""
        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse with correct precedence")


class TestComplexExpressions:
    """Test parsing of complex dice and arithmetic combinations."""

    @pytest.mark.parametrize("input_str,expected_tree", COMPLEX_CASES)
    def test_dice_with_modifier(self, input_str, expected_tree):
        """Test parsing dice rolls with arithmetic modifiers."""
        actual = parser.parse(input_str)

        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse mixed expression")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.parametrize("input_str,expected_tree", EDGE_CASES)
    def test_edge_cases(self, input_str, expected_tree):
        """Test edge cases that should parse successfully."""
        actual = parser.parse(input_str)
        assert_trees_equal(actual, expected_tree, input_str, message="Failed to parse edge case")


class TestErrorCases:
    """Test cases that should fail to parse."""

    @pytest.mark.parametrize("input_str", SHOULD_FAIL_CASES)
    def test_invalid_syntax(self, input_str):
        """Test that invalid syntax raises parsing errors."""
        with pytest.raises(LarkError):
            parser.parse(input_str)


if __name__ == "__main__":
    # Run tests with: python test_grammar.py
    pytest.main([__file__, "-v"])
