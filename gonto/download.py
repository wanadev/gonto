import urllib.request
from pathlib import Path
from collections.abc import Callable


def http_get(
    url: str,
    destination: str | Path,
    allow_overwrite: bool = False,
    callback: Callable[[float], None] | None = None,
) -> None:
    """Download a file using HTTP protocol.

    .. NOTE::

       The progress passed to callback function may stay to ``0`` during all
       the download. This occurs if the HTTP server does not provide the
       ``Content-Length``.

    :param url: The URL of the file to download.
    :param destination: The path of the destination file.
    :param allow_overwrite: Allow to overwrite existing files (default:
        ``False``).
    :param callback: A callable to track download progress (default: ``None``).

        Callback definition::

            def callback(progress: float) -> None:
                pass

    :raises FileExistsError: If the output file already exists and
        ``allow_overwrite`` is False.
    :raise IOError: If the download was incomplete or if server sent more bytes
        than expected.
    """
    output_file_path = Path(destination)
    output_file_path_partial = output_file_path.with_suffix(".part")

    if output_file_path.is_file() and not allow_overwrite:
        raise FileExistsError(
            "The output file already exists: %s" % str(output_file_path)
        )

    if not output_file_path_partial.parent.is_dir():
        output_file_path_partial.parent.mkdir(parents=True)

    response = urllib.request.urlopen(url)
    downloaded_length = 0
    total_length = int(response.getheader("Content-Length") or 0)

    with open(output_file_path_partial, "wb") as output_file:
        while chunk := response.read(1024 * 1024):
            output_file.write(chunk)
            downloaded_length += len(chunk)
            if total_length and downloaded_length > total_length:
                raise IOError(
                    "Downloaded more data than expected (%i/%i Bytes)"
                    % (
                        downloaded_length,
                        total_length,
                    )
                )
            progress = downloaded_length / total_length if total_length else 0
            if callback:
                callback(progress)

    if total_length and downloaded_length != total_length:
        raise IOError(
            "Incomplete download (%i/%i Bytes)"
            % (
                downloaded_length,
                total_length,
            )
        )

    if output_file_path.is_file():
        output_file_path.unlink()

    output_file_path_partial.rename(output_file_path)
