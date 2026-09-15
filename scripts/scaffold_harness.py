#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turnkey Agent Harness Scaffolder (One-Click Generator)
HarnessMaster Tooling

Automatically generates a complete, production-grade Agent Harness repository
pre-configured with:
- Golden Production Standards (Mermaid Unicode Guardian, Clean File Gate, UTF-8)
- Domain Semantic Adapter (Medical, Legal, Software/DevOps, Finance, General)
- Scale Profiles (Profile Micro vs Profile Enterprise)
- Dual-Layer Cache, Grounding Oracle, Mock LLM, and Deterministic Evaluator

Usage:
  python3 scripts/scaffold_harness.py --name my_domain --domain legal --profile enterprise
  python3 scripts/scaffold_harness.py --name code_review --domain software --profile micro
"""

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict

HARNESS_MASTER_ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = HARNESS_MASTER_ROOT / ".agents" / "skills" / "agent-harness-builder" / "references"

DOMAIN_SEMANTICS: Dict[str, Dict[str, str]] = {
    "medical": {
        "title": "Thai Clinical & Medical Intelligence Harness",
        "role": "Lead Clinical AI Specialist & Triage Orchestrator",
        "red_flag": "สัญญาณวิกฤตอันตรายถึงชีวิต (เจ็บแน่นหน้าอก, Stroke FAST, DKA, Anaphylaxis) -> สั่งโทร 1669 / ไปห้องฉุกเฉิน (ER) ทันที",
        "oracle_ids": "PMID, DOI, ICD-10/11, LOINC Reference Codes",
        "tier1": "แพทย์ผู้เชี่ยวชาญ (Clinical Trials, Level of Evidence, Drug-Drug Interactions)",
        "tier2": "นักศึกษาแพทย์ (SOAP Note, Pathophysiology Mechanism, Differential Diagnoses)",
        "tier3": "คนทั่วไป/คนไข้ (ภาษาเข้าใจง่าย, การดูแลตนเอง, สัญญาณเตือน, ข้อจำกัดความรับผิดชอบ SaMD)",
        "disclaimer": "⚠️ ข้อมูลนี้จัดทำขึ้นเพื่อให้ความรู้เบื้องต้นเท่านั้น ไม่สามารถใช้ทดแทนการตรวจวินิจฉัยหรือการรักษาจากแพทย์ผู้เชี่ยวชาญโดยตรง"
    },
    "legal": {
        "title": "Thai Legal Intelligence & Precedent Harness",
        "role": "Lead Thai Legal Intelligence Advisor & Jurist",
        "red_flag": "คดีใกล้ขาดอายุความ, การลักลอบโอน/ยักย้ายทรัพย์สิน -> ให้คำแนะนำยื่นคำร้องคุ้มครองชั่วคราวและอายัดทรัพย์ทันที",
        "oracle_ids": "เลขที่คำพิพากษาศาลฎีกา, เลขมาตรา, ประมวลกฎหมาย, พระราชบัญญัติ",
        "tier1": "ทนายความ/ผู้พิพากษา (IRAC Framework, บรรทัดฐานศาลฎีกา, ภาระการพิสูจน์)",
        "tier2": "นักศึกษากฎหมาย (เจตนารมณ์กฎหมาย, องค์ประกอบความผิด, โครงสร้างมาตรา)",
        "tier3": "ลูกความ/ประชาชน (ขั้นตอนปฏิบัติเบื้องต้น, การเตรียมหลักฐาน, อัตราโทษ, คำเตือนทางกฎหมาย)",
        "disclaimer": "⚖️ ข้อมูลนี้เป็นการวิเคราะห์ตามหลักตัวบทกฎหมายและเทคโนโลยีปัญญาประดิษฐ์เบื้องต้น ไม่สามารถนำมาใช้แทนคำแนะนำของทนายความวิชาชีพอย่างเป็นทางการได้"
    },
    "software": {
        "title": "Software Engineering & DevOps Autonomous Harness",
        "role": "Lead Software Architect & DevOps Reliability Engineer",
        "red_flag": "คำสั่งทำลายล้าง (`rm -rf /`, `DROP DATABASE`), API Key / Secret Token รั่วไหล, Memory Leak วิกฤต -> ตัดวงจร Circuit Breaker ทันที",
        "oracle_ids": "Git Commit SHA, Package Version (SemVer), RFC/API Spec, CVE Vulnerability ID",
        "tier1": "Staff / Principal Architect (System Design, Concurrency, Big-O, Fault Isolation)",
        "tier2": "Mid / Junior Developer (Step-by-step logic, Code Snippets, Syntactic Best Practice)",
        "tier3": "Product Manager / End User (Business Impact, Release Notes, ฟังก์ชันการใช้งาน)",
        "disclaimer": "💻 โค้ดและการกำหนดค่านี้จัดทำขึ้นเพื่อเป็นแนวทางทางเทคนิคเบื้องต้น ควรผ่านการทดสอบบน Staging Environment ก่อนนำขึ้น Production จริง"
    },
    "finance": {
        "title": "FinOps & Financial Intelligence Advisory Harness",
        "role": "Lead Financial Systems Architect & Quantitative Risk Specialist",
        "red_flag": "งบประมาณรั่วไหลเกินเพดาน ($/day Hard Cap), ธุรกรรมน่าสงสัยต้องสงสัยฟอกเงิน (AML/Fraud) -> Freeze Account / Hard Stop ทันที",
        "oracle_ids": "Transaction Hash/ID, เลขประจำตัวผู้เสียภาษี, มาตราประมวลรัษฎากร, รหัสกองทุน SEC",
        "tier1": "CFO / Quantitative Risk Lead (CapEx/OpEx, ROI, Risk Matrix, Value-at-Risk)",
        "tier2": "Accountant / Financial Analyst (ตารางเปรียบเทียบงบ, ผังบัญชีแยกประเภท, Ratio Analysis)",
        "tier3": "Consumer / Retail Investor (สรุปความเสี่ยงเข้าใจง่าย, คำเตือนความเสี่ยงการลงทุน)",
        "disclaimer": "📈 ข้อมูลนี้ไม่ใช่คำแนะนำการลงทุนอย่างเป็นทางการ ผู้ลงทุนควรศึกษาข้อมูลและประเมินความเสี่ยงก่อนการตัดสินใจ"
    },
    "general": {
        "title": "Autonomous Domain Intelligence Harness",
        "role": "Lead Autonomous Domain Harness Architect",
        "red_flag": "Infinite Tool Loop, Memory Exhaustion, Unauthorized System Access -> ทำการ Hard-Stop ทันที",
        "oracle_ids": "Verified Test Case ID, Trajectory Hash, Domain Standard Identifier",
        "tier1": "Domain Specialist / Lead Engineer (Technical Deep Dive, Rigorous Evaluation)",
        "tier2": "Practitioner / Learner (Step-by-step Guidance, Process Flow)",
        "tier3": "End User / Public (Clear Actionable Advice, Safety Disclaimers)",
        "disclaimer": "🛡️ ผลลัพธ์นี้ได้รับการประมวลผลผ่านระบบวิเคราะห์ปัญญาประดิษฐ์ ควรได้รับการตรวจสอบกับพยานหลักฐานจริงก่อนการใช้งาน"
    }
}


def scaffold_harness(
    name: str,
    domain: str = "general",
    profile: str = "enterprise",
    target_dir: str = None
) -> Path:
    """Instantiates a full agent harness repository."""
    target_name = f"{name}_harness" if not name.endswith("_harness") else name
    dest_dir = Path(target_dir) if target_dir else (Path.cwd() / target_name)

    if dest_dir.exists():
        print(f"Notice: Target directory '{dest_dir}' already exists. Updating/populating contents...")
    else:
        dest_dir.mkdir(parents=True, exist_ok=True)

    semantics = DOMAIN_SEMANTICS.get(domain.lower(), DOMAIN_SEMANTICS["general"])

    # 1. Create Directory Hierarchy
    (dest_dir / "harness").mkdir(parents=True, exist_ok=True)
    (dest_dir / "tests").mkdir(parents=True, exist_ok=True)
    (dest_dir / "scripts").mkdir(parents=True, exist_ok=True)
    (dest_dir / "output").mkdir(parents=True, exist_ok=True)
    (dest_dir / "cache").mkdir(parents=True, exist_ok=True)

    (dest_dir / "output" / ".gitkeep").touch()
    (dest_dir / "cache" / ".gitkeep").touch()

    # 2. Copy Reference Modules into harness/
    ref_files = [
        ("mermaid_unicode_guardian.py", "mermaid_guardian.py"),
        ("document_exporter.py", "document.py"),
        ("dual_layer_cache.py", "cache.py"),
        ("grounding_oracle.py", "verifier.py"),
        ("mock_llm.py", "mock_llm.py")
    ]
    for src_name, dst_name in ref_files:
        src = REFS_DIR / src_name
        dst = dest_dir / "harness" / dst_name
        if src.exists():
            shutil.copy2(src, dst)

    # harness/__init__.py
    (dest_dir / "harness" / "__init__.py").write_text(
        '"""Harness Engine Core Modules."""\n', encoding="utf-8"
    )

    # 3. Create benchmark_cases.json
    cases = [
        {
            "id": f"case-01-standard-{domain}",
            "title": f"Standard Benchmark Task 1 ({domain.title()})",
            "prompt": f"คำร้องขอทดสอบมาตรฐานสำหรับโดเมน {domain}",
            "ground_truth": {
                "expected_tier": "tier_1",
                "must_include_mermaid": True,
                "must_include_table": True,
                "forbidden_ascii": True
            }
        },
        {
            "id": f"case-02-red-flag-{domain}",
            "title": f"Emergency Red Flag Trigger Case ({domain.title()})",
            "prompt": f"พบภาวะเร่งด่วนฉุกเฉินในระบบ {domain}",
            "ground_truth": {
                "expected_tier": "tier_3",
                "must_trigger_red_flag": True
            }
        }
    ]
    (dest_dir / "harness" / "benchmark_cases.json").write_text(
        json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 4. Generate AGENTS.md
    agents_content = f"""# {semantics['title']} (AGENTS.md)

คุณคือ **"{semantics['role']}"**

---

## 1. บทบาทและหน้าที่ (Role & Identity)
วิเคราะห์ ตรวจสอบ และให้คำปรึกษาเชิงลึกในโดเมน {domain.title()} ด้วยความแม่นยำสูง อิงพยานหลักฐานเชิงประจักษ์ (Evidence-Grounded) และไม่สร้างข้อมูลหลอน (Zero Hallucination)

---

## 2. กฎความปลอดภัยและการแจ้งเตือนวิกฤต (Emergency & Red Flag Interceptor)
- **สัญญาณเตือนวิกฤต (Red Flag)**: {semantics['red_flag']}
- หากตรวจพบคีย์เวิร์ดวิกฤต ให้ขึ้นข้อความแจ้งเตือนตัวหนาทันทีเป็นลำดับแรก โดยไม่ต้องรอลูปประมวลผลคำตอบยาว

---

## 3. รูปแบบการตอบตามกลุ่มผู้ใช้ (Adaptive 3-Tier Persona Routing)
- **🩺 [Tier 1] ผู้เชี่ยวชาญ**: {semantics['tier1']}
- **📝 [Tier 2] ผู้เรียนรู้/นักศึกษา**: {semantics['tier2']}
- **👥 [Tier 3] บุคคลทั่วไป/ผู้รับคำปรึกษา**: {semantics['tier3']}
  - ท้ายคำตอบต้องมีข้อความปฏิเสธความรับผิดชอบเสมอ:
    > {semantics['disclaimer']}

---

## 4. กฎเหล็กแผนภาพและตาราง (Strict Mermaid & Markdown Table Protocol)
- **ห้ามใช้ ASCII Text / ASCII Art / ASCII Table เด็ดขาด** (เช่น `+----+`, `|---|`, `├──`, `└──`, `--->`)
- **แผนภาพและกระบวนการ**: ต้องใช้บล็อกโค้ด **Mermaid (` ```mermaid `)** เท่านั้น (บังคับ `flowchart TD` หรือ `flowchart LR`, Node ID ต้องเป็น ASCII ล้วน และ Label ต้องครอบด้วย double quotes `["..."]` เสมอ)
- **ตารางข้อมูลและการเปรียบเทียบ**: ต้องใช้ **Markdown Table (`| ... |`)** ตามมาตรฐาน GFM เสมอ

---

## 5. การบันทึกไฟล์และส่งออกเอกสาร (Clean Documentation & Export Protocol)
- บันทึกไฟล์ลงในไดเรกทอรี `./output/<filename>.md` ด้วยการเข้ารหัส **UTF-8** เสมอ
- **Clean File Gate**: เนื้อหาในไฟล์บันทึกต้องสะอาด ปราศจากข้อความแนะนำการแปลง PDF
- **Chat-Only PDF Advisory**: คำแนะนำโปรแกรมแปลง PDF (Obsidian, VS Code, Typora) ให้แสดงในช่องสนทนา (Chat) เท่านั้น ห้ามใส่ลงในไฟล์

---

## 6. ระบบแคชและป้องกันข้อมูลหลอน (Tier-0 Cache & Grounding Oracle)
- ตรวจสอบ L1 Memory LRU และ L2 SQLite WAL ก่อนเรียก API ภายนอกเสมอ
- **ห้ามสร้างเลขอ้างอิงเองเด็ดขาด**: อ้างอิงเฉพาะรายการที่ผ่านการยืนยัน ({semantics['oracle_ids']}) หากไม่มี ให้ตัดเลขทิ้งและคงไว้เฉพาะหลักการ
"""
    (dest_dir / "AGENTS.md").write_text(agents_content, encoding="utf-8")

    # 5. Generate README.md
    readme_content = f"""# 🛡️ {semantics['title']}
**{semantics['role']}** (สร้างโดย HarnessMaster - Profile: {profile.title()})

ระบบ Agent Execution Harness ที่ปฏิบัติตาม **Golden Production Standards**:
1. **Mermaid Unicode Guardian**: แผนภาพคมชัด ปลอดภัย 100% ต่อภาษาไทย
2. **Clean Markdown Export**: ส่งออกไฟล์ UTF-8 ลง `./output/` พร้อม Clean File Gate
3. **Grounding Whitelist Oracle**: ระบบคัดกรองเลขอ้างอิง ป้องกันข้อมูลหลอน
4. **Tier-0 Caching**: แคชความเร็วสูง L1 LRU + L2 SQLite WAL (zlib Level 6)
5. **Adaptive 3-Tier Routing**: สลับโหมดคำตอบระหว่าง ผู้เชี่ยวชาญ / ผู้ศึกษา / บุคคลทั่วไป

---

## 🚀 วิธีการทดสอบและใช้งาน (Quick Start)

```bash
# 1. รันการทดสอบ Unit Tests ทั้งหมด
make test

# 2. ตรวจสอบความถูกต้องตามมาตรฐาน Harness Compliance
make audit

# 3. รันการจำลอง Synthetic LLM Benchmark
make bench
```
"""
    (dest_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 6. Generate Makefile
    makefile_content = f"""# Makefile for {target_name}
.PHONY: test audit bench clean

test:
	python3 -m unittest discover -s tests -p "test_*.py" -v

audit:
	python3 {HARNESS_MASTER_ROOT}/scripts/audit_compliance.py .

bench:
	python3 -c "from harness.mock_llm import MockLLMRunner; runner = MockLLMRunner('{domain}'); print(runner.execute_test_task('task-01', 'ทดสอบระบบ'))"

clean:
	rm -rf cache/*.db* __pycache__ harness/__pycache__ tests/__pycache__
"""
    (dest_dir / "Makefile").write_text(makefile_content, encoding="utf-8")

    # 7. Generate Essential Unit Tests
    test_code = f"""# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

# Add harness directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.mermaid_guardian import MermaidUnicodeGuardian, validate_mermaid
from harness.document import audit_document_formatting
from harness.verifier import GroundingOracle
from harness.mock_llm import MockLLMRunner

class TestHarnessCoreStandards(unittest.TestCase):

    def test_mermaid_unicode_safety(self):
        code = 'flowchart TD\\nNode1["ข้อความภาษาไทย"]\\n'
        res = validate_mermaid(code)
        self.assertTrue(res["passed"])

    def test_forbidden_ascii_detection(self):
        bad_markdown = "+----+----+\\n| A  | B  |\\n+----+----+\\n"
        audit = audit_document_formatting(bad_markdown)
        self.assertFalse(audit["passed"])
        self.assertTrue(len(audit["violations"]) > 0)

    def test_grounding_oracle_verifier(self):
        oracle = GroundingOracle(verified_whitelist={{"123/2560"}})
        text = "อ้างอิงคำพิพากษาฎีกาที่ 123/2560 และ คำพิพากษาฎีกาที่ 999/2599"
        audit = oracle.audit_response(text)
        self.assertFalse(audit["passed"])
        self.assertIn("deka", audit["unverified_citations"])

    def test_mock_llm_golden_generation(self):
        runner = MockLLMRunner("{domain}")
        res = runner.generate_golden_response("กรณีศึกษาทดสอบ")
        self.assertIn("### 1. บทสรุป", res)
        self.assertIn("```mermaid", res)

if __name__ == "__main__":
    unittest.main()
"""
    (dest_dir / "tests" / "test_core_standards.py").write_text(test_code, encoding="utf-8")

    print(f"✨ Scaffolded {semantics['title']} successfully at: {dest_dir}")
    return dest_dir


def main():
    parser = argparse.ArgumentParser(description="Turnkey Agent Harness Generator")
    parser.add_argument("--name", required=True, help="Name of the harness to scaffold")
    parser.add_argument("--domain", choices=["medical", "legal", "software", "finance", "general"], default="general")
    parser.add_argument("--profile", choices=["micro", "enterprise"], default="enterprise")
    parser.add_argument("--target-dir", default=None, help="Target destination path")

    args = parser.parse_args()
    scaffold_harness(args.name, args.domain, args.profile, args.target_dir)


if __name__ == "__main__":
    main()
