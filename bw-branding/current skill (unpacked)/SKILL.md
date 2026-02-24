---
name: bw-branding
description: Apply Bellwether's house style and visual branding to any output Claude creates or edits. Use this skill whenever the user asks to create, format, or update a Word document (.docx), PowerPoint presentation (.pptx), Excel spreadsheet (.xlsx), report, memo, letter, or slide deck. Also trigger for any chart, graph, or data visualization. This skill defines the complete brand standard — colors, fonts, templates, and data viz rules — that should be layered on top of the docx, pptx, and xlsx skills. Activate even when the user does not mention brand or style explicitly; Bellwether branding should be applied to all professional document output by default.
---

# Bellwether Brand Style Skill

This skill makes all outputs Claude produces consistent with Bellwether's brand. Read this file first, then proceed with the relevant document skill (docx, pptx, xlsx). Consult the files in `references/` for additional detail as needed.

---

## Workflow

1. **Determine if the task produces a document** (Word, PowerPoint, or Excel file). If the output is not a document — e.g., a dashboard, standalone visualization, or in-conversation output — skip to step 5.
2. **If the output is a document, determine the destination platform.** If the user has already indicated whether the file will ultimately live in Microsoft Office or be uploaded to Google Drive, use that. If it is not clear from context, ask: *"Will this document be used in Microsoft Office, or uploaded to Google Drive?"* The answer determines which body font to use (see Typography below).
3. **Identify the document type** and select the correct template from the table below. If the user mentions PowerPoint or requests a chart or data visualization for a presentation, always load the PPT template first.
4. **Open the template** using the docx or pptx skill — do not build structure from scratch.
5. **Apply typography** using the guidance below.
6. **Apply colors** using the guidance below.
7. **For charts and data tables**, follow the color sequence and visual rules in `references/data-viz.md`.
8. **Do not add colors, fonts, or design elements not specified in this guide.**

When reformatting an existing document, preserve all content and update only appearance to match the brand spec.

---

## Template Selection

If the output is a document, always start from a template in this skill's `assets/` folder rather than building from scratch. The templates already contain the correct logo placement, margins, and header/footer styling.

Note: The output file is always a Microsoft Office format (.docx, .pptx, .xlsx) regardless of whether it will ultimately live in Office or Google Drive. The destination platform only governs which body font is embedded in that file.

| Document type | Template |
|---|---|
| Formal letters, official reports, board materials | `Official Letterhead Template 2024.dotx` |
| Memos, working drafts, client-facing deliverables | `Standard Letterhead.dotx` |
| Presentations and slide decks | `Extended PPT Deck Template 2024.potx` |
| Spreadsheets / data tables | No template — apply colors and fonts manually |
| Charts, graphs, dashboards, data visualizations | No template, see `references/data-viz.md` for the full data visualization ruleset |

When the formality level is unclear, default to the Standard Letterhead. Use the Official Letterhead only when the user signals the document is formal or external-facing in an official capacity.

---

## Typography

All Bellwether documents use **Garamond** for titles and slide titles regardless of destination platform. The body and heading font depends on the output type and destination:

- **Microsoft Office (staying in Office):** Use **Avenir Next LT Pro** for all headings and body text. Avenir Next LT Pro is assumed to be installed in all Bellwether M365 environments. Only fall back to **Aptos** if the user explicitly says the font is unavailable.
- **Google Drive upload:** Use **Inter** for all headings and body text. Inter is assumed to be installed. Fall back to **Avenir Next LT Pro** if the user says it is unavailable, or **Aptos** as a last resort.
- **Non-document outputs (dashboards, HTML, CSS, visualizations):** Use **Inter**. Inter was designed specifically for computer screens and digital interfaces, making it the preferred choice for any output rendered in a browser or digital environment rather than printed or viewed as an Office file. Load it via the following HTML/CSS:

  ```html
  <!-- In <head> -->
  <link rel="preconnect" href="https://rsms.me/">
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
  ```

  ```css
  /* CSS */
  :root {
    font-family: Inter, sans-serif;
    font-feature-settings: 'liga' 1, 'calt' 1; /* fix for Chrome */
  }
  @supports (font-variation-settings: normal) {
    :root { font-family: InterVariable, sans-serif; }
  }
  ```

See `references/typography.md` for recommended font sizes, weights, and line spacing by document section.

---

## Primary Colors

These are the colors to reach for first. Use them for headings, dividing rules, accent shapes, and backgrounds.

| Name | Hex | Primary use |
|---|---|---|
| Bellwether Plum | `#6D1E4A` | Lead brand color — headings, dominant accents |
| Bellwether Teal | `#007786` | Secondary accent |
| Deep Green | `#0D525A` | Tertiary accent |
| Navy | `#212B46` | Dark backgrounds, alternative text on light backgrounds |
| Gray | `#5A6675` | Secondary text, captions, borders |
| Cream | `#F0DEC1` | Light backgrounds, callout boxes |

**Action / highlight colors** (not for primary palette use — reserved for emphasis and callouts):

| Name | Hex | Use |
|---|---|---|
| Yellow | `#FFC762` | Key findings, callout boxes, primary emphasis |
| Orange | `#FFB653` | Data highlights, supporting emphasis |

Do not introduce colors outside this palette. Full hex codes for secondary and desaturated variants are in `references/colors.md`.