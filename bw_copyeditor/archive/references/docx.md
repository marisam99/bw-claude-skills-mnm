# Word Document (.docx) Workflow

This reference covers the technical workflow for copyediting Word documents.

## Overview

Word documents use a two-step process:
1. Extract text with paragraph indices
2. Apply edits as tracked changes with comments

## Step 1: Extract Text

Run the extraction script to get the document text with paragraph indices:
```bash
python <skill_location>/scripts/docx/extract_text.py <input.docx>
```

This outputs each paragraph with its index:
```
[ 14] Formulating Success
[ 15] A Primer on Outcomes-Based Funding
[ 50] In fiscal year (FY) 2024, states contributed...
```

Use these indices in the `para` field of your edit JSON.

## Step 2: Review and Create Edit JSON

Review the extracted text following the copyediting phases in the main skill. Create a JSON edit list using the paragraph indices from Step 1.

Save the JSON to a file (e.g., `edits.json`):
```json
{
  "deliverable_type": "publication",
  "edits": [
    {
      "type": "replace",
      "para": 50,
      "find": "fiscal year (FY) 2024",
      "replacement": "fiscal year (FY) 2025",
      "comment": "Updated to current fiscal year",
      "category": "factual"
    }
  ],
  "summary": {"factual": 1}
}
```

## Step 3: Apply Edits

Run the apply script to create the output document with tracked changes:
```bash
echo "y" | python <skill_location>/scripts/docx/apply_edits.py <input.docx> edits.json <output.docx>
```

The script will:
1. Verify all edits can be found
2. Apply tracked changes (deletions/insertions)
3. Add comments with rationale
4. Create the output file

## Step 4: Provide Output

Share the output `.docx` file with the user. It contains:
- Tracked changes (deletions in strikethrough, insertions highlighted)
- Comments attached to each edit
- Author set to "Claude"

The user can review in Microsoft Word and accept/reject changes.

## Edit Types

| Type | Description |
|------|-------------|
| `replace` | Delete `find` text and insert `replacement` |
| `delete` | Remove `find` text entirely |
| `insert_after` | Insert `replacement` after `find` text |
| `comment_only` | Add comment anchored to `find` text without changing it |

## Important Notes

- The `para` field must match indices from `extract_text.py`
- Text must exist exactly as written in the specified paragraph
- The script verifies all edits before applying any changes
- Replace `<skill_location>` with the actual path to this skill's directory

## Verification Mode

To check edits without applying them:
```bash
python <skill_location>/scripts/docx/apply_edits.py --verify-only <input.docx> edits.json
```

This reports any edits that would fail (wrong paragraph index or text not found).
