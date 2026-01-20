import argparse

from ast_roller.grammar import parser, transformer
import ast_roller.config as config

def main():
    arg_parser = argparse.ArgumentParser(description="Dice Roller using Abstract Syntax Trees")

    arg_parser.add_argument(
        '-s', '--sort',
        action='count',
        default=0,
        help="Specify sort level. -s sorts leaf-level rolls, -ss attempts to sort nested rolls."
    )

    arg_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose output with detailed roll information."
    )

    arg_parser.add_argument("roll_string", nargs='*', help="The dice roll string to evaluate.")

    global args
    args = arg_parser.parse_args()
    # Set global config based on args
    config.sort_level = args.sort
    config.verbose = args.verbose

    roll_string = " ".join(args.roll_string) if args.roll_string else '1d20'

    try:
        parse_tree = parser.parse(roll_string)
        eval_tree = transformer.transform(parse_tree)
        result_tree = eval_tree.evaluate()

        if config.verbose:
            print(result_tree.pretty_print())
        else:
            print(result_tree.raw_result)

    except Exception as e:
        print(f"Could not process roll string {roll_string}")
        print(f"Error: {e}")
