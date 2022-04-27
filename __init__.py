import os
import time  # TODO: isort, delete unused
import sys

from . import borders
from . import cursor

cursor.enable_ansi()


class Window:
    def __init__(
        self,
        position=(0, 0),
        size=(10, 10),
        style="double",
        fill=True,
        padding=None,
    ):
        """Initialize an empty window.

        :param position: A tuple of x,y coordinates for the top left outer corner
        :param size: The outer size of a window (i.e. including borders)
        :param style: Window border style (see borders.py)
        :param fill: Whether the background of the window should be cleared
        """
        self.style = borders.STYLES[style]
        self.position = position
        self.size = size
        self.fill = fill
        self.padding = padding
        self.content = []
        if self.padding is None:
            self.padding = [1, 2, 1, 2]  # top right bottom left

    def _translate(self, x, y):
        return (x + self.position[0], y + self.position[1])

    @property
    def inner_position(self):
        return (self.position[0] + self.padding[3], self.position[1] + self.padding[0])

    @property
    def inner_width(self):
        return self.size[0] - self.padding[1] - self.padding[3]

    @property
    def inner_height(self):
        return self.size[1] - self.padding[0] - self.padding[2]

    @property
    def inner_size(self):
        return (self.inner_width(), self.inner_height())

    def draw_border(self, canvas):
        """Draw own border onto a given canvas."""
        # top, bottom
        for i in range(self.size[0]):
            pos_up = self._translate(i, 0)
            pos_down = self._translate(i, self.size[1] - 1)
            if i != 0:
                canvas.set_border(pos_up, "left", self.style)
                canvas.set_border(pos_down, "left", self.style)
            if i != self.size[0] - 1:
                canvas.set_border(pos_up, "right", self.style)
                canvas.set_border(pos_down, "right", self.style)
            # clear inner borders
            if self.fill and i != 0 and i != self.size[0] - 1:
                canvas.set_border(pos_up, "down", 0)
                canvas.set_border(pos_down, "up", 0)

        # left, right
        for j in range(self.size[1]):
            pos_left = self._translate(0, j)
            pos_right = self._translate(self.size[0] - 1, j)
            if j != 0:
                canvas.set_border(pos_left, "up", self.style)
                canvas.set_border(pos_right, "up", self.style)
            if j != self.size[1] - 1:
                canvas.set_border(pos_left, "down", self.style)
                canvas.set_border(pos_right, "down", self.style)
            # clear inner borders
            if self.fill and j != 0 and j != self.size[1] - 1:
                canvas.set_border(pos_right, "left", 0)
                canvas.set_border(pos_left, "right", 0)

    def draw_fill(self, canvas, fill_ch=" "):
        for j in range(1, self.size[1] - 1):
            for i in range(1, self.size[0] - 1):
                pos = self._translate(i, j)
                canvas.set_content(pos, fill_ch)

    def draw_content(self, canvas):
        """Draw own content (text only) onto a given canvas."""
        pos = list(self.inner_position)
        for line in self.content:
            while len(line) > 0:
                canvas.print_line(pos, line[: self.inner_width])
                line = line[self.inner_width :]
                pos[1] += 1
                if pos[1] >= self.inner_height:
                    return

    def draw(self, canvas):
        """Draw the entire window onto a given canvas."""
        self.draw_border(canvas)
        if self.fill:
            self.draw_fill(canvas)
        self.draw_content(canvas)

    def print(self, text):
        """Set window content."""
        self.content.append(text)

    def clear(self):
        """Remove all content."""
        self.content = []


class Canvas:
    def __init__(self, windows=None):
        """Initialize an empty canvas.

        :param windows: An array of windows on the canvas
        """
        self.size = cursor.get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]
        self.is_rendering = False
        self.is_drawing = False

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
        self.size = cursor.get_terminal_size()
        self.data = [[0 for j in range(self.size[1])] for i in range(self.size[0])]
        for window in self.windows:
            window.draw(self)

    def render(self):
        """Render current canvas data into a buffer for printing."""
        while self.is_rendering:
            time.sleep(0.1)
        self.is_rendering = True

        self.buffer = ""
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                px = self.data[i][j]
                if isinstance(px, int):  # px is a border type
                    self.buffer += borders.get(px)
                else:  # px is a content character
                    self.buffer += px
            # end the line, unless it's the last line
            if j != self.size[1] - 1:
                self.buffer += "\n"

        self.is_rendering = False

    def print(self):
        """Print the current canvas buffer onto the terminal."""
        print(self.buffer, end="")
        sys.stdout.flush()

    def draw(self):
        while self.is_drawing:
            time.sleep(0.1)
        self.is_drawing = True
        self.redraw()
        self.render()
        print("\x1B7", end='') # save cursor position
        cursor.move(0, 0)
        self.print()
        print("\x1B8", end='', flush=True) # restore cursor position
        self.is_drawing = False

    def print_line(self, position, text):
        for ch in text:
            self.set_content(position, ch)
            position = (position[0] + 1, position[1])


import random

if __name__ == "__main__":
    i = 0
    j = 0
    background = Window(size=cursor.get_terminal_size(), style="double")
    static = Window(style="thin", size=(10, 10), position=(2, 1))
    cat = Window(style="thin", size=(1, 4), position=(6, 9))
    canvas = Canvas([background, static, cat])

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
        static.print(f"Welcome to Iteration {i},{j}")
        static.size = (10 + j, 10)
        cat.position = (6 + j, 9 + j)
        cat.size = (1 + i, 4)
        canvas.redraw()
        canvas.print(debug=False)
        cursor.move(0, 0)
        time.sleep(0.1)
