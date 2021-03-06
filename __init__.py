import os
import sys
import time

from . import borders, cursor

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
        return (self.inner_width, self.inner_height)

    def render_border(self, canvas):
        """Render own border onto a given canvas."""
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

    def render_fill(self, canvas, fill_ch=" "):
        for j in range(1, self.size[1] - 1):
            for i in range(1, self.size[0] - 1):
                pos = self._translate(i, j)
                canvas.set_content(pos, fill_ch)

    def render_content(self, canvas):
        """Render own content (text only) onto a given canvas."""
        pos = list(self.inner_position)
        for line in self.content:
            while len(line) > 0:
                canvas.print_line(pos, line[: self.inner_width])
                line = line[self.inner_width :]
                pos[1] += 1
                if pos[1] >= self.inner_height:
                    return

    def render(self, canvas):
        """Render the entire window onto a given canvas."""
        self.render_border(canvas)
        if self.fill:
            self.render_fill(canvas)
        self.render_content(canvas)

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
        self.is_printing = False
        self.is_refreshing = False
        self.debug_mode = False

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

    def get_window_bounds(self, window=None):
        if window is None:
            x, y = (0, 0)
            width, height = self.size
        else:
            x, y = window.position
            width, height = window.size
        return ((x, y), (width, height))

    def render(self, window=None):
        """Scrap canvas data and re-render."""
        self.size = cursor.get_terminal_size()
        (x, y), (width, height) = self.get_window_bounds(window)
        for j in range(y, height):
            for i in range(x, width):
                if isinstance(self.data, str):
                    self.data[i][j] = 0
        for w in self.windows if window is None else [window]:
            w.render(self)

    def print(self, window=None):
        """Print the current canvas onto the terminal."""
        while self.is_printing:
            time.sleep(0.1)
        self.is_printing = True

        start_pos, (width, height) = self.get_window_bounds(window)

        self.buffer = ""
        if not self.debug_mode:
            self.buffer = cursor.move(*start_pos, now=False)

        for j in range(start_pos[1], height):
            for i in range(start_pos[0], width):
                px = self.data[i][j]
                if isinstance(px, int):  # px is a border type
                    self.buffer += borders.get(px)
                else:  # px is a content character
                    self.buffer += px
            # move to a new line, unless it's the last line
            if j != self.size[1] - 1:
                self.buffer += cursor.move(start_pos[0], j + 1, now=False)  # "\n"
        print(self.buffer, end="")
        sys.stdout.flush()
        self.is_printing = False

    def refresh(self, window=None):
        """Render self and print to (0, 0)."""
        while self.is_refreshing:
            time.sleep(0.1)
        self.is_refreshing = True
        self.render(window)
        print("\x1B7", end="")  # save cursor position
        self.print(window)
        print("\x1B8", end="", flush=True)  # restore cursor position
        self.is_refreshing = False

    def print_line(self, position, text):
        for ch in text:
            self.set_content(position, ch)
            position = (position[0] + 1, position[1])


if __name__ == "__main__":
    import random

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
        canvas.render()
        canvas.print(debug=False)
        cursor.move(0, 0)
        time.sleep(0.1)
