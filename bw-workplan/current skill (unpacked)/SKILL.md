---
name: bw-workplan
description: Generate a project workplan spreadsheet (.xlsx) from a Statement of Work, proposal, or project description. Use when the user asks to build a workplan, project plan, project schedule, task timeline, or Gantt-style tracker — especially for Bellwether consulting projects. Also trigger when the user uploads a SOW and asks to turn it into a schedule or timeline, or mentions "workplan," "project plan," "task breakdown," or "schedule from SOW."
---

# Bellwether Workplan Generator

Reads a SOW or project description, infers the task structure and schedule, and outputs a formatted `.xlsx` workplan the user can upload to Google Drive or open in Excel.

## Contents
- Workflow
- Edge Cases

---

## Workflow

### Step 1: Read the document

Read the full document before doing anything else. Note:
- All phases, workstreams, deliverables, and tasks explicitly mentioned
- Any deadline, date, or timeline signal (explicit or implicit — see `references/estimation-guide.md`)
- Owner assignments, if named
- Any OOO or PTO mentioned in the document itself

### Step 2: Gather missing information

If any of the following are missing, ask in a single message before proceeding:

> "Before I build the schedule, I need a few things:
> 1. What is the project start date?
> 2. What is the final deadline or project end date?
> 3. Who are the team members? (up to 5 names)
> 4. What is the cost code? (or skip)
> 5. Any PTO, holidays, significant work travel, or OOO dates to block off? Paste as a list."

Do not proceed to Step 3 until both dates are confirmed. Start date is required; end date is required. If start date is missing, use the next business day from today and flag it as a placeholder.

### Step 3: Extract project structure

Identify and list:
- **Phases**: Named project phases or stages. If not explicitly named, infer from deliverables and headings. Fallback: "Phase 0 - Setup / Phase 1 - Factbase / Phase 2 - Client Support / Phase 3 - Strategy Development / Phase 4 - Client Support / Phase 5 - Implementation Planning."
- **Workstreams**: Recurring work categories within phases (e.g., "Research," "Stakeholder Engagement," "Communications"). Set to null if not applicable.
- **Tasks**: One action verb per task. Decompose deliverables into their constituent tasks (e.g., "Draft report" → "Write draft," "Internal review," "Revise and finalize"). Extract enough tasks to fill the schedule.
- **Dependencies**: Which tasks must finish before others can start. Record as task ID references.
- **Owners**: Assign by name if the SOW specifies. Otherwise set to null.
- **Milestones**: Deliverables due to the client or external parties (`type: "external"`), internal checkpoints like reviews (`type: "internal"`).

Note any structural inferences in the task `notes` field (e.g., "Inferred from 'Phase 2 deliverable' language in SOW section 3").

### Step 4: Estimate durations

Use `references/estimation-guide.md` as your primary reference. Default to **3 business days** for any task without a matching heuristic, and note the assumption. Sum all durations as `estimated_total_days`.

### Step 5: Check feasibility and assign dates

**Count available business days:**
- Start from `calendar.start_date`, end at `calendar.end_date`
- Exclude weekends and all dates in `calendar.pto_dates`
- Store result as `available_business_days`

**Set feasibility flag:**

| Ratio (estimated ÷ available) | Flag | Note |
|---|---|---|
| ≤ 90% | `ok` | Adequate buffer |
| 90–100% | `tight` | No buffer; recommend scope reduction or +1 week |
| > 100% | `infeasible` | Tasks cannot fit; recommend scope reduction or deadline extension |

Always populate `feasibility_note` with a plain-English sentence (e.g., "38 estimated days fit comfortably within 47 available days" or "Timeline is infeasible: 62 estimated days exceed 47 available. Recommend reducing scope or extending the end date by 3 weeks.").

**Assign dates (backwards-map from end date):**

1. Divide the project window proportionally across phases by their estimated day totals.
2. Within each phase, work backwards in reverse dependency order:
   - The last task in a phase ends on the last day of the phase window.
   - Each prior task ends the business day before its successor begins.
   - `start_date` = `deadline` − `duration_days` + 1 (in business days, skipping weekends and OOO).
3. Parallel tasks (no dependency between them) share the same start and deadline within their phase window.
4. Ensure `start_date` is never before the project `start_date`.
5. All dates must be business days (not weekends, not in `pto_dates`).
6. Store both machine-readable (`YYYY-MM-DD`) and display (`M/D/YYYY`) formats for every task date.

### Step 6: Build the timeline matrix

For each calendar week from `start_date` through `end_date` (week starting Monday):

- `week_start`: the Monday of that week (`YYYY-MM-DD`)
- `week_display`: formatted as `M/D/YYYY`
- `internal_meetings`: any internal milestone or meeting this week (e.g., `"Kickoff (Mon 3/3)"`)
- `external_meetings`: any external-facing meeting or delivery this week
- `phase`: the phase name active this week (use the phase of the majority of tasks active this week)
- `key_activities`: comma-separated short names of tasks with deadlines or active work this week
- `deadlines_milestones`: milestone names with dates (e.g., `"Draft report due (3/26)"`)
- `pto`: team-wide OOO notes this week (e.g., `"Alice OOO Fri 3/14"`)
- `team_capacity`: array of 5 strings — one per position in `project.team_members` (in order). Each entry is a short OOO note for that person this week, or `""` if they are available. Array length must always equal 5, padded with `""`.

### Step 7: Write workplan.json

Write the complete JSON to `workplan.json`. See `references/workplan-schema.md` for the full schema with field notes. Before finalizing, verify:

- [ ] All task IDs are unique
- [ ] No `dependencies` reference an ID that doesn't exist
- [ ] All dates are `YYYY-MM-DD` format
- [ ] All `start_date` and `deadline` values are business days (not weekends, not in `pto_dates`)
- [ ] `timeline[]` has one entry per calendar week (no gaps, no duplicates)
- [ ] Each `team_capacity` array has exactly 5 elements
- [ ] `estimated_total_days` equals the sum of all task `duration_days`
- [ ] `feasibility_flag` is consistent with `estimated_total_days / available_business_days`

### Step 8: Run the script

This script uses the `workplan.json` to fill in an Excel template set up by the user:

```bash
python bw-strat-workplan/scripts/generate_workplan.py workplan.json [project-name]-workplan.xlsx
```

Save the output `.xlsx` file to the user's workspace directory so they can access it. Share it with the user. If `feasibility_flag` is not `"ok"`, call it out explicitly:

> "Note: This timeline is **[tight / infeasible]**. [feasibility_note]. The workplan has been generated anyway — a warning banner appears at the top of the Detailed Workplan tab."

---

## Edge Cases

| Situation | Handling |
|---|---|
| No start date | Use next business day from today; flag in `metadata.notes` as placeholder |
| No end date | Ask for it; do not proceed without it |
| No OOO/PTO | Set `pto_dates: []`; note "all business days treated as available" |
| Infeasible timeline | Set flag and note; still generate the file; warning banner appears in workplan |
| No phases in SOW | Infer from headings and deliverables; fallback: Phase 0 - Setup / Phase 1 - Factbase / Phase 2 - Client Support / Phase 3 - Strategy Development / Phase 4 - Client Support / Phase 5 - Implementation Planning |
| No workstreams | Set `workstream: null`; leave Workstream column blank |
| No owners named | Set `owner: null`; leave Owner column blank |
| No cost code | Set `cost_code: null`; leave cell blank |
| Fewer than 5 team members | Pad `team_members` to exactly 5 with `""` |
| Parallel tasks | Same start and deadline within phase window; no dependency between them |
| Hours specified instead of days | Convert: 8h = 1 day; note conversion in task `notes` |
| Circular dependency | Flag in both tasks' `notes`; assign dates sequentially as if the cycle were broken |
| Project exceeds 25 weeks | Script warns and truncates timeline display at week 25; note in summary to user |
| SOW says "rapid turnaround" | Compress estimates by 30–40%; flag schedule as aggressive in `feasibility_note` |
| SOW says "iterative" or "agile" | Plan for at least 2 review-revise cycles per major deliverable |
| SOW says "pending client approval" | Add 3–5 business days lag after each deliverable delivery task |
