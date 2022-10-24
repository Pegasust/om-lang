import sys

import tokens


def error(msg: str, coord: tokens.Coord):
    raise Exception(f"{coord}: {msg}")
