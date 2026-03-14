from lark import Token, Tree

"""
Test cases for the dice rolling grammar.
Contains test data separated from test logic for easier maintenance.
"""

# TODO: Test eval by mocking in static results for random.randint.
# TODO: Once results node logic is fleshed out, set a seed on random.randint for
# each run and use snapshot testing between accepted pretty-print output and
# tested output


def number_tree(value):
    """Helper to create a number parse tree."""
    num_type = "integer"
    if isinstance(value, float):
        num_type = "float"
    elif value > 0:
        num_type = "natural_num"

    return Tree(num_type, [Token(num_type.upper(), str(value))])


def die_tree(count, sides, directives=[]):
    """Helper to create a dice roll parse tree."""
    count_str = count if count is not None else ""

    directives_subtree = Tree("dice_roll_directives", [Token("DICE_ROLL_DIRECTIVE", dir_str) for dir_str in directives])

    return Tree("dice_roll", [(Token("DICE_ROLL", f"{count_str}d{sides}")), directives_subtree])


def tree_root(children):
    """Helper to create a root parse tree."""
    return Tree("start", [list_tree(children)])


def seq_tree(children):
    """Helper to create a sequence expression parse tree."""

    child_tokens = [children[0]]

    for child in children[1:]:
        child_tokens.append(Token("SEQUENCE_SEP", ", "))
        child_tokens.append(child)

    return Tree("sequence_expression", child_tokens)


def list_tree(elements):
    """Helper to create a list expression parse tree."""

    if len(elements) == 1:
        return Tree("list_expression", elements)
    return Tree("list_expression", [elements[0], Token("LIST_SEP", " "), list_tree(elements[1:])])


def binary_op_as_tree(op_name, left, right):
    """Helper for addition/subtraction binary operations."""
    return Tree("binary_op_as", [left, Token("OPERATOR_AS", op_name), right])


def binary_op_md_tree(op_name, left, right):
    """Helper for multiplication/division binary operations."""
    return Tree("binary_op_md", [left, Token("OPERATOR_MD", op_name), right])


def parens_tree(inner):
    """Helper for parentheses trees."""
    return Tree("parens", [inner])


# Basic parsing test cases
BASIC_PARSING_CASES = {
    "numbers": [
        ("867", tree_root([number_tree(867)])),
        ("-530", tree_root([number_tree(-530)])),
        ("9", tree_root([number_tree(9)])),
        ("3.14", tree_root([number_tree(3.14)])),
        ("-11", tree_root([number_tree(-11)])),
    ],
    "dice_rolls": [
        ("d6", tree_root([die_tree(None, 6)])),
        ("3d6", tree_root([die_tree(3, 6)])),
        ("1d20", tree_root([die_tree(1, 20)])),
        ("dF", tree_root([die_tree(None, "F")])),
        ("4df", tree_root([die_tree(4, "f")])),
        ("4d6 dl1", tree_root([die_tree(4, 6, directives=["dl1"])])),
        ("10d100 dh2 dl2 kh1 kl1", tree_root([die_tree(10, 100, directives=["dh2", "dl2", "kh1", "kl1"])])),
    ],
    "basic_arithmetic": [
        ("3+4", tree_root([binary_op_as_tree("+", number_tree(3), number_tree(4))])),
        ("10-2", tree_root([binary_op_as_tree("-", number_tree(10), number_tree(2))])),
        ("5*6", tree_root([binary_op_md_tree("*", number_tree(5), number_tree(6))])),
        ("8/2", tree_root([binary_op_md_tree("/", number_tree(8), number_tree(2))])),
    ],
    "parentheses": [
        (
            "(5+(4+(3)))",
            tree_root(
                [
                    parens_tree(
                        binary_op_as_tree(
                            "+",
                            number_tree(5),
                            parens_tree(binary_op_as_tree("+", number_tree(4), parens_tree(number_tree(3)))),
                        )
                    )
                ]
            ),
        ),
        ("(5)", tree_root([parens_tree(number_tree(5))])),
        ("(3+4)", tree_root([parens_tree(binary_op_as_tree("+", number_tree(3), number_tree(4)))])),
    ],
}

# List expression test cases
LIST_EXPRESSION_CASES = [
    ("3", tree_root([number_tree(3)])),
    ("3 4 5", tree_root([number_tree(3), number_tree(4), number_tree(5)])),
    ("d6 d8", tree_root([die_tree(None, 6), die_tree(None, 8)])),
    ("1d4 2d6 3d8", tree_root([die_tree(1, 4), die_tree(2, 6), die_tree(3, 8)])),
    ("5 2d6", tree_root([number_tree(5), die_tree(2, 6)])),
    ("d20 15 3d4", tree_root([die_tree(None, 20), number_tree(15), die_tree(3, 4)])),
]


def generate_sequence_expression_case(expr_tuples):
    """Helper to generate sequence expression test cases."""

    children = [expected_tree.children[0] for _, expected_tree in expr_tuples]
    expression = ", ".join([expr for expr, _ in expr_tuples])
    expected_tree = Tree("start", [seq_tree(children)])
    return (expression, expected_tree)


SEQUENCE_EXPRESSION_CASES = [
    generate_sequence_expression_case([LIST_EXPRESSION_CASES[x], LIST_EXPRESSION_CASES[y]])
    for x in range(3)
    for y in range(3, len(LIST_EXPRESSION_CASES))
]

# Operator precedence test cases
PRECEDENCE_CASES = [
    # Multiplication before addition - should parse as 2+(3*4)
    (
        "2+3*4",
        tree_root([binary_op_as_tree("+", number_tree(2), binary_op_md_tree("*", number_tree(3), number_tree(4)))]),
    ),
    # Addition after multiplication - should parse as (3*4)+5
    (
        "1.5*4+5",
        tree_root([binary_op_as_tree("+", binary_op_md_tree("*", number_tree(1.5), number_tree(4)), number_tree(5))]),
    ),
    # Division before subtraction - should parse as 10-(6/2)
    (
        "10-6/2",
        tree_root([binary_op_as_tree("-", number_tree(10), binary_op_md_tree("/", number_tree(6), number_tree(2)))]),
    ),
    # Subtraction after division - should parse as (8/2)-1
    (
        "8/2-1",
        tree_root([binary_op_as_tree("-", binary_op_md_tree("/", number_tree(8), number_tree(2)), number_tree(1))]),
    ),
    # Parentheses override precedence - should parse as (2+3)*4
    (
        "(2+3)*4",
        tree_root(
            [
                binary_op_md_tree(
                    "*", parens_tree(binary_op_as_tree("+", number_tree(2), number_tree(3))), number_tree(4)
                )
            ]
        ),
    ),
    # Parentheses override precedence - should parse as 2*(3+4)
    (
        "2*(3+4)",
        tree_root(
            [
                binary_op_md_tree(
                    "*", number_tree(2), parens_tree(binary_op_as_tree("+", number_tree(3), number_tree(4)))
                )
            ]
        ),
    ),
]

# Complex expression test cases
COMPLEX_CASES = [
    # Dice with arithmetic
    ("2d6+3", tree_root([binary_op_as_tree("+", die_tree(2, 6), number_tree(3))])),
    ("1d20-5", tree_root([binary_op_as_tree("-", die_tree(1, 20), number_tree(5))])),
    ("3d4*2", tree_root([binary_op_md_tree("*", die_tree(3, 4), number_tree(2))])),
    ("4d6/2", tree_root([binary_op_md_tree("/", die_tree(4, 6), number_tree(2))])),
    # Arithmetic with dice
    ("5+2d8", tree_root([binary_op_as_tree("+", number_tree(5), die_tree(2, 8))])),
    ("10-1d6", tree_root([binary_op_as_tree("-", number_tree(10), die_tree(1, 6))])),
    # Multiple dice in expression
    ("2d6+1d8", tree_root([binary_op_as_tree("+", die_tree(2, 6), die_tree(1, 8))])),
    ("3d4-2d6", tree_root([binary_op_as_tree("-", die_tree(3, 4), die_tree(2, 6))])),
    # Complex combinations
    (
        "(2d6+3)*4",
        tree_root(
            [
                binary_op_md_tree(
                    "*", parens_tree(binary_op_as_tree("+", die_tree(2, 6), number_tree(3))), number_tree(4)
                )
            ]
        ),
    ),
    (
        "1d20+5-2",
        tree_root([binary_op_as_tree("-", binary_op_as_tree("+", die_tree(1, 20), number_tree(5)), number_tree(2))]),
    ),
]

# Edge cases and error conditions
EDGE_CASES = [
    # Should parse successfully
    ("d1", tree_root([die_tree(None, 1)])),
    ("100d100", tree_root([die_tree(100, 100)])),
    ("  3d6  ", tree_root([die_tree(3, 6)])),
    # Complex list expressions
    ("6 2d6+3", tree_root([number_tree(6), binary_op_as_tree("+", die_tree(2, 6), number_tree(3))])),
    ("3 (1d4+2)", tree_root([number_tree(3), parens_tree(binary_op_as_tree("+", die_tree(1, 4), number_tree(2)))])),
]

# Cases that should fail to parse
SHOULD_FAIL_CASES = [
    "",  # Empty string fails parse, but should have a configurable default
    "d",  # Incomplete dice
    "3d",  # Missing die size
    "d+3",  # Invalid die format
    "3++4",  # Double operator
    "3d6)",  # Unmatched parenthesis
    "(3d6",  # Unmatched parenthesis
    "3 d 6",  # Spaces in dice
    "-3d6",  # Negative dice. Consider allowing as implicit subtraction from zero.
    "+4",  # leading plus
    "3,",  # single-expr sequence, trailing comma
    ",4",  # single-expr sequence, leading comma
]
