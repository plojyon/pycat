from . import Window


class ConsoleWindow(Window):
    """Window with upwards scrolling text."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reversed = kwargs.pop("reversed", True)
        self.content = []

    def render_content(self, canvas):
        """Render own content (text only) onto a given canvas."""
        inner_x, inner_y = self.inner_position

        if self.reversed:
            position = [inner_x, inner_y + self.inner_height - 1]
        else:
            position = [inner_x, inner_y]

        iterator = reversed(self.content) if self.reversed else self.content
        for line in iterator:
            parts = []
            while len(line) > 0:
                parts.append(line[: self.inner_width])
                line = line[self.inner_width :]

            for part in reversed(parts):
                canvas.print_line(position, part)
                position[1] += -1 if self.reversed else 1

                if position[1] < inner_y:  # reached top
                    return


class InputWindow(Window):
    """A window with an input prompt."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListWindow(Window):
    """Display an alphabetically ordered list."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render_content(self, canvas):
        """Render own content (text only) onto a given canvas."""
        self.content.sort()
        super().render_content(canvas)
