---
name: bw-branding
description: >
  Apply Bellwether's house style and visual branding to any document Claude 
  creates or edits. Use this skill whenever the user asks to create, format, 
  or update a Word document (.docx), PowerPoint presentation (.pptx), Excel 
  spreadsheet (.xlsx), report, memo, letter, or slide deck. Also trigger for 
  any chart, graph, or data visualization. This skill defines the complete 
  brand standard — colors, fonts, templates, and data viz rules — that should 
  be layered on top of the docx, pptx, and xlsx skills. Activate even when the 
  user doesn't mention "brand" or "style" explicitly; Bellwether branding 
  should be applied to all professional document output by default.
---

# Bellwether Brand Style Skill

This skill makes every document Claude produces consistent with Bellwether's brand. 
Read this file first, then proceed with the relevant document skill (docx, pptx, xlsx). 
Consult the files in `references/` for additional detail as needed.

---

## Workflow

1. **Identify the document type** and select the correct template from the table below. If the user mentions PowerPoint or requests a chart or data visualization for a presentation, always load the PPT template first.
2. **Open the template** using the docx or pptx skill — do not build structure from scratch.
3. **Apply typography** using the guidance below.
4. **Apply colors** using the guidance below.
5. **For charts and data tables**, follow the color sequence and visual rules in `references/data-viz.md`.
6. **Do not add colors, fonts, or design elements not specified in this guide.**

When reformatting an existing document, preserve all content and update only
appearance to match the brand spec.

---

## Template Selection

Always start from a template in this skill's `assets/` folder rather than
building from scratch. The templates already contain the correct logo placement,
margins, and header/footer styling.

| Document type | Template |
|---|---|
| Formal letters, official reports, board materials | `Official Letterhead Template 2024.dotx` |
| Memos, working drafts, client-facing deliverables | `Standard Letterhead.dotx` |
| Presentations and slide decks | `Extended PPT Deck Template 2024.potx` |
| Spreadsheets / data tables | No template — apply colors and fonts manually |

When the formality level is unclear, default to the Standard Letterhead. Use
the Official Letterhead only when the user signals the document is formal or
external-facing in an official capacity.

---

## Typography

The same font pairing applies across Microsoft documents:
1. **Garamond** is used for titles, including slide titles
2. **Avenir Next LT Pro** is used for headings and all body text
    - Avenir Next LT Pro is assumed to be installed in all Bellwether M365 environments. Only fall back to **Aptos** if the user explicitly says the font is unavailable.

See `references/typography.md` for recommended font sizes and line spacing by
document section.

---

## Primary Colors

These are the colors to reach for first. Use them for headings, dividing rules,
accent shapes, and backgrounds.

| Name | Hex | Primary use |
|---|---|---|
| Bellwether Plum | `#6D1E4A` | Lead brand color — headings, dominant accents |
| Bellwether Teal | `#007786` | Secondary accent |
| Deep Green | `#0D525A` | Tertiary accent |
| Navy | `#212B46` | Dark backgrounds, alternative text on light backgrounds |
| Gray | `#5A6675` | Secondary text, captions, borders |
| Cream | `#F0DEC1` | Light backgrounds, callout boxes |

**Action / highlight colors** (not for primary palette use — reserved for
emphasis and callouts):

| Name | Hex | Use |
|---|---|---|
| Yellow | `#FFC762` | Key findings, callout boxes, primary emphasis |
| Orange | `#FFB653` | Data highlights, supporting emphasis |

Do not introduce colors outside this palette. Full hex codes for secondary and
desaturated variants are in `references/colors.md`.

---

## Data Visualization Color Sequence

See `references/data-viz.md` for chart formatting, annotation style, axis
treatment, and the full data visualization ruleset.
