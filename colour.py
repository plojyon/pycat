# colour options
NORMAL = 0

BOLD = 1
UNDERLINE = 4
BLINK = 5

FOREGROUND = 30
BACKGROUND = 40
BRIGHT = 60
COLOURS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

# {
#     foreground: str,
#     background: str,
#     extra: [BOLD, UNDERLINE, BLINK],
# }


def encode_options(style):
    """Return a ;-separated list of numbers representing the given style."""

    def get_colour(_style):
        """Convert a colour string to int."""
        assembled = 0
        if "bright_" in _style:
            assembled += BRIGHT
            _style = _style[len("bright_"):]
        assembled += COLOURS.index(_style)
        return assembled

    options = []
    if "foreground" in style:
        options.append(FOREGROUND + get_colour(style["foreground"]))
    if "background" in style:
        options.append(BACKGROUND + get_colour(style["background"]))
    if "extra" in style:
        options += style["extra"]

    return ";".join([str(o) for o in options])


class SegmentIterator:
    def __init__(self, segment):
        self.segment = segment
        self.i = 0

    def __next__(self):
        try:
            char = self.segment.text[self.i]
            self.i += 1
            return Colour(char, self.segment.clone().style)
        except:
            raise StopIteration("thanks for coming")


class ColourSegment:
    def __init__(self, text="", style=None):
        self.text = text
        self.style = style
        if self.style is None:
            self.style = {}

    def get_text(self, pos=None):
        text = self.text
        if pos is not None:
            text = self.text[pos]
        clone = self.clone()
        clone.text = text
        return clone

    def clone(self):
        clone = ColourSegment(self.text)
        clone.add_style(self.style)
        return clone

    def add_style(self, other_style, merge=True):
        if other_style is None:
            return

        merged = {}
        if merge:
            styles = [self.style, other_style]
        else:
            styles = [other_style, self.style]

        for style in styles:
            for key,value in style.items():
                if key not in merged:
                    merged[key] = value

        if merge and "extra" in self.style and "extra" in other_style:
            merged["extra"] = list(set(self.style["extra"]) + set(other_style["extra"]))

        self.style = merged

    def __str__(self):
        return "\033[" + encode_options(self.style) + "m" + self.text + "\033[0m"

    def __len__(self):
        return len(self.text)

    def __iter__(self):
        return SegmentIterator(self)


class ColourIterator:
    def __init__(self, colour):
        self.colour = colour
        self.i = 0
        self.segment = self.colour.segments[self.i].__iter__()

    def __next__(self):
        try:
            return self.segment.__next__()
        except StopIteration:
            self.i += 1
            if self.i >= len(self.colour.segments):
                raise StopIteration("Thank you for using ColourIterator!")
            self.segment = self.colour.segments[self.i].__iter__()
            return self.__next__()


class Colour:
    def __init__(self, text, style=None, merge_style=True):
        """Initialize a Colour object.

        :param text: A string or a Colour object to use as text.
        :param style: A style object (see definition above)
        :param merge_style: if True, text effects will merge and overwrite only
            undefined effects on the child Colour. Otherwise only inherit text.
        """
        if isinstance(text, Colour):
            # merge options, copy text
            self.segments = [seg.clone() for seg in text.segments]
            for seg in self.segments:
                seg.add_style(style, merge=merge_style)
        elif isinstance(text, str):
            self.segments = [ColourSegment(text, style)]
        else:
            raise ValueError("Invalid text " + str(text))

    def __str__(self):
        return "".join([str(seg) for seg in self.segments])

    def add(self, first, second):
        ret = Colour(first)
        if not isinstance(second, Colour):
            second = Colour(second)
        ret.segments += second.segments.copy()
        return ret

    def __add__(self, second):
        return self.add(self, second)

    def __radd__(self, second):
        return self.add(second, self)

    def __iadd__(self, second):
        if not isinstance(second, Colour):
            second = Colour(second)
        self.segments += second.segments
        return self

    def __len__(self):
        return sum([len(seg) for seg in self.segments])

    def __iter__(self):
        return ColourIterator(self)

    def __getitem__(self, key):
        return [ch for ch in self][key]
        # if isinstance(key, slice):
        #     return [self.__getitem__(i) for i in slice]
        # else:
        #     pass

    # def __setitem__(self, key, value):
    #     pass
    #
    # def __delitem__(self, key):
    #     pass


class Red(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "red"}, merge_style)


class Green(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "green"}, merge_style)


class Yellow(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "yellow"}, merge_style)


class Blue(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "blue"}, merge_style)

class Magenta(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "magenta"}, merge_style)

class Cyan(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "cyan"}, merge_style)

class White(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"foreground": "white"}, merge_style)

##########

class Bold(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"extra": [BOLD]}, merge_style)

class Blink(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"extra": [BLINK]}, merge_style)

class Underline(Colour):
    def __init__(self, text, merge_style=True):
        super().__init__(text, {"extra": [UNDERLINE]}, merge_style)

###########

class Simple(Colour):
    def __init__(self, text, colour, merge_style=True):
        super().__init__(text, {"foreground": colour}, merge_style)


# desired syntax:
# "Hello " + Red(username) + "!"
# or
# "Hello " + Colour(username, style={"foreground": {"colour": "red", bold=True}}) + "!"
# or
# "Hello " + Bold(Red(username)) + "!"
# or
# Green("Hello" + Red(username) + "!", force=False)
# or
# Simple("hello", "purple")
