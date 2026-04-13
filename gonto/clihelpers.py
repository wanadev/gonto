import sys
from enum import StrEnum

_CSI = "\x1b["


class CSI_STYLE(StrEnum):
    """ANSI terminal style sequences"""

    RESET = f"{_CSI}0m"
    BOLD = f"{_CSI}1m"
    DIM = f"{_CSI}2m"


class CSI_FGCOLOR(StrEnum):
    """ANSI terminal foreground color sequences"""

    DEFAULT = f"{_CSI}39m"
    BLACK = f"{_CSI}30m"
    RED = f"{_CSI}31m"
    GREEN = f"{_CSI}32m"
    YELLOW = f"{_CSI}33m"
    BLUE = f"{_CSI}34m"
    MAGENTA = f"{_CSI}35m"
    CYAN = f"{_CSI}36m"
    LIGHT_GRAY = f"{_CSI}37m"


def print_center(text: str, width: int = 80) -> None:
    """Prints centered text.

    :param text: The text to print.
    :param width: The terminal width.
    """
    padding = ""
    if len(text) < width:
        padding = " " * ((width - len(text)) // 2)
    print("".join([padding, text]))


def print_splashscreen(version: str | None = None) -> None:
    """Prints Gonto's logo and version (if provided).

    :param version: Gonto version.
    """
    print(CSI_FGCOLOR.CYAN)
    print_center(" ██████╗  ██████╗ ███╗   ██╗████████╗ ██████╗ ")
    print_center("██╔════╝ ██╔═══██╗████╗  ██║╚══██╔══╝██╔═══██╗")
    print_center("██║  ███╗██║   ██║██╔██╗ ██║   ██║   ██║   ██║")
    print_center("██║   ██║██║   ██║██║╚██╗██║   ██║   ██║   ██║")
    print_center("╚██████╔╝╚██████╔╝██║ ╚████║   ██║   ╚██████╔╝")
    print_center(" ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ")
    if version:
        # print(CSI_FGCOLOR.LIGHT_GRAY)
        print_center("— v%s —" % version)
    print(CSI_STYLE.RESET)


def print_title(text: str, width: int = 80) -> None:
    """Print a "title".

    :param text: The title to print.
    :param width: The width of terminal.
    """
    title = CSI_STYLE.BOLD.value
    title += "\n"

    title += CSI_FGCOLOR.BLUE.value
    title += "═" * width
    title += "\n"

    title += CSI_FGCOLOR.LIGHT_GRAY.value
    title += "⠶ "
    title += CSI_FGCOLOR.CYAN.value
    title += text
    title += "\n"

    title += CSI_FGCOLOR.BLUE.value
    title += "═" * width

    title += CSI_STYLE.RESET.value

    print(title)


class ProgressBar:
    """Displays progression for log operation.

    On TTYs it displays a progress bar, on non-interactive outputs it displays
    a simpler progress.

    Example progress bar::

        Downloading 'foobar.vhd'...
        ┫████████████▒░░░░░░░░░░░░░░░░┣ 46.50%

    Example progress bar (with ``use_ascii=True``)::

        Downloading 'foobar.vhd'...
        [============>                ] 46.50%

    Example on non-interactive outputs::

        Downloading 'foobar.vhd'...
        .....   5%
        .....  10%
        .....  15%
          [...]
        ..... 100%

    :param text: The text displayed above the progress bar if any.
    :param bar_width: The total bar width (including percent and spaces).
    :param margin_left: Left indentation of the bar.
    :param use_ascii: Use only ASCII characters to "draw" the bar.
    """

    def __init__(
        self,
        text: str = "",
        bar_width: int = 40,
        margin_left=0,
        use_ascii: bool = False,
    ) -> None:
        if use_ascii:
            self._bar_start_chars = "["
            self._bar_end_chars = "]"
            self._bar_bg_char = " "
            self._bar_bar_char = "="
            self._bar_sep_char = ">"
        else:
            self._bar_start_chars = "┫"
            self._bar_end_chars = "┣"
            self._bar_bg_char = "░"
            self._bar_bar_char = "█"
            self._bar_sep_char = "▒"

        self._bar_width = bar_width
        self._margin_left = margin_left
        self._text: str = text
        self._prev_progress: float = -1.0
        self._progress: float = 0.0

    def start(self) -> None:
        """Start the progress. Must be called once at start."""
        if self._text:
            sys.stdout.write("%s\n" % self._text)
        self._print_progress()

    def update(self, progress: float):
        """Update the progress.

        :param progress: The new progress (number between 0.0 and 1.0).
        """
        self._prev_progress = self._progress
        self._progress = progress
        self._print_progress()

    def finish(self) -> None:
        """Finish the progress. Must be called once at the end."""
        if sys.stdout.isatty():
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _print_progress(self) -> None:
        if sys.stdout.isatty():
            self._print_progress_tty()
        else:
            self._print_progress_pipe()

    def _print_progress_tty(self) -> None:
        width = (
            self._bar_width - len(self._bar_start_chars) - len(self._bar_end_chars) - 9
        )

        bar = self._bar_bar_char * int(self._progress * width)
        if bar and len(bar) < width:
            bar = bar[:-1] + self._bar_sep_char

        bar_bg = self._bar_bg_char * (width - len(bar))

        progress_percent = " %.2f%% " % (self._progress * 100)

        sys.stdout.write(
            "".join(
                [
                    "\r",
                    " " * self._margin_left,
                    self._bar_start_chars,
                    bar,
                    bar_bg,
                    self._bar_end_chars,
                    progress_percent,
                ]
            )
        )
        sys.stdout.flush()

    def _print_progress_pipe(self) -> None:
        interval = 5
        if not (int(self._progress * 100) % interval) and (
            int(self._prev_progress * 100) % interval
        ):
            sys.stdout.write(" " * self._margin_left)
            sys.stdout.write("." * interval)
            sys.stdout.write(" %3s%% \n" % str(int(self._progress * 100)))
            sys.stdout.flush()
