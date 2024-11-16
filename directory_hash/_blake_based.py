from __future__ import annotations

from hashlib import blake2b
from pathlib import Path


def _check_symlink(base_path: Path, to_check: Path, /) -> tuple[str, Path]:
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
    name_component = blake2b(name.encode(), last_node=True, person=b"name")
    file_data = path.read_bytes()
    data_component = blake2b(file_data, last_node=False, person=b"data")
    file_node = blake2b(last_node=False, person=b"file")
    file_node.update(data_component.digest())
    file_node.update(name_component.digest())
    return file_node.digest()


def make_dir_node(rel_root: Path, path: Path, name: str | None = None) -> bytes:
    bname = (name if name is not None else path.name).encode()
    name_component = blake2b(bname, last_node=True, person=b"name")
    data_component = blake2b(last_node=False, person=b"children")

    digests: list[bytes] = []
    for child in path.iterdir():
        name, resolved = _check_symlink(rel_root, child)
        if resolved.is_dir():
            digests.append(make_dir_node(rel_root, resolved, name))
        else:
            digests.append(make_file_node(resolved, name))

    digests.sort()
    for digest in digests:
        data_component.update(digest)

    is_last = rel_root == path

    dir_node = blake2b(last_node=is_last, person=b"dir", digest_size=32 if is_last else 64)
    dir_node.update(data_component.digest())
    dir_node.update(name_component.digest())
    return dir_node.digest()


def hash_dir(dir_path: Path) -> str:
    if not dir_path.is_dir():
        msg = "This function is intended for use on paths"
        raise ValueError(msg)

    if dir_path.is_symlink():
        msg = "Top level paths must not be symlinks"
        raise ValueError(msg)

    return "b1:" + make_dir_node(dir_path, dir_path).hex()
