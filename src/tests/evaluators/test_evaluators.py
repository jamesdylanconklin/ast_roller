"""
Tests for evaluator node classes.
"""

import pytest
from unittest.mock import patch, call, Mock

from ast_roller.evaluators import DiceRollEvaluatorNode, NumberEvaluatorNode, BinaryOpEvaluatorNode, ListEvaluatorNode, SequenceEvaluatorNode
from evaluators_test_cases import DICE_ROLL_CASES, NUMBER_EVALUATOR_CASES, BINARY_OP_CASES, LIST_EVALUATOR_CASES, SEQUENCE_EVALUATOR_CASES, DummyEvalNode

mock_random_fn = lambda _, max_val: max_val  # Always return max for testing

class RollingRandom:
    """Helper class to incrementally return increasing random values for testing."""
    def __init__(self):
        self.current = 0

    def randint(self, min_val, max_val):
        result = self.current % (max_val - min_val + 1) + min_val
        self.current += 1
        return result


class TestNumberEvaluatorNode:
    """Test NumberEvaluatorNode evaluation."""

    @pytest.mark.parametrize("num_string,num_type,value", NUMBER_EVALUATOR_CASES['valid'])
    def test_integer_evaluation(self, num_string, num_type, value):
        """Test integer number evaluation."""
        node = NumberEvaluatorNode(num_string, num_type)
        result_node = node.evaluate()
        assert result_node.raw_result == value
        # TODO: Type check when resultNode numeric subclass ready.

    @pytest.mark.parametrize("num_string,num_type", NUMBER_EVALUATOR_CASES['invalid'])
    def test_invalid_handling(self, num_string, num_type):
        """Test invalid number string raises ValueError."""
        with pytest.raises(ValueError):
            node = NumberEvaluatorNode(num_string, num_type)
            node.evaluate()


class TestBinaryOpEvaluatorNode:
    """Test BinaryOpEvaluatorNode evaluation."""

    @pytest.mark.parametrize("left_node, right_node, expected", BINARY_OP_CASES['valid']['addition'])
    def test_addition(self, left_node, right_node, expected):
        """Test addition operation."""
        node = BinaryOpEvaluatorNode(left_node, '+', right_node)
        result_node = node.evaluate()
        assert result_node.raw_result == expected

    @pytest.mark.parametrize("left_node, right_node, expected", BINARY_OP_CASES['valid']['subtraction'])
    def test_subtraction(self, left_node, right_node, expected):
        """Test subtraction operation."""
        node = BinaryOpEvaluatorNode(left_node, '-', right_node)
        result_node = node.evaluate()
        assert result_node.raw_result == expected

    @pytest.mark.parametrize("left_node, right_node, expected", BINARY_OP_CASES['valid']['multiplication'])
    def test_multiplication(self, left_node, right_node, expected):
        """Test multiplication operation."""
        node = BinaryOpEvaluatorNode(left_node, '*', right_node)
        result_node = node.evaluate()
        assert result_node.raw_result == expected

    @pytest.mark.parametrize("left_node, right_node, expected", BINARY_OP_CASES['valid']['division'])
    def test_division(self, left_node, right_node, expected):
        """Test division operation."""
        node = BinaryOpEvaluatorNode(left_node, '/', right_node)
        result_node = node.evaluate()
        assert result_node.raw_result == expected

    @pytest.mark.parametrize("operator,left_node,right_node", BINARY_OP_CASES['invalid'])
    def test_invalid_operator(self, operator, left_node, right_node):
        """Test invalid operator raises ValueError."""
        with pytest.raises(ValueError):
            BinaryOpEvaluatorNode(left_node, operator, right_node).evaluate()

    def test_division_by_zero_passthrough(self):
        """Test division by zero raises ZeroDivisionError."""
        left_node = DummyEvalNode(5)
        right_node = DummyEvalNode(0)
        node = BinaryOpEvaluatorNode(left_node, '/', right_node)
        with pytest.raises(ZeroDivisionError):
            node.evaluate()


class TestDiceRollEvaluatorNode:
    """Test DiceRollEvaluatorNode evaluation with mocked random."""

    @pytest.mark.parametrize("die_str,case_config", DICE_ROLL_CASES['single_die'])
    @patch('random.randint', side_effect=mock_random_fn)
    def test_single_die_roll(self, mock_randint, die_str, case_config):
        """Test single die roll (d6, d20, etc.)."""
        node = DiceRollEvaluatorNode(die_str)
        result_node = node.evaluate()
        assert result_node.raw_result == case_config["result"]
        mock_randint.assert_has_calls([call(*args) for args in case_config["calls"]])
        # TODO: Add assertions for individual die results when ResultsNode Dice subclass ready.

    @pytest.mark.parametrize("die_str,case_config", DICE_ROLL_CASES['multiple_dice'])
    @patch('random.randint', side_effect=mock_random_fn)
    def test_multiple_dice_roll(self, mock_randint, die_str, case_config):
        """Test multiple dice roll (3d6, 4d8, etc.)."""
        node = DiceRollEvaluatorNode(die_str)
        result_node = node.evaluate()
        assert result_node.raw_result == case_config["result"]
        mock_randint.assert_has_calls([call(*args) for args in case_config["calls"]])

    @pytest.mark.parametrize("die_str,case_config", DICE_ROLL_CASES['fudge_dice'])
    @patch('random.randint', side_effect=mock_random_fn)
    def test_fate_dice_roll(self, mock_randint, die_str, case_config):
        """Test Fate dice roll (dF, 4dF, etc.)."""
        node = DiceRollEvaluatorNode(die_str)
        result_node = node.evaluate()
        assert result_node.raw_result == case_config["result"]
        mock_randint.assert_has_calls([call(*args) for args in case_config["calls"]])

    @pytest.mark.parametrize("die_str", DICE_ROLL_CASES['invalid_dice'])
    def test_invalid_dice_token(self, die_str):
        """Test invalid dice token raises ValueError."""
        with pytest.raises(ValueError):
            DiceRollEvaluatorNode(die_str)

    @pytest.mark.parametrize("die_str,directives,case_config", DICE_ROLL_CASES['keep_drop']['valid'])
    @patch('random.randint')
    def test_keep_drop_dice_roll(self, mock_randint, die_str, directives, case_config):
        """Test dice rolls with keep/drop directives."""
        mock_randint.side_effect = RollingRandom().randint
        node = DiceRollEvaluatorNode(die_str, directives)
        result_node = node.evaluate()
        assert result_node.raw_result == case_config["result"]
        mock_randint.assert_has_calls([call(*args) for args in case_config["calls"]])

    @pytest.mark.parametrize("die_str,directives", DICE_ROLL_CASES['keep_drop']['invalid'])
    def test_invalid_keep_drop_directives(self, die_str, directives):
        """Keeping/Dropping more dice than are to be rolled raises ValueError"""
        with pytest.raises(ValueError):
            DiceRollEvaluatorNode(die_str, directives)

class TestSequenceEvaluatorNode:
    """Test SequenceEvaluatorNode evaluation."""

    @pytest.mark.parametrize("children,result", SEQUENCE_EVALUATOR_CASES['valid'])
    def test_valid_sequence_evaluation(self, children, result):
        """Test valid sequence expression evaluation."""
        # Child evaluators should be called exactly once each.
        mock_fns = []
        for child in children:
            mock_fn = Mock(wraps=child.evaluate)
            child.evaluate = mock_fn
            mock_fns.append(mock_fn)

        seq_eval_node = SequenceEvaluatorNode(children)
        result_node = seq_eval_node.evaluate()
        assert result_node.raw_result == result
        for mock_fn in mock_fns:
            mock_fn.assert_called_once()

    @pytest.mark.parametrize("children", SEQUENCE_EVALUATOR_CASES['invalid'])
    def test_invalid_sequence_evaluation(self, children):
        """Test invalid sequence expression raises ValueError."""
        with pytest.raises(ValueError):
            SequenceEvaluatorNode(children)


class TestListEvaluatorNode:
    """Test ListEvaluatorNode evaluation."""

    @pytest.mark.parametrize("eval_node, result", LIST_EVALUATOR_CASES['non_looping'])
    def test_single_expression(self, eval_node, result):
        """Test single expression (no loop)."""

        mock_fn = Mock(wraps=eval_node.evaluate)
        eval_node.evaluate = mock_fn

        list_eval_node = ListEvaluatorNode(None, eval_node)

        result_node = list_eval_node.evaluate()
        assert result_node.raw_result == [result]
        mock_fn.assert_called_once()

    @pytest.mark.parametrize("count_node, expr_node, result", LIST_EVALUATOR_CASES['one_dimensional'])
    def test_non_nested_loop_expression(self, count_node, expr_node, result):
        """Test count and loop expression."""
        mock_count_node = Mock(wraps=count_node)
        mock_expr_node = Mock(wraps=expr_node)
        list_eval_node = ListEvaluatorNode(mock_count_node, mock_expr_node)

        result_node = list_eval_node.evaluate()
        assert result_node.raw_result == result
        mock_count_node.evaluate.assert_called_once()
        # Expr evals once per leaf result
        mock_expr_node.evaluate.assert_has_calls([call() for _ in result])

    @pytest.mark.parametrize("l1_node,l2_node,l3_node,result", LIST_EVALUATOR_CASES['n_dimensional'])
    def test_nested_loop_expression(self, l1_node, l2_node, l3_node, result):
        """Test nested count and loop expressions."""

        # Gist: Expand out to List (L1, List(L2, L3))
        # Test L3 called once per leaf in results
        # Test L2 called once per size of results
        # Test L1 called once
        mock_l1_node = Mock(wraps=l1_node)
        mock_l2_node = Mock(wraps=l2_node)
        mock_l3_node = Mock(wraps=l3_node)

        list_eval_node = ListEvaluatorNode(mock_l1_node, ListEvaluatorNode(mock_l2_node, mock_l3_node))

        result_node = list_eval_node.evaluate()
        assert result_node.raw_result == result
        mock_l1_node.evaluate.assert_called_once()
        mock_l2_node.evaluate.assert_has_calls([call() for _ in result])
        mock_l3_node.evaluate.assert_has_calls([call() for _ in result for _ in result[0]])

    # TODO: Negative count explicitly allowed and defaulted to 0 right now,
    # but I'm finding it counter to expectations as an actual user.
    # def test_negative_count(self):
    #     """Test negative count behavior."""
    #     count_node = DummyEvalNode(-3)
    #     expr_node = DummyEvalNode(5)
    #     mock_count_node = Mock(wraps=count_node)
    #     mock_expr_node = Mock(wraps=expr_node)

    #     list_eval_node = ListEvaluatorNode(mock_count_node, mock_expr_node)

    #     # with pytest.raises(ValueError):
    #     list_eval_node.evaluate()

    #     mock_count_node.evaluate.assert_called_once()
    #     mock_expr_node.evaluate.assert_not_called()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])