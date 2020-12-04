#!/usr/bin/env python3.8

import click
import os
from typing import *

"""
Program execution
1. Main loads text and options
2. Load the layout
3. Generate possible choices for each character
4. Choose which choice(s) to display
5. Print output to stdout

Programming plan
1. Write layout loader
2. Cipher text
3. Implement all the command-line options

Validation checks
* Each character appears only once in the layout file
* (Characters in the input that are not in the layout are skipped)
* Optional: ensure that each letter appears once in the layout (no skipped letters)
"""


def p(content):
    click.echo(content, err=False)


def e(content):
    click.echo(content, err=True)


class Keycap:
    def __init__(self, display: chr):
        self.blank: bool = False if display.strip() else True
        self.name: chr = display if not self.blank else " "
        self.right: Keycap
        self.left: Keycap
        self.up: Keycap
        self.down: Keycap
        self.surround: List[Keycap] = []  # these ones are reversible

    def __repr__(self) -> str:
        return self.name if not self.blank else "∞"

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
        return [
            self.right,
            self.NE,
            self.up,
            self.NW,
            self.left,
            self.SW,
            self.down,
            self.SE,
        ]

    @property
    def surround_str(self) -> str:
        return "".join([str(s) for s in self.surround])

    @property
    def raw_surround_str(self) -> str:
        return "".join(str(s) for s in self.raw_surround)

    def bake_surround(self) -> int:
        """
        Filters out the blank and non-reversible keys from raw_surround
        and then saves it to self.surround

        Returns the number of non-reverisble keys that were thrown out
        (not counting blanks)
        """
        self.surround = [
            k for k in self.raw_surround if self in k.raw_surround and not k.blank
        ]
        return (
            len(self.raw_surround)
            - len(self.surround)
            - len([k for k in self.raw_surround if k.blank])
        )


class Cipher:
    def __init__(
        self, layout: str = "QWERTY", alphabet_check: int = 26, reverse: bool = None
    ):
        layout = layout.lower().strip()
        if not layout:
            layout = "qwerty"
        if reverse is None and layout == "dvorak":
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
            for chr in row:
                c = Keycap(chr)
                self.letter_index[chr] = c
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

                k.up = u
                k.down = d
                u.down = k
                d.up = k

        # bake in the reversible keys
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


nav_guide = ("❇", ["➡️", "↗️", "⬆️", "↖️", "⬅️", "↙️", "⬇️", "↘️"])


def letter_test_grid(c: Cipher, l: chr) -> str:
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
    for letter in "abcdefghijklmnopqrstuvwxyz":
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
@click.argument("text", nargs=-1)
@click.option(
    "-k",
    "--layout",
    default="QWERTY",
    type=click.STRING,
    help="""
        The layout of the keyboard you use for the cipher.

        Technically, this is the name of a file in the layouts directory.

        The -k shortname stands for keyboard.
        """,
)
@click.option(
    "-f",
    "--from-file",
    "file",
    type=click.File(),
    help=""" 
        Ignore the TEXT in favor of sharking a file one line at a time.  A
        value of '-' will shark stdin.
        """,
)
def shark(text: str, layout: str = "QWERTY"):
    """
    Runs TEXT through the shark cipher

    TEXT can be either the plaintext or the ciphertext.  Due to the
    eccentricities of human keyboard layouts, this cipher is not fully
    reversible.
    """
    c = Cipher(layout)


if __name__ == "__main__":
    shark()
