# This file is licensed under the terms of the MIT license. See the file
# "LICENSE" in the project root for more information.
#
# This module was developed by Daren Thomas at the assistant chair for
# Sustainable Architecture and Building Technologies (Suat) at the Institute of
# Technology in Architecture, ETH Zürich. See http://suat.arch.ethz.ch for
# more information.

"""
parseidf.py


parses an idf file into a dictionary of lists in the following manner:

    each idf object is represented by a list of its fields, with the first
    field being the objects type.

    each such list is appended to a list of objects with the same type in the
    dictionary, indexed by type:

    { [A] => [ [A, x, y, z], [A, a, b, c],
      [B] => [ [B, 1, 2], [B, 1, 2, 3] }

    also, all field values are strings, i.e. no interpretation of the values is
    made.
"""
import argparse
import sys
from pathlib import Path
from typing import Any, NoReturn, Union

import ply.lex as lex
import ply.yacc as yacc

# list of token names
tokens = ("VALUE", "COMMA", "SEMICOLON")

# regular expression rules for simple tokens
t_COMMA = r"[ \t]*,[ \t]*"
t_SEMICOLON = r"[ \t]*;[ \t]*"


# ignore comments, tracking line numbers at the same time
def t_COMMENT(t) -> None:
    r"[ \t\r\n]*!.*"
    newlines = [n for n in t.value if n == "\n"]
    t.lineno += len(newlines)
    pass
    # No return value. Token discarded


# Define a rule so we can track line numbers
def t_newline(t) -> None:
    r"[ \t]*(\r?\n)+"
    t.lexer.lineno += len(t.value)


def t_VALUE(t) -> Any:
    r"[ \t]*([^!,;\n]|[*])+[ \t]*"
    return t


# Error handling rule
def t_error(t) -> NoReturn:
    raise SyntaxError(
        f"Illegal character '{t.value[0]}' at line {t.lexer.lineno} of input"
    )


# define grammar of idf objects
def p_idffile(p) -> None:
    "idffile : idfobjectlist"
    result: dict[str, list[list[str]]] = {}
    for idfobject in p[1]:
        name = idfobject[0]
        result.setdefault(name.upper(), []).append(idfobject)
    p[0] = result


def p_idfobjectlist(p) -> None:
    "idfobjectlist : idfobject"
    p[0] = [p[1]]


def p_idfobjectlist_multiple(p) -> None:
    "idfobjectlist : idfobject idfobjectlist"
    p[0] = [p[1]] + p[2]


def p_idfobject(p) -> None:
    "idfobject : objectname SEMICOLON"
    p[0] = [p[1]]


def p_idfobject_with_values(p) -> None:
    "idfobject : objectname COMMA valuelist SEMICOLON"
    p[0] = [p[1]] + p[3]


def p_objectname(p) -> None:
    "objectname : VALUE"
    p[0] = p[1].strip()


def p_valuelist(p) -> None:
    "valuelist : VALUE"
    p[0] = [p[1].strip()]


def p_valuelist_multiple(p) -> None:
    "valuelist : VALUE COMMA valuelist"
    p[0] = [p[1].strip()] + p[3]


# oh, and handle errors
def p_error(p) -> NoReturn:
    if p:
        raise SyntaxError(f"Syntax error at token '{p.value}' on line {p.lineno}")
    else:
        raise SyntaxError("Syntax error at EOF")


def parse(
    idf_text: str, debug: bool = False, write_tables: bool = False
) -> dict[str, list[list[str]]]:
    """
    Parses a string with the contents of the IDF file and returns a dictionary
    mapping object types to lists of their field values.
    """
    lexer = lex.lex(debug=debug)
    parser = yacc.yacc(debug=debug, write_tables=write_tables)
    result = parser.parse(idf_text, lexer=lexer, debug=debug)
    return result


def parse_file(
    file_path: Union[str, Path], debug: bool = False, write_tables: bool = False
) -> dict[str, list[list[str]]]:
    """
    Reads an IDF file from a path and parses its contents.

    :param file_path: The path to the IDF file.
    :param debug: Passed to the parser/lexer's debug setting.
    :param write_tables: Passed to the parser's write_tables setting.
    :return: A dictionary mapping object types (str, uppercased) to lists
        of their field value lists.
    """
    path = Path(file_path)

    try:
        idf_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        raise
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise

    return parse(idf_text, debug=debug, write_tables=write_tables)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Parse an EnergyPlus IDF file into a Python dictionary."
    )
    parser.add_argument("file", type=str, help="Path to the IDF file to be parsed.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable lexer/parser debugging."
    )
    parser.add_argument(
        "-t",
        "--tables",
        action="store_true",
        help="Write parser tables (for development/caching).",
    )

    args = parser.parse_args()

    try:
        print(f"Parsing file: {args.file}...")
        idf_data = parse_file(
            file_path=args.file, debug=args.debug, write_tables=args.tables
        )

        print("\n--- Parse Successful ---")
        print(f"Total objects parsed: {sum(len(v) for v in idf_data.values())}")
        print("Object counts by type:")

        for obj_type, obj_list in sorted(idf_data.items()):
            print(f"  {obj_type:<30}: {len(obj_list)}")

    except (SyntaxError, FileNotFoundError) as e:
        print(f"\n--- PARSE FAILED ---", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR ---", file=sys.stderr)
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
