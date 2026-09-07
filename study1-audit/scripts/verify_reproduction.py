"""Check one complete rerun for byte-exact aggregate/report reproducibility."""

from pathlib import Path
import hashlib
import subprocess
from sources import ROOT, write_json


def generated_hashes():
    files = [ROOT / "REPORT.md", ROOT / "evidence/source-inventory.json"]
    files += sorted((ROOT / "results").glob("*.json")) + sorted(
        (ROOT / "results").glob("*.csv")
    )
    return {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }


def main():
    before = generated_hashes()
    log = ROOT / "local/reproduction-check.log"
    with log.open("w") as f:
        subprocess.run(
            ["bash", str(ROOT / "reproduce.sh")],
            check=True,
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    after = generated_hashes()
    changed = sorted(
        p for p in before.keys() | after.keys() if before.get(p) != after.get(p)
    )
    write_json(
        ROOT / "evidence/reproduction-verification.json",
        {
            "generated_files_checked": len(after),
            "byte_exact": not changed,
            "changed_files": changed,
            "sha256": after,
        },
    )
    if changed:
        raise SystemExit("Regenerated files changed: " + ", ".join(changed))
    print(
        f"{len(after)} generated files reproduce byte-for-byte; full pipeline and tests passed."
    )


if __name__ == "__main__":
    main()
