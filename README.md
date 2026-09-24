# cub_scouts

Scripts and printable materials for Cub Scouts.

This repo contains small Python scripts that generate printable PDF flash cards
for memorizing the Cub Scout Oath and the Cub Scout Law. Each script produces a
single letter-size page laid out as a grid of cards. The cards fill the page
edge-to-edge, so you only cut the interior grid lines. Every card includes:

- The oath phrase / law point
- A kid-friendly meaning from the Cub Scout Handbook
- A sequence number (e.g. `#3/12`) so cards stay in order
- A hole-punch guide mark (top-center) so finished cards stack neatly on a ring
- Dashed scissor-cut lines on the interior dividers

## Contents

| Folder | Script | Output | Cards |
| --- | --- | --- | --- |
| `cub_scout_oath_flashcards/` | `cub_scout_oath_flashcards.py` | `cub_scout_oath_flashcards.pdf` | 10 (2 x 5 grid) |
| `cub_scout_law_flashcards/` | `cub_scout_law_flashcards.py` | `cub_scout_law_flashcards.pdf` | 12 (2 x 6 grid) |

A pre-generated PDF is included in each folder if you just want to print.

## Requirements

- Python 3
- [reportlab](https://pypi.org/project/reportlab/) (`>=4.0.0`)

## Usage

Each folder is self-contained. From within a folder:

```bash
cd cub_scout_oath_flashcards
pip install -r requirements.txt
python cub_scout_oath_flashcards.py
```

This writes `cub_scout_oath_flashcards.pdf` in the same folder. The Law cards
work the same way:

```bash
cd cub_scout_law_flashcards
pip install -r requirements.txt
python cub_scout_law_flashcards.py
```

## Printing & assembly

1. Print the PDF on letter-size paper (best on cardstock).
2. Cut along the dashed interior lines — the page edges are the outer card edges.
3. Punch a hole at the top-center guide mark on each card.
4. Put the cards on a ring in numeric order.

## Customizing

Card text lives in the `CARDS` list at the top of each script. Layout settings
(grid size, margins, hole position, padding) are defined just below in the
`LAYOUT SETTINGS` section.
