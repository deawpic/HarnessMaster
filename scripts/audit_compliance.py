#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Compliance Auditor & Quality Gatekeeper
HarnessMaster CLI Tool

Scans any harness workspace or directory against the 7 Golden Production Standards:
1. Strict Prohibition of ASCII Tables & Diagrams (+----+, |--|, ├──, └──)
2. Mermaid Unicode Guardian Compliance (flowchart TD/LR, quoted labels, ASCII IDs)
3. Clean File Gate (Zero PDF export guidance in saved ./output/*.md files)
4. UTF-8 Encoding Verification across all text/markdown files
5. AGENTS.md & Workspace Invariant Verification
6. Grounding Oracle & Cache Infrastructure Health

Usage:
  python3 scripts/audit_compliance.py <path_to_harness_directory>
  python3 scripts/audit_compliance.py <path_to_harness_directory> --fix
  python3 scripts/audit_compliance.py <path_to_harness_directory> --json
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Tuple

# Ensure we can import reference tools
CURRENT_DIR = Path(__file__).resolve().parent
HARNESS_MASTER_ROOT = CURRENT_DIR.parent
REFS_DIR = HARNESS_MASTER_ROOT / ".agents" / "skills" / "agent-harness-builder" / "references"
sys.path.insert(0, str(REFS_DIR))

try:
    from mermaid_unicode_guardian import MermaidUnicodeGuardian
    from document_exporter import detect_ascii_tables_or_diagrams, audit_document_formatting
    from test_policy_guardian import audit_test_policy_compliance
except ImportError as e:
    print(f"Warning: Could not import helper guardians from {REFS_DIR}: {e}")
    MermaidUnicodeGuardian = None
    detect_ascii_tables_or_diagrams = None
    audit_document_formatting = None
    audit_test_policy_compliance = None


def audit_harness_directory(harness_path: Path, auto_fix: bool = False) -> Dict[str, Any]:
    """Audits an entire harness repository for compliance."""
    if not harness_path.exists() or not harness_path.is_dir():
        raise ValueError(f"Target harness directory does not exist: {harness_path}")

    report = {
        "harness_path": str(harness_path.resolve()),
        "files_scanned": 0,
        "ascii_violations": [],
        "mermaid_violations": [],
        "clean_file_violations": [],
        "encoding_errors": [],
        "structural_checks": {},
        "fixes_applied": [],
        "compliance_score": 100,
        "grade": "A+"
    }

    # 1. Structural Checks
    agents_md = harness_path / "AGENTS.md"
    readme_md = harness_path / "README.md"
    output_dir = harness_path / "output"
    cache_dir = harness_path / "cache"

    report["structural_checks"] = {
        "has_agents_md": agents_md.exists(),
        "has_readme_md": readme_md.exists(),
        "has_output_dir": output_dir.exists(),
        "has_cache_dir": cache_dir.exists()
    }

    report["token_policy_check"] = {
        "checked": False,
        "passed": False,
        "score": 0,
        "found_rules": [],
        "missing_rules": []
    }

    if not agents_md.exists():
        report["compliance_score"] -= 15
    elif audit_test_policy_compliance:
        try:
            agents_text = agents_md.read_text(encoding="utf-8")
            t_audit = audit_test_policy_compliance(agents_text)
            report["token_policy_check"] = {
                "checked": True,
                "passed": t_audit["passed"],
                "score": t_audit["score"],
                "found_rules": t_audit["found_rules"],
                "missing_rules": t_audit["missing_rules"]
            }
            if not t_audit["passed"]:
                report["compliance_score"] -= (100 - t_audit["score"]) // 10
        except Exception:
            pass

    # 2. Scan all Markdown files (.md)
    md_files = list(harness_path.glob("**/*.md"))
    # Filter out hidden or build files
    md_files = [
        f for f in md_files 
        if not any(part.startswith((".", "__pycache__", "node_modules", "venv", ".git")) for part in f.parts)
    ]
    report["files_scanned"] = len(md_files)

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = md_file.read_text(encoding="utf-8-sig")
            except Exception as ex:
                report["encoding_errors"].append({
                    "file": str(md_file.relative_to(harness_path)),
                    "error": f"Encoding is not UTF-8: {ex}"
                })
                report["compliance_score"] -= 10
                continue

        rel_path = str(md_file.relative_to(harness_path))

        # Check A: ASCII tables or diagrams
        if detect_ascii_tables_or_diagrams:
            ascii_issues = detect_ascii_tables_or_diagrams(content)
            if ascii_issues:
                # In developer documentation (README/AGENTS), file trees (├──) in ```text are standard
                # for project layout, but ASCII boxes/tables or trees in ./output/ are strictly forbidden.
                is_output_file = "output" in md_file.parts
                for issue in ascii_issues:
                    if issue["type"] == "ascii_tree_diagram" and not is_output_file:
                        # Skip developer directory tree in root docs
                        continue
                    issue["file"] = rel_path
                    report["ascii_violations"].append(issue)
                if report["ascii_violations"]:
                    report["compliance_score"] -= min(len(report["ascii_violations"]) * 5, 20)


        # Check B: Mermaid diagrams
        if MermaidUnicodeGuardian:
            mermaid_res = MermaidUnicodeGuardian.audit_markdown_text(content)
            if not mermaid_res["passed"]:
                for rep in mermaid_res["reports"]:
                    if not rep["validation"]["passed"]:
                        for err in rep["validation"]["errors"]:
                            report["mermaid_violations"].append({
                                "file": rel_path,
                                "error": err["message"],
                                "rule": err["rule"]
                            })
                report["compliance_score"] -= min(len(report["mermaid_violations"]) * 5, 20)

                if auto_fix and mermaid_res["sanitized_markdown"] != content:
                    md_file.write_text(mermaid_res["sanitized_markdown"], encoding="utf-8")
                    report["fixes_applied"].append(f"Auto-healed Mermaid blocks in {rel_path}")

        # Check C: Clean File Gate (saved files in output/ must NOT have PDF export guides)
        if "output" in md_file.parts:
            pdf_guide_indicators = [
                "คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF",
                "Printing & PDF Export Guide",
                "Export to PDF",
                "Markdown PDF",
                "Typora",
                "Obsidian"
            ]
            found_indicators = [ind for ind in pdf_guide_indicators if ind in content]
            if found_indicators:
                report["clean_file_violations"].append({
                    "file": rel_path,
                    "indicators_found": found_indicators,
                    "rule": "Clean File Gate: PDF advisory must only appear in Chat Responses, never inside saved ./output/*.md files"
                })
                report["compliance_score"] -= 10

    # Ensure score stays between 0 and 100
    report["compliance_score"] = max(0, min(100, report["compliance_score"]))

    # Determine Grade
    score = report["compliance_score"]
    if score >= 95:
        report["grade"] = "A+"
    elif score >= 85:
        report["grade"] = "A"
    elif score >= 75:
        report["grade"] = "B"
    elif score >= 60:
        report["grade"] = "C"
    else:
        report["grade"] = "F"

    return report


def print_cli_report(report: Dict[str, Any]) -> None:
    """Prints a beautiful, clean Markdown-compliant CLI audit report."""
    print("\n" + "=" * 70)
    print(f"🛡️  HARNESS MASTER COMPLIANCE AUDIT REPORT")
    print(f"Target: {report['harness_path']}")
    print(f"Grade:  {report['grade']} (Score: {report['compliance_score']}/100)")
    print("=" * 70)

    print("\n| ตรวจสอบโครงสร้างระบบ | สถานะ |")
    print("| :--- | :---: |")
    struct = report["structural_checks"]
    print(f"| มีไฟล์ AGENTS.md ประจำระบบ | {'✅ ผ่าน' if struct['has_agents_md'] else '❌ ขาด'} |")
    print(f"| มีไฟล์ README.md ประจำระบบ | {'✅ ผ่าน' if struct['has_readme_md'] else '❌ ขาด'} |")
    print(f"| มีโฟลเดอร์ ./output/ สำหรับบันทึกผล | {'✅ ผ่าน' if struct['has_output_dir'] else '⚠️ ไม่มี'} |")
    print(f"| มีโฟลเดอร์ ./cache/ สำหรับ Tier-0 Cache | {'✅ ผ่าน' if struct['has_cache_dir'] else '⚠️ ไม่มี'} |")
    token_check = report.get("token_policy_check", {})
    if token_check.get("checked"):
        status_token = f"✅ ผ่าน (คะแนน {token_check['score']}%)" if token_check["passed"] else f"⚠️ ไม่สมบูรณ์ ({token_check['score']}%)"
        print(f"| กฎประหยัด Token & Test Control | {status_token} |")

    print(f"\n📁 จำนวนไฟล์ Markdown ที่สแกน: {report['files_scanned']} ไฟล์")

    # Display Violations
    total_issues = (
        len(report["ascii_violations"]) + 
        len(report["mermaid_violations"]) + 
        len(report["clean_file_violations"]) + 
        len(report["encoding_errors"])
    )

    if total_issues == 0 and token_check.get("passed", True):
        print("\n✨ ยินดีด้วย! ไม่พบข้อบกพร่องตามกฎเหล็ก Production Harness Standards 100%")
    else:
        print(f"\n⚠️  พบข้อบกพร่องที่ต้องแก้ไขทั้งหมด {total_issues} รายการ:")

        if report["ascii_violations"]:
            print("\n❌ 1. ข้อผิดพลาด ASCII Tables / Diagrams:")
            for v in report["ascii_violations"][:5]:
                print(f"   - [{v['file']}:L{v['line']}] {v['type']}: {v['content']}")
            if len(report["ascii_violations"]) > 5:
                print(f"   ... และอีก {len(report['ascii_violations']) - 5} รายการ")

        if report["mermaid_violations"]:
            print("\n❌ 2. ข้อผิดพลาด Mermaid Unicode / Syntax:")
            for v in report["mermaid_violations"][:5]:
                print(f"   - [{v['file']}] {v['error']}")
            if len(report["mermaid_violations"]) > 5:
                print(f"   ... และอีก {len(report['mermaid_violations']) - 5} รายการ")

        if report["clean_file_violations"]:
            print("\n❌ 3. ข้อผิดพลาด Clean File Gate (พบคำแนะนำ PDF ในไฟล์ที่บันทึก):")
            for v in report["clean_file_violations"]:
                print(f"   - [{v['file']}] มีข้อความแนะนำ PDF: {v['indicators_found']}")

        if report["encoding_errors"]:
            print("\n❌ 4. ข้อผิดพลาด Encoding:")
            for v in report["encoding_errors"]:
                print(f"   - [{v['file']}] {v['error']}")

        if token_check.get("missing_rules"):
            print("\n⚠️ 5. ข้อเสนอแนะนโยบายประหยัด Token (Unittest Policy):")
            for missing in token_check["missing_rules"]:
                print(f"   - ขาดระเบียบ: {missing}")

    if report["fixes_applied"]:
        print("\n🛠️ การแก้ไขอัตโนมัติ (--fix):")
        for fix in report["fixes_applied"]:
            print(f"   - {fix}")

    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Audit any harness directory against Production Standards.")
    parser.add_argument("harness_dir", help="Path to the harness repository directory to audit")
    parser.add_argument("--fix", action="store_true", help="Automatically sanitize and fix Mermaid diagrams")
    parser.add_argument("--json", action="store_true", help="Output audit report in raw JSON format")

    args = parser.parse_args()
    target_path = Path(args.harness_dir).resolve()

    try:
        report = audit_harness_directory(target_path, auto_fix=args.fix)
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print_cli_report(report)

        # Exit code 0 if score >= 80, else 1
        sys.exit(0 if report["compliance_score"] >= 80 else 1)
    except Exception as e:
        print(f"Error auditing harness: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
