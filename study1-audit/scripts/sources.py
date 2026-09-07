"""Read-only, checksum-pinned access to the retained author archive."""

from __future__ import annotations
import hashlib
import io
import os
import json
from pathlib import Path
import warnings
import zipfile
import pandas as pd

ARCHIVE_SHA256 = "c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15"
ARCHIVE_URL = "https://www.dropbox.com/s/2q47bj8arbcgr3i/Schmeduling%20Replication%20Code.zip?dl=1"
DEFAULT_ARCHIVE = Path(
    os.environ.get(
        "RJT_ARCHIVE",
        "/Users/maxghenis/capacity-sprint-20260907/disutility/source-evidence/Schmeduling_Replication_Code.zip",
    )
)
ROOT = Path(__file__).resolve().parents[1]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )


def read_archive(path=DEFAULT_ARCHIVE):
    raw = Path(path).read_bytes()
    if digest(raw) != ARCHIVE_SHA256:
        raise ValueError(
            "Archive checksum mismatch; source bytes must match pinned archive"
        )
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return {
            n: z.read(n)
            for n in z.namelist()
            if n.startswith("Replication Code/") and not n.endswith("/")
        }


def frame(members, name, columns=None):
    # Numeric codes preserve native flags. The native financial-literacy label
    # has a UTF-8 defect: pandas falls back to Latin-1; no text outcome is parsed.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = pd.read_stata(
            io.BytesIO(members["Replication Code/Study 1/" + name + ".dta"]),
            columns=columns,
            convert_categoricals=False,
        )
    for w in caught:
        if not issubclass(w.category, UnicodeWarning):
            warnings.warn(w.message, w.category)
    return result


def inventory(path=DEFAULT_ARCHIVE):
    members = read_archive(path)
    metadata = {}
    for name in ("RJT_study_1_data", "individualestimates"):
        raw = members["Replication Code/Study 1/" + name + ".dta"]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnicodeWarning)
            with pd.io.stata.StataReader(
                io.BytesIO(raw), convert_categoricals=False
            ) as reader:
                labels = reader.variable_labels()
                d = reader.read()
        metadata[name] = {
            "rows": len(d),
            "respondents": int(d.mid.nunique()),
            "qnum_counts": {
                str(k): int(v) for k, v in d.qnum.value_counts().sort_index().items()
            },
            "variables": {
                c: {
                    "label": labels[c],
                    "dtype": str(d[c].dtype),
                    "missing": int(d[c].isna().sum()),
                }
                for c in d
            },
        }
    manifest = {
        "citation": "Alex Rees-Jones and Dmitry Taubinsky (2020), Measuring “Schmeduling”, Review of Economic Studies 87(5), 2399–2438; doi:10.1093/restud/rdz045",
        "archive_url": ARCHIVE_URL,
        "archive_sha256": ARCHIVE_SHA256,
        "members": {
            n: {"sha256": digest(b), "bytes": len(b)}
            for n, b in sorted(members.items())
        },
        "encoding_note": "Native unused financial-literacy label triggers pandas Latin-1 fallback. Analyses use numeric fields; original string forecasts are not interpreted as raw survey exports.",
        "raw_data_policy": "Read archive in memory. No raw microdata copied, modified, committed or published.",
        "metadata": metadata,
    }
    write_json(ROOT / "evidence/source-inventory.json", manifest)
    local = ROOT / "local/native"
    local.mkdir(parents=True, exist_ok=True)
    for n, b in members.items():
        if n.endswith((".do", ".txt")):
            (local / (Path(n).name + ".numbered.txt")).write_text(
                "\n".join(
                    f"{i}: {line}" for i, line in enumerate(b.decode().splitlines(), 1)
                )
                + "\n"
            )
    return members


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    args = p.parse_args()
    inventory(args.archive)
