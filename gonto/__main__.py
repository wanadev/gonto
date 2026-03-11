import sys
import argparse
import subprocess

from . import APPLICATION_NAME, VERSION
from .log import logger
from .config import read_config, validate_config
from .target import Target, SCRIPT_TYPE
from .clihelpers import print_title, print_splashscreen
from .clihelpers import CSI_FGCOLOR, CSI_STYLE
from .clihelpers import ProgressBar

# Used for later to display progress
# Not pretty but we have to keep a global ref...
_progressbar: ProgressBar


def generate_run_subcommand_cli(subparsers: argparse._SubParsersAction) -> None:
    """Generates the CLI for the "run" subcommand.

    :param subparsers: The subparsers action instance as given by
        ``argparse.ArgumentParser.add_subparsers()``.
    """
    parser = subparsers.add_parser(
        "run",
        help="runs the requested target",
    )

    parser.add_argument(
        "target",
        help="the target to run",
        type=str,
    )


def generate_list_subcommand_cli(subparsers: argparse._SubParsersAction) -> None:
    """Generates the CLI for the "list" subcommand.

    :param subparsers: The subparsers action instance as given by
        ``argparse.ArgumentParser.add_subparsers()``.
    """
    subparsers.add_parser(
        "list",
        help="lists available targets",
    )


def generate_cli() -> argparse.ArgumentParser:
    """Generates the CLI.

    :returns: The argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=" ".join([APPLICATION_NAME, VERSION]),
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
    )

    generate_run_subcommand_cli(subparsers)
    generate_list_subcommand_cli(subparsers)

    return parser


def subcommand_run(config: dict, args: argparse.Namespace) -> None:
    """Run the "run" subcommand.

    Actions:

    * Run ``before_script`` commands,
    * Check if required disk images are available in the cache,
    * Download missing disk images from configured repository,
    * Mount all disk images in order,
    * Run ``script`` commands,
    * Unmount disk images,
    * Run ``after_script`` commands.

    :param config: The final configuration.
    :param args: The args parsed by ``argparse.ArgumentParser.parse_args()``.
    """

    if args.target not in config["targets"]:
        logger.error("Target '%s' does not exist." % args.target)
        sys.exit(1)

    target = Target(args.target, config)
    script_error = False

    # Before Script

    if target.has_script(SCRIPT_TYPE.BEFORE_SCRIPT):
        print_title("Before Script")
        try:
            target.run_script(SCRIPT_TYPE.BEFORE_SCRIPT)
        except subprocess.CalledProcessError as error:
            logger.error("Before script terminated with an error: %s" % str(error))
            script_error = True

    if script_error:
        sys.exit(1)

    # Requirement Check

    print_title("Requirements Check")
    images = [img["path"] for img in target.list_required_images()]
    uncached_images = [img["path"] for img in target.list_missing_images()]

    if images:
        for image in images:
            print(
                "* [%s%8s%s] %s"
                % (
                    (
                        CSI_FGCOLOR.GREEN
                        if image not in uncached_images
                        else CSI_FGCOLOR.YELLOW
                    ),
                    "CACHED" if image not in uncached_images else "DOWNLOAD",
                    CSI_STYLE.RESET,
                    image,
                )
            )
    else:
        print("* No requirements.")

    # Download

    if uncached_images:
        print_title("Missing Requirement Download")

        def _progress_cb(
            currentdl: int, dlcount: int, image_name: str, progress: float
        ) -> None:
            global _progressbar
            if progress == 0.0:
                _progressbar = ProgressBar(
                    text="* Downloading '%s'... (%i/%i)"
                    % (
                        image_name,
                        currentdl,
                        dlcount,
                    ),
                    margin_left=2,
                )
                _progressbar.start()
            elif int(progress) == 1:
                _progressbar.update(progress)
                _progressbar.finish()
            else:
                _progressbar.update(progress)

        target.download_missing_images(_progress_cb)
        print("\r%s" % (" " * 40))

    # Mount

    if images:
        print_title("Disk Image Mount")
        target.mount_images()

    # Main Script

    print_title("Main Script")
    try:
        target.run_script(SCRIPT_TYPE.SCRIPT)
    except subprocess.CalledProcessError as error:
        logger.error("Script terminated with an error: %s" % str(error))
        script_error = True

    # Unmount

    if images:
        print_title("Disk Image Unmount")
        target.umount_images()

    # After Script

    if target.has_script(SCRIPT_TYPE.AFTER_SCRIPT) and not script_error:
        print_title("After Script")
        try:
            target.run_script(SCRIPT_TYPE.AFTER_SCRIPT)
        except subprocess.CalledProcessError as error:
            logger.error("After script terminated with an error: %s" % str(error))
            script_error = True

    if script_error:
        sys.exit(1)


def subcommand_list(config: dict, args: argparse.Namespace) -> None:
    """Run the "list" subcommand.

    :param config: The final configuration.
    :param args: The args parsed by ``argparse.ArgumentParser.parse_args()``.
    """
    for target in config["targets"]:
        print(target)


def main(args=sys.argv[1:]):
    parser = generate_cli()
    parsed_args = parser.parse_args(args)

    print_splashscreen(version=VERSION)

    config = read_config()
    logger.debug("Final config: %s" % str(config))
    is_valid, error_message = validate_config(config)
    if not is_valid:
        logger.error("Configuration error: %s" % error_message)
        sys.exit(1)

    if parsed_args.subcommand == "run":
        subcommand_run(config, parsed_args)
    elif parsed_args.subcommand == "list":
        subcommand_list(config, parsed_args)


if __name__ == "__main__":
    main()
