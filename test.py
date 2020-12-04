#!/usr/bin/env python3.8

import click
from typing import *
from cipher import *

"""

Tests the cipher by taking an input string, enciphering it randomly, and then
running the ciphertext through the cipher to ensure that each alphabetic
character is in the 8 possibilities presented for each character of ciphertext.

"""


def phrase_check(phrase: str) -> str:
    """
    Checks that the phrase exists and is in the lower case

    If it does not exist, use a default phrase
    """
    ph = phrase.lower().strip()
    return ph if ph else "the quick brown fox jumped over the lazy god"


def reverse(layout: str, phrase: str) -> bool:
    """
    Encrypts a phrase randomly and then checks that the original phrase exists
    among the possible decryptions
    """
    phrase = phrase_check(phrase)
    return True  # TODO


def association_check(layout: str) -> bool:
    """
    Checks that each letter is contained in the surrounding of each letter that
    surrounds it.
    """
    c = Cipher(layout)
    fail_count: int = 0
    for letter in "abcdefghijklmnopqrstuvwxyz":
        if all(letter in q.surround_str for q in c.letter_index[letter].surround):
            pass
        else:
            e(f"'{letter}' lacks proper linkbacks under {layout}")
            e(letter_test_grid(c, letter))
            fail_count += 1
    if fail_count:
        e(f"{fail_count} mismatches in {layout}")
        return False
    return True


def test_invalid_repeat() -> bool:
    """Ensure invalid layouts are not accepted"""
    try:
        c = Cipher("test-invalid")
    except AssertionError:
        return True  # that's probably what threw the error
    return False  # no error thrown on bad layout file => FAIL


def test_catch_missing() -> bool:
    """Ensure that layouts with missing letters are caught"""
    try:
        c = Cipher("test-missing")
    except AssertionError:
        return True  # it's probably the assertion, check stderr
    return False  # it didn't catch the missing letters


def test_ignore_missing() -> bool:
    """Do not raise an error if there are more letters than expected"""
    try:
        c = Cipher("test-missing", 4)
    except AssertionError:
        return False
    return True


def run_tests(phrase: str) -> List[bool]:
    phrase = phrase_check(phrase)
    p(f"Test layout validation")
    p(f"Expect something in stderr")
    results: List[bool] = [
        test_catch_missing(),
        test_invalid_repeat(),
        test_ignore_missing(),
    ]
    for layout in [
        "QWERTY",
        "Colemak",
        "Workman",
        "Dvorak",
        "test-colemak",
        "test-alphabet",
    ]:
        p(f"Testing in {layout}…")
        results.extend(
            [
                association_check(layout),
                reverse(layout, phrase),
            ]
        )
    return results


@click.command()
@click.argument("ph", nargs=-1)
def cli_test(ph: List[str]) -> bool:
    """
    Runs the tests.

    PH is an optional argument for a custom phrase to test.
    """
    phrase: str = " ".join(ph) if ph else "Jackdaws love my big sphinx of quartz."
    # p(phrase)
    if all(tsts := run_tests(phrase)):
        p("Tests passed!")
    else:
        e(f"{len([t for t in tsts if t is False])} out of {len(tsts)} tests failed!")


if __name__ == "__main__":
    cli_test()
