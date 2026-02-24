---
name: bellwether-copyeditor
description: Copyedit Word (.docx) documents using Bellwether's house style (AP Style with org-specific exceptions). Outputs the original file with tracked changes and comments so authors can review and accept/reject each edit. Use when the user asks to copyedit, proofread, or style-check a .docx file, or mentions "AP Style," "Bellwether style," or "copy edit."
---

# Bellwether Copyeditor

Copyedits the uploaded document according to Bellwether's house rules and returns it with tracked changes and comments for authors' review. **Do not produce a clean document.** Every correction must appear as a tracked change or comment so the author(s) retain full control.

## Contents
- Workflow
- Style Rules
- What Not To Do
- Calibration Examples

---

## Workflow

### Step 1: Read the document

```bash
pandoc --track-changes=all document.docx -o document.md
```

Read the full text before making any edits. Note the deliverable type (publication, client deliverable, blog post, or internal document) as this affects tone conventions (see Style Rules below).

### Step 2: Identify all issues and write them to a findings file

Work through the document from start to finish. For each issue found, immediately write it to `findings.jsonl` (one JSON object per line, no trailing commas) — do not rely on memory. This file is the source of truth for Step 3.

**Every finding must include a named issue category.** Use one of:

`AP Style` · `Bellwether Style` · `Grammar` · `Spelling` · `Verbosity` · `Repetition` · `Precision` · `Clarity` · `Formatting` · `Inclusive Language` · `Factual Flag`  · `Other`

Every edit falls into one of two types:

- **Tracked change** — for clear rule violations and prose-level improvements (e.g., spelling, verbosity, repetitive phrasing, parallelism, precision, word choice, punctuation). These categories have very high acceptance rates and should be edited directly, not just flagged. Every tracked change must be accompanied by a comment that names the category and briefly cites the rule or rationale. Example: *"Verbosity: unnecessary 'to.'"* or *"AP Style: use 'such as' for examples, 'like' for comparisons."* The comment on a tracked change should be concise (one to two sentences) and name the category and rule so the author learns from it, not just accepts it.
- **Comment only** — for issues where the author must decide: deficit-based language, possible meaning changes, domain terminology questions, structural issues (e.g., sidebar numbering inconsistencies), heading inconsistencies, and factual flags (typos in citations, unmatched parentheses). Explain the concern and suggest options where helpful.

**JSON Field rules:**

- **`old_text`** (tracked changes): The exact text to be replaced, copied verbatim from the document. Must include enough surrounding context to match uniquely — at minimum 5-6 words, never just the changed word. For example, use `"can help to highlight"` not just `"to"`.
- **`new_text`** (tracked changes): The replacement text, with the edit applied within the same context span as `old_text`.
- **`anchor_text`** (comment-only): The exact text the comment should attach to, copied verbatim from the document. Same uniqueness requirement as `old_text`.
- **`type`**: Either `"tracked_change"` or `"comment_only"`.
- **`category`**: One of the categories listed above.
- **`comment`**: The rationale that will appear as a Word comment. Begin with the category name and a colon.
- Escape internal double quotes with a backslash (`\"`) so each line is valid JSON. After writing each line, verify it parses with `json.loads()`.

**No overlapping findings.** If two edits touch the same text span, combine them into a single finding with the cumulative change in `old_text`/`new_text`. The script applies findings sequentially, so the first edit consumes the original text and makes it unmatchable for any later finding that overlaps it.

**Be thorough.** A typical 10-15 page publication will have 40-100+ findings spanning rule violations, prose tightening, and flags. If you are finding fewer than 30 issues, you are likely under-editing — re-read with attention to verbosity, repetitive phrasing, parallelism, and comma usage.

**Examples:**
For tracked changes:
```json
{"old_text": "can help to highlight", "new_text": "can help highlight", "type": "tracked_change", "category": "Verbosity", "comment": "Verbosity: unnecessary 'to.'"}
```

For comment-only findings:
```json
{"anchor_text": "low-income households", "type": "comment_only", "category": "Inclusive Language", "comment": "Inclusive Language: Consider avoiding deficit-based language unless quoting from another source"}
```

Complete the full document pass and finish creating `findings.jsonl` before moving to Step 3.

### Step 3: Apply edits and output

```bash
python bellwether-copyeditor/scripts/apply_copyedits.py document.docx findings.jsonl output.docx
```

This script reads `findings.jsonl`, applies each finding as a tracked change or comment in the docx XML using lxml, and writes the result to `output.docx`. It uses **"Claude"** as the author name on all tracked changes and comments. Any findings that cannot be applied (e.g., text not found in the document) are reported at the end — apply these manually.

Output the edited `.docx` file along with `findings.jsonl`.

---

## Style Rules

Bellwether follows AP Style with the exceptions and clarifications below. When rules conflict, follow this hierarchy: (1) Bellwether-specific rules, (2) AP Style, (3) deliverable and audience conventions, (4) clarity and common sense.

### Formatting and Punctuation

- One space between sentences, never two.
- Spell out numbers one through nine; use numerals for 10 and above. Always use numerals for course numbers, addresses, ages, court decisions, decimals, percentages, and units of measurement.
- Use "%" in text (AP style); be mindful of "percent" vs. "percentage."
- Avoid contractions in publications. Contractions are acceptable in blog posts and commentary pieces.
- Spell out "and" — do not use "&" unless it is part of a formal entity name.
- Documents that are three or more pages long should have page numbers. If missing, flag with a comment.
- Heading formatting should be consistent throughout — all bold, all italic, or all bold-italic, but not a mix. Flag inconsistencies with a comment rather than changing them, as the author may have intentional hierarchy in mind.
- Use underline formatting sparingly. Flag instances where underline is used for emphasis (as opposed to a hyperlink), as it can read like a broken link.
- Periods and commas always go inside quotation marks, even if they were not in the original quote. Dashes, semicolons, question marks, and exclamation points go inside quotation marks when they apply to the quoted matter. They go outside when they apply to the whole sentence.

### Prose-Level Editing

Beyond rule-based corrections, actively tighten prose. The following types of edits have very high acceptance rates when accompanied by a brief rationale. Make these as tracked changes, not comments.

- **Verbosity**: Remove filler words and unnecessary constructions. For example, drop "also" when it adds nothing; remove "that" when the sentence reads clearly without it.
- **Repetition**: When the same word appears twice in adjacent sentences — especially modal verbs ("may," "might," "could") — vary it. When a noun repeats unnecessarily close to its last use, substitute a pronoun or synonym. If two sentences in a row start with the same word, suggest a change. Across all of these, do not change the meaning; just vary the expression.
- **Parallel construction**: Ensure lists and paired verb phrases use matching forms. "exacerbate… rather than improve" (not "rather than improving"). "track and analyze" (not "tracking and analyzing" if the first verb in the pair is bare infinitive).
- **Precision**: Prefer exact words over vague ones and idiomatic clichés. Avoid "impactful" as an adjective, and avoid ascribing trauma to others' experiences; use "disruptive" instead of "traumatic." Do not use "citizen" interchangeably with "resident" or "person" when referring to inhabitants of states and cities. Replace "move the needle" and similar idioms with plain language ("make a meaningful impact"). Use "such as" (not "like") when introducing examples (not comparisons).
- **Clarity**: Avoid throat-clearing ("It is important to note that…"), adverbs, unnecessary jargon, and passive voice. Use phrasing that will make the most sense for the audience of the piece (e.g., "existing" is more accessible than "extant" for the majority of readers).

### Hyphenation, Dashes, and Slashes

- "Nonprofit" is one word. "For-profit" is hyphenated.
- "Dual language learners" and "English learners" — no hyphens.
- "Underserved," "socioeconomic," and "underrepresented" — no hyphens, even before "students."
- Pre-kindergarten = "pre-K." Grade range = "K-12." Spell out "pre-K through Grade 12" when combining with other grades.
- Hyphenate compound adjectives before a noun ("low-performing schools") but not after ("the schools are low performing").
- Words ending in "ly" do not take a hyphen ("highly effective").
- Em dashes take a space on either side — like this. Do not use two hyphens (--) as an em dash.
- Use a regular hyphen for ranges (K-12, SY25-26), not an en dash.
- No spaces around forward slashes ("content/questions"). Avoid slashes in written content unless necessary.

### Grammar and Spelling

- "Comprised of" is never correct. Use "comprises" or "is composed of."
- Use “between” for two items and “among” for more than two items. Use “each other” for two people and “one another” for more than two people.
- "Advisers" (not "advisors"), but "advisory" is correct.
- "Child care," "health care," and "ed tech" are each two words.
- Oxford (serial) comma is always required.
- Flag any instance of "pubic" (should be "public").
- Spell out “artificial intelligence (AI)” on first mention and globally use “AI” thereafter in a document.

### Capitalization

- Lowercase "theory of action" and "theory of change."
- Capitalize "Black"; lowercase "white" and "brown."
- Do not hyphenate "Asian American" or "African American."
- Capitalize "Civil Rights Movement" when referring to the 1950s–60s movement.
- "LGBTQ+" is the correct form.
- For report titles and blog post headlines, capitalize the first letter of every word except articles (a, an, the), coordinating conjunctions (and, but, or), and prepositions of three letters or fewer (of, on, to, at, in). An exception is made for e-marketing and other newsletter material subject lines given open-rate techniques.
- Capitalize job titles only when they appear before the person’s name (“Bellwether Senior Partner Anson Jackson” but “Anson Jackson, a senior partner at Bellwether”).

### Person and Voice

- Publications should be written primarily in third person. Foreground the research, not the researchers.
- First person is acceptable when describing research steps/methods or in blog/commentary pieces.
- Field-facing publications should not use "I" or "me" unless in a direct third-party quote.
- Avoid the editorial "we" for broad statements; "we" should refer only to the authors.
- A study cannot "interpret" or "conclude" — only the authors can.

### Abbreviations

- Only abbreviate a term that is repeated in the document. Do not abbreviate terms used only once.
- On first use, write out the full term followed by the abbreviation in parentheses ("Institute of Education Sciences (IES)"); use the abbreviation from that point forward.
- If a document uses too many abbreviations, flag the ones that could be spelled out globally for readability.

### Inclusive and People-First Language

- Use people-first language unless a community prefers identity-first: "students with disabilities" (not "disabled students"), "students in foster care" (not "foster students"), "students from low-income households" (not "low-income students").
- Use "racially minoritized" rather than "minority."
- **Flag deficit-based language with a comment** — do not change it. The author must decide.

### Bellwether-Specific Exceptions to AP Style

- **Teach For America**: Capitalize all three words (exception to AP style).
- **U.S. Department of Education**: Spell out in full where possible; refer to as "the Department" if context is clear. Do not abbreviate as "DOE," "ED," or any other form.
- **Gates Foundation**: As of FY25+, use "Gates Foundation." Remove "Bill & Melinda Gates Foundation."
- **English learners**: Use "English learner students" or "EL students" in field-facing materials. Do not use "English language learners (ELLs)."
- **Free and reduced-price meals**: Use this phrase. If used as a socioeconomic indicator in analysis, write "free and reduced-price meal eligibility (FRPL)" on first mention.
- **Fiscal year**:
  - First mention: "In fiscal year (FY) 2023…"
  - Subsequent: "In FY23…"
  - Ranges: "From FY09 to FY12…" (never "FY09-10")
- **School year**:
  - First mention: "In school year (SY) 2023-24…"
  - Subsequent: "In SY23-24…"
  - Ranges: "From SY23-24 to SY24-25…"

### Deliverable and Audience Considerations
- **Publications**: No contractions, strict AP Style adherence (with house exceptions). Figures, tables, and sidebars are numbered sequentially, and a professional formal tone throughout.
- **Blog Posts**: Less formal than publications, but still professional and requires AP Style adherence. Consider SEO strategies and keyword usage.
- **Client Deliverables**: Professional, but flexible on AP Style (e.g., it may make sense to use first-person or use widely-accepted abbreviations). Prioritize clarity, consistency, and readability.
- **Internal Reference Documents (e.g., How-To Guides)**: Professional but flexible on AP Style. Prioritize BW house rules, spelling, grammar, verbosity, and clarity. May not require full sentences and paragraphs.

---

## What Not to Do

- Do not restructure, reorganize, or cut substantive content.
- Do not suggest new or alternate citations.
- Do not produce a clean copy — every edit must be a tracked change or comment.
- Do not flag things that are already correct.

### Do Not Edit: Protected Sections and Patterns

The following guardrails reflect common rejection patterns. Violating them erodes author trust.

- **Template and boilerplate sections**: Do not edit the Acknowledgments, About Bellwether, About the Authors, or Creative Commons sections. These are organizational templates maintained separately. Skip them entirely.
- **Intentional tense**: Do not change present tense to past (or vice versa) for descriptions of active policies, current formulas, or ongoing programs. A formula "in operation today" should stay in present tense. If tense seems genuinely inconsistent, flag with a comment — do not change it.
- **Intentional hedging**: Do not swap modal verbs ("could" → "would," "may" → "can") unless correcting a specific rule violation such as repetition. Authors often use weaker modals deliberately to reflect uncertainty. When in doubt, leave the original modal and a comment.
- **Domain-specific terminology**: Policy writing uses terms with precise meanings that differ from everyday usage. "Completions" (the count) is not the same as "completion" (the process). For example, "Degree production" is field-standard and should not be changed to "degree completion." "Appropriations" (plural, meaning funds) differs from "appropriation" (the process). When unsure whether a term is field-specific, flag with a comment rather than making a tracked change.
- **Restrictive vs. nonrestrictive clauses**: Do not swap "that" for "which" (or vice versa) when it would change the clause from restrictive to nonrestrictive or the reverse. These have different meanings: "the programs that serve rural students" (only some programs) vs. "the programs, which serve rural students" (all of them). If the author's intent is unclear, flag with a comment.
- **Meaning-preserving constraint**: Do not change singular/plural, add or remove articles, or restructure sentences in ways that shift the author's intended meaning. If the original is grammatically defensible but could be clearer, use a comment suggesting the improvement — do not make the change directly.

---

## Calibration Examples

These examples are drawn from real edits that were accepted by Bellwether authors. Use them to calibrate the level and style of editing expected.

**Verbosity**
- Before: "…but can help to highlight unconventional or newer approaches…"
- After: "…but can help highlight unconventional or newer approaches…"
- Comment: "Verbosity: unnecessary 'to.'"

**Repetition**
- Before: "…including too many metrics may blunt any incentive… new approaches may better align funding…"
- After: "…including too many metrics could blunt any incentive… new approaches may better align funding…"
- Comment: "Repetitive phrasing: 'may' used in adjacent sentences; vary modal verbs."

**AP Style**
- Before: "…focused on a limited set of metrics like completion rates and time to degree."
- After: "…focused on a limited set of metrics, such as completion rates and time to degree."
- Comment: "AP Style: use 'such as' for examples, 'like' for comparisons. Nonrestrictive clause set off by commas."

**Grammar/Spelling**
- Before: "…only exacerbate the issues rather than improving students' experiences…"
- After: "…only exacerbate the issues rather than improve students' experiences…"
- Comment: "Grammar: 'improve' should mirror 'exacerbate' in form to ensure parallelism."

**Precision/Word Choice**
- Before: "…in states where a significant amount of institutional funding comes from local sources…"
- After: "…in states where a significant portion of institutional funding comes from local sources…"
- Comment: "Precision: 'portion' for a share of a whole; 'amount' refers to a total quantity."

**Clarity**
- Before: "…rather, it is a resource for anyone — policymakers, advocates, funders, or others — who seeks to understand…"
- After: "…rather, it serves as a resource for policymakers, advocates, funders, and others seeking to understand…"
- Comment: "Clarity: simplify parenthetical construction."

**Multiple Issues**
- Before: "…credentials awarded to first-generation students might have a premium compared to other students."
- After: "…credentials awarded to first-generation students could carry a premium compared to those of other students."
- Comment: "Word Choice: 'carry a premium' is more precise; 'those of' clarifies the comparison is between credentials, not students. Repetitive Phrasing: 'might' → 'could' to vary modal verbs."