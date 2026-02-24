#!/usr/bin/env python3
"""
apply_copyedits.py — Apply tracked changes and comments to a Word .docx file.

Reads a JSONL findings file produced by the Bellwether copyeditor skill,
applies each finding as a tracked change or comment in the source docx, and
writes the result to an output docx.

Usage:
    python apply_copyedits.py <source.docx> <findings.jsonl> <output.docx>

Requirements:
    - Python 3.8+
    - lxml (installed automatically if missing)

The script uses lxml to parse and modify the OOXML inside the docx. This is
critical: Python's built-in xml.etree.ElementTree does NOT preserve namespace
prefixes (it rewrites w:del to ns0:del, etc.), which causes Word to report
"unreadable content." lxml preserves prefixes exactly.
"""

import copy
import json
import os
import random
import re
import subprocess
import sys
import zipfile

# ─── Ensure lxml is available ───────────────────────────────────────────────
try:
    from lxml import etree
except ImportError:
    print("lxml not found. Installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "lxml", "--break-system-packages"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    from lxml import etree

# ─── OOXML Namespaces ───────────────────────────────────────────────────────
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
W16CID = "http://schemas.microsoft.com/office/word/2016/wordml/cid"
XML_NS = "http://www.w3.org/XML/1998/namespace"

AUTHOR = "Claude"
RSID = "00AA0001"

# ═══════════════════════════════════════════════════════════════════════════
#  ENSURE COMMENTS.XML FILE EXISTS
# ═══════════════════════════════════════════════════════════════════════════
def ensure_comments_infrastructure(work_dir, src_docx):
    """Ensure comments.xml exists and is registered in rels and [Content_Types].xml."""

    comments_path = os.path.join(work_dir, "word", "comments.xml")
    rels_path = os.path.join(work_dir, "word", "_rels", "document.xml.rels")
    ct_path = os.path.join(work_dir, "[Content_Types].xml")

    COMMENTS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
    COMMENTS_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
    CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

    # 1. Create comments.xml if missing
    if not os.path.exists(comments_path):
        nsmap = {
            'w': W,
            'w14': W14,
            'w15': W15,
            'r': "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
            'mc': "http://schemas.openxmlformats.org/markup-compatibility/2006",
        }
        root = etree.Element(f'{{{W}}}comments', nsmap=nsmap)
        tree = etree.ElementTree(root)
        tree.write(comments_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # 2. Add relationship if missing
    _parser = etree.XMLParser(remove_blank_text=False)
    rels_tree = etree.parse(rels_path, _parser)
    rels_root = rels_tree.getroot()
    max_rid = 0
    has_rel = False
    for rel in rels_root:
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                max_rid = max(max_rid, int(rid[3:]))
            except ValueError:
                pass
        if rel.get('Type') == COMMENTS_REL_TYPE:
            has_rel = True
    if not has_rel:
        rel_elem = etree.SubElement(rels_root, 'Relationship')
        rel_elem.set('Id', f'rId{max_rid + 1}')
        rel_elem.set('Type', COMMENTS_REL_TYPE)
        rel_elem.set('Target', 'comments.xml')
        rels_tree.write(rels_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # 3. Add content type if missing
    ct_tree = etree.parse(ct_path, _parser)
    ct_root = ct_tree.getroot()
    has_ct = any(
        o.get('PartName') == '/word/comments.xml'
        for o in ct_root.findall(f'{{{CT_NS}}}Override')
    )
    if not has_ct:
        override = etree.SubElement(ct_root, f'{{{CT_NS}}}Override')
        override.set('PartName', '/word/comments.xml')
        override.set('ContentType', COMMENTS_CT)
        ct_tree.write(ct_path, xml_declaration=True, encoding='UTF-8', standalone=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PARSE FINDINGS
# ═══════════════════════════════════════════════════════════════════════════

def parse_findings(findings_path):
    """Parse a JSONL findings file into a list of dicts.

    Each line must be a valid JSON object with keys:
        type        — "tracked_change" or "comment_only"
        category    — issue category name
        comment     — rationale text for the Word comment
        old_text    — (tracked_change) exact text to replace
        new_text    — (tracked_change) replacement text
        anchor_text — (comment_only) exact text to attach the comment to
    """
    findings = []
    with open(findings_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                finding = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  WARNING: line {i} invalid JSON, skipping: {e}")
                continue

            # Validate required fields
            ftype = finding.get('type', '')
            if ftype not in ('tracked_change', 'comment_only'):
                print(f"  WARNING: line {i} unknown type '{ftype}', skipping")
                continue

            if ftype == 'tracked_change':
                old = finding.get('old_text', '')
                new = finding.get('new_text', '')
                if not old:
                    print(f"  WARNING: line {i} tracked_change missing old_text, skipping")
                    continue
                if old == new:
                    print(f"  WARNING: line {i} identity edit (old==new), skipping: "
                          f"{old[:60]}...")
                    continue

            elif ftype == 'comment_only':
                if not finding.get('anchor_text', ''):
                    print(f"  WARNING: line {i} comment_only missing anchor_text, skipping")
                    continue

            findings.append(finding)

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  XML MANIPULATION
# ═══════════════════════════════════════════════════════════════════════════

# Common em-dash variants for encoding retry
EM_DASH_VARIANTS = [
    '\u2014',       # Unicode em dash
    '---',          # triple hyphen (pandoc convention)
    '\u2013',       # en dash (sometimes used erroneously)
    '--',           # double hyphen
]


def normalize_for_search(text):
    """Generate search variants for text containing em dashes or special chars."""
    variants = [text]
    for em in EM_DASH_VARIANTS:
        if em in text:
            for replacement in EM_DASH_VARIANTS:
                if replacement != em:
                    variants.append(text.replace(em, replacement))
    # Also try curly vs straight quotes
    curly_to_straight = text.replace('\u2018', "'").replace('\u2019', "'") \
                            .replace('\u201c', '"').replace('\u201d', '"')
    if curly_to_straight != text:
        variants.append(curly_to_straight)
    straight_to_curly = text.replace("'", '\u2019').replace('"', '\u201d')
    if straight_to_curly != text:
        variants.append(straight_to_curly)
    return variants


def find_text_in_paragraph(para, search_text):
    """Find runs containing search_text when concatenated.

    Returns list of (run_element, text_element, local_start, local_end) or None.
    Tries encoding variants if the literal text isn't found.
    """
    runs = para.findall(f'.//{{{W}}}r')
    if not runs:
        return None

    # Build text map from runs NOT inside existing del/ins
    text_map = []
    pos = 0
    for run in runs:
        parent = run.getparent()
        if parent.tag in (f'{{{W}}}del', f'{{{W}}}ins'):
            continue
        t_elem = run.find(f'{{{W}}}t')
        if t_elem is not None and t_elem.text:
            text_map.append((run, t_elem, pos, pos + len(t_elem.text)))
            pos += len(t_elem.text)
        else:
            text_map.append((run, t_elem, pos, pos))

    full_text = ''.join(
        t.text for _, t, _, _ in text_map if t is not None and t.text
    )

    # Try the search text and its encoding variants
    for variant in normalize_for_search(search_text):
        idx = full_text.find(variant)
        if idx != -1:
            end_idx = idx + len(variant)
            affected = []
            for run, t_elem, cs, ce in text_map:
                if ce > idx and cs < end_idx:
                    local_start = max(0, idx - cs)
                    local_end = min(ce - cs, end_idx - cs)
                    affected.append((run, t_elem, local_start, local_end))
            return affected

    return None


def get_run_props(run):
    """Return a deep copy of a run's w:rPr, or None."""
    rpr = run.find(f'{{{W}}}rPr')
    return copy.deepcopy(rpr) if rpr is not None else None


def set_space_preserve(elem):
    """Add xml:space='preserve' if text has leading/trailing whitespace."""
    if elem.text and (elem.text[0] == ' ' or elem.text[-1] == ' '):
        elem.set(f'{{{XML_NS}}}space', 'preserve')


def apply_tracked_change(para, old_text, new_text, change_id, date):
    """Insert w:del + w:ins into a paragraph, replacing old_text with new_text.

    Returns True on success, False if old_text not found.
    """
    affected = find_text_in_paragraph(para, old_text)
    if affected is None:
        return False

    first_run = affected[0][0]
    last_run = affected[-1][0]
    rpr = get_run_props(first_run)

    parent = first_run.getparent()

    # If parent is not w:p (e.g., w:hyperlink), move the edit to the grandparent
    # paragraph. OOXML requires del/ins as children of w:p.
    target_parent = parent
    if parent.tag != f'{{{W}}}p':
        grandparent = parent.getparent()
        if grandparent is not None and grandparent.tag == f'{{{W}}}p':
            target_parent = grandparent
        # If nested deeper, we still try — Word may tolerate it in some cases

    insert_pos = list(target_parent).index(
        first_run if target_parent is parent else parent
    )

    new_elements = []

    # ── Prefix run (text before the match in the first run) ──
    first_t = affected[0][1]
    prefix_offset = affected[0][2]
    if prefix_offset > 0 and first_t is not None and first_t.text:
        prefix_run = copy.deepcopy(first_run)
        pt = prefix_run.find(f'{{{W}}}t')
        pt.text = first_t.text[:prefix_offset]
        set_space_preserve(pt)
        new_elements.append(prefix_run)

    # ── w:del ──
    del_elem = etree.Element(f'{{{W}}}del')
    del_elem.set(f'{{{W}}}id', str(change_id))
    del_elem.set(f'{{{W}}}author', AUTHOR)
    del_elem.set(f'{{{W}}}date', date)

    del_run = etree.SubElement(del_elem, f'{{{W}}}r')
    if rpr is not None:
        del_run.append(copy.deepcopy(rpr))
    del_run.set(f'{{{W}}}rsidDel', RSID)
    del_text = etree.SubElement(del_run, f'{{{W}}}delText')
    del_text.text = old_text
    set_space_preserve(del_text)
    new_elements.append(del_elem)

    # ── w:ins ──
    ins_elem = etree.Element(f'{{{W}}}ins')
    ins_elem.set(f'{{{W}}}id', str(change_id + 1))
    ins_elem.set(f'{{{W}}}author', AUTHOR)
    ins_elem.set(f'{{{W}}}date', date)

    ins_run = etree.SubElement(ins_elem, f'{{{W}}}r')
    if rpr is not None:
        ins_run.append(copy.deepcopy(rpr))
    ins_run.set(f'{{{W}}}rsidR', RSID)
    ins_text = etree.SubElement(ins_run, f'{{{W}}}t')
    ins_text.text = new_text
    set_space_preserve(ins_text)
    new_elements.append(ins_elem)

    # ── Suffix run (text after the match in the last run) ──
    last_t = affected[-1][1]
    suffix_offset = affected[-1][3]
    if last_t is not None and last_t.text and suffix_offset < len(last_t.text):
        suffix_run = copy.deepcopy(last_run)
        st = suffix_run.find(f'{{{W}}}t')
        st.text = last_t.text[suffix_offset:]
        set_space_preserve(st)
        new_elements.append(suffix_run)

    # ── Remove original runs and insert new elements ──
    if target_parent is parent:
        # Normal case: runs are direct children of w:p
        for run, _, _, _ in affected:
            parent.remove(run)
        for i, elem in enumerate(new_elements):
            target_parent.insert(insert_pos + i, elem)
    else:
        # Runs were inside a container (e.g., w:hyperlink).
        # Remove the runs from the container, move del/ins to the paragraph.
        for run, _, _, _ in affected:
            parent.remove(run)
        for i, elem in enumerate(new_elements):
            target_parent.insert(insert_pos + 1 + i, elem)

    return True


def add_comment_anchor(para, anchor_text, comment_id):
    """Wrap anchor_text in commentRangeStart/End + commentReference."""
    affected = find_text_in_paragraph(para, anchor_text)
    if affected is None:
        return False

    first_run = affected[0][0]
    last_run = affected[-1][0]
    parent = first_run.getparent()

    start_pos = list(parent).index(first_run)
    crs = etree.Element(f'{{{W}}}commentRangeStart')
    crs.set(f'{{{W}}}id', str(comment_id))
    parent.insert(start_pos, crs)

    end_pos = list(parent).index(last_run) + 1
    cre = etree.Element(f'{{{W}}}commentRangeEnd')
    cre.set(f'{{{W}}}id', str(comment_id))
    parent.insert(end_pos, cre)

    ref_run = etree.Element(f'{{{W}}}r')
    ref_rpr = etree.SubElement(ref_run, f'{{{W}}}rPr')
    ref_style = etree.SubElement(ref_rpr, f'{{{W}}}rStyle')
    ref_style.set(f'{{{W}}}val', 'CommentReference')
    cref = etree.SubElement(ref_run, f'{{{W}}}commentReference')
    cref.set(f'{{{W}}}id', str(comment_id))
    parent.insert(end_pos + 1, ref_run)

    return True


def add_comment_anchor_around_change(para, del_id, ins_id, comment_id):
    """Add comment anchors wrapping an existing del/ins pair in a paragraph."""
    del_elem = None
    ins_elem = None
    for child in para:
        if child.tag == f'{{{W}}}del' and child.get(f'{{{W}}}id') == str(del_id):
            del_elem = child
        if child.tag == f'{{{W}}}ins' and child.get(f'{{{W}}}id') == str(ins_id):
            ins_elem = child

    if del_elem is None or ins_elem is None:
        return False

    del_pos = list(para).index(del_elem)
    crs = etree.Element(f'{{{W}}}commentRangeStart')
    crs.set(f'{{{W}}}id', str(comment_id))
    para.insert(del_pos, crs)

    ins_pos = list(para).index(ins_elem)
    cre = etree.Element(f'{{{W}}}commentRangeEnd')
    cre.set(f'{{{W}}}id', str(comment_id))
    para.insert(ins_pos + 1, cre)

    ref_run = etree.Element(f'{{{W}}}r')
    ref_rpr = etree.SubElement(ref_run, f'{{{W}}}rPr')
    ref_style = etree.SubElement(ref_rpr, f'{{{W}}}rStyle')
    ref_style.set(f'{{{W}}}val', 'CommentReference')
    cref = etree.SubElement(ref_run, f'{{{W}}}commentReference')
    cref.set(f'{{{W}}}id', str(comment_id))
    para.insert(ins_pos + 2, ref_run)

    return True


def create_comment_element(comment_id, date, text):
    """Build a <w:comment> element for comments.xml."""
    comment = etree.Element(f'{{{W}}}comment')
    comment.set(f'{{{W}}}id', str(comment_id))
    comment.set(f'{{{W}}}author', AUTHOR)
    comment.set(f'{{{W}}}date', date)
    comment.set(f'{{{W}}}initials', 'C')

    p = etree.SubElement(comment, f'{{{W}}}p')
    p.set(f'{{{W14}}}paraId', format(0x80000000 + comment_id, '08X'))
    p.set(f'{{{W14}}}textId', '77777777')
    p.set(f'{{{W}}}rsidR', RSID)
    p.set(f'{{{W}}}rsidRDefault', RSID)

    # Annotation reference run
    ref_run = etree.SubElement(p, f'{{{W}}}r')
    ref_rpr = etree.SubElement(ref_run, f'{{{W}}}rPr')
    ref_style = etree.SubElement(ref_rpr, f'{{{W}}}rStyle')
    ref_style.set(f'{{{W}}}val', 'CommentReference')
    etree.SubElement(ref_run, f'{{{W}}}annotationRef')

    # Text run
    text_run = etree.SubElement(p, f'{{{W}}}r')
    t = etree.SubElement(text_run, f'{{{W}}}t')
    t.text = text
    set_space_preserve(t)

    return comment


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) != 4:
        print("Usage: python apply_copyedits.py <source.docx> <findings.jsonl> <output.docx>")
        sys.exit(1)

    src_docx = sys.argv[1]
    findings_path = sys.argv[2]
    output_docx = sys.argv[3]

    if not os.path.exists(src_docx):
        print(f"Error: source file not found: {src_docx}")
        sys.exit(1)
    if not os.path.exists(findings_path):
        print(f"Error: findings file not found: {findings_path}")
        sys.exit(1)

    # ── Parse findings ──
    findings = parse_findings(findings_path)
    tc_count = sum(1 for f in findings if f['type'] == 'tracked_change')
    co_count = sum(1 for f in findings if f['type'] == 'comment_only')
    print(f"Parsed {len(findings)} findings ({tc_count} tracked changes, {co_count} comments)")

    # ── Extract docx ──
    work_dir = output_docx + ".work"
    if os.path.exists(work_dir):
        import shutil
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)

    with zipfile.ZipFile(src_docx, 'r') as z:
        z.extractall(work_dir)

    # ── Parse XML files ──
    parser = etree.XMLParser(remove_blank_text=False)

    doc_path = os.path.join(work_dir, "word", "document.xml")
    doc_tree = etree.parse(doc_path, parser)
    doc_root = doc_tree.getroot()

    # Ensure comments.xml and its relationships/content types exist
    # (no-ops if everything is already in place)
    ensure_comments_infrastructure(work_dir, src_docx)

    comments_path = os.path.join(work_dir, "word", "comments.xml")
    comments_tree = etree.parse(comments_path, parser)
    comments_root = comments_tree.getroot()

    footnotes_path = os.path.join(work_dir, "word", "footnotes.xml")
    footnotes_tree = None
    if os.path.exists(footnotes_path):
        footnotes_tree = etree.parse(footnotes_path, parser)

    endnotes_path = os.path.join(work_dir, "word", "endnotes.xml")
    endnotes_tree = None
    if os.path.exists(endnotes_path):
        endnotes_tree = etree.parse(endnotes_path, parser)

    # ── Find safe starting ID ──
    max_id = 100
    for tree in [doc_tree, comments_tree, footnotes_tree, endnotes_tree]:
        if tree is None:
            continue
        for elem in tree.getroot().iter():
            wid = elem.get(f'{{{W}}}id')
            if wid is not None:
                try:
                    max_id = max(max_id, int(wid))
                except ValueError:
                    pass
    next_id = max_id + 100

    # ── Generate timestamp ──
    from datetime import datetime, timezone
    date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # ── Collect all searchable paragraphs ──
    doc_paras = doc_root.findall(f'.//{{{W}}}p')
    fn_paras = (footnotes_tree.getroot().findall(f'.//{{{W}}}p')
                if footnotes_tree else [])
    en_paras = (endnotes_tree.getroot().findall(f'.//{{{W}}}p')
                if endnotes_tree else [])

    # ── Apply findings ──
    applied = 0
    failed = []
    new_comments = []

    for finding in findings:
        ftype = finding['type']
        found = False

        if ftype == 'tracked_change':
            old_text = finding.get('old_text', '')
            new_text = finding.get('new_text', '')
            if not old_text:
                failed.append(finding)
                continue

            # Search in document, then footnotes, then endnotes
            for para_list in [doc_paras, fn_paras, en_paras]:
                for para in para_list:
                    if find_text_in_paragraph(para, old_text) is not None:
                        success = apply_tracked_change(
                            para, old_text, new_text, next_id, date
                        )
                        if success:
                            # Add rationale comment
                            comment_id = next_id + 2
                            ce = create_comment_element(
                                comment_id, date, finding['comment']
                            )
                            new_comments.append(ce)

                            # Anchor comment around the del/ins pair
                            target_para = para
                            # If the del was moved to grandparent, find it
                            if para.find(f'{{{W}}}del[@{{{W}}}id="{next_id}"]') is None:
                                # Search parent paragraph
                                for p in doc_paras + fn_paras + en_paras:
                                    if p.find(f'{{{W}}}del[@{{{W}}}id="{next_id}"]') is not None:
                                        target_para = p
                                        break

                            add_comment_anchor_around_change(
                                target_para, next_id, next_id + 1, comment_id
                            )

                            next_id += 3
                            applied += 1
                            found = True
                            break
                if found:
                    break

        elif ftype == 'comment_only':
            anchor = finding.get('anchor_text', '')
            if not anchor:
                failed.append(finding)
                continue

            for para_list in [doc_paras, fn_paras, en_paras]:
                for para in para_list:
                    if find_text_in_paragraph(para, anchor) is not None:
                        comment_id = next_id
                        success = add_comment_anchor(para, anchor, comment_id)
                        if success:
                            ce = create_comment_element(
                                comment_id, date, finding['comment']
                            )
                            new_comments.append(ce)
                            next_id += 1
                            applied += 1
                            found = True
                            break
                if found:
                    break

        if not found:
            failed.append(finding)
            anchor = finding.get('old_text', finding.get('anchor_text', '?'))
            print(f"  FAILED: {anchor[:70]}...")

    print(f"\nApplied: {applied}/{len(findings)}")
    if failed:
        print(f"Failed:  {len(failed)}")

    # ── Update comments.xml ──
    for ce in new_comments:
        comments_root.append(ce)

    # ── Update commentsExtended.xml ──
    ce_path = os.path.join(work_dir, "word", "commentsExtended.xml")
    if os.path.exists(ce_path):
        ce_tree = etree.parse(ce_path, parser)
        ce_root = ce_tree.getroot()
        existing = {
            e.get(f'{{{W15}}}paraId')
            for e in ce_root.findall(f'{{{W15}}}commentEx')
        }
        for c in new_comments:
            p = c.find(f'{{{W}}}p')
            if p is not None:
                para_id = p.get(f'{{{W14}}}paraId')
                if para_id and para_id not in existing:
                    ex = etree.SubElement(ce_root, f'{{{W15}}}commentEx')
                    ex.set(f'{{{W15}}}paraId', para_id)
                    ex.set(f'{{{W15}}}done', '0')
        ce_tree.write(ce_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # ── Update commentsIds.xml ──
    ci_path = os.path.join(work_dir, "word", "commentsIds.xml")
    if os.path.exists(ci_path):
        ci_tree = etree.parse(ci_path, parser)
        ci_root = ci_tree.getroot()
        existing = {
            e.get(f'{{{W16CID}}}paraId')
            for e in ci_root.findall(f'{{{W16CID}}}commentId')
        }
        for c in new_comments:
            p = c.find(f'{{{W}}}p')
            if p is not None:
                para_id = p.get(f'{{{W14}}}paraId')
                if para_id and para_id not in existing:
                    cid = etree.SubElement(ci_root, f'{{{W16CID}}}commentId')
                    cid.set(f'{{{W16CID}}}paraId', para_id)
                    cid.set(f'{{{W16CID}}}durableId',
                            format(random.randint(0, 0xFFFFFFFF), '08X'))
        ci_tree.write(ci_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # ── Update people.xml ──
    people_path = os.path.join(work_dir, "word", "people.xml")
    if os.path.exists(people_path):
        people_tree = etree.parse(people_path, parser)
        people_root = people_tree.getroot()
        existing_authors = [
            p.get(f'{{{W15}}}author')
            for p in people_root.findall(f'{{{W15}}}person')
        ]
        if AUTHOR not in existing_authors:
            person = etree.SubElement(people_root, f'{{{W15}}}person')
            person.set(f'{{{W15}}}author', AUTHOR)
            presence = etree.SubElement(person, f'{{{W15}}}presenceInfo')
            presence.set(f'{{{W15}}}providerId', 'None')
            presence.set(f'{{{W15}}}userId', 'claude-copyeditor')
        people_tree.write(
            people_path, xml_declaration=True, encoding='UTF-8', standalone=True
        )

    # ── Write modified XML files ──
    doc_tree.write(doc_path, xml_declaration=True, encoding='UTF-8', standalone=True)
    comments_tree.write(
        comments_path, xml_declaration=True, encoding='UTF-8', standalone=True
    )
    if footnotes_tree is not None:
        footnotes_tree.write(
            footnotes_path, xml_declaration=True, encoding='UTF-8', standalone=True
        )
    if endnotes_tree is not None:
        endnotes_tree.write(
            endnotes_path, xml_declaration=True, encoding='UTF-8', standalone=True
        )

    # ── Repackage as docx ──
    print("\nRepackaging...")
    if os.path.exists(output_docx):
        os.remove(output_docx)

    # Preserve original ZIP entry order
    with zipfile.ZipFile(src_docx, 'r') as orig:
        orig_names = orig.namelist()

    # Include comments.xml if it was newly created
    if 'word/comments.xml' not in orig_names:
        orig_names.append('word/comments.xml')

    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name in orig_names:
            local = os.path.join(work_dir, name)
            if os.path.isfile(local):
                zf.write(local, name)

    # Clean up work directory
    import shutil
    shutil.rmtree(work_dir)

    size = os.path.getsize(output_docx)
    print(f"Output: {output_docx} ({size:,} bytes)")

    if failed:
        print(f"\n{'='*60}")
        print(f"WARNING: {len(failed)} finding(s) could not be applied:")
        for f in failed:
            anchor = f.get('old_text', f.get('anchor_text', f.get('fix_raw', '?')))
            print(f"  - [{f.get('category','')}] {anchor[:80]}")
        print("These must be applied manually.")
        print(f"{'='*60}")

    return len(failed)


if __name__ == "__main__":
    sys.exit(main())