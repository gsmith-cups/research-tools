#!/usr/bin/env python3
"""
bib_names.py

This code was written by Claude.

Checks that every bib name in a .bib file (or a plain list of bib keys)
appears somewhere inside the \\cite{...} groups of an Overleaf/LaTeX table.

Usage:
    python bib_names.py --bib refs.bib --table table.tex
    python bib_names.py --bib_names_file names.txt --table table.tex

You can also just edit the BIB_NAMES / TABLE_FILE variables below and run
the script with no arguments.
"""

import argparse
import re
import sys


def extract_bib_names_from_bib_file(path):
    """Pull all @entrytype{key, ...} keys out of a .bib file."""
    text = open(path, encoding="utf-8").read()
    keys = re.findall(r'@\w+\{\s*([^,\s]+)\s*,', text)
    return keys


def extract_bib_names_from_plain_list(path):
    """One bib name per line (commas/whitespace also tolerated)."""
    text = open(path, encoding="utf-8").read()
    # split on commas, whitespace, and newlines
    keys = re.split(r'[,\s]+', text.strip())
    return [k for k in keys if k]


def extract_cited_keys_from_table(path):
    """Find every \\cite{...} (or \\hangindent=1em\\cite{...}) block and
    pull out the comma-separated keys inside."""
    text = open(path, encoding="utf-8").read()

    cite_groups = re.findall(r'\\cite\{([^}]*)\}', text)

    keys = []
    for group in cite_groups:
        for key in group.split(','):
            key = key.strip()
            if key:
                keys.append(key)
    return keys

def check_paper_counts(path):
    """
    Parses each table row of the form:
        Group Name & <number> & \\cite{key1, key2, ...} \\\\
    (also handles \\hangindent=1em\\cite{...} style rows) and checks whether
    the stated number of papers matches the number of keys actually listed
    in the \\cite{} for that row.
 
    Returns a list of dicts describing any rows where the counts don't match:
        [{"group": str, "stated": int, "actual": int, "keys": [str, ...]}, ...]
    """
    text = open(path, encoding="utf-8").read()
 
    # Match: group name & number & ... \cite{...} ... row-ending \\
    row_pattern = re.compile(
        r'([^\n&]+?)\s*&\s*(\d+)\s*&\s*(?:\\hangindent=[\d.]+\w*)?\\cite\{([^}]*)\}',
        re.MULTILINE,
    )
 
    mismatches = []
    for match in row_pattern.finditer(text):
        group = match.group(1).strip()
        stated = int(match.group(2))
        keys = [k.strip() for k in match.group(3).split(',') if k.strip()]
        actual = len(keys)
 
        if actual != stated:
            mismatches.append(
                {"group": group, "stated": stated, "actual": actual, "keys": keys}
            )
 
    return mismatches

def main():
    parser = argparse.ArgumentParser(
        description="Find bib names missing from an Overleaf cite table."
    )
    parser.add_argument("--bib", help="Path to a .bib file")
    parser.add_argument(
        "--bib_names_file",
        help="Path to a plain text file containing bib names "
             "(comma or newline separated)",
    )
    parser.add_argument(
        "--table", required=True, help="Path to the .tex file containing the table"
    )

    # If run with no arguments at all, show full help instead of a bare error.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # ---- EDIT THESE IF YOU WANT TO RUN WITHOUT COMMAND-LINE ARGS ----
    BIB_FILE = args.bib or None
    NAMES_FILE = args.bib_names_file or None
    TABLE_FILE = args.table
    # -------------------------------------------------------------

    if BIB_FILE:
        bib_names = extract_bib_names_from_bib_file(BIB_FILE)
    elif NAMES_FILE:
        bib_names = extract_bib_names_from_plain_list(NAMES_FILE)
    else:
        print("ERROR: provide --bib or --bib_names_file", file=sys.stderr)
        sys.exit(1)

    cited_keys = set(extract_cited_keys_from_table(TABLE_FILE))

    missing = [name for name in bib_names if name not in cited_keys]

    print(f"Total bib names checked: {len(bib_names)}")
    print(f"Total unique keys found in table: {len(cited_keys)}")
    print(f"Missing from table: {len(missing)}\n")

    if missing:
        print("The following bib names are NOT in the Overleaf table:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("All bib names were found in the table. ")

    print()
    mismatches = check_paper_counts(TABLE_FILE)
    if mismatches:
        print("The following rows have a paper count that doesn't match the number of citations listed:")
        for m in mismatches:
            print(f"  - {m['group']}: stated {m['stated']}, but found {m['actual']} citation(s)")
    else:
        print("All row paper counts match their citation counts. ")
 

if __name__ == "__main__":
    main()