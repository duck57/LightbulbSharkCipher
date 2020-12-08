#!/usr/bin/env python3.8

from cipher import *

"""
Draw the keyboard layouts for manual inspection to
ensure proper linking
"""


@click.command()
@click.argument(
    "layout",
    type=click.Choice(
        os.listdir(os.path.join(os.path.dirname(__file__), "layouts")),
        case_sensitive=False,
    ),
    nargs=1,
)
def draw(layout) -> None:
    c = Cipher(layout)
    c.draw_keyboard()


if __name__ == "__main__":
    draw()
