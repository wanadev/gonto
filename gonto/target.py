import os
import time
from enum import StrEnum
from pathlib import Path
from collections.abc import Iterator
from collections.abc import Callable
from typing import Any

from .log import logger
from .download import http_get
from .diskimage import DiskImage
from .win32.virtdisk import ATTACH_VIRTUAL_DISK_FLAG


class SCRIPT_TYPE(StrEnum):
    """Types of scripts for a Gonto target."""

    BEFORE_SCRIPT = "before_script"
    SCRIPT = "script"
    AFTER_SCRIPT = "after_script"


class TargetDoesNotExist(ValueError):
    pass


class MissingImage(Exception):
    pass


class VolumeNotMounted(Exception):
    pass


class VolumeNotReady(Exception):
    pass


def requirement_to_image_path(requirement: dict):
    """Returns the image path from a Gonto requirement definition.

    :param requirement: A Gonto requirement definition.

    :returns: The image path.

    >>> requirement_to_image_path({"name": "foobar", "version": "1.2.3"})
    'foobar/foobar_v1.2.3_win64.vhd'
    >>> requirement_to_image_path(
    ...     {"name": "foobar", "version": "42", "platform": "multi", "format": "vhdx"}
    ... )
    'foobar/foobar_v42_multi.vhdx'
    """
    return "%s/%s_v%s_%s.%s" % (
        requirement["name"],
        requirement["name"],
        requirement["version"],
        requirement.get("platform", "win64"),
        requirement.get("format", "vhd"),
    )


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

        self._diskimages: list[DiskImage] = []

    def list_required_images(self) -> Iterator[dict[str, Any]]:
        """Lists target's required disk image.

        :returns: The required images.

            Image definition::

                {
                    "path": "foobar/foobar_v1.2.3_win64.vhd",
                    "name": "foobar",
                    "version": "1.2.3",
                    "platform": "win64",
                    "format": "vhd",
                    "mount_point": "",
                    "env": {},
                }
        """
        if "requires" not in self._target:
            return
        for requirement in self._target["requires"]:
            yield {
                "path": requirement_to_image_path(requirement),
                "name": requirement["name"],
                "version": requirement["version"],
                "platform": requirement.get("platform", "win64"),
                "format": requirement.get("format", "vhd"),
                "mount_point": requirement.get("mount_point", ""),
                "env": dict(requirement.get("env", {})),
            }

    def list_missing_images(self) -> Iterator[dict[str, Any]]:
        """List required images that are not available in the cache.

        :returns: the uncached images.

            Image definition::

                {
                    "path": "foobar/foobar_v1.2.3_win64.vhd",
                    "name": "foobar",
                    "version": "1.2.3",
                    "platform": "win64",
                    "format": "vhd",
                    "mount_point": "",
                    "env": {},
                }
        """
        for image in self.list_required_images():
            cached_image_path = Path(self._config["gonto"]["cache_dir"]) / image["path"]
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
        missing_images = list(self.list_missing_images())
        currentdl = 0
        for image in missing_images:
            currentdl += 1
            image_url = self._config["gonto"]["repository"]
            if image_url[-1] != "/":
                image_url += "/"
            image_url += image["path"]
            cached_image_path = Path(self._config["gonto"]["cache_dir"]) / image["path"]

            if callback:
                callback(currentdl, len(missing_images), image["path"], 0)

            http_get(
                image_url,
                cached_image_path,
                callback=lambda p: (
                    callback(currentdl, len(missing_images), image["path"], p)
                    if callback
                    else None
                ),
            )

    def mount_images(self) -> None:
        """Mount disk images required for the target.

        :raise MissingImage: If an image is missing from the cache.
        :raise VolumeNotMounted: If the assignation of the drive letter failed.
        :raise VolumeNotReady: The disk image was not attached in time or
            contains no volumes.
        """
        cache_dir = Path(self._config["gonto"]["cache_dir"])

        for requirement in self.list_required_images():
            mount_point = requirement["mount_point"]
            image_path = cache_dir / requirement["path"]

            if not image_path.is_file():
                raise MissingImage("Missing disk image: %s" % image_path)

            diskimage = DiskImage()
            diskimage.open(image_path)

            attach_flags = (
                ATTACH_VIRTUAL_DISK_FLAG.NO_DRIVE_LETTER
                if mount_point
                else ATTACH_VIRTUAL_DISK_FLAG.NONE
            )
            diskimage.attach(attach_flags)

            retries = 10
            attached = False
            while retries:
                if list(diskimage.list_volumes()):
                    attached = True
                    break
                retries -= 1
                time.sleep(0.1)

            if not attached:
                raise VolumeNotReady(
                    "Cannot attach disk image in time or disk image contains no volume: %s"
                    % requirement["path"]
                )

            self._diskimages.append(diskimage)

            if mount_point:
                diskimage.mount_volume(mount_point)

            retries = 10
            final_mount_point = None
            while retries:
                final_mount_point = diskimage.get_volume_mount_point()
                if final_mount_point:
                    break
                retries -= 1
                time.sleep(0.1)

            if not final_mount_point:
                raise VolumeNotMounted(
                    "The volume in the '%s' image was not mounted by the system in time."
                    % requirement["path"]
                )

            for name, value in requirement["env"].items():
                value = value.replace("{{mount_point}}", final_mount_point)
                self._env[name] = value

    def umount_images(self) -> None:
        """Umount all disk images of the target."""
        while self._diskimages:
            diskimage = self._diskimages.pop()
            try:
                diskimage.detach()
            except Exception as error:
                logger.error(
                    "An error occured when detaching a disk image: %s" % str(error)
                )

    def run_script(self, script_type: SCRIPT_TYPE) -> None:
        """Run a target script with proper environment.

        :param script_type: The type of script.
        """
        pass  # TODO

    def __repr__(self):
        return "<Gonto.Target %s>" % self._target_name
