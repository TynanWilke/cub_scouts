# Balancing Bears — Pattern Animals coloring sheet

Single-page (letter) black-and-white coloring sheet for the Cub Scouts
"Balancing Bears" adventure. Four animals in quadrants — frog, zebra,
butterfly, snake — drawn in a consistent bold-outline cartoon style with
large EMPTY bodies so the kids can invent their own patterns
(stripes, spots, zigzags, spirals).

## Files

- `balancing_bears_coloring.pdf` — the printable sheet (print at 100%, letter)
- `sheet.html` — the sheet layout (2×2 grid, labels, title)
- `img/*.png` — the four Poe-generated (gpt-image-2) line-art animals
- `poe_gen.py` — regenerates the four images via the Poe API
  (reads the key from `/etc/tw-pa/env` or 1Password; never hardcode it)

## Reworking

To change an animal, edit the prompt in `poe_gen.py` and rerun it for that
animal, then re-render the PDF from `sheet.html` (e.g.
`google-chrome --headless=new --print-to-pdf=... sheet.html`).
