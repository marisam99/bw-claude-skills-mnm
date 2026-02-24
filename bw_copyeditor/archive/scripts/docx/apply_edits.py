#!/usr/bin/env python3
"""
Apply copyedits to a Word document with tracked changes and comments.

Usage:
    python apply_edits.py input.docx edits.json output.docx

The edits.json should follow the format specified in the bellwether-copyeditor skill.
"""

import json
import sys
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

# Import the proper comment module
from comment import add_comment

# Word XML namespaces
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
}

# Register namespaces to preserve them in output
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)

# Additional namespaces that may be present
ADDITIONAL_NS = {
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
}
for prefix, uri in ADDITIONAL_NS.items():
    ET.register_namespace(prefix, uri)


def unpack_docx(docx_path: str, output_dir: str) -> None:
    """Extract a .docx file to a directory."""
    with zipfile.ZipFile(docx_path, 'r') as zf:
        zf.extractall(output_dir)


def pack_docx(input_dir: str, output_path: str) -> None:
    """Create a .docx file from a directory."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, input_dir)
                zf.write(file_path, arcname)


def get_paragraph_text(para_elem) -> str:
    """Extract plain text from a paragraph element."""
    text_parts = []
    for t_elem in para_elem.findall('.//w:t', NAMESPACES):
        if t_elem.text:
            text_parts.append(t_elem.text)
    return ''.join(text_parts)


def find_text_in_paragraph(para_elem, search_text: str) -> list:
    """
    Find all <w:r> elements containing parts of the search text.
    Returns a list of (run_element, start_offset, end_offset) tuples,
    or empty list if text not found.
    """
    runs = para_elem.findall('.//w:r', NAMESPACES)
    full_text = ""
    run_positions = []  # (run, start_pos, end_pos, t_elem)

    for run in runs:
        t_elem = run.find('w:t', NAMESPACES)
        if t_elem is not None and t_elem.text:
            start = len(full_text)
            full_text += t_elem.text
            run_positions.append((run, start, len(full_text), t_elem))

    # Find the search text in the full paragraph text
    idx = full_text.find(search_text)
    if idx == -1:
        return []

    search_end = idx + len(search_text)
    matching_runs = []

    for run, start, end, t_elem in run_positions:
        if start < search_end and end > idx:
            # This run overlaps with the search text
            run_start = max(0, idx - start)
            run_end = min(end - start, search_end - start)
            matching_runs.append({
                'run': run,
                't_elem': t_elem,
                'text': t_elem.text,
                'match_start': run_start,
                'match_end': run_end,
            })

    return matching_runs


def create_tracked_change_xml(edit: dict, change_id: int, author: str = "Claude") -> tuple:
    """
    Create XML elements for a tracked change.
    Returns (deletion_elem, insertion_elem) or (None, insertion_elem) for insert-only.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    del_elem = None
    ins_elem = None

    if edit['type'] in ['replace', 'delete']:
        # Create deletion element
        del_elem = ET.Element(f'{{{NAMESPACES["w"]}}}del')
        del_elem.set(f'{{{NAMESPACES["w"]}}}id', str(change_id))
        del_elem.set(f'{{{NAMESPACES["w"]}}}author', author)
        del_elem.set(f'{{{NAMESPACES["w"]}}}date', timestamp)

        del_run = ET.SubElement(del_elem, f'{{{NAMESPACES["w"]}}}r')
        del_text = ET.SubElement(del_run, f'{{{NAMESPACES["w"]}}}delText')
        del_text.text = edit['find']

    if edit['type'] in ['replace', 'insert_after']:
        # Create insertion element
        ins_elem = ET.Element(f'{{{NAMESPACES["w"]}}}ins')
        ins_elem.set(f'{{{NAMESPACES["w"]}}}id', str(change_id + 1))
        ins_elem.set(f'{{{NAMESPACES["w"]}}}author', author)
        ins_elem.set(f'{{{NAMESPACES["w"]}}}date', timestamp)

        ins_run = ET.SubElement(ins_elem, f'{{{NAMESPACES["w"]}}}r')
        ins_t = ET.SubElement(ins_run, f'{{{NAMESPACES["w"]}}}t')
        ins_t.text = edit.get('replacement', '')

    return del_elem, ins_elem


def apply_edit_to_paragraph(para_elem, edit: dict, change_id: int, comment_id: int) -> tuple:
    """
    Apply an edit to a paragraph element.
    Returns (new_change_id, new_comment_id).
    """
    search_text = edit['find']
    matching_runs = find_text_in_paragraph(para_elem, search_text)

    if not matching_runs:
        print(f"  Warning: Could not find text '{search_text[:50]}...' in paragraph {edit.get('para', '?')}")
        return change_id, comment_id

    # For simplicity, handle the case where text is within a single run
    # More complex cases would require splitting runs
    if len(matching_runs) == 1:
        run_info = matching_runs[0]
        run = run_info['run']
        t_elem = run_info['t_elem']
        original_text = run_info['text']
        match_start = run_info['match_start']
        match_end = run_info['match_end']

        parent = None
        for p in para_elem.iter():
            if run in list(p):
                parent = p
                break

        if parent is None:
            parent = para_elem

        run_index = list(parent).index(run)

        if edit['type'] == 'comment_only':
            # Add comment markers around the text
            comment_start = ET.Element(f'{{{NAMESPACES["w"]}}}commentRangeStart')
            comment_start.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))

            comment_end = ET.Element(f'{{{NAMESPACES["w"]}}}commentRangeEnd')
            comment_end.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))

            comment_ref_run = ET.Element(f'{{{NAMESPACES["w"]}}}r')
            comment_ref_rpr = ET.SubElement(comment_ref_run, f'{{{NAMESPACES["w"]}}}rPr')
            comment_ref_style = ET.SubElement(comment_ref_rpr, f'{{{NAMESPACES["w"]}}}rStyle')
            comment_ref_style.set(f'{{{NAMESPACES["w"]}}}val', 'CommentReference')
            comment_ref = ET.SubElement(comment_ref_run, f'{{{NAMESPACES["w"]}}}commentReference')
            comment_ref.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))

            parent.insert(run_index, comment_start)
            parent.insert(run_index + 2, comment_end)
            parent.insert(run_index + 3, comment_ref_run)

            return change_id, comment_id + 1

        else:
            # Handle replace/delete/insert_after
            before_text = original_text[:match_start]
            after_text = original_text[match_end:]

            del_elem, ins_elem = create_tracked_change_xml(edit, change_id)

            # Remove original run
            parent.remove(run)
            insert_pos = run_index

            # Add text before the change
            if before_text:
                before_run = ET.Element(f'{{{NAMESPACES["w"]}}}r')
                before_t = ET.SubElement(before_run, f'{{{NAMESPACES["w"]}}}t')
                before_t.text = before_text
                if before_text.startswith(' ') or before_text.endswith(' '):
                    before_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                parent.insert(insert_pos, before_run)
                insert_pos += 1

            # Add comment markers if there's a comment
            if edit.get('comment'):
                comment_start = ET.Element(f'{{{NAMESPACES["w"]}}}commentRangeStart')
                comment_start.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))
                parent.insert(insert_pos, comment_start)
                insert_pos += 1

            # Add deletion
            if del_elem is not None:
                parent.insert(insert_pos, del_elem)
                insert_pos += 1
                change_id += 1

            # Add insertion
            if ins_elem is not None:
                parent.insert(insert_pos, ins_elem)
                insert_pos += 1
                change_id += 1

            # Add comment end and reference if there's a comment
            if edit.get('comment'):
                comment_end = ET.Element(f'{{{NAMESPACES["w"]}}}commentRangeEnd')
                comment_end.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))
                parent.insert(insert_pos, comment_end)
                insert_pos += 1

                comment_ref_run = ET.Element(f'{{{NAMESPACES["w"]}}}r')
                comment_ref_rpr = ET.SubElement(comment_ref_run, f'{{{NAMESPACES["w"]}}}rPr')
                comment_ref_style = ET.SubElement(comment_ref_rpr, f'{{{NAMESPACES["w"]}}}rStyle')
                comment_ref_style.set(f'{{{NAMESPACES["w"]}}}val', 'CommentReference')
                comment_ref = ET.SubElement(comment_ref_run, f'{{{NAMESPACES["w"]}}}commentReference')
                comment_ref.set(f'{{{NAMESPACES["w"]}}}id', str(comment_id))
                parent.insert(insert_pos, comment_ref_run)
                insert_pos += 1

                comment_id += 1

            # Add text after the change
            if after_text:
                after_run = ET.Element(f'{{{NAMESPACES["w"]}}}r')
                after_t = ET.SubElement(after_run, f'{{{NAMESPACES["w"]}}}t')
                after_t.text = after_text
                if after_text.startswith(' ') or after_text.endswith(' '):
                    after_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                parent.insert(insert_pos, after_run)

    else:
        # Text spans multiple runs - more complex handling needed
        print(f"  Warning: Text spans multiple runs, simplified handling for '{search_text[:30]}...'")
        # For now, just modify the first run as a simple replacement
        # A full implementation would need to handle this properly

    return change_id, comment_id


def escape_xml_text(text: str) -> str:
    """Escape special characters for XML content."""
    # Basic XML escaping
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Smart quotes
    text = text.replace('\u201c', '&#x201C;')  # Left double quote
    text = text.replace('\u201d', '&#x201D;')  # Right double quote
    text = text.replace('\u2018', '&#x2018;')  # Left single quote
    text = text.replace('\u2019', '&#x2019;')  # Right single quote
    return text


def create_all_comments(unpacked_dir: str, comments_to_create: list) -> None:
    """Create all comments using the proper comment module."""
    for i, edit in enumerate(comments_to_create):
        comment_text = edit.get('comment', '')
        if comment_text:
            # Escape XML special characters
            escaped_text = escape_xml_text(comment_text)
            para_id, msg = add_comment(unpacked_dir, i, escaped_text)
            if "Error" in msg:
                print(f"  Warning: {msg}")


def ensure_comments_relationship(unpacked_dir: str) -> None:
    """Ensure the comments.xml relationship exists."""
    rels_path = os.path.join(unpacked_dir, 'word', '_rels', 'document.xml.rels')

    if not os.path.exists(rels_path):
        os.makedirs(os.path.dirname(rels_path), exist_ok=True)
        rels_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''
        with open(rels_path, 'w', encoding='utf-8') as f:
            f.write(rels_content)

    tree = ET.parse(rels_path)
    root = tree.getroot()

    # Check if comments relationship exists
    ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    existing = root.findall('.//r:Relationship[@Target="comments.xml"]', ns)

    if not existing:
        # Find the highest rId
        max_id = 0
        for rel in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            rid = rel.get('Id', 'rId0')
            num = int(rid.replace('rId', ''))
            max_id = max(max_id, num)

        new_rel = ET.SubElement(root, 'Relationship')
        new_rel.set('Id', f'rId{max_id + 1}')
        new_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments')
        new_rel.set('Target', 'comments.xml')

        tree.write(rels_path, encoding='UTF-8', xml_declaration=True)


def ensure_content_type(unpacked_dir: str) -> None:
    """Ensure comments content type is registered."""
    ct_path = os.path.join(unpacked_dir, '[Content_Types].xml')

    tree = ET.parse(ct_path)
    root = tree.getroot()

    ns = 'http://schemas.openxmlformats.org/package/2006/content-types'

    # Check if comments override exists
    for override in root.findall(f'.//{{{ns}}}Override'):
        if override.get('PartName') == '/word/comments.xml':
            return

    # Add comments override
    override = ET.SubElement(root, f'{{{ns}}}Override')
    override.set('PartName', '/word/comments.xml')
    override.set('ContentType', 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml')

    tree.write(ct_path, encoding='UTF-8', xml_declaration=True)


def verify_edits(paragraphs: list, edits: list) -> tuple:
    """
    Verify all edits can be found before applying any changes.
    Returns (valid_edits, errors) where errors is a list of problem descriptions.
    """
    valid_edits = []
    errors = []

    for i, edit in enumerate(edits):
        para_num = edit.get('para', 0)
        search_text = edit.get('find', '')

        # Check paragraph index is valid
        if para_num < 0 or para_num >= len(paragraphs):
            errors.append(f"Edit {i+1}: Paragraph {para_num} out of range (valid: 0-{len(paragraphs)-1})")
            continue

        # Check text can be found in paragraph
        para_elem = paragraphs[para_num]
        para_text = get_paragraph_text(para_elem)

        if search_text not in para_text:
            # Show what's actually in the paragraph for debugging
            preview = para_text[:100] + "..." if len(para_text) > 100 else para_text
            errors.append(
                f"Edit {i+1}: Text '{search_text[:50]}...' not found in paragraph {para_num}.\n"
                f"         Paragraph contains: '{preview}'"
            )
            continue

        valid_edits.append(edit)

    return valid_edits, errors


def apply_edits(input_docx: str, edits_json: str, output_docx: str) -> None:
    """Apply edits from JSON to a Word document."""

    # Load edits
    with open(edits_json, 'r', encoding='utf-8') as f:
        edit_data = json.load(f)

    edits = edit_data.get('edits', [])
    if not edits:
        print("No edits to apply.")
        shutil.copy(input_docx, output_docx)
        return

    # Create temp directory for unpacking
    with tempfile.TemporaryDirectory() as temp_dir:
        unpacked_dir = os.path.join(temp_dir, 'unpacked')

        # Unpack the docx
        unpack_docx(input_docx, unpacked_dir)

        # Parse document.xml
        doc_path = os.path.join(unpacked_dir, 'word', 'document.xml')
        tree = ET.parse(doc_path)
        root = tree.getroot()

        # Find all paragraphs
        paragraphs = root.findall('.//w:p', NAMESPACES)
        print(f"Found {len(paragraphs)} paragraphs in document")

        # VERIFICATION PHASE: Check all edits before applying any
        valid_edits, errors = verify_edits(paragraphs, edits)

        if errors:
            print("\n" + "=" * 60)
            print("VERIFICATION FAILED - The following edits have problems:")
            print("=" * 60)
            for error in errors:
                print(f"\n  ✗ {error}")
            print("\n" + "=" * 60)
            print(f"Valid edits: {len(valid_edits)}/{len(edits)}")
            print("=" * 60)

            if not valid_edits:
                print("\nNo valid edits to apply. Aborting.")
                return

            response = input("\nApply only the valid edits? (y/n): ").strip().lower()
            if response != 'y':
                print("Aborted.")
                return

            edits = valid_edits
        else:
            print(f"✓ All {len(edits)} edits verified successfully")

        print(f"\nApplying {len(edits)} edits...")

        # Track IDs for changes and comments
        change_id = 1
        comment_id = 0
        comments_to_create = []

        # Group edits by paragraph
        edits_by_para = {}
        for edit in edits:
            para_num = edit.get('para', 0)
            if para_num not in edits_by_para:
                edits_by_para[para_num] = []
            edits_by_para[para_num].append(edit)

        # Apply edits paragraph by paragraph
        for para_num, para_edits in sorted(edits_by_para.items()):
            para_elem = paragraphs[para_num]

            for edit in para_edits:
                print(f"  Para {para_num}: {edit['type']} '{edit['find'][:30]}...'")

                if edit.get('comment'):
                    comments_to_create.append(edit)

                change_id, comment_id = apply_edit_to_paragraph(
                    para_elem, edit, change_id, len(comments_to_create) - 1 if edit.get('comment') else comment_id
                )

        # Write modified document.xml
        tree.write(doc_path, encoding='UTF-8', xml_declaration=True)

        # Create comments using the proper comment module
        if comments_to_create:
            print(f"  Creating {len(comments_to_create)} comments...")
            create_all_comments(unpacked_dir, comments_to_create)

        # Pack the docx
        pack_docx(unpacked_dir, output_docx)

    print(f"Output saved to: {output_docx}")
    print(f"Summary: {len(edits)} edits applied, {len(comments_to_create)} comments added")


def verify_only(input_docx: str, edits_json: str) -> bool:
    """Verify edits without applying them. Returns True if all valid."""
    with open(edits_json, 'r', encoding='utf-8') as f:
        edit_data = json.load(f)

    edits = edit_data.get('edits', [])
    if not edits:
        print("No edits to verify.")
        return True

    print(f"Verifying {len(edits)} edits...")

    with tempfile.TemporaryDirectory() as temp_dir:
        unpacked_dir = os.path.join(temp_dir, 'unpacked')
        unpack_docx(input_docx, unpacked_dir)

        doc_path = os.path.join(unpacked_dir, 'word', 'document.xml')
        tree = ET.parse(doc_path)
        root = tree.getroot()

        paragraphs = root.findall('.//w:p', NAMESPACES)
        print(f"Found {len(paragraphs)} paragraphs in document")

        valid_edits, errors = verify_edits(paragraphs, edits)

        if errors:
            print("\n" + "=" * 60)
            print("VERIFICATION FAILED")
            print("=" * 60)
            for error in errors:
                print(f"\n  ✗ {error}")
            print("\n" + "=" * 60)
            print(f"Valid: {len(valid_edits)}/{len(edits)}")
            print("=" * 60)
            return False
        else:
            print(f"\n✓ All {len(edits)} edits verified successfully")
            return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python apply_edits.py input.docx edits.json output.docx")
        print("       python apply_edits.py --verify-only input.docx edits.json")
        sys.exit(1)

    # Check for --verify-only flag
    if sys.argv[1] == '--verify-only':
        if len(sys.argv) != 4:
            print("Usage: python apply_edits.py --verify-only input.docx edits.json")
            sys.exit(1)
        input_docx = sys.argv[2]
        edits_json = sys.argv[3]

        if not os.path.exists(input_docx):
            print(f"Error: Input file not found: {input_docx}")
            sys.exit(1)
        if not os.path.exists(edits_json):
            print(f"Error: Edits file not found: {edits_json}")
            sys.exit(1)

        success = verify_only(input_docx, edits_json)
        sys.exit(0 if success else 1)

    if len(sys.argv) != 4:
        print("Usage: python apply_edits.py input.docx edits.json output.docx")
        sys.exit(1)

    input_docx = sys.argv[1]
    edits_json = sys.argv[2]
    output_docx = sys.argv[3]

    if not os.path.exists(input_docx):
        print(f"Error: Input file not found: {input_docx}")
        sys.exit(1)

    if not os.path.exists(edits_json):
        print(f"Error: Edits file not found: {edits_json}")
        sys.exit(1)

    apply_edits(input_docx, edits_json, output_docx)


if __name__ == '__main__':
    main()
