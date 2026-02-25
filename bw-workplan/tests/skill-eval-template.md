# Skill Evaluation Template: bw-workplan

Use this checklist after running the bw-workplan skill to evaluate the output. Open the generated `.xlsx` in Excel or Google Sheets and review the conversation transcript.

**Test input:**
**Project dates used:**
**Team members used:**
**OOO dates used:**

---

## Part 1: Conversation and Skill Behavior

### 1.1 Information Gathering

- [ ] Skill asked for start date, end date, team members, cost code, and OOO before building the schedule
- [ ] Asked in a single message (not multiple back-and-forth rounds)
- [ ] Did not proceed until dates were confirmed

### 1.2 Summary Message

- [ ] Summary clearly states project name, timeline window, and feasibility status
- [ ] Task count mentioned
- [ ] If timeline is tight or infeasible: explicitly called out with explanation
- [ ] Any assumptions or inferences noted (e.g., "I inferred phases from the SOW headings")

---

## Part 2: Cover Sheet

- [ ] Project name is correct (not "Untitled Project" or placeholder)
- [ ] Cost code matches what was provided (or blank if none)
- [ ] Team member names listed correctly
- [ ] Phase names listed and match the phases used in the Detailed Workplan

---

## Part 3: Project Timeline

- [ ] Week columns start from the project start date
- [ ] Week columns end at or near the project end date
- [ ] No extra blank week columns visible after the project ends
- [ ] Team member names match the Cover Sheet
- [ ] Phase names appear for each week and progress logically
- [ ] Key activities are populated for active weeks (not all blank)
- [ ] Milestones and deadlines appear in the correct weeks
- [ ] OOO/PTO notes appear in the correct weeks (if applicable)
- [ ] Team capacity rows reflect individual OOO correctly (if applicable)

---

## Part 4: Detailed Workplan

### 4.1 Task Content

- [ ] Tasks are specific and actionable (action verbs, not vague labels)
- [ ] Deliverables are decomposed into steps (e.g., "Draft report" broken into drafting, review, revision)
- [ ] At least 3 distinct phases visible
- [ ] Reasonable number of tasks (typically 15+ for a multi-phase project)
- [ ] Dependencies make sense (e.g., synthesis comes after interviews, not before)
- [ ] Client review periods are included where the SOW specifies them
- [ ] Owners assigned where specified in the SOW (or blank if not)

### 4.2 Dates

- [ ] All start dates fall on weekdays
- [ ] All deadlines fall on weekdays
- [ ] No tasks start before the project start date
- [ ] No tasks end after the project end date
- [ ] Start date is on or before deadline for every task
- [ ] No tasks scheduled during OOO dates (if applicable)
- [ ] Dates progress logically (earlier phases have earlier dates)

### 4.3 Formatting and Interactivity

- [ ] Status column defaults to "Not started" for all tasks
- [ ] Status dropdown works (click a status cell — should show Not started / To-Do / In progress / Completed)
- [ ] Changing status to "Completed" grays out the row
- [ ] If timeline is tight/infeasible: orange warning banner appears at the top of the task list
- [ ] If timeline is feasible: no warning banner

---

## Part 5: Overall Quality

- [ ] The workplan is a reasonable interpretation of the source document
- [ ] Phase structure makes sense for the project
- [ ] Duration estimates feel realistic (not all tasks defaulting to 3 days)
- [ ] Schedule has some buffer (not every day packed end-to-end)
- [ ] Could share this with a project team as a starting point without embarrassment

---

## Summary

| Check area | Items | Pass | Fail | Notes |
|---|---|---|---|---|
| Conversation & behavior | 7 | | | |
| Cover Sheet | 4 | | | |
| Project Timeline | 9 | | | |
| Task content | 7 | | | |
| Dates | 7 | | | |
| Formatting & interactivity | 5 | | | |
| Overall quality | 5 | | | |
| **Total** | **44** | | | |

**Overall verdict:** Pass / Fail / Pass with notes

**Issues to address:**

1.
2.
3.
