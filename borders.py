"""Border styles for pycat.

Access a specific border type:
    type = SIDES["up"]*STYLES["double"] + SIDES["down"]*STYLES["double"]
    print(BORDERS[type])
"""
from collections import defaultdict

# This value should not exceed 32/4 = 8. Bad things might happen.
bits_per_style = 3  # allows up to 2 ** bits_per_style different styles

STYLES = {
    "empty": 0b000,
    "double": 0b001,
    "thin": 0b010,
    "thick": 0b011,
    "full": 0b100,
    ...: ...,  # add your own styles here
}
SIDES = {
    "up": 1 << 3 * bits_per_style,
    "right": 1 << 2 * bits_per_style,
    "down": 1 << 1 * bits_per_style,
    "left": 1 << 0 * bits_per_style,
}


def mask_1(length):
    """Return a one-mask (0b1111...11) with a given bit length."""
    mask = 1
    for bit in range(length - 1):
        mask <<= 1
        mask += 1
    return mask


def mask_side(side):
    """Return a mask of ones at the given side."""
    return SIDES[side] * mask_1(bits_per_style)


def to_str(x):
    mask = mask_1(bits_per_style)
    sides = {
        "up": (x & (mask * SIDES["up"])) >> 3 * bits_per_style,
        "right": (x & (mask * SIDES["right"])) >> 2 * bits_per_style,
        "down": (x & (mask * SIDES["down"])) >> 1 * bits_per_style,
        "left": (x & (mask * SIDES["left"])) >> 0 * bits_per_style,
    }

    def int_to_style(key):
        """Find a dictionary key by value."""
        return list(STYLES.keys())[list(STYLES.values()).index(key)]

    sides = [
        side + "=" + int_to_style(style)
        for side, style in sides.items()
        if int_to_style(style) != "empty"
    ]

    return "<" + ",".join(sides) + ">"


# 0baabbccdd - a=top, b=right, c=bottom, d=left

u = SIDES["up"]
d = SIDES["down"]
l = SIDES["left"]
r = SIDES["right"]
D = STYLES["double"]
t = STYLES["thin"]
T = STYLES["thick"]
F = STYLES["full"]

BORDERS = {
    0: " ",
    l * D + r * D: "═",
    u * D + d * D: "║",
    d * t + r * D: "╒",
    d * D + r * t: "╓",
    d * D + r * D: "╔",
    l * D + d * t: "╕",
    d * D + l * t: "╖",
    d * D + l * D: "╗",
    u * t + r * D: "╘",
    u * D + r * t: "╙",
    u * D + r * D: "╚",
    l * D + u * t: "╛",
    l * t + u * D: "╜",
    l * D + u * D: "╝",
    u * t + r * D + d * t: "╞",
    u * D + d * D + r * t: "╟",
    u * D + r * D + d * D: "╠",
    l * D + u * t + d * t: "╡",
    l * t + u * D + d * D: "╢",
    l * D + u * D + d * D: "╣",
    l * D + r * D + d * t: "╤",
    l * t + r * t + d * D: "╥",
    l * D + r * D + d * D: "╦",
    l * D + r * D + u * t: "╧",
    u * D + l * t + r * t: "╨",
    u * D + l * D + r * D: "╩",
    u * t + d * t + l * D + r * D: "╪",
    u * D + d * D + l * t + r * t: "╫",
    u * D + r * D + l * D + d * D: "╬",
    l * t + r * t: "─",
    u * t + d * t: "│",
    r * t + d * t: "┌",
    l * t + d * t: "┐",
    u * t + r * t: "└",
    u * t + l * t: "┘",
    u * t + r * t + d * t: "├",
    u * t + d * t + l * t: "┤",
    l * t + r * t + d * t: "┬",
    u * t + l * t + r * t: "┴",
    u * t + l * t + r * t + d * t: "┼",
    l * F + r * F: "█",
    u * F + d * F: "█",
    r * F + d * F: "█",
    l * F + d * F: "█",
    u * F + r * F: "█",
    u * F + l * F: "█",
    u * F + r * F + d * F: "█",
    u * F + d * F + l * F: "█",
    l * F + r * F + d * F: "█",
    u * F + l * F + r * F: "█",
    u * F + l * F + r * F + d * F: "█",
    # add your own styles here
}


def get(x, debug=False, default="?"):
    if x in BORDERS:
        return BORDERS[x]
    if debug:
        return to_str(x)
    return default
