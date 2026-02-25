---
name: bw-workplan
description: Generate a project workplan spreadsheet (.xlsx) from a Statement of Work, proposal, or project description. Reads the document, accepts project start and end dates, team member names, cost code, and PTO/OOO dates, extracts phases, workstreams, tasks, deliverables, and milestones, estimates durations, backwards-maps deadlines from the final due date, checks feasibility, and produces a formatted Excel file based on the Bellwether workplan template (Cover Sheet, Project Timeline, Detailed Workplan). Use when the user asks to build a workplan, project schedule, or task timeline.
---

# Bellwether Workplan Generator

Reads a SOW or project description, infers the task structure and schedule, and outputs a formatted `.xlsx` workplan the user can upload to Google Drive or open in Excel.

## Contents
- Workflow
- workplan.json Schema
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
> 5. Any PTO, holidays, or OOO dates to block off? Paste as a list."

Do not proceed to Step 3 until both dates are confirmed. Start date is required; end date is required. If start date is missing, use the next business day from today and flag it as a placeholder.

### Step 3: Extract project structure

Identify and list:
- **Phases**: Named project phases or stages. If not explicitly named, infer from deliverables and headings. Fallback: "Discovery / Development / Delivery."
- **Workstreams**: Recurring work categories within phases (e.g., "Research," "Stakeholder Engagement," "Communications"). Set to null if not applicable.
- **Tasks**: One action verb per task. Decompose deliverables into their constituent tasks (e.g., "Draft report" → "Write draft," "Internal review," "Revise and finalize"). Extract enough tasks to fill the schedule.
- **Dependencies**: Which tasks must finish before others can start. Record as task ID references.
- **Owners**: Assign by name if the SOW specifies. Otherwise set to null.
- **Milestones**: Deliverables due to the client or external parties (`type: "external"`), internal checkpoints like reviews or presentations (`type: "internal"`).

Note any structural inferences in the task `notes` field (e.g., "Inferred from 'Phase 2 deliverable' language in SOW section 3").

### Step 4: Estimate durations

Use `references/estimation-guide.md` as your primary reference. Key heuristics:

- Kickoff meeting: 1–2 days
- Per stakeholder interview: 1 day (active); add 2–3 days scheduling lag per round
- Desk/literature review (broad): 5–10 days
- Interview synthesis (per 5–8 interviews): 3–5 days
- Draft report (per 10–15 pages): 5–10 days
- Draft deck (per 15–20 slides): 3–5 days
- Internal review round: 2–3 days
- Client/external review: 3–5 days
- Revisions (light): 1–2 days; (major rework): 3–5 days
- Delivery/presentation: 1 day
- PM overhead: 0.5 days/week ongoing

Default to **3 business days** for any task without a matching heuristic, and note the assumption.

Sum all durations as `estimated_total_days`.

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

Write the complete JSON to `workplan.json`. Before finalizing, verify:

- [ ] All task IDs are unique
- [ ] No `dependencies` reference an ID that doesn't exist
- [ ] All dates are `YYYY-MM-DD` format
- [ ] All `start_date` and `deadline` values are business days (not weekends, not in `pto_dates`)
- [ ] `timeline[]` has one entry per calendar week (no gaps, no duplicates)
- [ ] Each `team_capacity` array has exactly 5 elements
- [ ] `estimated_total_days` equals the sum of all task `duration_days`
- [ ] `feasibility_flag` is consistent with `estimated_total_days / available_business_days`

### Step 8: Run the script

```bash
python bw-workplan/generate_workplan.py workplan.json [project-name]-workplan.xlsx
```

Share the output `.xlsx` file with the user. If `feasibility_flag` is not `"ok"`, call it out explicitly:

> "Note: This timeline is **[tight / infeasible]**. [feasibility_note]. The workplan has been generated anyway — a warning banner appears at the top of the Detailed Workplan tab."

---

## workplan.json Schema

```json
{
  "metadata": {
    "project_name": "string",
    "generated_date": "YYYY-MM-DD",
    "source_document": "filename or 'pasted text'",
    "notes": "top-level assumptions or caveats"
  },
  "project": {
    "name": "string",
    "cost_code": "string or null",
    "team_members": ["Alice", "Bob", "", "", ""]
  },
  "calendar": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "available_business_days": 47,
    "estimated_total_days": 38,
    "feasibility_flag": "ok",
    "feasibility_note": "38 estimated days fit comfortably within 47 available days.",
    "pto_dates": ["YYYY-MM-DD"]
  },
  "tasks": [
    {
      "id": "T01",
      "phase": "Phase 1: Discovery",
      "workstream": "Research",
      "task": "Conduct kickoff meeting",
      "owner": "Alice",
      "duration_days": 1,
      "dependencies": [],
      "start_date": "2025-03-03",
      "start_date_display": "3/3/2025",
      "deadline": "2025-03-03",
      "deadline_display": "3/3/2025",
      "notes": null
    }
  ],
  "milestones": [
    {
      "name": "Kickoff",
      "type": "internal",
      "date": "2025-03-03",
      "date_display": "3/3/2025"
    }
  ],
  "timeline": [
    {
      "week_start": "2025-03-03",
      "week_display": "3/3/2025",
      "internal_meetings": "Kickoff (Mon 3/3)",
      "external_meetings": "",
      "phase": "Phase 1: Discovery",
      "key_activities": "Kickoff meeting, begin desk research",
      "deadlines_milestones": "Kickoff",
      "pto": "",
      "team_capacity": ["", "", "", "", ""]
    }
  ]
}
```

`team_capacity` must always have exactly 5 elements, one per position in `project.team_members`, even if the project has fewer than 5 team members.

---

## Edge Cases

| Situation | Handling |
|---|---|
| No start date | Use next business day from today; flag in `metadata.notes` as placeholder |
| No end date | Ask for it; do not proceed without it |
| No OOO/PTO | Set `pto_dates: []`; note "all business days treated as available" |
| Infeasible timeline | Set flag and note; still generate the file; warning banner appears in workplan |
| No phases in SOW | Infer from headings and deliverables; fallback: Discovery / Development / Delivery |
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
