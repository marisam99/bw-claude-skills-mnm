# bw-branding Skill

The `bw-branding` skill Apply Bellwether's house style and visual branding to any output Claude creates or edits. This includes text documents, slides, spreadsheets, and code/data visualizations. It is designed to layer on top of the existing `docx`, `pptx`, and `xlsx` skills and activates by default on any professional output, even when the user doesn't explicitly request branding.

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

**Template strategy**: Rather than building documents from scratch, the skill always opens a bundled template as the starting point. This ensures logo placement, margins, and header/footer styling are preserved automatically.

**Microsoft Office Output**: Currently, Claude does not support creating Google Workspace documents (Docs, Sheets, Slides) directly. Any output from Claude must first be created in Microsoft Office and then uploaded to Google Drive. 

**Downloading Inter** To make the transition from Office to Google Drive simpler, I downloaded Inter and plan to test Claude on creating outputs meant for Google.

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

The skill is regularly evaluated against [Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). Summary:

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

## Files in This Directory

| File | Purpose |
|---|---|
| `current skill (unpacked)` | Core skill files for viewing/editing |
| `bw-branding.skill` | Packaged skill file for installation |
| `source materials` | Source brand and data viz guides |
| `tests/` | Evaluation data and summaries |