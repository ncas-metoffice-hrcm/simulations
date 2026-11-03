from pathlib import Path
import re
import yaml


SOURCE = Path("simulations.yml")
OUTPUT_DIR = Path("simulations")
OUTPUT_DIR.mkdir(exist_ok=True)


# Explicit exception supplied for this abbreviated group.
SPECIAL_EXPANSIONS = {
    "xgjbh,i,j,xgtxa": [
        "xgjbh",
        "xgjbi",
        "xgjbhj",
        "xgtxa",
    ],
}


# Accepted complete ID formats.
VALID_ID = re.compile(
    r"(?:[a-z]{5}|u-[a-z]{2}\d{3}|mi-[a-z]{2}\d{3})",
    re.IGNORECASE,
)

# Older IDs such as ab-377 are converted to u-ab377.
LEGACY_ID = re.compile(r"([a-z]{2})-(\d{3})", re.IGNORECASE)

# Square-bracket alternatives, e.g. amql[fr].
BRACKET_SET = re.compile(r"([a-z]{4})\[([a-z]+)\]", re.IGNORECASE)

# IDs with year ranges, e.g. mi-ad605 (1979-1994).
MI_WITH_PERIOD = re.compile(
    r"(mi-[a-z]{2}\d{3})\s*\((\d{4}-\d{4})\)",
    re.IGNORECASE,
)

# Abbreviated suffixes, e.g. i, p2, q.
SUFFIX = re.compile(r"[a-z]\d?", re.IGNORECASE)


def parse_token(token):
    """Parse one complete ID or bracket expression."""
    token = token.strip()

    if token in ("…", "..."):
        return []

    match = MI_WITH_PERIOD.fullmatch(token)
    if match:
        return [(match.group(1), {"run_ID_period": match.group(2)})]

    if VALID_ID.fullmatch(token):
        return [(token, {})]

    match = LEGACY_ID.fullmatch(token)
    if match:
        run_id = f"u-{match.group(1)}{match.group(2)}"
        return [(run_id, {})]

    match = BRACKET_SET.fullmatch(token)
    if match:
        prefix, endings = match.groups()
        return [(prefix + ending, {}) for ending in endings]

    raise ValueError(f"Unrecognised run_ID token: {token!r}")


def expand_run_ids(value):
    """Return individual IDs and any ID-specific extra fields."""
    raw = str(value or "").strip()

    if not raw:
        return []

    normalised = re.sub(r"\s+", "", raw).lower()

    # Handle the explicitly specified exception.
    if normalised in SPECIAL_EXPANSIONS:
        return [(run_id, {}) for run_id in SPECIAL_EXPANSIONS[normalised]]

    # Split comma-, semicolon- and slash-separated IDs.
    tokens = [
        token.strip()
        for token in re.split(r"[,;/]", raw)
        if token.strip()
    ]

    if not tokens:
        return []

    # Handle abbreviated groups based on a five-letter initial ID.
    if re.fullmatch(r"[a-z]{5}", tokens[0], re.IGNORECASE):
        base = tokens[0]
        results = [(base, {})]

        for token in tokens[1:]:
            if SUFFIX.fullmatch(token):
                results.append((base[:4] + token, {}))
            else:
                results.extend(parse_token(token))

        return results

    # Otherwise, parse each token as an individual ID.
    results = []

    for token in tokens:
        results.extend(parse_token(token))

    return results


# Read the source YAML.
with SOURCE.open(encoding="utf-8") as f:
    simulations = yaml.safe_load(f)


file_counts = {}
created = 0
blank_entries = []
incomplete_entries = []
duplicates = []

for row_number, simulation in enumerate(simulations, start=1):

    run_id_value = str(simulation.get("run_ID") or "").strip()

    # Collect entries without a run_ID for manual checking.
    if not run_id_value:
        blank_entries.append(simulation)
        continue

    # Record rows containing ellipses (omitted IDs).
    if "…" in run_id_value or "..." in run_id_value:
        incomplete_entries.append((row_number, run_id_value))

    expanded_ids = expand_run_ids(run_id_value)

    for run_id, extra_fields in expanded_ids:

        # Duplicate all original fields, replacing run_ID.
        single_simulation = {
            **simulation,
            "run_ID": run_id,
        }

        # Preserve ID-specific information such as year ranges.
        single_simulation.update(extra_fields)

        # Avoid overwriting files for duplicate IDs.
        file_counts[run_id] = file_counts.get(run_id, 0) + 1
        occurrence = file_counts[run_id]

        if occurrence == 1:
            filename = f"{run_id}.yml"
        else:
            filename = f"{run_id}_{occurrence}.yml"
            duplicates.append((run_id, filename))

        output_file = OUTPUT_DIR / filename

        with output_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                single_simulation,
                f,
                sort_keys=False,
                allow_unicode=True,
            )

        created += 1


# Write all entries without a run_ID to one .txt file.
manual_check_file = OUTPUT_DIR / "simulations_for_manual_check.txt"

with manual_check_file.open("w", encoding="utf-8") as f:
    f.write("# Entries without a run_ID - for manual checking\n\n")
    yaml.safe_dump(
        blank_entries,
        f,
        sort_keys=False,
        allow_unicode=True,
    )


# Report the results.
print(f"Created {created} individual simulation files.")
print(f"Collected {len(blank_entries)} entries in {manual_check_file}.")

if duplicates:
    print("\nDuplicate run_IDs:")
    for run_id, filename in duplicates:
        print(f"  {run_id} -> {filename}")

if incomplete_entries:
    print("\nRows containing ellipses (only explicitly listed IDs were created):")
    for row_number, value in incomplete_entries:
        print(f"  Entry {row_number}: {value}")

