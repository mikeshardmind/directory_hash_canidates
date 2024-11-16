from __future__ import annotations

from hashlib import sha256
from pathlib import Path


def _check_symlink(base_path: Path, to_check: Path, /) -> tuple[str, Path]:

    if "\n" in to_check.name:
        msg = "New lines not allowed in file names"
        raise ValueError(msg) from None

    if to_check.is_symlink():
        resolved = to_check.resolve(strict=True)
        try:
            resolved.relative_to(base_path)
        except ValueError as exc:
            msg = "Dangerous symlink detected"
            raise ValueError(msg) from exc
        return to_check.name, resolved
    return to_check.name, to_check


def make_file_node(path: Path, name: str | None = None) -> bytes:
    name = name if name is not None else path.name
    file_data = path.read_bytes()
    return ("file %s %s" % (name, sha256(file_data).hexdigest())).encode()


def make_dir_node(rel_root: Path, path: Path, name: str | None = None) -> bytes:
    if rel_root != path:
        bname = (name if name is not None else path.name)
        prefix = f"dir {bname} "
    else:
        prefix = "s1:"

    digests: list[bytes] = []
    for child in path.iterdir():
        name, resolved = _check_symlink(rel_root, child)
        if resolved.is_dir():
            digests.append(make_dir_node(rel_root, resolved, name))
        else:
            digests.append(make_file_node(resolved, name))

    digests.sort()
    return (prefix + sha256(b"\n".join(digests)).hexdigest()).encode()


def hash_dir(dir_path: Path) -> str:
    if not dir_path.is_dir():
        msg = "This function is intended for use on paths"
        raise ValueError(msg)

    if dir_path.is_symlink():
        msg = "Top level paths must not be symlinks"
        raise ValueError(msg)

    return make_dir_node(dir_path, dir_path).decode("utf-8")
