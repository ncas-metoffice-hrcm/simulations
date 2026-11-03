#!/usr/bin/env python3
"""Create a blank HRCM simulation metadata template named simulation_id.yml."""

from __future__ import annotations

import sys
from pathlib import Path


OUTPUT_FILE = Path("simulation_id.yml")

COMMENT = (
    '# Rename this .yml file to your simulation ID (e.g., "UM/suite_ID.yml").\n'
    '# Including "UM/" moves this file to the UM/ directory.\n'
    '# Populate the fields below with the simulation details.\n'
    "# To leave a field blank, use ''.\n"
    '# Finally, remove these comments, and commit your changes.'
)

FIELDS = (
    "run_ID",
    "model_version",
    "documentation",
    "resolution",
    "ssts",
    "platform",
    "num_years",
    "years",
    "notes",
    "cape_timescale_hr",
    "simulation_author",
    "data_owner",
    "data_location",
    "known_data_issues",
    "pis",
    "funding_agency",
)


def main() -> int:
    if OUTPUT_FILE.exists():
        print(
            f"Error: {OUTPUT_FILE} already exists; refusing to overwrite it.",
            file=sys.stderr,
        )
        return 1

    content = COMMENT + "\n" + "".join(f"{field}: ''\n" for field in FIELDS)
    OUTPUT_FILE.write_text(content, encoding="utf-8", newline="\n")
    print(f"Created {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
