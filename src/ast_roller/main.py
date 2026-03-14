import argparse
import logging
import sys
from pathlib import Path

from ast_roller.grammar import parser, transformer
import ast_roller.config as config

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if args.log_file:
        log_dir = Path(args.log_file).parent
        if not log_dir.exists():
            raise FileNotFoundError(f"Specified log file directory {log_dir} does not exist.")
        
        logger.addHandler(logging.FileHandler(args.log_file))
    return logger


def main(argv=None):
    arg_parser = argparse.ArgumentParser(
        description="Dice Roller using Abstract Syntax Trees",
        allow_abbrev=False,
    )

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

    arg_parser.add_argument(
        '-l', '--log',
        action='store_true',
        default=False,
        help='Enable logging via configured base handlers without writing to a dedicated file.',
    )

    arg_parser.add_argument(
        '--log-file',
        default=None,
        help='Target file for persisted log. Use -l=<file> or --log=<file>.',
    )

    arg_parser.add_argument(
        '-d', '--desc',
        default='*',
        help='Line descriptor for result in log file'
    )

    arg_parser.add_argument("roll_string", nargs='*', help="The dice roll string to evaluate.")

    global args
    argv = sys.argv[1:] if argv is None else argv
    args = arg_parser.parse_args(argv)

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

        if args.log or args.log_file:
            logger = get_logger()
            logger.info(f"{args.desc}: {roll_string} => {result_tree.raw_result}")

    except Exception as e:
        print(f"Could not process roll string {roll_string}", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
