import sys
import argparse

from . import APPLICATION_NAME, VERSION
from .log import logger
from .config import read_config, validate_config
from .target import Target


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

    # TODO run before_script (opt)

    print("Checking requirements...")
    images = list([img["path"] for img in target.list_required_images()])
    uncached_images = list([img["path"] for img in target.list_missing_images()])

    if images:
        for image in images:
            print(
                "* [%8s] %s"
                % (
                    "CACHED" if image not in uncached_images else "DOWNLOAD",
                    image,
                )
            )
    else:
        print("* No requirements.")

    if uncached_images:
        print("Downloading missing requirements...")

        def _progress_cb(
            currentdl: int, dlcount: int, image_name: str, progress: float
        ) -> None:
            if progress == 0:
                print(
                    "\r* Downloading '%s'... (%i/%i)"
                    % (
                        image_name,
                        currentdl,
                        dlcount,
                    )
                )
            sys.stdout.write(
                "\r  [%-20s] %.2f %%  "
                % (
                    "=" * int(progress * 20),
                    progress * 100,
                )
            )
            sys.stdout.flush()

        target.download_missing_images(_progress_cb)
        print("\r%s" % (" " * 40))

    if images:
        print("Mounting requirements...")
        pass  # TODO mount images

    # TODO run script

    if images:
        print("Unmounting requirements...")
        pass  # TODO umount images

    # TODO run after script (opt)


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
