# research-tools
This repo has scripts to use in research and paper writing.

## bib_names.py

A small Python script that checks whether all of your bibliography keys appear in an Overleaf/LaTeX table that uses `\cite{...}` commands.

### What it does

1. Reads your bib keys, either from a `.bib` file or a plain text list (comma or newline separated).
2. Scans a `.tex` file for every `\cite{...}` block and collects all the keys inside them.
3. Compares the two lists and reports any bib keys that are **not** found in the table.

### Usage

```bash
# From a .bib file
python check_bib_names.py --bib refs.bib --table table.tex

# From a plain text list of names
python check_bib_names.py --bib_names_file names.txt --table table.tex
```

Both `--table` and one of `--bib` / `--bib_names_file` are required. Running the script with no arguments prints full usage instructions.

### Output

Prints a summary (number of keys checked, number found in the table, number missing) followed by a list of any bib names missing from the table, if any.