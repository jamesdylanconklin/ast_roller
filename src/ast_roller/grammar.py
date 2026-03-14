"""
Grammar definition for AST parsing using Lark.
"""

from lark import Lark, Transformer, v_args

from .evaluators import (
    BinaryOpEvaluatorNode,
    DiceRollEvaluatorNode,
    ListEvaluatorNode,
    NumberEvaluatorNode,
    SequenceEvaluatorNode,
)

# Lark grammar definition
# This will be populated with the actual grammar rules

# TODO: Support comma separated expression sequences

GRAMMAR = r"""
start: (list_expression | sequence_expression)
sequence_expression: list_expression (SEQUENCE_SEP list_expression)+
list_expression: (expression | expression LIST_SEP list_expression)
expression: "(" expression ")" -> parens
          | expression OPERATOR_AS expression -> binary_op_as
          | expression OPERATOR_MD expression -> binary_op_md
          | DICE_ROLL dice_roll_directives -> dice_roll
          | FLOAT -> float
          | NATURAL_NUM -> natural_num
          | INTEGER -> integer

dice_roll_directives: (DICE_ROLL_DIRECTIVE | DICE_REROLL_DIRECTIVE)*
DICE_ROLL: /([1-9]\d*)?d([1-9]\d*|[Ff])/i
DICE_ROLL_DIRECTIVE: /[kd][hl]\d+/i
DICE_REROLL_DIRECTIVE: /r[hl]?[-]?\d+/i
OPERATOR_AS: "+" | "-"
OPERATOR_MD: "*" | "/"
FLOAT: /-?\d*\.\d+/
INTEGER: /-?\d+/
NATURAL_NUM: /[1-9]\d*/
LIST_SEP: /\s+/
SEQUENCE_SEP: /,\s*/

%import common.WS_INLINE
%ignore WS_INLINE  # Only ignore inline whitespace in expressions

"""


### TRANSFORMER


@v_args(inline=True)
class CalculateTree(Transformer):
    """
    Transforms the parse tree into an evaluable structure.
    """

    def start(self, child):
        # We want one of these structural nodes at the root, as they force rounding.
        if isinstance(child, (ListEvaluatorNode, SequenceEvaluatorNode)):
            return child

        return ListEvaluatorNode(None, child)

    def sequence_expression(self, *expressions):
        """Transform sequence expression - comma-separated expressions."""
        # Ignore the separator tokens.
        expr_nodes = [expression for expression in expressions if hasattr(expression, "evaluate")]

        return SequenceEvaluatorNode(expr_nodes)

    def list_expression(self, expr_left, _sep=None, expr_right=None):
        """Transform list expression - either single or count + loop."""

        if expr_right is None:
            # Single expression case
            return expr_left

        return ListEvaluatorNode(expr_left, expr_right)

    def parens(self, inner):
        """Transform parentheses - just return inner expression (prune)."""
        return inner

    def binary_op_as(self, left, op_token, right):
        return BinaryOpEvaluatorNode(left, str(op_token), right)

    # Alias for multiplication/division
    binary_op_md = binary_op_as

    def dice_roll(self, dice_token, directives):
        return DiceRollEvaluatorNode(dice_token, directives.children)

    def float(self, token):
        return NumberEvaluatorNode(token, "float")

    def integer(self, token):
        return NumberEvaluatorNode(token, "integer")

    def natural_num(self, token):
        return NumberEvaluatorNode(token, "natural_num")


parser = Lark(GRAMMAR, parser="earley")
transformer = CalculateTree()
