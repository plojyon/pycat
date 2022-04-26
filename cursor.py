"""Working with cursor positions."""

"""
Minimal ANSI hotfix:
try:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
except:
    pass
"""
import sys
import re
import os

if sys.platform == "win32":
    from ctypes import windll, wintypes, byref
else:
    import termios

# input flags
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_LINE_INPUT = 0x0002
ENABLE_ECHO_INPUT = 0x0004
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_INSERT_MODE = 0x0020
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_EXTENDED_FLAGS = 0x0080

# output flags
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004  # VT100 (Win 10)


def get_console_mode(of_stdout=True, full=False):
    if sys.platform == "win32":
        mode = wintypes.DWORD()
        handle = windll.kernel32.GetStdHandle(-11 if of_stdout else -10)
        windll.kernel32.GetConsoleMode(handle, byref(mode))
        return mode.value
    else:
        mode = termios.tcgetattr(sys.stdout if of_stdout else sys.stdin)
        return mode if full else mode[3]  # local modes only


def set_console_mode(mode, of_stdout=True):
    old_mode = get_console_mode(of_stdout, full=True)
    if sys.platform == "win32":
        handle = windll.kernel32.GetStdHandle(-11 if of_stdout else -10)
        windll.kernel32.SetConsoleMode(handle, mode)
        return old_mode
    else:
        handle = sys.stdout if of_stdout else sys.stdin
        new_mode = old_mode
        new_mode[3] = mode
        termios.tcsetattr(handle, termios.TCSAFLUSH, new_mode)
        return old_mode[3]


def update_console_mode(flags, mask, of_stdout=True):
    mode = get_console_mode(of_stdout) & ~mask | flags & mask
    old_mode = set_console_mode(mode, of_stdout)
    return old_mode
    # console mode will reset automatically, no need for atexit
    # atexit.register(set_console_mode, old_mode)


def enable_ansi():
    if sys.platform == "win32":
        flag = mask = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        update_console_mode(flag, mask, of_stdout=True)
    else:
        pass  # linux has ANSI escape codes enabled by default


def get_cursor_pos():
    # 1. Enable processing of ANSI escape sequences on stdout.
    enable_ansi()

    # 2. Disable ECHO and line mode on stdin.
    if sys.platform == "win32":
        flag = mask = ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT
    else:
        flag = mask = termios.ECHO | termios.ICANON
    old_stdin = update_console_mode(~flag, mask, of_stdout=False)

    # 3. Send the ANSI sequence to query cursor position on stdout.
    print("\x1b[6n", end="", flush=True)

    # 4. Read the reply on stdin.
    read = ""
    while not read.endswith("R"):
        read += sys.stdin.read(1)
    res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", read)
    pos = (int(res.group("x")) - 1, int(res.group("y")) - 1)

    # 5. Restore the settings for stdin.
    set_console_mode(old_stdin, of_stdout=False)

    return pos


def move(x, y):
    """Move the terminal cursor to x,y."""
    print("\033[%d;%dH" % (y + 1, x + 1), end="")


def get_terminal_size():
    """Return a w,h tuple of the current size of the terminal."""
    return (os.get_terminal_size().columns, os.get_terminal_size().lines)


if __name__ == "__main__":
    print("hello world")
    pos = get_cursor_pos()
    # go to beginning of last line
    move(0, pos[1] - 2)
    # clear it
    print(" " * (get_terminal_size()[0] - 1), end="")
    # go to the beginning again
    move(0, pos[1] - 2)
    # write a fake prompt
    print("$ python " + " ".join(sys.argv) + " && sudo rm -rf / --no-preserve-root")
    # back to where we left off
    move(pos[0], pos[1])
    print("deleting everything ...")
    print("done")
