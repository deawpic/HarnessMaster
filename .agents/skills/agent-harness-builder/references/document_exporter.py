# -*- coding: utf-8 -*-
"""
Markdown-Native Document & Report Exporter
HarnessMaster - Reusable Reference Implementation
Synthesized from: MedMate & thlawdeka Production Harnesses

Architecture:
- Native UTF-8 Markdown (.md) export into ./output/ (Single Source of Truth)
- Strict Prohibition of ASCII tables (+----+), ASCII trees (├──), and ASCII box art
- Preservation of Mathematical and Chemical Formulas (LaTeX / KaTeX)
- Separation of Concerns: Clean Saved Files vs Chat-Only PDF/Printing Advisory
- Subprocess multi-line execution safety (sys.executable + NamedTemporaryFile)
"""

import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger("HarnessMaster.DocumentExporter")

# Detection Regexes for ASCII art / boxes / tables
BOX_DRAWING_REGEX = re.compile(r'[\u2500-\u257F]')
ASCII_BOX_BORDER_REGEX = re.compile(r'^\s*(?:\+[=\-+]{2,}\+\s*)+$')
ASCII_FLOWCHART_ARROW_REGEX = re.compile(r'(?:\[.+?\]|\|.+?\|)\s*(?:-{2,}>|={2,}>)\s*(?:\[.+?\]|\|.+?\|)')
ASCII_TREE_REGEX = re.compile(r'[\u251C\u2514\u2502\u2500]?\s*[├└][─\-]+')
MARKDOWN_TABLE_SEPARATOR_REGEX = re.compile(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$')
MERMAID_BLOCK_REGEX = re.compile(r'```mermaid\s*\n.*?```', re.DOTALL | re.IGNORECASE)


def detect_ascii_tables_or_diagrams(text: str) -> List[Dict[str, Any]]:
    """
    Scans markdown text (excluding valid ```mermaid ... ``` code blocks)
    for forbidden ASCII text diagrams, ASCII box drawings, and ASCII border tables.
    Returns list of detected violations with line number, content, type, and recommendation.
    """
    violations: List[Dict[str, Any]] = []
    lines = text.splitlines()
    in_mermaid = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.lower().startswith("```mermaid"):
            in_mermaid = True
            continue
        if in_mermaid and stripped.startswith("```"):
            in_mermaid = False
            continue
        if in_mermaid:
            continue

        # Mask inline code snippets (`...`) to prevent rule documentation from self-flagging
        clean_line = re.sub(r'`[^`\n]+`', '', stripped)
        if not clean_line:
            continue

        # 1. Check ASCII box or table border (e.g. +------+------+ or +======+======+)
        if ASCII_BOX_BORDER_REGEX.match(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_table_border",
                "recommendation": "Replace ASCII border table with standard Markdown table (| ... |)."
            })
        # 2. Check ASCII tree branch symbols (e.g. ├─, └─, ├──, └──)
        elif ASCII_TREE_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_tree_diagram",
                "recommendation": "Use Mermaid flowchart (flowchart TD/LR) or Markdown table instead of ASCII tree structure."
            })
        # 3. Check Unicode box-drawing characters (e.g. ┌, ─, ━, ┃, ├, └, etc.)
        elif BOX_DRAWING_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "box_drawing_characters",
                "recommendation": "Use Mermaid diagram (```mermaid ... ```) for diagrams or Markdown table (| ... |) for tables."
            })
        # 4. Check ASCII flowchart arrow connections in text (e.g. [Step 1] ---> [Step 2])
        elif ASCII_FLOWCHART_ARROW_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_flowchart_arrow",
                "recommendation": "Convert ASCII arrow flowchart into a native Mermaid diagram (flowchart TD/LR)."
            })

    return violations


def audit_document_formatting(markdown_text: str) -> Dict[str, Any]:
    """
    Audits markdown text for compliance with:
    1. Mermaid Diagram protocol (blocks are valid)
    2. Markdown Table protocol (GFM tables used)
    3. Absence of forbidden ASCII diagrams and tables
    """
    mermaid_matches = MERMAID_BLOCK_REGEX.findall(markdown_text)

    table_separator_count = sum(
        1 for line in markdown_text.splitlines() if MARKDOWN_TABLE_SEPARATOR_REGEX.match(line)
    )

    violations = detect_ascii_tables_or_diagrams(markdown_text)
    passed = len(violations) == 0

    return {
        "passed": passed,
        "has_mermaid": len(mermaid_matches) > 0,
        "mermaid_block_count": len(mermaid_matches),
        "has_markdown_table": table_separator_count > 0,
        "markdown_table_count": table_separator_count,
        "violations": violations,
        "violation_count": len(violations),
        "summary": "Document formatting fully compliant (Mermaid & Markdown tables)" if passed
                   else f"Found {len(violations)} ASCII formatting violations that must be converted to Mermaid or Markdown table."
    }


def get_pdf_export_guidance() -> str:
    """
    Returns standardized guidance for chat responses on how to print or
    export Markdown documents to PDF using modern tools with full
    LaTeX / KaTeX math and Mermaid rendering.
    
    IMPORTANT: This string should ONLY be shown in Chat Responses,
    and NEVER written into saved files in ./output/*.md.
    """
    return (
        "> 💡 **คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF (Printing & PDF Export Guide):**\n"
        "> เอกสารนี้ถูกจัดทำในรูปแบบ Markdown (`.md`) มาตรฐานสากล เพื่อรักษาความถูกต้องของสูตรคำนวณและโครงสร้างข้อมูล\n"
        ">\n"
        "> หากต้องการพิมพ์เป็นเอกสารกระดาษหรือบันทึกเป็น PDF แนะนำให้เปิดไฟล์ `.md` ผ่านโปรแกรมดังต่อไปนี้:\n"
        "> 1. **Obsidian** (แนะนำสูงสุด): เปิดไฟล์ `.md` แล้วเลือกเมนู `Export to PDF` (รองรับภาษาไทย, แผนภาพ Mermaid และสูตร $\\LaTeX$ อัตโนมัติ 100%)\n"
        "> 2. **VS Code**: ติดตั้งส่วนขยาย *Markdown PDF* หรือ *Markdown Preview Enhanced* แล้วคลิกขวาเลือก `Export (pdf)`\n"
        "> 3. **Typora**: เลือกเมนู `File -> Export -> PDF` จัดหน้าเอกสารได้สวยงามตามมาตรฐานงานสารบรรณ\n"
        "> 4. **Google Chrome / Microsoft Edge**: ติดตั้ง Extension เช่น *Markdown Viewer* หรือเปิดดูผ่าน GitHub แล้วกด `Ctrl + P` (Print -> Save as PDF)\n"
    )


def export_markdown_document(
    title: str,
    markdown_content: str,
    filename: str,
    output_dir: Optional[Path] = None,
    include_pdf_guidance: bool = False
) -> Path:
    """
    Saves document into ./output/<filename>.md with UTF-8 encoding.
    Enforces Clean Document Protocol: PDF/Print guidance is excluded from saved files
    by default (include_pdf_guidance=False).
    """
    base_dir = output_dir or (Path.cwd() / "output")
    base_dir.mkdir(parents=True, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"

    target_file = base_dir / filename

    # Audit markdown content against ASCII text tables and diagrams protocol
    audit = audit_document_formatting(markdown_content)
    if not audit["passed"]:
        logger.warning(
            f"ASCII Formatting Violations detected in {filename} ({audit['violation_count']} issues): "
            f"{[v['type'] for v in audit['violations']]}"
        )

    content_parts = [f"# {title}\n"]
    content_parts.append(markdown_content.strip())

    if include_pdf_guidance:
        content_parts.append("\n---\n")
        content_parts.append(get_pdf_export_guidance())

    full_text = "\n\n".join(content_parts) + "\n"

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(full_text)

    logger.info(f"Exported clean markdown document to: {target_file}")
    return target_file


def run_safe_python_script(
    script_code: str,
    args: Optional[List[str]] = None,
    timeout: int = 30
) -> subprocess.CompletedProcess:
    """
    Multi-OS Subprocess Execution Safety:
    - Enforces sys.executable (never hardcodes 'python' or 'python3')
    - Writes script to tempfile.NamedTemporaryFile (never multi-line inline -c)
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as f:
        f.write(script_code)
        temp_script_path = Path(f.name)

    try:
        cmd = [sys.executable, str(temp_script_path)]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
    finally:
        temp_script_path.unlink(missing_ok=True)
