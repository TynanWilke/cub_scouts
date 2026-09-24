"""
Cub Scout Law Flash Cards
--------------------------
Generates a single printable PDF page of Cub Scout Law flash cards.
One card per point of the Scout Law, with the meaning of each point
drawn from the Cub Scout handbook. Each card contains the Scout Law
point, its meaning, a sequence number (so cards can be kept in order),
dashed scissor-cut lines, and a hole-punch guide mark so kids can cut
them out and put them on a ring.

The cards fill the whole page edge-to-edge, so the paper's outer edges
serve as the outer card edges. Kids only cut the interior grid lines
(1 vertical down the middle + 5 horizontal between rows) instead of a
full border around each card.

Content reference:
Cub Scout Handbook - the 12 points of the Scout Law

Requires:  reportlab   ->  pip install reportlab
Run:       python cub_scout_law_flashcards.py
Output:    cub_scout_law_flashcards.pdf
"""

import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# CARD CONTENT
# ----------------------------------------------------------------------
# One card per point of the Scout Law (12 points total).
CARDS = [
    {
        "title": "SCOUT LAW \u2022 1",
        "main": "Trustworthy",
        "meaning": ("Tell the truth and keep promises. People can depend "
                    "on you."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 2",
        "main": "Loyal",
        "meaning": ("Show that you care about your family, friends, Scout "
                    "leaders, school, and country."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 3",
        "main": "Helpful",
        "meaning": "Volunteer to help others without expecting a reward.",
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 4",
        "main": "Friendly",
        "meaning": ("Be a friend to everyone, even people who are very "
                    "different from you."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 5",
        "main": "Courteous",
        "meaning": "Be polite to everyone and always use good manners.",
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 6",
        "main": "Kind",
        "meaning": ("Treat others as you want to be treated. Never harm or "
                    "kill any living thing without good reason."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 7",
        "main": "Obedient",
        "meaning": ("Follow the rules of your family, school, and pack. "
                    "Obey the laws of your community and country."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 8",
        "main": "Cheerful",
        "meaning": ("Look for the bright side of life. Cheerfully do tasks "
                    "that come your way. Try to help others be happy."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 9",
        "main": "Thrifty",
        "meaning": ("Work to pay your own way. Try not to be wasteful. Use "
                    "time, food, supplies, and natural resources wisely."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 10",
        "main": "Brave",
        "meaning": ("Face difficult situations even when you feel afraid. "
                    "Do what you think is right despite what others might "
                    "be doing or saying."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 11",
        "main": "Clean",
        "meaning": ("Keep your body and mind fit. Help keep your home and "
                    "community clean."),
        "source": "Cub Scout Handbook"
    },
    {
        "title": "SCOUT LAW \u2022 12",
        "main": "Reverent",
        "meaning": ("Be reverent toward God. Be faithful in your religious "
                    "duties. Respect the beliefs of others."),
        "source": "Cub Scout Handbook"
    },
]

# ----------------------------------------------------------------------
# LAYOUT SETTINGS
# ----------------------------------------------------------------------
PAGE_WIDTH, PAGE_HEIGHT = letter
# Cards fill the whole page edge-to-edge, so the paper's outer edges ARE the
# outer card edges. Kids only cut the interior grid lines (1 vertical down the
# middle + 5 horizontal between rows) instead of a full border around each card.
MARGIN = 0                     # no page margin: cards go edge-to-edge
COLS = 2
ROWS = 6                       # 2 x 6 = 12 slots, one per Scout Law point
HOLE_RADIUS = 0.09 * inch
HOLE_INSET = 0.30 * inch       # distance of hole center from card edges
NUMBER_INSET = 0.30 * inch     # distance of number from top-right corner

# Content is kept inset from the paper edge so it stays inside the printer's
# printable area (most printers can't print to the very edge of the page).
CONTENT_PAD = 0.35 * inch

CARD_AREA_WIDTH = PAGE_WIDTH - 2 * MARGIN
CARD_AREA_HEIGHT = PAGE_HEIGHT - 2 * MARGIN
CARD_WIDTH = CARD_AREA_WIDTH / COLS
CARD_HEIGHT = CARD_AREA_HEIGHT / ROWS

TOTAL_CARDS = len(CARDS)  # actual number of unique cards


def draw_interior_grid(c):
    """Draw only the interior cut lines (shared card edges).

    The paper's outer edges serve as the outer card edges, so we skip the
    outer border entirely. Kids just cut the vertical column divider(s) and
    the horizontal row dividers.
    """
    c.setDash([3, 2], 0)
    c.setLineWidth(0.75)

    # Interior vertical lines (between columns), full page height
    for col in range(1, COLS):
        x = MARGIN + col * CARD_WIDTH
        c.line(x, MARGIN, x, PAGE_HEIGHT - MARGIN)

    # Interior horizontal lines (between rows), full page width
    for row in range(1, ROWS):
        y = MARGIN + row * CARD_HEIGHT
        c.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)

    c.setDash([], 0)  # reset to solid


def draw_hole_punch_mark(c, x, y, w, h):
    """Hole-punch guide centered along the top edge of every card.

    A consistent top-middle hole means every finished card punches in the same
    spot, so they stack neatly on a ring regardless of which column they came
    from, and it stays well within the printable area.
    """
    hole_x = x + w / 2
    hole_y = y + h - HOLE_INSET
    c.setDash([], 0)
    c.setLineWidth(0.75)
    c.circle(hole_x, hole_y, HOLE_RADIUS, stroke=1, fill=0)


def draw_card_number(c, x, y, w, h, number, total):
    """Sequence number in the lower-right corner of the card.

    Inset by CONTENT_PAD so it stays within the printable area.
    """
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(x + w - CONTENT_PAD, y + CONTENT_PAD, f"#{number}/{total}")


def draw_card_content(c, x, y, w, h, card, number, total, col):
    """Write the number, Scout Law point, and meaning on the card."""
    center_x = x + w / 2
    usable_w = w - 2 * CONTENT_PAD

    # Sequence number (lower-right corner)
    draw_card_number(c, x, y, w, h, number, total)

    # Main Scout Law point (word-wrapped, auto-sized to fit card width)
    main_font_size = 20
    main_text = card["main"]
    # Reduce font size until all words fit within the usable width
    while main_font_size > 8:
        c.setFont("Helvetica-Bold", main_font_size)
        approx_chars = int(usable_w / (main_font_size * 0.55))
        wrapped = textwrap.wrap(main_text, width=max(approx_chars, 8))
        # Accept if no single line is too wide
        too_wide = any(c.stringWidth(ln, "Helvetica-Bold", main_font_size) > usable_w
                       for ln in wrapped)
        if not too_wide:
            break
        main_font_size -= 1
    c.setFont("Helvetica-Bold", main_font_size)
    line_height = main_font_size * 1.3
    total_main_height = len(wrapped) * line_height
    main_top = y + h / 2 + total_main_height / 2
    for ln in wrapped:
        c.drawCentredString(center_x, main_top, ln)
        main_top -= line_height

    # Meaning (word-wrapped)
    c.setFont("Helvetica", 8)
    wrap_width = int(usable_w / (0.055 * inch))  # approx chars per line at 8pt
    lines = textwrap.wrap(card["meaning"], width=max(wrap_width, 10))
    text_y = y + h / 2 - 0.25 * inch
    for line in lines:
        c.drawCentredString(center_x, text_y, line)
        text_y -= 0.14 * inch

    # Source footer
    c.setFont("Helvetica-Oblique", 6)
    c.drawCentredString(center_x, y + CONTENT_PAD, card["source"])


def build_pdf(filename="cub_scout_law_flashcards.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)

    # Interior cut lines are drawn once for the whole page (shared card edges).
    draw_interior_grid(c)

    card_index = 0
    for row in range(ROWS):
        for col in range(COLS):
            x = MARGIN + col * CARD_WIDTH
            y = PAGE_HEIGHT - MARGIN - (row + 1) * CARD_HEIGHT

            card = CARDS[card_index % len(CARDS)]
            sequence_number = card_index + 1  # 1-based numbering, left-to-right, top-to-bottom
            card_index += 1

            draw_hole_punch_mark(c, x, y, CARD_WIDTH, CARD_HEIGHT)
            draw_card_content(c, x, y, CARD_WIDTH, CARD_HEIGHT,
                               card, sequence_number, TOTAL_CARDS, col)

    c.showPage()
    c.save()
    print(f"Saved: {filename}")


if __name__ == "__main__":
    build_pdf()
