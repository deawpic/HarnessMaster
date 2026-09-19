#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Optimization & Test Control Guardian (unittest_policy_guardian)
HarnessMaster Production Reference Module

Enforces the Strict Token Optimization & Test Control Protocol:
1. Zero-Test by default (Implementation-Only Mode).
2. Explicit Opt-In Trigger Verification ("write test", "unit test", "test this", "run tests", "generate test suite").
3. Minimal Context & Execution Log Suppression flags (pytest -q --tb=short --maxfail=1).
4. Strict Auto-Fix Loop Limit: Maximum 2 attempts before immediate stop.
5. Lightweight Verification Alternatives (Static linters / type checkers).
"""

import re
from typing import Any, Dict, List, Optional


TRIGGER_KEYWORDS: List[str] = [
    "write test",
    "unit test",
    "test this",
    "run tests",
    "generate test suite",
    "run test",
    "เขียนเทส",
    "รันเทส",
    "ทดสอบระบบ"
]

SUPPRESSED_COMMANDS: Dict[str, str] = {
    "python": "pytest {path} -q --tb=short --maxfail=1",
    "typescript": "npx vitest run {path} --reporter=compact",
    "javascript": "npm test -- {path} --bail",
    "go": "go test -v -run {test_name} {pkg}",
    "rust": "cargo test {test_name} -- --nocapture"
}

STATIC_CHECKERS: Dict[str, List[str]] = {
    "python": ["ruff check .", "mypy --quick ."],
    "typescript": ["npx tsc --noEmit"],
    "javascript": ["npm run lint"],
    "go": ["golangci-lint run"],
    "rust": ["cargo check"]
}

MAX_AUTO_FIX_ATTEMPTS: int = 2


class TestControlGuardian:
    """Guardian enforcing the strict token optimization and test execution directive."""

    def __init__(self, max_auto_fix_attempts: int = MAX_AUTO_FIX_ATTEMPTS):
        self.max_auto_fix_attempts = max_auto_fix_attempts
        self.current_attempt = 0

    @staticmethod
    def is_testing_triggered(prompt: str) -> bool:
        """Determines if the prompt explicitly opts into testing mode."""
        prompt_lower = prompt.lower()
        return any(keyword.lower() in prompt_lower for keyword in TRIGGER_KEYWORDS)

    @staticmethod
    def get_suppressed_command(
        language: str,
        path: str = "",
        test_name: str = "",
        pkg: str = ""
    ) -> str:
        """Returns the token-suppressed test command for the specified language."""
        lang_key = language.lower()
        template = SUPPRESSED_COMMANDS.get(lang_key, SUPPRESSED_COMMANDS["python"])
        return template.format(
            path=path or "<path>",
            test_name=test_name or "<test_name>",
            pkg=pkg or "<pkg>"
        )

    @staticmethod
    def get_static_checkers(language: str) -> List[str]:
        """Returns lightweight static checkers and linters as alternatives to heavy unit tests."""
        return STATIC_CHECKERS.get(language.lower(), [])

    def record_attempt(self) -> Dict[str, Any]:
        """Records an auto-fix attempt and checks if the hard loop limit has been exceeded."""
        self.current_attempt += 1
        allowed = self.current_attempt <= self.max_auto_fix_attempts
        return {
            "attempt": self.current_attempt,
            "max_allowed": self.max_auto_fix_attempts,
            "allowed": allowed,
            "must_stop": not allowed,
            "message": (
                f"Attempt {self.current_attempt} of {self.max_auto_fix_attempts}"
                if allowed
                else f"Hard stop triggered: Maximum {self.max_auto_fix_attempts} auto-fix attempts reached. Reverting broken test changes."
            )
        }

    def reset_attempts(self) -> None:
        """Resets the auto-fix attempt counter."""
        self.current_attempt = 0

    @staticmethod
    def format_concise_failure(raw_output: str, max_lines: int = 5) -> str:
        """Extracts and formats error signature to under max_lines to prevent token bloat."""
        lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
        if not lines:
            return "Test failed with no output."

        error_lines: List[str] = []
        for line in reversed(lines):
            if any(term in line.lower() for term in ["failed", "error", "assert", "exception", "fail"]):
                error_lines.insert(0, line)
                if len(error_lines) >= max_lines:
                    break

        if not error_lines:
            error_lines = lines[-max_lines:]

        return "\n".join(error_lines[:max_lines])

    @staticmethod
    def audit_file_access(file_path: str, is_testing_mode: bool) -> Dict[str, Any]:
        """Validates file access against the Zero-Test policy when in Implementation-Only mode."""
        test_patterns = [
            r"(^|/)(test_|.*_test\.|__tests__/|tests/|\.spec\.|\.test\.)"
        ]
        is_test_file = any(re.search(pat, file_path) for pat in test_patterns)

        if is_test_file and not is_testing_mode:
            return {
                "allowed": False,
                "reason": (
                    f"Zero-Test Policy Violation: File '{file_path}' is a test file. "
                    "Access is prohibited in Implementation-Only Mode unless explicit testing trigger is present."
                )
            }
        return {"allowed": True, "reason": "Access allowed"}


def audit_test_policy_compliance(agents_md_content: str) -> Dict[str, Any]:
    """Audits whether an AGENTS.md document incorporates the Strict Token Optimization directive."""
    indicators = [
        ("zero_test_policy", r"(zero-test|implementation-only|ห้ามเขียน.*test|ห้ามรัน.*test)", "Strict Zero-Test Policy"),
        ("explicit_opt_in", r"(opt-in|trigger words|write test|unit test)", "Explicit Opt-In Triggers"),
        ("log_suppression", r"(--tb=short|-q|--reporter=compact|ระงับ.*log)", "Test Log Suppression Flags"),
        ("auto_fix_limit", r"(max.*2|ไม่เกิน 2|2 attempts|auto-fix)", "Max 2 Auto-Fix Attempts Limit"),
        ("static_checks", r"(static|linter|ruff|mypy|tsc)", "Lightweight Static Verification Alternative")
    ]

    missing = []
    found = []
    for key, pattern, label in indicators:
        if re.search(pattern, agents_md_content, re.IGNORECASE):
            found.append(label)
        else:
            missing.append(label)

    score = int((len(found) / len(indicators)) * 100)
    return {
        "passed": len(missing) == 0,
        "score": score,
        "found_rules": found,
        "missing_rules": missing
    }


if __name__ == "__main__":
    guardian = TestControlGuardian()
    print("Testing Trigger Check:")
    print("  'please implement auth' ->", guardian.is_testing_triggered("please implement auth"))
    print("  'please write test for auth' ->", guardian.is_testing_triggered("please write test for auth"))

    print("\nSuppressed Test Commands:")
    print("  Python:", guardian.get_suppressed_command("python", "tests/test_auth.py"))
    print("  TypeScript:", guardian.get_suppressed_command("typescript", "src/auth.test.ts"))

    print("\nAuto-Fix Loop Counter:")
    print("  Attempt 1:", guardian.record_attempt())
    print("  Attempt 2:", guardian.record_attempt())
    print("  Attempt 3:", guardian.record_attempt())

    print("\nFile Access Check:")
    print("  'tests/test_foo.py' (Testing Mode OFF) ->", guardian.audit_file_access("tests/test_foo.py", False))
    print("  'tests/test_foo.py' (Testing Mode ON) ->", guardian.audit_file_access("tests/test_foo.py", True))
    print("  'src/foo.py' (Testing Mode OFF) ->", guardian.audit_file_access("src/foo.py", False))
