from __future__ import annotations

from hashlib import sha256
from pathlib import Path


def _check_symlink(base_path: Path, to_check: Path, /) -> Path:
    if to_check.is_symlink():
        resolved = to_check.resolve(strict=True)
        try:
            resolved.relative_to(base_path)
        except ValueError as exc:
            msg = "Dangerous symlink detected"
            raise ValueError(msg) from exc
        return resolved
    return to_check


def _portable_path_repr(base_path: Path, dir_path: Path, /) -> str:
    """don't rely on os.pathsep"""
    base = base_path.as_posix()
    d = dir_path.as_posix()
    port = "." + d.removeprefix(base)
    if "\n" in port:
        msg = "New lines not allowed in file names"
        raise ValueError(msg) from None
    return port


def hash_dir(dir_path: Path, /) -> str:
    if not dir_path.is_dir():
        msg = "This function is intended for use on paths"
        raise ValueError(msg)

    if dir_path.is_symlink():
        msg = "Top level paths must not be symlinks"
        raise ValueError(msg)

    rel_root = dir_path.resolve(strict=True)

    file_hashes: list[str] = []

    walk_gen = dir_path.walk(top_down=False, follow_symlinks=False)
    for root, _dirs, files in walk_gen:
        for name in files:
            fp = root / name
            resolved = _check_symlink(dir_path, fp)
            port_path = _portable_path_repr(rel_root, resolved)
            digest = sha256(resolved.read_bytes()).hexdigest()
            file_hashes.append(f"h1:{port_path} {digest}")

    file_hashes.sort()

    data = "\n".join(file_hashes).encode()
    return f"h1:{sha256(data).hexdigest()}"
