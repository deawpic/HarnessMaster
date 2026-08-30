# 🛡️ HarnessMaster — Master Agent Harness & Evaluation System

**HarnessMaster** เป็นระบบและสภาพแวดล้อมสำหรับพัฒนา ออกแบบ ตรวจสอบ ปรับปรุง (Audit & Refactor) ประเมินผล (Evaluate) และเพิ่มประสิทธิภาพ (Optimize) ให้กับ **Autonomous AI Agent Harnesses** ในระดับ Production โดยเน้นความแม่นยำ (Deterministic Execution), การแยกสภาพแวดล้อมอย่างปลอดภัย (Sandbox Isolation), และการวัดผลบน Ground Truth

---

## 🎯 พันธกิจและบทบาทหลัก (Core Mission & Identity)

- **Role**: Lead Agent Harness Architect, Evaluation Specialist & Harness Optimizer
- **Objective**: 
  1. **สร้างระบบใหม่ (Build from Scratch)**: ออกแบบ Agent Execution Harnesses, Benchmark Suites, Mock Tool Layers และ Verification Guardrails
  2. **ตรวจสอบและยกระดับ Harness เดิม (Audit & Refactor Existing Harnesses)**: สแกนหา Anti-Patterns, แก้ไข Memory/State Leaks, ยกระดับ Sandbox Isolation, และแปลงระบบ Synchronous ให้รันแบบ Async Parallel ประสิทธิภาพสูง

---

## 🏗️ สถาปัตยกรรม 6 ชั้นของ Agent Harness (6-Layer Architecture)

```text
┌──────────────────────────────────────────────────────────────┐
│                   1. Agent Testbed Runner                    │
│      (Dataset Loader, Parallel Execution, Benchmark Matrix)  │
├──────────────────────────────────────────────────────────────┤
│                2. Trajectory & Observability                 │
│         (Step Traces, Token Counters, Latency, Replay)       │
├──────────────────────────────────────────────────────────────┤
│           3. Verification & Evaluation Engine                │
│     (Deterministic State Diffs, Test Runners, LLM Judge)     │
├──────────────────────────────────────────────────────────────┤
│            4. Guardrails & Circuit Breakers                  │
│        (Loop Detection, Budget Caps, Safety Interceptors)    │
├──────────────────────────────────────────────────────────────┤
│               5. Tool & Protocol Mocking Layer               │
│        (MCP Proxies, Mock APIs, Fault Injection Engine)      │
├──────────────────────────────────────────────────────────────┤
│               6. Isolated Sandbox Environment                │
│       (Docker / Subprocess / Temp Workspaces / Git State)    │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 โครงสร้างโฟลเดอร์ในโปรเจกต์ (Workspace Structure)

```text
HarnessMaster/
├── README.md                                # รายละเอียดภาพรวมของโปรเจกต์ (ไฟล์นี้)
├── AGENTS.md                                # กฎระเบียบและบทบาทของ Agent ระดับ Workspace
└── .agents/
    ├── AGENTS.md                            # Workspace rules mirror
    └── skills/                              # คลังทักษะเฉพาะทางสำหรับงาน Harness & Evaluation
        ├── agent-harness-builder/           # [Flagship] ออกแบบ, สร้าง, ตรวจสอบ และ Optimize Harness ครบวงจร
        ├── agent-evaluation/                # ประเมิน & Benchmark AI Agents (SWE-bench, GAIA, Trajectory)
        ├── ai-agents-architect/             # สถาปัตยกรรม ReAct, Plan-and-Solve, Memory & Multi-Agent
        ├── mcp-builder/                     # พัฒนาและเชื่อมต่อ Model Context Protocol (MCP) Servers
        ├── langfuse/                        # Tracing, Telemetry, Latency & Eval Datasets
        ├── tool-use-guardian/               # Guardrails ดักจับ Tool Failures และป้องกัน Infinite Loop
        ├── context-window-management/       # ป้องกัน Context Rot, Compaction & Sliding Window
        ├── prompt-engineering/              # ปรับปรุง System Prompts และแบบจำลองการให้คะแนน (Rubrics)
        ├── subagent-orchestrator/           # ประสานงานและกระจายงานให้ Subagents แบบคู่ขนาน
        ├── test-driven-development/         # ระเบียบวิธี TDD สำหรับสร้าง Tool Mocks & Evaluators
        ├── python-testing-patterns/         # Pytest Fixtures, Mock Servers & Async Testing
        └── systematic-debugging/            # วิเคราะห์ Root Cause เมื่อ Agent ทำงานผิดพลาด
```

---

## ⚡ สรุปทักษะเฉพาะทาง (Skills Matrix)

| Workflow / งาน | Skills หลักที่ใช้งาน | คำอธิบาย |
| :--- | :--- | :--- |
| **สร้าง & วางระบบ Harness ใหม่** | `agent-harness-builder`, `ai-agents-architect` | วางโครงสร้าง Sandbox, Mock Tool Registry, Execution Loops และ Test Runners |
| **ตรวจสอบ & Optimize Harness เดิม** | `agent-harness-builder`, `systematic-debugging` | สแกนหาจุดรั่วไหลของ State, เพิ่ม Concurrency/Async, ฝัง Tracing และลดความ Flaky |
| **ประเมินผล & Benchmark** | `agent-evaluation`, `langfuse` | รันชุด Benchmark (SWE-bench, GAIA), คำนวณ Pass@k, วิเคราะห์ Trajectory และประเมินด้วย LLM-as-a-Judge |
| **จำลอง Tools & Protocol** | `mcp-builder`, `tool-use-guardian` | สร้าง MCP Servers, จำลอง Mock APIs และแทรกความผิดพลาด (Fault Injection) เพื่อทดสอบ Resilience |
| **จัดการ Context & Prompt** | `context-window-management`, `prompt-engineering` | ป้องกัน Context Degradation, บีบอัด Context, ปรับแต่ง Prompt และ System Instructions |
| **ทดสอบความถูกต้องของ Harness** | `test-driven-development`, `python-testing-patterns` | พัฒนา Unit & Integration Tests สำหรับเครื่องมือและ Evaluator ก่อนรันโมเดลจริง |
| **ตรวจแก้บั๊กและ Loop** | `systematic-debugging`, `tool-use-guardian` | หาสาเหตุที่แท้จริง (Root Cause) ของ Agent Failures, Trajectory Stalls และลดความ Flaky |
| **บริหารจัดการ Multi-Agent** | `subagent-orchestrator`, `ai-agents-architect` | กระจายงานแบบขนานระหว่าง Subagents พร้อมควบคุม Quota และการส่งผ่าน Context |

---

## 🔍 กระบวนการตรวจสอบและยกระดับ Harness (Audit & Optimization Protocol)

เมื่อผู้ใช้นำโค้ด Harness เดิมมาให้ปรับปรุง ระบบจะดำเนินการตาม 4 ขั้นตอน:
1. **Diagnostic Audit (Anti-Pattern Scan)**:
   - ตรวจสอบว่ารันโค้ดบน Host ตรงๆ หรือไม่ (ขาด Sandbox Isolation)
   - ตรวจสอบว่า Evaluator ตัดสินจากคำพูดโมเดลหรือไม่ (ขาด Deterministic Assertions)
   - ตรวจสอบการปนเปื้อนของ Mock State ข้ามรอบการทดสอบ
2. **Performance & Concurrency Optimization**:
   - ปรับเปลี่ยนชุดทดสอบขนาดใหญ่ให้รองรับ **AsyncIO / Multiprocessing Batch Execution** พร้อม Rate Limiting (Token Bucket) ป้องกัน HTTP 429
   - เพิ่ม RAM Disk / In-Memory Mocking เพื่อลด Disk I/O Bottleneck
3. **Hardening & Guardrails Retrofitting**:
   - ติดตั้ง Schema Validator บน Tool Arguments และเพิ่ม Loop Detector อัตโนมัติ
4. **Harness Regression Testing**:
   - สร้าง Mock Agent จำลองเพื่อทดสอบตัว Harness เอง ให้มั่นใจว่าไม่เกิด False Positive / False Negative

---

## ⚖️ กฎเหล็กและมาตรฐานคุณภาพ (Engineering Quality Gates)

1. **Deterministic Verification (Iron Law)**:
   - ห้ามตัดสินผลลัพธ์จากข้อความบอกเล่าของ Agent เอง ("Done" หรือ "สำเร็จแล้ว")
   - ผลลัพธ์ต้องได้รับการตรวจทานกับ **Ground Truth** เสมอ เช่น Unit Test Exit Codes, AST / Git Diffs, Database State หรือ Deterministic Oracle Checks
2. **Sandbox Isolation**:
   - การทดสอบหรือรัน Benchmark ต้องทำงานใน Ephemeral / Isolated Workspace เสมอ ไม่กระทบต่อ Host Repository
3. **Traceability by Default**:
   - ทุก Step ของ Agent จะต้องบันทึก: `step_index`, `thought`, `tool_name`, `arguments`, `raw_output`, `latency` และ `token_usage`
4. **Fault Injection & Resilience**:
   - ระบบ Harness ต้องมีเครื่องมือทดสอบ Edge Cases เช่น HTTP 429 Rate Limits, Network Timeout, Corrupted Tool Outputs และ Context Overflow
5. **High Throughput & Concurrency**:
   - ระบบ Harness ต้องรองรับการประเมินผลแบบขนาน (Parallel Batch Execution) โดยไม่เกิด Race Conditions หรือ State Leakage
6. **Test-First Implementation (TDD)**:
   - เขียน Unit Test และ Mock สำหรับ Tool และ Evaluator ให้พร้อมก่อนส่งงานให้ Agent รันจริง
