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