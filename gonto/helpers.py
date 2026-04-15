import os
from pathlib import Path
from typing import Any


def dict_merge(dest: dict[Any, Any], other: dict[Any, Any]) -> None:
    """Deep merge of ``"other"`` dict in ``"dest"`` dict.

    :param dest: Destination dict.
    :param other: Other dict to merge into ``dest``.

    >>> d1 = {"a": 1, "b": {"c": 3}, "d": 4, "f": 5}
    >>> d2 = {"b": {"e": 10}, "d": 14, "f": {"f": 15}}
    >>> dict_merge(d1, d2)
    >>> d1
    {'a': 1, 'b': {'c': 3, 'e': 10}, 'd': 14, 'f': {'f': 15}}
    >>> d2
    {'b': {'e': 10}, 'd': 14, 'f': {'f': 15}}
    """
    for key, value in other.items():
        if isinstance(value, dict):
            if key not in dest or not isinstance(dest[key], dict):
                dest[key] = {}
            dict_merge(dest[key], value)
        else:
            dest[key] = value


def ntfs_disk_use(
    folder: Path | str,
    cluster_size: int = 4096,
    mft_record_size: int = 1024,
) -> tuple[int, int, int, int]:
    """Estimates "physical" disk usage of a folder and its files on a NTFS file
    system.

    :param folder: The input folder.
    :param cluster_size: The size of a cluster (minimal disk space that can be
        allocated to hold a file) on the file system (default: 4096).
    :param mft_record_size: The size of a record in the master file table
        (generaly 1024 B so it is our default).

    :returns: A tuple of 4 integers containing:

        * The estimated file and folder size on an NTFS file system
        * The raw size of the files
        * The folder count
        * The file count

    See: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc781134(v=ws.10)
    """
    _ESTIMATED_MFT_ATTRS_OVERHEAD = 400
    _INDEX_FILE_NAME_OVERHEAD = 82
    _INDEX_DOS_8DOT3_FILE_NAME_MAX_LEN = 112  # overhead + 12 * 2 (12 WCHAR) + padding

    file_count = 0
    folder_count = 0
    raw_size = 0
    estimated_size = 0

    for root, dirs, files in os.walk(folder):

        file_count += len(files)
        folder_count += len(dirs)

        # Compute current folder size
        folder_entry_size = _ESTIMATED_MFT_ATTRS_OVERHEAD
        folder_entry_size += len(Path(root).name) * 2

        folder_index_size = 0

        for item in dirs + files:
            child_entry_bytes = _INDEX_FILE_NAME_OVERHEAD + len(item) * 2
            child_entry_bytes = (child_entry_bytes + 7) // 8 * 8  # Padding
            child_entry_bytes += _INDEX_DOS_8DOT3_FILE_NAME_MAX_LEN

            folder_index_size += child_entry_bytes

        if folder_entry_size + folder_index_size <= mft_record_size:
            estimated_size += mft_record_size
        else:
            estimated_size += mft_record_size
            estimated_size += (
                (folder_index_size + cluster_size - 1) // cluster_size * cluster_size
            )

        # Compute each file sizes
        for file in files:
            file_bytes = _ESTIMATED_MFT_ATTRS_OVERHEAD
            file_bytes += len(file) * 2
            file_stat = (Path(root) / file).stat()

            if file_bytes + file_stat.st_size <= mft_record_size:
                raw_size += file_stat.st_size
                estimated_size += mft_record_size
            else:
                raw_size += file_stat.st_size
                estimated_size += mft_record_size
                estimated_size += (
                    (file_stat.st_size + cluster_size - 1)
                    // cluster_size
                    * cluster_size
                )

    return estimated_size, raw_size, folder_count, file_count
