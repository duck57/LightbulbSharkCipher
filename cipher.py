#!/usr/bin/env python3
import random

import click
import os
from typing import *

"""
See readme.md, other docstrings, or run ./cipher.py --help from the terminal
to view detailed information.
"""


ALPHABET: str = "abcdefghijklmnopqrstuvwxyz"


def p(content):
    click.echo(content, err=False)


def e(content):
    click.echo(content, err=True)


class Keycap:
    """
    Represents a keycap on an ortholinear keyboard.

    The three notable lists are:
    1. self.surround gives a list of fully-reversible keys
    2. self.deciphers_to returns a list of keys for going from ciphertext to cleartext
        in the manner described in the book
    3. self.encrypts_to returns a list of keys that contain self in their deciphers_to

    These attributes are not fully-baked until Cipher.__init__ has finished
    """

    def __init__(self, display: chr):
        self.blank: bool = False if display.strip() else True
        self.name: chr = display if not self.blank else " "
        self.right: Keycap
        self.left: Keycap
        self.up: Keycap
        self.down: Keycap
        # these two are set at the end of Cipher.__init__
        self.surround: List[Keycap] = []  # these ones are reversible
        self.encrypts_to: List[Keycap] = []

    def __repr__(self) -> str:
        return self.name if not self.blank else "∞"

    def __str__(self) -> str:
        return self.name

    @property
    def NE(self) -> "Keycap":
        return self.up.right

    @property
    def NW(self) -> "Keycap":
        return self.up.left

    @property
    def SW(self) -> "Keycap":
        return self.down.left

    @property
    def SE(self) -> "Keycap":
        return self.down.right

    @property
    def raw_surround(self) -> "List[Keycap]":
        """
        Returns the 8 characters surrounding the letter starting with the one
        to the right and proceeding counterclockwise
        """
        #  noqa lines are for resolved references due to program flow
        return [
            self.right,  # noqa
            self.NE,
            self.up,
            self.NW,
            self.left,  # noqa
            self.SW,
            self.down,
            self.SE,
        ]

    @property
    def deciphers_to(self) -> "List[Keycap]":
        return [k for k in self.raw_surround if not k.blank]

    def bake_surround(self) -> int:
        """
        Filters out the blank and non-reversible keys from raw_surround
        and then saves it to self.surround

        Returns the number of non-reversible keys that were thrown out
        (not counting blanks)
        """
        self.surround = [k for k in self.deciphers_to if k in self.encrypts_to]
        return len(self.deciphers_to) - len(self.surround)

    def draw(self, out: bool = True) -> "List[str]":
        o: List[str] = []

        def make_row(
            keys: "List[Union[Keycap, chr]]", substitutes: str, connect: chr = "─"
        ) -> str:
            x: List[chr] = []
            for i, key in enumerate(keys):
                if str(key).strip():
                    x.append(str(key))
                else:
                    x.append(substitutes[i])
            o.append((connect * 2).join(x))
            return o[-1]

        bnk = "│ │"
        mbr = (bnk, "   ", " ")

        make_row([self.NW, self.up, self.NE], "┌─┐")
        make_row(*mbr)
        make_row([self.left, self, self.right], bnk, " ")
        make_row(*mbr)
        make_row([self.SW, self.down, self.SE], "└─┘")

        if out:
            p("\n".join(o))
        return o


def cap_list_str(surrounding: List[Keycap]) -> str:
    return "".join(str(k) for k in surrounding)


# If your layout has its "blank" keys to the left,
# add it to this list
# Layout names (including filenames) should be lower-case
REVERSE_LAYOUTS: List[str] = [
    "dvorak",
]


class Cipher:
    def __init__(
        self, layout: str = "QWERTY", alphabet_check: int = 26, reverse: bool = None
    ):
        layout = layout.lower().strip()
        if not layout:
            layout = "qwerty"
        if reverse is None and layout in REVERSE_LAYOUTS:
            reverse = True  # the symbol keys are on the left on Dvorak

        # Load the layout
        self.alphabet: str = ""
        self.letter_index: Dict[chr, Keycap] = {}
        self.grid: List[List[Keycap]] = []
        self.height: int = 0
        for row in open(os.path.join(os.path.dirname(__file__), f"layouts/{layout}")):
            row = row.lower().strip()
            self.alphabet += row
            self.grid.append([])
            for char in row:
                c = Keycap(char)
                self.letter_index[char] = c
                self.grid[self.height].append(c)
            self.height += 1
        self.row_lengths: List[int] = [len(r) for r in self.grid]
        max_len = max(self.row_lengths)

        # Validity checks
        assert len(self.alphabet) == len(
            self.letter_index.keys()
        ), f"Layout has at least one repeated letter"
        if alphabet_check > 0:
            dif: int = len(self.alphabet) - alphabet_check
            if dif > 0:
                e(f"Layout contains {dif} more letters than the alphabet, continuing.")
            assert (
                dif >= 0
            ), f"Layout is missing {-dif} letter{'s' if dif < -1 else ''} of the alphabet"

        # Arrange the keycaps to a grid
        for r in range(self.height):
            if reverse:
                self.grid[r].reverse()
            for c in range(1, l := self.row_lengths[r]):
                cap: Keycap = self.grid[r][c]
                left: Keycap = self.grid[r][c - 1]
                right: Keycap = self.grid[r][(c + 1) % l]

                cap.left = left
                cap.right = right
                left.right = cap
                right.left = cap

            # blank keycaps for padding
            # ALWAYS ON THE RIGHT
            for x in range(l, max_len):
                k = Keycap("")
                k.left = self.grid[r][x - 1]
                if k.left.blank:
                    k.left.right = k
                if x == max_len - 1:
                    k.right = self.grid[r][0]
                self.grid[r].append(k)
            if reverse:
                self.grid[r].reverse()

        # assign top and bottom keys
        for r in range(self.height - 1):
            up = r - 1
            down = r + 1
            for c in range(0, max_len):
                k = self.grid[r][c]
                u = self.grid[up][c]
                d = self.grid[down][c]

                # fix left & right in reversed layouts
                if reverse:
                    tmp: Keycap = k.left
                    k.left = k.right
                    k.right = tmp

                k.up = u
                k.down = d
                u.down = k
                d.up = k

        # bake in the reversible keys
        for k1 in self.letter_index.values():
            for k2 in k1.deciphers_to:
                k2.encrypts_to.append(k1)
        [(key, key.bake_surround(), key.surround) for key in self.letter_index.values()]

    def surround(self, letter: chr, full: bool = False) -> List[chr]:
        """
        Returns the 8 characters surrounding the letter starting with the one
        to the right and proceeding counterclockwise

        Param `full` controls whether or not to display the blank keys
        """
        return [
            k.name for k in self.letter_index[letter].surround if not k.blank or full
        ]

    def encode_chr(
        self, ch: chr, direction: chr = "R", drop: bool = True, rnd: bool = False
    ) -> str:
        """
        Encodes a single character and returns the output possibilities
        Params drop and direction are the same as in Cipher.encode_text
            except direction also has option '0' to echo back the input character if it was found
        """
        direction = direction.upper().strip()[0]
        letter: Keycap = self.letter_index.get(ch)
        if letter:
            s = letter.__getattribute__(direction_methods[direction])
            if rnd:
                random.shuffle(s)
            return cap_list_str(s)
        if drop:
            return ""
        return ch

    def encode_text(
        self,
        text: str,
        drop: bool = True,
        direction: chr = "r",
        rnd: bool = True,
        limit_possibilities: int = 8,
        start: int = 0,
        jump: int = 1,
    ) -> List[str]:
        """
        This is where the magic occurs.  Encode or decode the text.

        text: the text to run through the algorithm
        drop: set true to ignore non-alphabetic characters; false includes them
        direction: 'R', 'E', or 'D' for reversible, encrypt, or decipher; '0' to echo the input
        rnd: if True, scrambles the possibilities for each character and ignores start and jump
        limit_possibilities: how many possibilities are returned
        start: start index for which possibility is chosen
        jump: how much to jump—set to 0 to always choose the start possibility

        :returns:
        A list:
        row 0 is the input text with the extra characters dropped or included as specified by drop
        the rest of the rows are the possibilities
            the start index, when applicable, increments by 1 on each new row
        The output will look grid-like if each row is separated by \n
        """
        # prep work
        results: List[str] = [
            "".join([self.encode_chr(c, "0", drop) for c in text.strip().lower()])
        ]
        if direction == "0":  # echo the input
            return results * 2  # ensures that the results[1] is a valid index

        # get possibilities for each character
        possibilities: List[str] = [
            self.encode_chr(c, direction, drop, rnd) for c in results[0]
        ]

        return results + [
            "".join(  # create string for each possible result
                [
                    possibilities[char_no][
                        (start + offset + (char_no * jump))
                        % len(possibilities[char_no])
                    ]
                    for char_no in range(
                        len(results[0])
                    )  # each character in stripped input phrase
                ]
            )
            for offset in range(limit_possibilities)
        ]

    def draw_keyboard(self) -> None:
        """
        Prints the keyboard layout to stdout
        """
        # Must print row-by-row
        for row in self.grid:
            tmp: List[List[str]] = [[], [], [], [], []]
            for letter in row:
                for i, o in enumerate(letter.draw(False)):
                    tmp[i].append(o)
            for line in tmp:
                p("  ".join(line))
            p("\n")


def display_possibilities(
    possibilities: List[str], only_one: bool = False, separator: str = "-"
) -> str:
    if only_one:
        return possibilities[
            1
        ]  # return the first possibility (index 0 is the input phrase)
    inp: str = possibilities[0]
    possibilities.append(inp)  # repeat the input at the end for human-readable output
    if s := separator.replace("\n", "").replace("\t", ""):
        s = (s * (len(inp) // len(s) + 1))[: len(inp)]
        possibilities.insert(1, s)
        possibilities.insert(
            -1, s
        )  # this has counter-intuitive behavior but it works for this usage
    return "\n".join(possibilities)


nav_guide = ("❇", ["➡️", "↗️", "⬆️", "↖️", "⬅️", "↙️", "⬇️", "↘️"])
direction_methods: Dict[chr, str] = {
    "R": "surround",
    "E": "encrypts_to",
    "D": "deciphers_to",
    "0": "name",
}


def letter_test_grid(c: Cipher, l: chr) -> str:  # noqa ignore short variable name 'l'
    """
    Generates a grid of letters that either appear in the surround of l or have
    l in their surrounding.  Exclamation points are appended to lines for
    letters that contain l in their surroundings but do not surround l.
    Question marks added to lines for letters in the surrounding of l that do
    not also contain l in their surrounding.
    """
    o: List[str] = []
    ring: List[str] = c.surround(l, True)
    o.append(str((l, ring)))
    o.append(str(nav_guide) + "🔛")
    for letter in ALPHABET:
        s = c.surround(letter)
        if l in s or letter in ring:
            o.append(
                str((letter, c.surround(letter, True)))
                + f"\t{'‼' if letter not in ring else ''}"
                + f"\t{'❔' if l not in s else ''}"
            )
    o.append(str(nav_guide) + "🔛")
    o.append(str((l, ring)))
    return "\n".join(o)


@click.command()
@click.argument("text", type=click.File(), nargs=1)
@click.option(
    "-k",
    "--layout",
    default="QWERTY",
    type=click.STRING,
    help="""
        The layout of the keyboard you use for the cipher.

        Technically, this is the name of a file in the layouts directory.

        The -k shortname stands for keyboard and defaults to QWERTY.
        """,
)
@click.option(
    "--only-one",
    is_flag=True,
    help="""
        Limit the output to a single substitution.
        If this flag is not set, then a grid of possibilities will be displayed
        (setting this flag negates the usefulness of setting --barrier).
        """,
)
@click.option(
    "-sep",
    "--barrier",
    type=click.STRING,
    default="-",
    help="""
        Separate input from output with the character(s) supplied here.  
        Default is a fence of hyphens.
        """,
)
@click.option(
    "--random/--fixed",
    "rnd",
    default=True,
    help="""
        Pass --fixed to always order the output possibilities in a consistent order.
        Otherwise, the possible substitutions for each letter are presented in a random order.
        If the step parameter is changed with random output order, the results may be
        less random than expected.
        """,
)
@click.option(
    "--direction",
    "-j",  # stands for jump
    "skip",
    type=click.INT,
    default=1,
    help="""
        How many positions to rotate between each subsequent letter.
        Negative values move clockwise and positive count clockwise.
        This one in particular will reduce randomness if it is set to
        values other than 1 or -1.

        A value of 0 here where --fixed is true will return the key that
        is at a constant offset from the right.

        (The j stands for jump)
        """,
)
@click.option(
    "--offset",
    "--start",
    "start",
    type=click.INT,
    default=0,
    help="""
        When --fixed is set, this controls the offset of the first
        letter of the output by moving it n spaces from the key directly
        to the right.  Use a negative number to move clockwise or, to move
        counter-clockwise, use a positive number.
        0 starts directly to the right.
        """,
)
@click.option(
    "--strip/--include",
    default=True,
    help="""
        Strip out [default] or pass through characters that are not in the cipher.
        Passing them through provides hints that make manual decoding easier. 
        """,
)
# These are placed at the end of the options so the --help output is prettier
@click.option(
    "--encrypt",
    "direction",
    flag_value="E",
    help="""Generate possibilities that can decipher to TEXT""",
)
@click.option(
    "--reversible",
    "direction",
    flag_value="R",
    default=True,
    help="""[DEFAULT] Generate fully-reversible options""",
)
@click.option(
    "--decipher",
    "direction",
    flag_value="D",
    help="""Display possible cleartext letters for TEXT""",
)
def shark(
    text,
    layout: str = "QWERTY",
    only_one: bool = False,
    barrier: str = "*",
    direction: chr = "R",
    rnd: bool = True,
    skip: int = 1,
    start: int = 0,
    strip: bool = False,
):
    """
    Runs TEXT through the shark cipher and displays the result to stdout

    To read from stdin rather than a specific TEXT file, use - for TEXT.

    For specific recipes on CLI usage, see the readme.
    """
    c = Cipher(layout)
    for line in text:
        p(
            display_possibilities(
                c.encode_text(line, strip, direction, rnd, start=start, jump=skip),
                only_one,
                barrier,
            )
        )


if __name__ == "__main__":
    shark()
