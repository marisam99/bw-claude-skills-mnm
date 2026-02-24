# Bellwether Copyeditor — Evaluation Summary

## Test Document

**test1.docx** — "Formulating Success," a ~15-page Bellwether publication on outcomes-based higher education funding. The document was previously copyedited by a human editor, providing a ground-truth comparison.

## Evaluation History

### Round 1: Editorial Quality (AI vs. Human Editor)

Claude's copyedits were compared against the human editor's markup on the same document.

- **Total findings (AI):** 78 (71 tracked changes, 7 comment-only flags)
- **Overlap with human editor:** High on rule-based corrections (AP Style, spelling, grammar). The AI caught several issues the human missed (e.g., inconsistent sidebar numbering, second instance of "like" → "such as").
- **Human caught but AI missed:** Some domain-specific nuances and a handful of comma refinements.
- **False positives (AI edits that would be rejected):** ~5, primarily in areas later addressed by guardrails (modal verb swaps, restrictive/nonrestrictive clause changes).

### Round 2: Tracked Changes Output (docx Generation)

Multiple iterations were needed to produce valid Word documents with tracked changes.

- **v1-v2 (ElementTree approach):** Documents opened with "unreadable content" warnings due to namespace prefix mangling (`w:del` → `ns0:del`). Root cause: Python's built-in `xml.etree.ElementTree` does not preserve namespace prefixes.
- **v3 (lxml approach):** First clean output. Switched to lxml, which preserves namespace prefixes exactly. Document opened without warnings; tracked changes and comments rendered correctly.
- **v4 (reusable script, markdown parser):** 76/79 applied, but user reported edits landing in wrong locations. Root cause: the findings parser extracted text fragments too short for unique matching.
- **v5 (parser with context expansion):** 74/79 applied. Remaining 5 failures were well-understood edge cases (3 headings without quoted context, 1 multi-run text span, 1 endnote formatting). User confirmed comments and edits were correctly placed.
- **v6 (JSONL format):** 78/79 applied. Switched findings format from markdown to JSONL, eliminating ~200 lines of fragile regex parsing. The 1 remaining failure was two overlapping findings on the same text span — addressed by adding a no-overlapping-findings rule to the skill instructions.

### Key Failure Modes Identified and Resolved

| Issue | Root Cause | Resolution |
|-------|-----------|------------|
| "Unreadable content" in Word | ElementTree mangles namespace prefixes | Switched to lxml |
| Edits in wrong locations | Parser extracted too-short text fragments | Switched to JSONL with explicit old_text/new_text fields |
| Tracked change inside hyperlink | OOXML requires del/ins as children of w:p | Script detects non-w:p parents, moves to grandparent paragraph |
| Overlapping findings | First edit consumes text, second can't match | Added no-overlapping-findings rule to SKILL.md |
| Modal verb false positives | Claude swapped hedging verbs without cause | Added "Intentional hedging" guardrail |
| Restrictive/nonrestrictive swaps | "that" ↔ "which" changes clause meaning | Added restrictive/nonrestrictive guardrail |

### Current Performance

- **Application rate:** 78/79 (98.7%) on a 15-page publication with 78 findings
- **Output validity:** Opens cleanly in Word on macOS without warnings
- **Comment accuracy:** All 78 applied comments render correctly and are anchored to the right text
- **Known limitation:** Text spanning multiple formatting runs in the XML may fail to match; script reports these for manual resolution