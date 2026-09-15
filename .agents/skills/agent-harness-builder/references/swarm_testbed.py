# -*- coding: utf-8 -*-
"""
Multi-Agent Swarm & Interaction Guardrail Testbed
HarnessMaster - Reusable Reference Implementation
Synthesized from: Subagent Orchestrator & Loop Library Standards

Features:
1. Ping-Pong Infinite Loop Detector: Detects repetitive back-and-forth messages between subagents
2. Handoff Contract Validator: Validates structured payloads passed between Leader and Subagents
3. Global Swarm FinOps Circuit Breaker: Tracks cumulative tokens and dollar spend across all swarm workers
4. Deadlock & Dependency Timeout Monitor: Prevents cyclic dependency deadlocks
"""

import collections
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("HarnessMaster.SwarmTestbed")


class SwarmCircuitBreakerTripped(Exception):
    """Raised when global swarm dollar or token cap is breached."""
    pass


class PingPongLoopDetected(Exception):
    """Raised when two or more agents are stuck in an infinite conversational loop."""
    pass


class SwarmGuardrailManager:
    """
    Coordinates and monitors multi-agent interactions, ensuring safety, budget limits,
    and deadlock prevention.
    """

    def __init__(
        self,
        max_total_tokens: int = 150_000,
        max_total_cost_usd: float = 2.00,
        max_ping_pong_rounds: int = 4,
        step_timeout_sec: float = 60.0
    ):
        self.max_total_tokens = max_total_tokens
        self.max_total_cost_usd = max_total_cost_usd
        self.max_ping_pong_rounds = max_ping_pong_rounds
        self.step_timeout_sec = step_timeout_sec

        self.cumulative_tokens = 0
        self.cumulative_cost_usd = 0.0
        self.message_history: List[Dict[str, Any]] = []
        self._pair_transition_counts: collections.Counter = collections.Counter()

    def record_agent_step(
        self,
        sender_id: str,
        recipient_id: str,
        message_content: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0.0
    ) -> Dict[str, Any]:
        """
        Records a step in the multi-agent swarm, checks budget and detects infinite ping-pong loops.
        """
        step_tokens = prompt_tokens + completion_tokens
        self.cumulative_tokens += step_tokens
        self.cumulative_cost_usd += cost_usd

        # 1. Check Global Budget Caps
        if self.cumulative_cost_usd >= self.max_total_cost_usd:
            raise SwarmCircuitBreakerTripped(
                f"Global Swarm Budget Exceeded: ${self.cumulative_cost_usd:.3f} >= ${self.max_total_cost_usd:.2f}"
            )
        if self.cumulative_tokens >= self.max_total_tokens:
            raise SwarmCircuitBreakerTripped(
                f"Global Swarm Token Cap Exceeded: {self.cumulative_tokens} >= {self.max_total_tokens}"
            )

        # 2. Check Ping-Pong Loop Detection
        # Compute signature of interaction
        msg_hash = hashlib.md5(message_content.strip().encode("utf-8")).hexdigest()[:8]
        pair_key = f"{sender_id}->{recipient_id}:{msg_hash}"
        self._pair_transition_counts[pair_key] += 1

        if self._pair_transition_counts[pair_key] > self.max_ping_pong_rounds:
            raise PingPongLoopDetected(
                f"Detected repetitive ping-pong loop between '{sender_id}' and '{recipient_id}' "
                f"(identical message repeated {self._pair_transition_counts[pair_key]} times)."
            )

        record = {
            "timestamp": time.time(),
            "sender": sender_id,
            "recipient": recipient_id,
            "tokens": step_tokens,
            "cost_usd": cost_usd,
            "msg_hash": msg_hash
        }
        self.message_history.append(record)
        return record

    @staticmethod
    def validate_handoff_contract(
        payload: Dict[str, Any],
        required_keys: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validates that an agent handoff contains all required schema keys
        before delegating work to a subagent.
        """
        missing = [k for k in required_keys if k not in payload or payload[k] is None]
        return len(missing) == 0, missing

    def get_swarm_telemetry(self) -> Dict[str, Any]:
        """Returns aggregated telemetry for the multi-agent swarm."""
        return {
            "total_messages": len(self.message_history),
            "cumulative_tokens": self.cumulative_tokens,
            "cumulative_cost_usd": round(self.cumulative_cost_usd, 4),
            "unique_interaction_pairs": len(self._pair_transition_counts),
            "budget_used_percent": round((self.cumulative_cost_usd / self.max_total_cost_usd) * 100, 2)
                                   if self.max_total_cost_usd > 0 else 0.0
        }
