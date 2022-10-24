import sys

import tokens


def error(msg: str, coord: tokens.Coord):
    assert coord is not None, "error() called with None coord"
    sys.stderr.write(f"{coord}: {msg}\n")
    sys.exit(1)
