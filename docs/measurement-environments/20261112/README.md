# marq04 / marq05 / marq06 / marq07 / e50server03 server specifications

Open `index.html` for the server index. Each `marqXX/` contains:

- `index.html`: Japanese detailed report.
- `assets/`: report stylesheet.
- `data/`: command logs when collected directly over SSH (marq04, marq05 and marq06).
- `slide-assets/`: English SVG, LaTeX sources and `build.sh`.
- `slide-assets/out/`: generated slide and paper-style PDFs.

marq07's report is based on command output supplied by the user; the raw output
is not stored here because it contains DIMM serial numbers. The memory details
in all four reports include user-supplied dmidecode output.

Run `./marqXX/slide-assets/build.sh` from the workspace root to build both PDFs.
LuaLaTeX, standalone, booktabs and caption are required; the marq06 slide version
also requires luatexja. Build files and font caches are removed automatically.
To include a paper table in another document, load `booktabs` and copy both
`marqXX-spec-paper-table.tex` and `marqXX-spec-paper-body.tex`, then input the
former. CPU clocks are manufacturer specifications; running kernel versions and
storage usage reflect the time of collection.

`e50server03/index.html` records the partial specifications from the 2025 measurement-system symposium slides. The user confirmed that this was the e50server03 benchmark environment; no live system inspection was performed.
