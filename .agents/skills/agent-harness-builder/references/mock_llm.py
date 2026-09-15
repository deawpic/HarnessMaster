# -*- coding: utf-8 -*-
"""
Synthetic & Adversarial Mock LLM Testbed
HarnessMaster - Reusable Reference Implementation
Synthesized from: MedMate & thlawdeka Production Harnesses

Features:
1. Deterministic offline benchmark evaluation (Zero API cost, Zero token spend)
2. Golden response generator matching domain schemas (IRAC, SOAP, 3-Tier)
3. Adversarial Mode: Injects intentional defects to verify that the harness correctly catches:
   - ASCII table / box-art violations
   - Mermaid Unicode violations (unquoted Thai, classDiagram with Thai)
   - Hallucinated citations (unverified Deka, fake PMID)
   - Absolute guarantee violations ("ชนะคดี 100%")
   - Missing required headers or schema drift
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("HarnessMaster.MockLLM")


class AdversarialDefectType:
    NONE = "none"
    ASCII_TABLE = "ascii_table"
    MERMAID_UNICODE_ERROR = "mermaid_unicode_error"
    HALLUCINATED_CITATION = "hallucinated_citation"
    ABSOLUTE_GUARANTEE = "absolute_guarantee"
    MISSING_SECTIONS = "missing_sections"


class MockLLMRunner:
    """
    Deterministic Synthetic LLM Engine for offline CI/CD and stress-testing harnesses.
    """

    def __init__(self, domain: str = "general"):
        self.domain = domain

    def generate_golden_response(self, topic: str, case_id: str = "case-01") -> str:
        """Generates a 100% compliant, fully grounded response."""
        return f"""# รายงานบทวิเคราะห์เชิงโครงสร้าง: {topic} (ID: {case_id})

---

### 1. บทสรุปของสถานการณ์ (Summary)
กรณีศึกษาว่าด้วย {topic} ได้รับการวิเคราะห์ตามข้อเท็จจริงเชิงประจักษ์อย่างเป็นระบบ

---

### 2. หมวดหมู่และขอบเขต (Category)
การจัดหมวดหมู่อยู่ในเกณฑ์มาตรฐานตามแนวทางวิชาการและแนวปฏิบัติสากล

---

### 3. รายการของหลักเกณฑ์และข้อกำหนด (Rules & Principles)

| รหัสข้อกำหนด | สาระสำคัญ | การปรับใช้กับกรณีนี้ |
| :--- | :--- | :--- |
| RULE-01 | ต้องบันทึกข้อมูลตามมาตรฐาน UTF-8 | ปฏิบัติตามมาตรฐานอย่างเคร่งครัด |
| RULE-02 | ตรวจสอบผ่าน Grounding Oracle | ผ่านการยืนยันจาก Verified Payload |

---

### 4. ลำดับขั้นตอนการดำเนินงาน (Workflow Diagram)

```mermaid
flowchart TD
    Node_Start["<b>เริ่มต้นกระบวนการ</b>"] --> Node_Check["<b>ตรวจสอบเงื่อนไข</b><br/>(Grounding Check)"]
    Node_Check --> Node_Done["<b>เสร็จสิ้นกระบวนการ</b>"]
```

---

### 5. ข้อพิจารณาความเสี่ยงและดุลพินิจ (Risk Evaluation)
การประเมินความเสี่ยงขึ้นอยู่กับพยานหลักฐานและข้อเท็จจริงแวดล้อม ไม่อาจการันตีผลลัพธ์ล่วงหน้าได้

---

### 6. คำแนะนำเพิ่มเติมเพื่อความปลอดภัย (Recommendations)
1. เก็บรวบรวมเอกสารหลักฐานให้ครบถ้วน
2. ดำเนินการตามกรอบเวลาที่กฎเกณฑ์กำหนด
"""

    def generate_adversarial_response(
        self,
        topic: str,
        defect_type: str = AdversarialDefectType.ASCII_TABLE
    ) -> str:
        """
        Generates an adversarial response containing intentional defects to verify
        that harness guardrails, linters, and auditors correctly catch them.
        """
        base = self.generate_golden_response(topic)

        if defect_type == AdversarialDefectType.ASCII_TABLE:
            # Injects forbidden ASCII table border
            bad_table = """
+-------------------+-------------------+
| รายการ            | สถานะ             |
+===================+===================+
| การทดสอบ 1        | ผ่าน              |
+-------------------+-------------------+
"""
            return base + "\n\n### ข้อบกพร่องจำลอง (ASCII Table)\n" + bad_table

        elif defect_type == AdversarialDefectType.MERMAID_UNICODE_ERROR:
            # Injects incompatible classDiagram with Thai and unquoted labels
            bad_mermaid = """
```mermaid
classDiagram
    คนไข้ <|-- หมอ : ดูแล
    class คนไข้ {
        +String ชื่อ
    }
```
"""
            return base + "\n\n### ข้อบกพร่องจำลอง (Mermaid Error)\n" + bad_mermaid

        elif defect_type == AdversarialDefectType.HALLUCINATED_CITATION:
            # Injects fake citation number
            fake_citation = "\n\nตามคำพิพากษาศาลฎีกาที่ 99999/2599 ศาลได้เคยวินิจฉัยไว้..."
            return base + fake_citation

        elif defect_type == AdversarialDefectType.ABSOLUTE_GUARANTEE:
            # Injects forbidden 100% guarantee
            bad_guarantee = "\n\nในกรณีนี้ รับรองผลชนะคดีอย่างแน่นอน 100% ศาลต้องยกฟ้องแน่นอน"
            return base + bad_guarantee

        elif defect_type == AdversarialDefectType.MISSING_SECTIONS:
            # Truncates essential sections
            return "# รายงานสั้นเกินไป\nไม่มีหัวข้อสำคัญตาม Schema"

        return base

    def execute_test_task(
        self,
        task_id: str,
        prompt: str,
        defect_type: str = AdversarialDefectType.NONE
    ) -> Dict[str, Any]:
        """Simulates agent execution returning trajectory and output."""
        if defect_type == AdversarialDefectType.NONE:
            output = self.generate_golden_response(prompt, case_id=task_id)
        else:
            output = self.generate_adversarial_response(prompt, defect_type=defect_type)

        return {
            "task_id": task_id,
            "status": "completed",
            "tokens_used": 850,
            "duration_sec": 0.45,
            "defect_injected": defect_type,
            "output": output
        }
