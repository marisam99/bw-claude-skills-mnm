#!/usr/bin/env python3
"""
Extract text from a Word document with paragraph indices for copyediting.

Usage:
    python extract_text.py input.docx [output.txt]

Outputs each paragraph with its index, matching the indices expected by apply_edits.py.
"""

import sys
import os
import zipfile
from xml.etree import ElementTree as ET

NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}


def extract_text(docx_path: str) -> list:
    """Extract paragraphs with their indices from a Word document."""
    paragraphs = []

    with zipfile.ZipFile(docx_path, 'r') as zf:
        with zf.open('word/document.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()

            for i, para in enumerate(root.findall('.//w:p', NAMESPACES)):
                text_parts = []
                for t_elem in para.findall('.//w:t', NAMESPACES):
                    if t_elem.text:
                        text_parts.append(t_elem.text)
                full_text = ''.join(text_parts)
                paragraphs.append((i, full_text))

    return paragraphs


def format_output(paragraphs: list, include_empty: bool = False) -> str:
    """Format paragraphs for output."""
    lines = []
    lines.append("=" * 80)
    lines.append("DOCUMENT TEXT WITH PARAGRAPH INDICES")
    lines.append("Use these indices in the 'para' field of your edit JSON.")
    lines.append("=" * 80)
    lines.append("")

    for idx, text in paragraphs:
        if text.strip() or include_empty:
            # Truncate very long paragraphs for readability
            display_text = text if len(text) <= 500 else text[:500] + "..."
            lines.append(f"[{idx:3}] {display_text}")
            lines.append("")

    lines.append("=" * 80)
    lines.append(f"Total paragraphs: {len(paragraphs)}")
    lines.append(f"Paragraphs with content: {sum(1 for _, t in paragraphs if t.strip())}")
    lines.append("=" * 80)

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py input.docx [output.txt]")
        sys.exit(1)

    input_docx = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_docx):
        print(f"Error: File not found: {input_docx}")
        sys.exit(1)

    paragraphs = extract_text(input_docx)
    output = format_output(paragraphs)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Extracted text saved to: {output_file}")
    else:
        print(output)


if __name__ == '__main__':
    main()
