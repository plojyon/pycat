import os
import time  # TODO: isort, delete unused
import borders
import sys


def get_terminal_size():
    """Return a w,h tuple of the current size of the terminal."""
    # TODO: remove -10
    return (os.get_terminal_size().columns, os.get_terminal_size().lines)


class Window:
    def __init__(self, location=(0, 0), size=(10, 10), style="double", title=""):
        """Initialize an empty window.

        :param location: A tuple of x,y coordinates for the top left outer corner
        :param size: The outer size of a window (i.e. including borders)
        :param style: Window border style (see borders.py)
        :param title: Text displayed on the top of the window
        """
        self.style = borders.STYLES[style]
        self.title = ""
        self.location = location
        self.size = size

    def draw(self, canvas):
        """Draw own borders onto a given canvas."""
        # top, bottom
        for i in range(self.size[0] + 1):
            border = 0
            if i != 0:
                border += borders.SIDES["left"] * self.style
            if i != self.size[0]:
                border += borders.SIDES["right"] * self.style
            # top
            canvas.add_border((self.location[0] + i, self.location[1]), border)
            # bottom
            canvas.add_border(
                (self.location[0] + i, self.location[1] + self.size[1]), border
            )

        # left, right
        for j in range(self.size[1] + 1):
            border = 0
            if j != 0:
                border += borders.SIDES["up"] * self.style
            if j != self.size[1]:
                border += borders.SIDES["down"] * self.style
            # left
            canvas.add_border((self.location[0], self.location[1] + j), border)
            # right
            canvas.add_border(
                (self.location[0] + self.size[0], self.location[1] + j), border
            )


class Canvas:
    def __init__(self, windows=None):
        """Initialize an empty canvas.

        :param windows: An array of windows on the canvas
        """
        self.size = get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]

        self.windows = set(windows)
        if self.windows is None:
            self.windows = set()

    def add_border(self, position, border):
        """Overlay a border onto the character at a given position.

        :param position: A coordinate tuple for the new border
        :param border: An integer representing the border type
        """
        if position[0] >= self.size[0] or position[1] >= self.size[1]:
            return
        self.data[position[0]][position[1]] |= border

    def remove_border(self, position, border):
        """Remove a part of the border at a given position.

        :param position: A coordinate tuple for the new border
        :param border: An binary integer with ones with bits to remove
        """
        if position[0] >= self.size[0] or position[1] >= self.size[1]:
            return

        mask = ~border & borders.mask_1(borders._bits_per_style * 4)
        self.data[position[0]][position[1]] &= mask

    def add_window(self, window):
        """Add a Window object to the canvas."""
        window.canvas = self
        self.windows += window

    def redraw(self):
        """Scrap all canvas data and redraw all windows."""
        self.size = get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]
        for window in self.windows:
            window.draw(self)

    def print(self, debug=False):
        """Print the current canvas onto the terminal as-is, even if terminal resized."""
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                print(borders.get(self.data[i][j], debug), end="")
            # last newline
            if j != self.size[1] - 1:
                print()
            else:
                sys.stdout.flush()


def move(x, y):
    """Move the terminal cursor to x,y."""
    print("\033[%d;%dH" % (y + 1, x + 1))


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
        win1 = Window(style="double", size=(10, 10), location=(1, 1))
        win2 = Window(title="hello", size=(1 + i, 4), location=(6 + j, 9 + j))
        win3 = Window(size=[i - 1 for i in get_terminal_size()], location=(0, 0))
        canvas = Canvas([win1, win2, win3])
        canvas.redraw()
        canvas.print(debug=False)
        time.sleep(0.1)
