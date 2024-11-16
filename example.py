from __future__ import annotations

import time

from directory_hash._blake_based import hash_dir as blake
from directory_hash._go_dirhash_deriv import hash_dir as go
from directory_hash._sha256_based import hash_dir as sha256
from pathlib import Path


def runner(path: Path) -> None:

    results: list[tuple[float, str, str]] = []
    for name, f in (("go (h1)", go), ("sha256_based (s1)", sha256), ("blake2 based (b1)", blake)):

        s1 = time.perf_counter()
        h = f(path)
        s2 = time.perf_counter()
        results.append((s2- s1, h, name))

    for elapsed, hash, name in results:
        print(f"Ran {name} in {elapsed}")
        print(hash)


if __name__ == "__main__":
    d = path = Path(__file__).with_name("directory_hash")
    runner(d)
