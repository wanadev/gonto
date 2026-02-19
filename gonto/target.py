import os
from enum import StrEnum
from pathlib import Path
from collections.abc import Iterator
from collections.abc import Callable


class SCRIPT_TYPE(StrEnum):
    """Types of scripts for a Gonto target."""

    BEFORE_SCRIPT = "before_script"
    SCRIPT = "script"
    AFTER_SCRIPT = "after_script"


class TargetDoesNotExist(ValueError):
    pass


class MissingImage(Exception):
    pass


class Target:
    """Actions that can be run on a Gonto target.

    :param target_name: The requested target name.
    :param config: The final Gonto configuration (containing all targets and
        main settings).

    :raises TargetDoesNotExist: if the requested target does not exist in the
        given config.
    """

    def __init__(self, target_name: str, config: dict):
        if target_name not in config["targets"]:
            raise TargetDoesNotExist("The '%s' target does not exist." % target_name)

        self._target_name = target_name
        self._config = config
        self._target = self._config["targets"][target_name]

        self._env = dict(os.environ)
        self._env.update(self._target.get("env", {}))

    def list_required_images(self) -> Iterator[str]:
        """Lists target's required disk image.

        :returns: The required images.
        """
        if "requires" not in self._target:
            return
        for requirement in self._target["requires"]:
            yield "%s/%s_v%s_%s.%s" % (
                requirement["name"],
                requirement["name"],
                requirement["version"],
                requirement.get("platform", "win64"),
                requirement.get("format", "vhd"),
            )

    def list_missing_images(self) -> Iterator[str]:
        """List required images that are not available in the cache.

        :returns: the uncached images.
        """
        for image in self.list_required_images():
            cached_image_path = Path(self._config["gonto"]["cache_dir"]) / image
            if not cached_image_path.is_file():
                yield image

    def download_missing_images(
        self, callback: Callable[[int, int, str, float], None] | None = None
    ) -> None:
        """Download missing disk images from the repository.

        :param callback: A callable called to track the progress of the
            download (default: ``None``).

            Callback definition::

                def callback(currentdl: int, dlcount: int, image_name: str, progress: float) -> None:
                    pass
        """
        pass  # TODO

    def mount_images(self) -> None:
        """Mount disk images required for the target.

        :raise MissingImage: If an image is missing from the cache.
        """
        # XXX Resolve/add image env vars to self._env
        pass  # TODO

    def umount_images(self) -> None:
        """Umount all disk images of the target."""
        pass  # TODO

    def run_script(self, script_type: SCRIPT_TYPE) -> None:
        """Run a target script with proper environment.

        :param script_type: The type of script.
        """
        pass  # TODO

    def __repr__(self):
        return "<Gonto.Target %s>" % self._target_name
