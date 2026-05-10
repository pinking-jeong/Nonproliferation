# OS-PM System Paper

Single-column arXiv preprint targeting *Science & Global Security* / *ESARDA Bulletin* / *Nonproliferation Review*.

## Build

```bash
# Requires: TeX Live (xelatex), latexmk
make
```

Output: `main.pdf`.

## Structure

- `main.tex` — manuscript with `\todo{...}` markers for content to fill in as experiments complete
- `references.bib` — canonical BibTeX
- `figures/` — TikZ-generated only initially; replace with PDF/PNG as experiments produce results

## Authoring conventions

- Use `\todo{...}` for content gaps (renders red in draft mode)
- Use `\note{...}` for review notes (renders blue)
- Uncomment `\linenumbers` for review-mode line numbers
- Keep `\bibliographystyle{plain}` until journal is chosen — switch to `unsrt`, `ieeetr`, or journal-specific style on submission

## Sections needing experimental data before submission

- §4 (Method) — confirm equations match implementation
- §5 (Experiments) — fill all `\todo{...}` after retrofit runs complete
- §5.4 (Results) — main table
- §5.5 (Ablations) — supplementary table
- Acknowledgments — funder + advisory committee names
