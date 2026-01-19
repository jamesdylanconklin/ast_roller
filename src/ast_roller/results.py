"""
Result node classes for the dice rolling evaluation system.
"""

from abc import ABC, abstractmethod
from collections import defaultdict

import ast_roller.config as config

class ResultNode:
    """
    Base class for all evaluation result nodes.
    Stores the computed result and provides interface for pretty printing.
    """

    def __init__(self, raw_result: int | list[int], token: str):
        self.raw_result = raw_result
        self.token = token

    # TODO: The initial thought was that traversing would support
    # pretty-printing results. However, I think we need a desired
    # output format for arbitrary nesting levels before that makes
    # sense. As is, we define two levels of verbosity and leave it
    # to structural result nodes to figure out how they want to
    # print their children. Might be useful as test helper?
    # @abstractmethod
    # def traverse(self):
    #     pass

    @abstractmethod
    # TODO: Find a use for depth or nix it.
    def pretty_print(self, depth: int, indent) -> str:
        pass

class StructuralResultNode(ResultNode):
    """Result node for structural constructs like lists."""

    pass

class SequenceResultNode(StructuralResultNode):
    def __init__(self, expr_result_nodes: list[ResultNode]):
        raw_result = [node.raw_result for node in expr_result_nodes]
        token = ', '.join(node.token for node in expr_result_nodes)
        super().__init__(raw_result, token)
        self.expr_result_nodes = expr_result_nodes

    def pretty_print(self, depth=0, indent=0):
        lines = []
        lines.append(f"{indent * '  '}Sequence: {self.token}")

        for expr_node_idx in range(len(self.expr_result_nodes)):
            expr_node = self.expr_result_nodes[expr_node_idx]
            lines.append(f"{(indent + 1) * '  '}Expression {expr_node_idx}: {expr_node.token} => {expr_node.raw_result}")
            prefix = f"{(indent + 1) * '  '}{expr_node_idx}: "
            lines.append(f"{expr_node.pretty_print(depth + 1, len(prefix) // 2)}")

        return "\n".join(lines)


class ListResultNode(StructuralResultNode):
    def __init__(self, count_result_node: ResultNode, expr_result_nodes: list[ResultNode], raw_result: list[int|list]):
        self.count_result_node = count_result_node
        self.expr_result_nodes = expr_result_nodes
        token = f'{count_result_node.token} {self.expr_result_token()}'
        if config.sort_level >= 1:
            if all(isinstance(result_elem, (int, float)) for result_elem in raw_result):
                raw_result.sort()
            elif config.sort_level >= 2:
                raw_result.sort()
        super().__init__(raw_result, token)

    # In cases where count is zero, we never eval the expr node into a result.
    def expr_result_token(self) -> str:
        if len(self.expr_result_nodes) > 0:
            return self.expr_result_nodes[0].token

        # TODO: Better verbiage. Not super clear to user right now
        # if the zero wasn't evaled or that the dropped expr was
        # skipped. Latter is true, needs to be more clearly noted.
        return '[Expression Not Evaluated]'


    # def traverse(self, depth=0):
    #     yield (self, depth)
    #     yield from self.count_result_node.traverse(depth + 1)
    #     for expr_node in self.expr_result_nodes:
    #         yield from expr_node.traverse(depth + 1)

    def pretty_print(self, depth=0, indent=0):
        lines = []
        lines.append(f"{indent * '  '}List Expansion: {self.token}")
        lines.append(f"{(indent + 1) * '  '}Count: {self.count_result_node.token} => {self.count_result_node.raw_result}")
        lines.append(f"{(indent + 1) * '  '}Expression: {self.expr_result_token()}")
        lines.append(f"{(indent + 1) * '  '}Results: {self.raw_result}")

        # I think list expressions are the only one that really need to worry about depth cutoffs.

        if not any(node.raw_result for node in self.expr_result_nodes):
            return "\n".join(lines)

        for expr_node_idx in range(len(self.expr_result_nodes)):
            expr_node = self.expr_result_nodes[expr_node_idx]
            prefix = f"{(indent + 1) * '  '}{expr_node_idx}: "
            if depth > 1:
                lines.append(f"{prefix}{expr_node.raw_result}")
            else:
                lines.append(prefix)
                lines.append(f"{expr_node.pretty_print(depth + 1, len(prefix) // 2)}")

        return "\n".join(lines)


class BinaryOpResultNode(StructuralResultNode):
    """Result node for binary operations."""

    def __init__(self, operator: str, left_node: ResultNode, right_node: ResultNode, raw_result: int | float):
        token = f"({left_node.token} {operator} {right_node.token})"
        super().__init__(raw_result, token)
        self.left = left_node
        self.right = right_node
        self.operator = operator

    def dice_expansion(self):
        left_expansion = self.left.token
        # There should be nothing but binop nodes and leaves below us.
        # If number, token suffices.
        # If binop, recurse on dice_expansion.
        # If dice, use die_results.
        if hasattr(self.left, 'dice_expansion'):
            left_expansion = self.left.dice_expansion()
        elif hasattr(self.left, 'format_die_results'):
            left_expansion = f"{self.left.format_die_results()}"

        right_expansion = self.right.token
        if hasattr(self.right, 'dice_expansion'):
            right_expansion = self.right.dice_expansion()
        elif hasattr(self.right, 'die_results'):
            right_expansion = f"{self.right.die_results}"

        return f"({left_expansion} {self.operator} {right_expansion})"

    # Right now, we don't delegate printing to children because we'd rather end up
    # using one line, and most pretty-prints themselves want to take that line.
    # If/when I figure out a nice way to split the ouput over multiple lines, we can
    # explore something more like ListResultNode's pretty_print.

    # Alternate TODO: has_dice_roll() function on ResultNode to see if we need
    # three-step print (raw => individual dice => fully evaled).
    def pretty_print(self, depth=0, indent=0):
        raw_eq = f"({self.left.token} {self.operator} {self.right.token})"
        expanded_dice_eq = self.dice_expansion()
        result_eq = f"{self.left.raw_result} {self.operator} {self.right.raw_result}"

        if expanded_dice_eq != raw_eq:
            return (f"{indent * '  '}{raw_eq} => {expanded_dice_eq} => {result_eq} = {self.raw_result}")
        return (f"{indent * '  '}{raw_eq} => {result_eq} = {self.raw_result}")

    # def traverse(self, depth=0):
    #     yield (self, depth)
    #     yield from self.children['left'].traverse(depth + 1)
    #     yield from self.children['right'].traverse(depth + 1)


class LeafResultNode(ResultNode):
    """Result node for leaf values like numbers and dice rolls."""

    # def traverse(self, depth=0):
    #     yield (self, depth)

class DiceResultNode(LeafResultNode):
    """Result node for dice rolls, storing individual die results."""
    def __init__(
        self,
        roll_string: str,
        raw_result: int,
        die_results: list[int],
        to_keep: dict[int, int] = {},
        to_drop: dict[int, int] = {},
        original_rolls: list[int] = [],
        rerolled_indices: list[bool] = []
    ):
        super().__init__(raw_result, token=roll_string)
        self.die_results = die_results  # List of individual die roll results
        self.to_keep = to_keep
        self.to_drop = to_drop
        self.original_rolls = original_rolls
        self.rerolled_indices = rerolled_indices

    def format_die_results(self) -> str:
        dropped, kept = defaultdict(int), defaultdict(int)

        green_start = '\033[92m'
        red_start = '\033[91m'
        color_end = '\033[0m'

        formatted_results = []
        for die, original_die, rerolled in zip(self.die_results, self.original_rolls, self.rerolled_indices):
            reroll_string = ''
            if rerolled:
                reroll_string = f"{original_die}->"

            if self.to_drop[die] > dropped[die]:
                formatted_results.append(f"{reroll_string}{red_start}{die}{color_end}")
                dropped[die] += 1
            elif self.to_keep[die] > kept[die]:
                formatted_results.append(f"{reroll_string}{green_start}{die}{color_end}")
                kept[die] += 1
            else:
                formatted_results.append(f"{reroll_string}{die}")
        return '[' + ', '.join(formatted_results) + ']'

    def pretty_print(self, _, indent, colorize=True):
        formatted_results = self.die_results
        if colorize:
            formatted_results = self.format_die_results()

        return f"{indent * '  '}{self.token} => {formatted_results} = {self.raw_result}"

class NumberResultNode(LeafResultNode):
    """Result node for numeric values."""

    def __init__(self, raw_result: int | float):
        super().__init__(raw_result, token=f"{raw_result}")

    def pretty_print(self, _, indent):
        return f"{indent * ''}{self.token} => {self.raw_result}"

