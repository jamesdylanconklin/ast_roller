# ast_roller

[![CI](https://github.com/jamesdylanconklin/ast_roller/workflows/CI/badge.svg)](https://github.com/jamesdylanconklin/ast_roller/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jamesdylanconklin/ast_roller/branch/main/graph/badge.svg)](https://codecov.io/gh/jamesdylanconklin/ast_roller)
[![PyPI version](https://badge.fury.io/py/ast-roller.svg)](https://badge.fury.io/py/ast-roller)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An expressive, abstract syntax tree-based dice roller.

### Installation
TBD

### Usage

As a library:

```shell
>>> from ast_roller.grammar import parser, transformer
>>> roll_string = '2 2d20 kh1 + 8'
>>> eval_root = transformer.transform(parser.parse(roll_string))
>>> result_root = eval_root.evaluate()
>>> print(result_root.pretty_print())
List Expansion: 2 (2d20 kh1 + 8)
  Count: 2 => 2
  Expression: (2d20 kh1 + 8)
  Results: [21, 26]
  0: 
    (2d20 kh1 + 8) => ([13, 8] + 8) => 13 + 8 = 21
  1: 
    (2d20 kh1 + 8) => ([6, 18] + 8) => 18 + 8 = 26
```

As a command-line tool:

```
TBD
```

### Design

This package processes dice rolls in tree main steps:
- 1. Parse dice roll strings into syntax trees using Lark and a defined roll string grammar.
- 2. Transforming the parse tree into an evaluation tree
- 3. Recursively call `evaluate()` from the root of the evaluation tree.

This logic is spread across three files:
- `grammar.py`: Contains the dice roll grammar and logic for transforming parse trees into eval trees.
- `evaluators.py`: Handles evaluation logic.
- `results.py`: Handles 

### Contributing

Contributions are welcome and should be pretty manageable. New roll features can be included by adding a definition for the new rule to the grammar and adding or modifying corresponding `EvaluatorNode` and `ResultNode` definitions to implement the actual logic.

Code changes must be accompanied by new or reconciled spec code in `src/tests`. 

I feel lukewarm at best about the current output formats so if anyone has better ideas, I'd love an issue suggesting the changes.