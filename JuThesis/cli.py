import argparse
import sys
from pathlib import Path

from JuThesis import __version__
from JuThesis.adapters import solve_with_protocol
from JuThesis.io.readers.json_reader import JsonReader
from JuThesis.io.writers.json_writer import JsonWriter

# Поддерживаемые версии протокола
SUPPORTED_PROTOCOL_VERSIONS = ["1.0.0"]


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="juthesis",
        description="JuThesis - a tool for test coverage optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="available commands",
        required=True
    )

    # Команда: solve
    solve_parser = subparsers.add_parser(
        "solve",
        help="solve the test coverage optimization problem",
        description="Reads an input file with functions and tests description, "
                    "solves the optimization problem and writes the result to an output file."
    )
    solve_parser.add_argument(
        "input_file",
        type=str,
        help="path to the input JSON file with problem data"
    )
    solve_parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        dest="output_file",
        help="path to the output JSON file with results"
    )
    solve_parser.add_argument(
        "--format",
        type=str,
        choices=["json"],
        default="json",
        help="input/output file format (default: json)"
    )

    # Команда: validate
    validate_parser = subparsers.add_parser(
        "validate",
        help="validate input file correctness",
        description="Validates the input file against the protocol without solving the problem."
    )
    validate_parser.add_argument(
        "input_file",
        type=str,
        help="path to the input JSON file for validation"
    )
    validate_parser.add_argument(
        "--format",
        type=str,
        choices=["json"],
        default="json",
        help="input file format (default: json)"
    )

    # Команда: version
    subparsers.add_parser(
        "version",
        help="show JuThesis version",
        description="Shows JuThesis version and supported protocol versions."
    )

    return parser


def cmd_solve(args: argparse.Namespace) -> int:
    """
    Обработка команды solve.

    :param args: аргументы командной строки
    :return: код возврата (0 - успех, 1 - ошибка)
    """
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    try:
        reader = JsonReader()
        protocol_input = reader.read(input_path)
        protocol_output = solve_with_protocol(protocol_input)

        print(f"Selected tests:     {len(protocol_output.tests)}")
        print(f"Covered functions:  {protocol_output.total_functions_covered}")
        print(f"Total time:         {protocol_output.total_execution_time}")
        for test_info in protocol_output.tests:
            print(f"  - {test_info.test}: {test_info.functions}")

        writer = JsonWriter()
        writer.write(protocol_output, output_path)
        print(f"Result saved to: {output_path}")

        return 0


    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """
    Обработка команды validate.

    :param args: аргументы командной строки
    :return: код возврата (0 - успех, 1 - ошибка)
    """
    input_path = Path(args.input_file)

    try:
        reader = JsonReader()
        reader.read(input_path)
        print(f"Input file is valid")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_version(args: argparse.Namespace) -> int:
    """
    Обработка команды version.

    :param args: аргументы командной строки
    :return: код возврата (0 - успех, 1 - ошибка)
    """
    print(f"JuThesis v{__version__}")
    print(f"Supported protocol versions: {', '.join(SUPPORTED_PROTOCOL_VERSIONS)}")
    return 0


def main():
    """
    Главная функция CLI.
    Точка входа для команды juthesis.
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "solve":
        exit_code = cmd_solve(args)
    elif args.command == "validate":
        exit_code = cmd_validate(args)
    elif args.command == "version":
        exit_code = cmd_version(args)
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
