# Task Duration Estimation Guide

## Purpose

This file provides generic heuristics for estimating task durations in business days. Use it during Step 4 of the workplan workflow to assign `duration_days` to each task. These are starting points — adjust based on team size, document complexity, stakeholder availability, and explicit SOW timelines.

---

## General Principles

1. **Elapsed time ≠ active working time.** A task estimated at 5 business days may span 2 calendar weeks if the team works on other things in parallel. Estimate active working time; the scheduling step handles elapsed time.

2. **Buffer at the phase level, not the task level.** Individual task estimates should be realistic best-estimates. Add a buffer at the end of each phase — typically 10–15% of the phase's total estimated duration — rather than padding every task individually.

3. **Review cycles are almost always underestimated.** Assume at least one round of revisions per deliverable unless the SOW explicitly states otherwise. When in doubt, add a revision task.

4. **Stakeholder-dependent tasks have high variance.** Estimate the active work, then add 2–3 business days of scheduling and response lag for any task that requires external feedback, approval, or coordination (interviews, client reviews, external sign-offs).

5. **Sequential reviews take longer than parallel.** If the SOW says "reviewed by X, then reviewed by Y," plan for the reviews to happen in sequence. Each reviewer adds their own duration.

---

## Duration Heuristics by Task Category

| Task Type | Typical Range (business days) | Notes |
|---|---|---|
| Project kickoff meeting (prep + meeting + notes) | 1–2 | Includes agenda preparation and follow-up action items |
| Stakeholder interview (per interview) | 1 | Active interview time only; scheduling lag is separate |
| Interview scheduling and coordination (per round) | 2–3 | Add to any task block involving interview scheduling |
| Desk/literature review (broad scope) | 5–10 | Scales with number of sources; flag if scope is unclear |
| Desk/literature review (targeted) | 2–5 | For a defined list of sources or data sets |
| Data pull and cleaning | 2–5 | Highly variable; flag with a note if data availability is uncertain |
| Quantitative analysis (defined dataset) | 3–7 | Depends on complexity of methods |
| Interview synthesis (per 5–8 interviews) | 3–5 | Identifying themes, writing up, cross-referencing |
| Document or landscape synthesis | 3–5 | Organizing findings from multiple sources |
| Draft report or memo (per 10–15 pages) | 5–10 | Allow more time for longer or more complex documents |
| Draft presentation (per 15–20 slides) | 3–5 | Allows for design iteration; assumes content is mostly developed |
| Internal review round | 2–3 | Per reviewer; add 1 day per additional reviewer |
| Client or external review round | 3–5 | Includes lag for client response; increases with client responsiveness uncertainty |
| Revisions after review (light edits) | 1–2 | For minor feedback; increase to 3–5 for substantial restructuring |
| Revisions after review (major rework) | 3–5 | Use when review is likely to require new content or restructuring |
| Stakeholder presentation delivery | 1 | Includes final prep and run-through |
| Project management overhead (per week) | 0.5 | Ongoing coordination, status updates, team check-ins |
| Project setup (folder creation, scheduling, onboarding) | 1–2 | One-time at project start |

---

## Reading SOW Language for Implicit Timeline Signals

When the SOW doesn't specify durations explicitly, use these signals:

| SOW phrase or pattern | How to interpret it |
|---|---|
| "X-week phase" or "X-week sprint" | X × 5 business days; divide by task count within the phase to distribute |
| "approximately X months" | X × 22 business days (about 4.4 weeks per month) |
| "rapid turnaround" or "accelerated timeline" | Compress estimates by 30–40%; flag the resulting schedule as aggressive |
| "iterative" or "agile approach" | Plan for at least 2 review-revise cycles per major deliverable |
| "pending client approval" or "subject to feedback" | Add 3–5 business days of lag after each deliverable delivery |
| "subject to stakeholder availability" | Add 2–3 days of scheduling buffer per meeting or interview block |
| "at the conclusion of Phase X" or "following delivery of X" | Hard dependency; do not start the task until the predecessor phase/deliverable is complete |
| "working sessions" or "co-creation" | Plan for preparation (1–2 days), facilitation (1 day), and synthesis (2–3 days) per session |
| "weekly check-ins" or "regular touchpoints" | Include a 0.5 day/week PM overhead task for the duration |
| "final deliverable" | Count backwards: final delivery date → client review window (3–5 days) → revision (2–3 days) → draft complete |

---

## Feasibility Thresholds

After summing all task durations, compare against available business days (start → end date, excluding OOO/PTO):

| Ratio (estimated ÷ available) | Feasibility flag | What it means |
|---|---|---|
| ≤ 90% | `ok` | Comfortable — adequate buffer for unexpected delays |
| 90–100% | `tight` | Achievable but no buffer; flag clearly; consider reducing scope or extending 1 week |
| > 100% | `infeasible` | Tasks cannot fit in the window; strongly recommend scope reduction or timeline extension |

Always include the feasibility note in the summary message, not just the flag.

---

## Default Fallback

If no heuristic above applies and no timeline signal is present in the SOW, assign **3 business days** and add a note:

> "Duration estimated generically at 3 days — review with project team before sharing externally."

This is conservative enough to avoid obviously wrong estimates while keeping the workplan usable as a starting point.
