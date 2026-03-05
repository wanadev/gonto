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


def print_title(text: str) -> None:
    """Print a "title".

    :param text: The title to print.
    """
    title = CSI_STYLE.BOLD.value
    title += "\n"

    title += CSI_FGCOLOR.BLUE.value
    title += "=" * 80
    title += "\n"

    title += CSI_FGCOLOR.LIGHT_GRAY.value
    title += ":: "
    title += CSI_FGCOLOR.CYAN.value
    title += text
    title += "\n"

    title += CSI_FGCOLOR.BLUE.value
    title += "=" * 80

    title += CSI_STYLE.RESET.value

    print(title)
