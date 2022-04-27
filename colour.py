# colour options
NORMAL = 0
BOLD = 1
UNDERLINE = 4
BLINK = 5

FOREGROUND = 30
BACKGROUND = 40
BRIGHT = 60
COLOURS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

# {foreground_colour, background_colour, bold, underline, blink}


def colour_to_int(options):
    x = 0
    for option in options:
        if option in COLOURS:
            x += COLOURS.index(option)
            continue


class ColourSegment:
    def __init__(self, text, options):
        self.text = text
        self.options = options

    def __str__(self):
        return "\033[" + ";".join(self.options) + "m" + self.text + "\033[0m"

    def __len__(self):
        return len(self.text)


class Colour:
    def __init__(self, text, options=None):
        self.segments = []
        if isinstance(text, Colour):
            # merge options, copy text
            self.segments = text.segments.copy()
            self.options = text.options.copy()
            # TODO: add options from kwargs
        elif isinstance(text, string):
            self.segments.append(ColourSegment(text, options))
        else:
            raise ValueError("Invalid text " + str(text))

    def __str__(self):
        return "".join([str(seg) for seg in self.segments])

    def add(self, first, second):
        return first + second

    def __add__(self, other):
        return self.add(self, other)

    def __radd__(self, other):
        return self.add(other, self)

    def __iadd__(self, other):
        return self.add(self, other)

    def __len__(self):
        return sum([len(seg) for seg in self.segments])


# desired syntax:
# "Hello " + Red(username) + "!"
# or
# "Hello " + Colour(username, options=["red", "bold"]) + "!"
# or
# "Hello " + Bold(Red(username)) + "!"
# or
# Green("Hello" + Red(username) + "!", force=False)
