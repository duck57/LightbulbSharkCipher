#!/usr/bin/env python3

import click
from typing import *
from cipher import *

"""

Tests the cipher by taking an input string, enciphering it randomly, and then
running the ciphertext through the cipher to ensure that each alphabetic
character is in the 8 possibilities presented for each character of ciphertext.

"""


def test(phrase: str) -> bool:
    phrase = phrase.lower().strip()
    pass  # TODO write the test


@click.command()
@click.argument("ph", nargs=-1)
def cli_test(ph: List[str]) -> bool:
    phrase: str = " ".join(ph) if ph else "Jackdaws love my big sphinx of quartz."
    if test(phrase):
        print("Test passed!")
    else:
        print("Test failure")


if __name__ == "__main__":
    cli_test()
