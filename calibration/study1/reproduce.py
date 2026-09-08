"""Reproduce frozen aggregate evidence in a temporary directory, using local data.

Usage: RJT_ARCHIVE=/path/to/author.zip uv run --no-sync python calibration/study1/reproduce.py
No network access, source-code execution from the archive, or raw-data export.
"""

import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from taxuncertainty.analysis.study1_evidence import verify_bundle

root = Path(__file__).resolve().parent
manifest = verify_bundle(root)
archive = Path(os.environ["RJT_ARCHIVE"]).resolve(strict=True)
env = {**os.environ, "RJT_ARCHIVE": str(archive)}
with TemporaryDirectory(prefix="study1-aggregate-reproduction-") as directory:
    work = Path(directory)
    for name in manifest["files"]:
        if not name.startswith("results/"):
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
    (work / "results").mkdir()
    subprocess.run([sys.executable, "audit.py"], cwd=work / "scripts", env=env, check=True)
    subprocess.run(
        [sys.executable, "-c", "from sensitivity import affine_model_checks, covariance_sensitivity; affine_model_checks(); covariance_sensitivity()"],
        cwd=work / "scripts", env=env, check=True,
    )
    subprocess.run([sys.executable, "verify_native_arithmetic.py"], cwd=work / "scripts", env=env, check=True)
    compared = []
    for name in manifest["files"]:
        if name.startswith("results/"):
            if (root / name).read_bytes() != (work / name).read_bytes():
                raise ValueError(f"Native aggregate reproduction differs: {name}")
            compared.append(name)
    print(f"All {len(compared)} frozen aggregate files reproduced byte-for-byte.")
