"""Consolidate legacy dotenv files into one canonical root .env file."""

from __future__ import annotations

import argparse
import os
from collections import OrderedDict
from pathlib import Path
from tempfile import NamedTemporaryFile


def read_dotenv(path: Path) -> OrderedDict[str, str]:
    values: OrderedDict[str, str] = OrderedDict()
    if not path.is_file():
        return values

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and (key[0].isalpha() or key[0] == "_") and all(
            char.isalnum() or char == "_" for char in key
        ):
            values[key] = value
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".env"))
    parser.add_argument("--remove-legacy", action="store_true")
    args = parser.parse_args()

    merged: OrderedDict[str, str] = OrderedDict()
    for source in args.sources:
        merged.update(read_dotenv(source))

    merged["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    merged["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    content = "# Canonical runtime configuration. Do not commit this file.\n"
    content += "\n".join(f"{key}={value}" for key, value in merged.items()) + "\n"

    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=output.parent, delete=False, newline="\n"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, output)

    if args.remove_legacy:
        for source in args.sources:
            resolved = source.resolve()
            if resolved != output and resolved.is_file():
                resolved.unlink()

    print(f"Consolidated {len(merged)} variables into {args.output}")


if __name__ == "__main__":
    main()
