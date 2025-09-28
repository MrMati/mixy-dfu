#!/usr/bin/env python3

import shutil

from pathlib import Path

# These variables are injected by shiv.bootstrap
site_packages: Path
env: "shiv.bootstrap.environment.Environment"

# Get a handle of the current PYZ's site_packages directory
current = site_packages.parent

# The parent directory of the site_packages directory is our shiv cache
cache_path = current.parent

name, build_id = current.name.split('_')

if __name__ == "__main__":
    for path in cache_path.iterdir():
        pname = path.name.rstrip("_lock")
        if pname.endswith(build_id):
          continue
        if pname.startswith(f"{name}_"):
            shutil.rmtree(path)
        elif pname.startswith(f".{name}_"):
          path.unlink()