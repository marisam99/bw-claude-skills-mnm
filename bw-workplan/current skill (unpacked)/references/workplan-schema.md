# workplan.json Schema

This is the expected structure for the JSON file that `generate_workplan.py` consumes. Every field shown below is required unless noted otherwise.

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

## Field notes

- `team_members` must always have exactly 5 elements, padded with `""` if the project has fewer than 5 people.
- `team_capacity` (in each timeline entry) must also have exactly 5 elements, one per position in `team_members`.
- `feasibility_flag` must be one of: `"ok"`, `"tight"`, `"infeasible"`.
- Milestone `type` must be one of: `"internal"`, `"external"`.
- All dates use `YYYY-MM-DD` format. Display dates use `M/D/YYYY`.
- `dependencies` is an array of task ID strings (e.g., `["T01", "T03"]`). Empty array if no dependencies.
- `notes` on tasks is nullable — use it to flag assumptions, inferences, or converted units.
