---
name: agent-harness-builder
description: >-
  Master guide for designing, architecting, implementing, auditing, refactoring, and optimizing production-grade
  Agent Harnesses. Covers execution sandboxing, benchmark evaluation runners, mock tool environments,
  trajectory verification, and performance optimization for existing and new harnesses.
---

# Agent Harness Builder & Optimizer

The **Agent Harness** is the mission-critical foundation surrounding an AI Agent. It provides isolated execution environments, tool/API mocking, deterministic state management, trajectory recording, automated evaluations, and guardrail enforcement.

---

## 1. Core Architecture of an Agent Harness

A production agent harness is composed of 6 modular layers:

```text
┌──────────────────────────────────────────────────────────────┐
│                   1. Agent Testbed Runner                    │
│      (Dataset Loader, Parallel Execution, Param Matrix)      │
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

## 2. The 6 Pillars of Agent Harnessing

### Pillar 1: Isolated Sandbox & Environment Management
- **Workspace Isolation**: Spin up ephemeral working directories per test case or session.
- **Clean State Reset**: Restore Git commit ancestry, database seed data, or filesystem trees before each task run.
- **Execution Boundaries**: Enforce strict timeouts, memory limits, and non-root execution permissions.

### Pillar 2: Tool Registry & Mocking Engine
- **Deterministic Tool Mocking**: Provide recorded or synthetic responses for external APIs (search, databases, email, HTTP).
- **Fault Injection**: Simulate real-world edge cases (HTTP 429 rate limits, socket timeouts, invalid JSON payloads) to test agent resilience.
- **Protocol Compliance**: Support standard protocols (MCP - Model Context Protocol, OpenAI Function Calling, LangChain Tools).

### Pillar 3: Trajectory Recording & Observability
- **Full Trace Capture**: Log every `step_index`, `thought` / reasoning chain, `tool_call` name/arguments, raw tool output, and model completion.
- **Standardized Schema**: Output standardized JSONL transcripts compatible with Langfuse, OpenTelemetry, or custom visualization dashboards.
- **Cost & Token Telemetry**: Aggregate prompt tokens, completion tokens, cached tokens, and USD cost per task run.

### Pillar 4: Verification & Grading Engine
- **Multi-Modal Evaluation**:
  - **Deterministic Assertions**: File diff checks, exit code checks, unit test pass rates (`pytest`, `vitest`).
  - **State Invariant Checks**: Database row verification, schema integrity validation.
  - **LLM-as-a-Judge**: Rubric-based scoring for fuzzy criteria, code quality, or stylistic adherence.
- **Anti-Hallucination Gate**: Never accept the agent's self-reported "Done" status without independent verification against ground truth artifacts.

### Pillar 5: Safety & Circuit Breakers
- **Infinite Loop Detection**: Detect repetitive tool calls with identical arguments or cyclic state transitions.
- **Token & Cost Budgets**: Hard-stop agent execution when token or dollar limits are breached.
- **Harmful Action Interception**: Blacklist dangerous shell operations (e.g. `rm -rf /`, raw disk formatting, unauthorized network egress).

### Pillar 6: Benchmark & Dataset Testbed
- **Dataset Connectors**: Support standard benchmarks (SWE-bench, GAIA, AgentBench, WebArena) and internal custom test suites.
- **Parallel Runner**: Execute task suites across concurrent worker threads or containers with deterministic seeding.
- **Metrics Aggregator**: Calculate `Pass@1`, `Pass@k`, precision/recall on tool usage, average step count, and cost-per-resolution.

---

## 3. Step-by-Step Runbook: Building a New Agent Harness

### Step 1: Define the Agent Interface & Contract
Standardize the agent invocation interface:
```python
from typing import Any, Protocol, TypedDict

class AgentStep(TypedDict):
    step: int
    thought: str
    tool: str | None
    tool_args: dict[str, Any] | None
    observation: str | None

class AgentResult(TypedDict):
    task_id: str
    status: str  # "completed", "max_steps", "error"
    trajectory: list[AgentStep]
    final_output: str
    tokens_used: int
    duration_sec: float

class AgentRunner(Protocol):
    def run_task(self, task_id: str, prompt: str, workspace_path: str) -> AgentResult:
        ...
```

### Step 2: Implement Ephemeral Workspace Sandbox
```python
import tempfile, shutil, subprocess
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def ephemeral_workspace(seed_repo_url: str = None, seed_files: dict[str, str] = None):
    temp_dir = tempfile.mkdtemp(prefix="agent_harness_")
    workspace = Path(temp_dir)
    try:
        if seed_repo_url:
            subprocess.run(["git", "clone", seed_repo_url, str(workspace)], check=True)
        if seed_files:
            for rel_path, content in seed_files.items():
                dest = workspace / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
        yield workspace
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
```

### Step 3: Implement Tool Interceptor & Mock Registry
```python
class MockToolRegistry:
    def __init__(self):
        self._mocks: dict[str, Any] = {}
        self._call_log: list[dict[str, Any]] = []

    def register_mock(self, tool_name: str, handler):
        self._mocks[tool_name] = handler

    def execute(self, tool_name: str, args: dict[str, Any]) -> str:
        self._call_log.append({"tool": tool_name, "args": args})
        if tool_name in self._mocks:
            return self._mocks[tool_name](args)
        raise ValueError(f"Tool {tool_name} not found in harness mock registry")
```

### Step 4: Verification & Evaluator Implementation
```python
class TaskEvaluator:
    @staticmethod
    def evaluate_code_fix(workspace: Path, test_command: list[str]) -> bool:
        result = subprocess.run(
            test_command,
            cwd=str(workspace),
            capture_output=True,
            text=True
        )
        return result.returncode == 0
```

---

## 4. Auditing, Refactoring & Optimizing Existing Harnesses

When tasked with improving an existing harness written by a user or team, follow this systematic 4-phase audit and optimization protocol:

### Phase A: Diagnostic Audit Checklist (Anti-Pattern Scan)
Inspect existing code against common harness anti-patterns:
1. 🚩 **Host Contamination**: Does the agent execute directly in the project directory without an ephemeral copy?
2. 🚩 **Self-Evaluation Bias**: Does the test assert on the LLM's textual reply instead of exit codes / AST diffs?
3. 🚩 **State Leakage Across Runs**: Are tool mocks or in-memory caches shared without resetting between test runs?
4. 🚩 **Blind Trajectories**: Are step reasoning, tool inputs/outputs, and tokens lost or unlogged?
5. 🚩 **Uncontrolled Spend/Timeouts**: Are there no maximum step guards, per-step timeouts, or budget circuit breakers?
6. 🚩 **Sequential Bottlenecks**: Does running 50 benchmark cases take hours due to synchronous single-thread execution?

### Phase B: Performance & Concurrency Optimization
- **Parallel Task Execution**: Implement an `asyncio` or `ProcessPoolExecutor` benchmark harness with rate-limit throttling (Token Bucket).
- **In-Memory / RAM-Disk Sandboxing**: For heavy filesystem benchmarks, leverage `tmpfs` or ramdisks to eliminate disk I/O bottlenecks.
- **Context Caching & Prompt Optimization**: Cache immutable system instructions across repeated benchmark tasks to cut token costs by up to 80%.

```python
import asyncio
from typing import Callable, Coroutine

class AsyncBenchmarkRunner:
    def __init__(self, concurrency_limit: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def run_item(self, item: dict, runner_fn: Callable[[dict], Coroutine]) -> dict:
        async with self.semaphore:
            return await runner_fn(item)

    async def run_suite(self, items: list[dict], runner_fn: Callable[[dict], Coroutine]) -> list[dict]:
        tasks = [self.run_item(item, runner_fn) for item in items]
        return await asyncio.gather(*tasks)
```

### Phase C: Hardening & Guardrail Retrofitting
- Add schema validators on tool arguments (Pydantic / Zod).
- Wrap external tool calls in exponential backoff retry decorators with circuit breakers.
- Implement an automated loop detector that halts execution if the agent repeats the exact same tool call 3+ times.

### Phase D: Harness Self-Testing & Regression Suite
- Create deterministic **Mock Agent** fixtures (Simulated LLMs returning predefined trajectories) to test the harness itself:
  - Test: Does the harness correctly mark a failing trajectory as Failed?
  - Test: Does the harness abort on infinite loops?
  - Test: Does the harness clean up temp directories upon crashing?

---

## 5. Quality Checklist for Agent Harnesses

- [ ] **Determinism**: Does the harness produce repeatable results given fixed model seeds and mock data?
- [ ] **Isolation**: Are file system and network modifications strictly confined to the sandbox?
- [ ] **Observability**: Does the harness output complete trajectory logs (transcripts) with timing and token usage?
- [ ] **Independent Truth**: Is success evaluated via ground-truth assertions rather than model self-reporting?
- [ ] **Fault Tolerance**: Does the harness gracefully handle agent timeouts, crashes, and OOMs without hanging the test suite?
- [ ] **High Performance**: Is parallel execution supported with proper rate-limit backoff and memory management?
