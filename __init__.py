import os
import time  # TODO: isort, delete unused
import borders
import sys


def get_terminal_size():
    """Return a w,h tuple of the current size of the terminal."""
    # TODO: remove -10
    return (os.get_terminal_size().columns, os.get_terminal_size().lines)


class Window:
    def __init__(
        self, position=(0, 0), size=(10, 10), style="double", title="", fill=True
    ):
        """Initialize an empty window.

        :param position: A tuple of x,y coordinates for the top left outer corner
        :param size: The outer size of a window (i.e. including borders)
        :param style: Window border style (see borders.py)
        :param title: Text displayed on the top of the window
        :param fill: Whether the background of the window should be cleared
        """
        self.style = borders.STYLES[style]
        self.title = ""
        self.position = position
        self.size = size
        self.fill = fill

    def _translate(self, x, y):
        return (x + self.position[0], y + self.position[1])

    def draw_border(self, canvas):
        """Draw own border onto a given canvas."""
        # top, bottom
        for i in range(self.size[0] + 1):
            pos_up = self._translate(i, 0)
            pos_down = self._translate(i, self.size[1])
            if i != 0:
                canvas.set_border(pos_up, "left", self.style)
                canvas.set_border(pos_down, "left", self.style)
            if i != self.size[0]:
                canvas.set_border(pos_up, "right", self.style)
                canvas.set_border(pos_down, "right", self.style)
            # clear inner borders
            if self.fill and i != 0 and i != self.size[0]:
                canvas.set_border(pos_up, "down", 0)
                canvas.set_border(pos_down, "up", 0)

        # left, right
        for j in range(self.size[1] + 1):
            pos_left = self._translate(0, j)
            pos_right = self._translate(self.size[0], j)
            if j != 0:
                canvas.set_border(pos_left, "up", self.style)
                canvas.set_border(pos_right, "up", self.style)
            if j != self.size[1]:
                canvas.set_border(pos_left, "down", self.style)
                canvas.set_border(pos_right, "down", self.style)
            # clear inner borders
            if self.fill and j != 0 and j != self.size[1]:
                canvas.set_border(pos_right, "left", 0)
                canvas.set_border(pos_left, "right", 0)

    def draw_content(self, canvas):
        if self.fill:
            for j in range(1, self.size[1]):
                for i in range(1, self.size[0]):
                    pos = self._translate(i, j)
                    canvas.set_content(pos, self.fill_ch)


class Canvas:
    def __init__(self, windows=None):
        """Initialize an empty canvas.

        :param windows: An array of windows on the canvas
        """
        self.size = get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]

        self.windows = windows
        if self.windows is None:
            self.windows = []

    def add_border(self, position, border):
        """Overlay a border onto the character at a given position.

        :param position: A coordinate tuple for the new border
        :param border: An integer representing the border type
        """
        if position[0] >= self.size[0] or position[1] >= self.size[1]:
            return

        if isinstance(self.data[position[0]][position[1]], str):
            self.data[position[0]][position[1]] = 0
        self.data[position[0]][position[1]] |= border

    def remove_border(self, position, border):
        """Remove a part of the border at a given position.

        :param position: A coordinate tuple for the new border
        :param border: An binary integer with ones with bits to remove
        """
        if position[0] >= self.size[0] or position[1] >= self.size[1]:
            return

        mask = ~border & borders.mask_1(borders.bits_per_style * 4)

        if isinstance(self.data[position[0]][position[1]], str):
            self.data[position[0]][position[1]] = 0
        self.data[position[0]][position[1]] &= mask

    def set_border(self, position, side, style):
        """Remove the existing border on a side and replace it with a given style.

        :param position: A coordinte tuple for the new border
        :param side: String "up"|"down"|"left"|"right"
        :param style: An integer representing the new border type
        """
        self.remove_border(position, borders.mask_side(side))
        self.add_border(position, borders.SIDES[side] * style)

    def set_content(self, position, content):
        if position[0] >= self.size[0] or position[1] >= self.size[1]:
            return
        self.data[position[0]][position[1]] = content

    def add_window(self, window):
        """Add a Window object to the canvas."""
        if window not in self.windows:
            self.windows += window

    def remove_window(self, window):
        """Remove a Window object from canvas."""
        if window in self.windows:
            self.windows.remove(window)

    def redraw(self):
        """Scrap all canvas data and redraw all windows."""
        self.size = get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]
        for window in self.windows:
            window.draw_border(self)
            window.draw_content(self)

    def print(self, debug=False):
        """Print the current canvas onto the terminal as-is, even if terminal resized."""
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                px = self.data[i][j]
                if isinstance(px, int):  # px is a border type
                    print(borders.get(px, debug), end="")
                else:  # px is a content character
                    print(px, end="")
            # last newline
            if j != self.size[1] - 1:
                print()
            else:
                sys.stdout.flush()


def move(x, y):
    """Move the terminal cursor to x,y."""
    print("\033[%d;%dH" % (y + 1, x + 1), end="")


import random

if __name__ == "__main__":
    i = 0
    j = 0
    while True:
        i %= 10
        i += 1
        j %= 10
        j += (
            random.randint(0, 2)
            * random.randint(0, 1)
            * random.randint(0, 1)
            * random.randint(0, 1)
        )
        background = Window(size=[i - 1 for i in get_terminal_size()], style="double")
        static = Window(style="thin", size=(10, 10), position=(2 + j, 1))
        cat = Window(
            style="thin", title="hello", size=(1 + i, 4), position=(6 + j, 9 + j)
        )

        background.fill_ch = "x"
        static.fill_ch = "s"
        cat.fill_ch = "c"

        canvas = Canvas([background, static, cat])
        canvas.redraw()
        canvas.print(debug=False)
        move(0, 0)
        time.sleep(0.1)