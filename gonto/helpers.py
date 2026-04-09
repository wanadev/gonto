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
) -> int:
    """Estimates "physical" disk usage of a folder and its files on a NTFS file
    system.

    :param folder: The input folder.
    :param cluster_size: The size of a cluster (minimal disk space that can be
        allocated to hold a file) on the file system (default: 4096 (worst case)).

        Typical values are:

        +------------------+--------------+
        | Volume Size      | Cluster Size |
        +==================+==============+
        | 7 M - 512 MB     | 512 B        |
        +------------------+--------------+
        | 513 MB - 1024 MB | 1 kB         |
        +------------------+--------------+
        | 1025 MB - 2GB    | 2 kB         |
        +------------------+--------------+
        | 2 GB - 2 TB      | 4 kB         |
        +------------------+--------------+

    :param mft_record_size: The size of a record in the master file table
        (generaly 1024 B so it is our default).

    :returns: The computed size in bytes.

    See: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc781134(v=ws.10)
    """
    _ESTIMATED_MFT_ATTRS_OVERHEAD = 300
    _INDEX_FILE_NAME_OVERHEAD = 82
    _INDEX_DOS_FILE_NAME_TOTAL_LEN_BYTES = (
        112  # DOS file name (overhead + 12 * 2 (12 WCHAR) + 6 (padding))
    )

    estimated_size = 0

    for root, dirs, files in os.walk(folder):

        # Compute current folder size
        folder_entry_size = _ESTIMATED_MFT_ATTRS_OVERHEAD
        folder_entry_size += len(Path(root).name) * 2

        folder_index_size = 0

        for item in dirs + files:
            child_entry_bytes = _INDEX_FILE_NAME_OVERHEAD + len(item) * 2
            child_entry_bytes = (child_entry_bytes + 7) // 8 * 8  # Padding
            child_entry_bytes += _INDEX_DOS_FILE_NAME_TOTAL_LEN_BYTES

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
            file_bytes += _INDEX_DOS_FILE_NAME_TOTAL_LEN_BYTES
            file_stat = (Path(root) / file).stat()

            if file_bytes + file_stat.st_size <= mft_record_size:
                estimated_size += mft_record_size
            else:
                estimated_size += mft_record_size
                estimated_size += (
                    (file_stat.st_size + cluster_size - 1)
                    // cluster_size
                    * cluster_size
                )

    return estimated_size
