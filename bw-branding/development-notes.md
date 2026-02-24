# bw-branding Skill — Development Notes

**Skill name**: `bw-branding`
**Current version**: Post-eval v1
**Last updated**: February 2026
**Model tested**: Opus 4.6

---

## Overview

The `bw-branding` skill applies Bellwether's house style and visual branding automatically to any document Claude produces — Word memos, PowerPoint decks, Excel spreadsheets, charts, and data visualizations. It is designed to layer on top of the existing `docx`, `pptx`, and `xlsx` skills and activates by default on any professional document output, even when the user doesn't explicitly request branding.

---

## Source Materials

The skill was built from the following Bellwether assets:

- **Bellwether Brand Guide** (`Bellwether Brand Guide_vCurrent.pdf`) — primary source for color palettes, typography system, and design principles
- **Bellwether Data Visualization Brand Guide** (`Bellwether Data Viz Brand Guide_vCurrent.pdf`) — source for chart color sequencing, annotation style, chart type guidance, and visual simplicity rules
- **Official Letterhead Template** (`Official Letterhead Template 2024.dotx`) — for formal letters, official reports, and board materials
- **Standard Letterhead** (`Standard Letterhead.dotx`) — for memos, working drafts, and client-facing deliverables
- **Extended PPT Deck Template** (`Extended PPT Deck Template 2024.potx`) — for presentations and slide decks; reduced from 49MB to 9.1MB by removing a placeholder stock photo before bundling

---

## Key Design Decisions

**Typography**: The brand guide specifies Teodor and Avenir as the primary type system, but Teodor requires a license and is used mainly by the external relations team. The skill instead standardizes on Garamond (headings and titles) and Avenir Next LT Pro (body text, bullets, labels) as the practical in-house pairing. Aptos was chosen as the fallback (over Calibri) given that the full team is on M365. Avenir Next LT Pro is assumed to be installed and Claude should only fall back to Aptos if the user explicitly says it's unavailable.

**Template strategy**: Rather than building documents from scratch, the skill always opens a bundled template as the starting point. This ensures logo placement, margins, and header/footer styling are preserved automatically.

**Data visualization**: The data viz guide was translated into a structured color sequence (Plum → Teal → Light Gray → Navy → Cream → Deep Green → Peach → Yellow → Lavender), with Yellow and Orange reserved exclusively for callouts and emphasis rather than series colors.

---

## Current Skill Structure

```
bw-branding/
├── SKILL.md                              — core instructions, loaded on trigger
├── assets/
│   ├── Extended PPT Deck Template 2024.potx
│   ├── Official Letterhead Template 2024.dotx
│   └── Standard Letterhead.dotx
└── references/
    ├── colors.md                         — full palette with hex codes and usage rules
    ├── typography.md                     — font sizes, weights, and spacing by document type
    └── data-viz.md                       — chart types, color sequence, annotation style
```

**Context cost**: SKILL.md is 99 lines and loaded on trigger. Reference files (colors: 80 lines, typography: 102 lines, data-viz: 145 lines) are loaded on demand. Assets are never loaded into context — they are opened directly as templates.

**Packaged size**: 9.1MB (within the 30MB install limit).

---

## Best Practices Review

The skill was evaluated against [Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Summary:

| Criterion | Status | Notes |
|---|---|---|
| SKILL.md under 500 lines | ✅ | 99 lines |
| Description in third person | ✅ | |
| Description includes what and when | ✅ | |
| Progressive disclosure | ✅ | Reference files one level deep |
| No time-sensitive content | ✅ | |
| Consistent terminology | ✅ | |
| No Windows-style paths | ✅ | |
| Gerund-form skill name | — | Kept as `bw-branding` intentionally; Anthropic's own `brand-guidelines` skill follows the same convention |
| Reference files >100 lines have TOC | — | Deferred; files are short enough that Claude can read them in full without issue |

---

## Iterative Edits

After the initial draft, Marisa reviewed all four files and made the following changes:

- **Typography overhaul**: Updated heading hierarchy so Garamond applies only to document/slide titles; H1–H3 headings now use Avenir Next LT Pro. Added a Color column to the heading table. Adjusted H2 from 14pt to 12pt after the first eval round.
- **Colors reorganization**: Moved Action colors (Yellow, Orange) into their own section above the secondary palette for clarity. Consolidated the five per-color desaturated variant tables into a single compact table.
- **PPT guidance**: Added a note distinguishing external/conference decks (less text, more visuals) from client deliverable/factbase decks (more text, citations), with an instruction to ask the user if the deck's purpose is unclear.
- **Fallback font**: Changed from Calibri to Aptos throughout, consistent with the team's M365 environment.
- **Data viz table header**: Loosened the table header color rule from "Plum or Navy fill" to "dark fill" to give authors more flexibility based on document context.

---

## Evaluation Round 1

**Date**: February 20, 2026
**Model**: Opus 4.6
**Tests run**: 3

### Results Summary

| Test | Document type | Template | Typography | Colors | Data Viz | Clarifying Qs | Brand feel |
|---|---|---|---|---|---|---|---|
| 1 — Internal memo | Word memo | 3 | 2 | 3 | N/A | N/A | 3 |
| 2 — Intro PPT deck | PowerPoint | 3 | 3 | 3 | N/A | 2 | 3 |
| 3 — Bar chart in PPT | PPT + chart | 1 | 2 | 3 | 2 | 1 | 3 |

*Scale: 1 = Poor, 2 = Acceptable, 3 = Good*

### Notable Observations

- Claude exported to PDF to visually verify output in Test 1 — not in the skill instructions, but a useful behavior worth considering for formal integration later.
- Test 1 produced a file with unreadable content on first open (content type declared as template rather than document). Claude self-corrected on follow-up.
- Test 3 failed to load the PPT template when the prompt focused on the chart rather than the deck context. Claude used Aptos instead of Avenir Next LT Pro despite the font being available.
- Test 2: Claude added contact information to the Thank You slide, which Bellwether does not do.

### Fixes Applied After Eval

1. **PPT template for chart requests**: Added a rule to SKILL.md that if the user mentions PowerPoint or requests a chart for a presentation, the PPT template should always load first.
2. **Avenir Next LT Pro assumption**: Changed from "fall back if unavailable" to "assume installed; only fall back if the user explicitly says it's unavailable."
3. **Thank You slide**: Added a rule to typography.md that closing/Thank You slides should not be modified with contact information.
4. **Paragraph spacing**: Added a rule to typography.md that body paragraphs should be separated by a blank line (Claude's default behavior of running paragraphs together with no visual break was flagged in Test 1).

---

## Open Items

- **Test 3 chart title vs. slide title**: Claude placed the finding in the slide title rather than the chart title itself. Flagged but intentionally left for authors to correct — considered an acceptable authorial decision rather than a skill fix.
- **PDF verification step**: Claude's self-initiated PDF export for visual verification (Test 1) was a positive surprise. Worth considering whether to formally add this as a step in the workflow.
- **Eval round 2**: A second round of testing is planned after the current fixes are validated, with a broader set of prompts and continued use of Opus 4.6.

---

## Files in This Directory

| File | Purpose |
|---|---|
| `SKILL.md` | Core skill instructions |
| `bw-branding.skill` | Packaged skill file for installation |
| `assets/` | Bundled templates |
| `references/` | Detailed brand spec reference files |
| `Bellwether Brand Guide_vCurrent.pdf` | Source brand guide |
| `Bellwether Data Viz Brand Guide_vCurrent.pdf` | Source data viz guide |
| `tests/skill-eval-template.md` | Blank evaluation form |
| `tests/rd1_opus/` | Round 1 eval inputs and outputs |