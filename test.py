#!/usr/bin/env python3

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


def reverse(layout: str, phrase: str, directed: bool = False) -> bool:
    """
    Encrypts a phrase randomly and then checks that the original phrase exists
    among the possible decipherings.

    Additionally tests support for dropping characters when directed or that
    additional characters do not cause problems when run reversible
    """
    phrase = phrase_check(phrase)
    c = Cipher(layout)
    p(f"\t{'Directed' if directed else 'Symmetric'} decipher check")
    crypt: str = display_possibilities(
        c.encode_text(phrase, drop=directed, direction="E" if directed else "R"),
        only_one=True,
    )
    if directed:  # drop invalid characters from the input phrase to make the test pass
        phrase = c.encode_text(phrase, drop=True, direction="0")[0]
    passed: bool = all(
        phrase[x] in c.encode_chr(ch, direction="D" if directed else "R", drop=directed)
        for x, ch in enumerate(crypt)
    )
    if passed:
        return True
    e(f"\t\tFAILED")
    return False


def association_check(layout: str) -> bool:
    """
    Checks that each letter is contained in the surrounding of each letter that
    surrounds it.
    """
    c = Cipher(layout)
    p(f"\tAssociation check")  # \t to put it under the layout name
    fail_count: int = 0
    for letter in ALPHABET:
        failed: int = 0
        if all(
            letter in cap_list_str(q.surround) for q in c.letter_index[letter].surround
        ):
            pass
        else:
            e(f"'{letter}' lacks proper symmetric linkbacks under {layout}")
            failed += 1
        if all(
            letter in cap_list_str(q.deciphers_to)
            for q in c.letter_index[letter].encrypts_to
        ):
            pass
        else:
            e(f"'{letter}' lacks proper directional linkbacks under {layout}")
            failed += 1
        if failed:
            e(letter_test_grid(c, letter))
            fail_count += failed
    if fail_count:
        e(f"{fail_count} mismatches in {layout}")
        return False
    return True


def test_invalid_repeat() -> bool:
    """Ensure invalid layouts are not accepted"""
    try:
        c = Cipher("test-invalid")  # noqa
    except AssertionError:
        return True  # that's probably what threw the error
    return False  # no error thrown on bad layout file => FAIL


def test_catch_missing() -> bool:
    """Ensure that layouts with missing letters are caught"""
    try:
        c = Cipher("test-missing")  # noqa
    except AssertionError:
        return True  # it's probably the assertion, check stderr
    return False  # it didn't catch the missing letters


def test_ignore_missing() -> bool:
    """Do not raise an error if there are more letters than expected"""
    try:
        c = Cipher("test-missing", 4)  # noqa
    except AssertionError:
        return False
    return True


def run_tests(phrase: str) -> List[bool]:
    phrase = phrase_check(phrase)
    p(f"Today's test phrase is '{phrase}'")
    p(f"Test layout validation\n\tExpect something in stderr")
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
                association_check(layout),  # make sure the letters are properly linked
                reverse(layout, phrase),  # encrypt and then decipher a text
                reverse(layout, phrase, directed=True),  # same as above but directed
            ]
        )
    return results


@click.command()
@click.argument("ph", nargs=-1)
def cli_test(ph: List[str]) -> int:
    """
    Runs the tests.

    PH is an optional argument for a custom phrase to test.

    To load your test phrase from a file, something similar to the following FISh command
    should be used.

    ./test.py (cat layouts/test-alphabet)
    """
    phrase: str = " ".join(ph) if ph else "Jackdaws love my big sphinx of quartz."
    # p(phrase)
    if all(tsts := run_tests(phrase)):
        p("All tests passed!")
        return 0
    else:
        fail_count = len([t for t in tsts if t is False])
        e(f"{fail_count} out of {len(tsts)} tests failed!")
        return fail_count


if __name__ == "__main__":
    if f := cli_test():
        raise SystemExit(f)
