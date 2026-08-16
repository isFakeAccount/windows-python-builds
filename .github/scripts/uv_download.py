#!/usr/bin/env python3
"""Script to download python using uv."""

from __future__ import annotations

import json
import re
import subprocess
from urllib.request import urlopen


def extract_python_version(build: str) -> str | None:
    """Extract the 'X.Y' minor version from a build string like
    'cpython-3.15.0a2-linux-x86_64-gnu' -> '3.15'."""
    match = re.search(r"-(\d+)\.(\d+)\.", build)
    if not match:
        return None
    major, minor = match.groups()
    return f"{major}.{minor}"


def list_available_versions() -> list[str]:
    """Gets the list of available python version using the ``uv python list`` command."""
    result = subprocess.run(
        ["uv", "python", "list", "--all-arches"],
        check=True,
        capture_output=True,
        text=True,
    )

    raw_lines = result.stdout.splitlines()
    return [raw_line.split()[0] for raw_line in raw_lines if raw_line.startswith("cpython")]


def get_python_versions_with_eol() -> set[str]:
    with urlopen("https://endoflife.date/api/v1/products/python") as response:
        eol_data = json.loads(response.read())
        releases = eol_data["result"]["releases"]
        return {release["name"] for release in releases if release["isMaintained"]}


def install_python_version(python_version: list[str]) -> None:
    """Installs the given python version using uv."""
    print(f"Installing {python_version}...")
    subprocess.run(["uv", "python", "install", "--no-bin", *python_version], check=True)


def main() -> None:
    """Entry point."""
    available_platform_builds = list_available_versions()
    supported_minor_versions = get_python_versions_with_eol()

    supported_platform_builds = []
    for build in available_platform_builds:
        python_version = extract_python_version(build)
        if python_version in supported_minor_versions:
            supported_platform_builds.append(build)

    install_python_version(supported_platform_builds)


if __name__ == "__main__":
    main()
