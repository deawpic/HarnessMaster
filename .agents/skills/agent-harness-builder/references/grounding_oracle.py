# -*- coding: utf-8 -*-
"""
Grounding Oracle & Anti-Hallucination Verifier
HarnessMaster - Reusable Reference Implementation
Synthesized from: MedMate & thlawdeka Production Harnesses

Features:
1. Citation & Identifier Extraction (PMIDs, Deka numbers, statutes, Git SHAs, SemVers)
2. Grounding Whitelist Oracle verification against verified cache/payload
3. Sanitizer: automatically strips unverified citations while preserving principle
4. Anti-Sycophancy & Discretion Gatekeeper: detects absolute guarantees (100% win/cure)
5. Domain-Adaptive Regex Engine (Medical, Legal, Software/DevOps, Finance, General)
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("HarnessMaster.GroundingOracle")

# 1. Absolute guarantee phrases violating Judicial / Clinical / System Discretion Gate
PROHIBITED_ABSOLUTE_GUARANTEES = [
    re.compile(r"ชนะ(?:คดี)?(?:อย่าง)?แน่นอน\s*(?:100%|ร้อยเปอร์เซ็นต์)?", re.IGNORECASE),
    re.compile(r"ศาลต้อง(?:ตัดสิน|พิพากษา|ยกฟ้อง)(?:ให้(?:ท่าน)?ชนะ)?(?:อย่าง)?แน่นอน", re.IGNORECASE),
    re.compile(r"การันตีผล(?:คดี|การรักษา|การทำงาน)?\s*(?:100%)?", re.IGNORECASE),
    re.compile(r"รับรองผล(?:คดี|แพ้ชนะ|หายขาด)?", re.IGNORECASE),
    re.compile(r"หายขาด(?:แน่นอน|100%)", re.IGNORECASE),
    re.compile(r"ไม่มีทาง(?:ผิดพลาด|ล้มเหลว|บั๊ก)", re.IGNORECASE),
]

# 2. Domain-specific Citation Regexes
CITATION_PATTERNS = {
    # Medical citations
    "pmid": re.compile(r"\bPMID:\s*(\d{6,9})\b", re.IGNORECASE),
    "doi": re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE),
    "icd": re.compile(r"\b(?:ICD-10|ICD-11)\s*([A-Z]\d{2}(?:\.\d{1,2})?)\b", re.IGNORECASE),

    # Legal citations
    "deka": re.compile(r"(?:คำพิพากษาศาลฎีกาที่|คำพิพากษาฎีกาที่|ฎีกาที่|ฎีกาเลขที่|ฎ\.)\s*(\d+/\d{2,4})", re.IGNORECASE),
    "statute": re.compile(r"(?:ประมวลกฎหมาย(?:แพ่งและพาณิชย์|อาญา|วิธีพิจารณาความแพ่ง|วิธีพิจารณาความอาญา|ที่ดิน)|ป\.(?:พ\.พ\.|อ\.|วิ\.พ\.|วิ\.อ\.|ที่ดิน)|พ\.ร\.บ\.)\s*(?:มาตรา|ม\.)?\s*(\d+)", re.IGNORECASE),

    # Software / DevOps citations
    "git_sha": re.compile(r"\bcommit\s+([0-9a-f]{7,40})\b", re.IGNORECASE),
    "cve": re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    "semver": re.compile(r"\bv?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?\b"),

    # Finance citations
    "tax_id": re.compile(r"\b(?:เลขประจำตัวผู้เสียภาษี|TAX ID)\s*(\d{13})\b", re.IGNORECASE),
    "sec_filing": re.compile(r"\b(?:Form|SEC)\s*(10-K|10-Q|8-K)\b", re.IGNORECASE),
}


class GroundingOracle:
    """
    Independent Verification Oracle ensuring AI Agents never hallucinate citations,
    statutes, case numbers, or commit hashes without ground-truth payload evidence.
    """

    def __init__(self, verified_whitelist: Optional[Set[str]] = None, cache_instance: Optional[Any] = None):
        self.verified_whitelist: Set[str] = set(verified_whitelist or [])
        self.cache = cache_instance

    def register_verified(self, identifier: str) -> None:
        """Adds a verified identifier to the in-memory whitelist and cache if present."""
        cleaned = identifier.strip()
        self.verified_whitelist.add(cleaned)
        if self.cache and hasattr(self.cache, "add_verified_identifier"):
            self.cache.add_verified_identifier(cleaned, source="grounding_oracle")

    def get_all_verified(self) -> Set[str]:
        """Combines in-memory and database cache verified identifiers."""
        combined = set(self.verified_whitelist)
        if self.cache and hasattr(self.cache, "get_all_verified_identifiers"):
            combined.update(self.cache.get_all_verified_identifiers())
        return combined

    @classmethod
    def extract_citations(cls, text: str, citation_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Extracts all domain citations from text."""
        extracted: Dict[str, List[str]] = {}
        patterns = {citation_type: CITATION_PATTERNS[citation_type]} if citation_type else CITATION_PATTERNS

        for ctype, pattern in patterns.items():
            matches = pattern.findall(text)
            cleaned_matches = []
            for m in matches:
                val = m[0] if isinstance(m, tuple) else m
                if val and val not in cleaned_matches:
                    cleaned_matches.append(val.strip())
            if cleaned_matches:
                extracted[ctype] = cleaned_matches

        return extracted

    def detect_unverified_citations(
        self,
        text: str,
        citation_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Finds any citations present in text that are NOT in the verified whitelist."""
        verified = self.get_all_verified()
        extracted = self.extract_citations(text, citation_type)
        unverified: Dict[str, List[str]] = {}

        for ctype, citations in extracted.items():
            diff = [c for c in citations if c not in verified]
            if diff:
                unverified[ctype] = diff

        return unverified

    def sanitize_unverified_citations(
        self,
        text: str,
        citation_type: str = "deka",
        fallback_phrase: str = "บรรทัดฐาน/แนวทางอ้างอิงที่พึงเทียบเคียง"
    ) -> str:
        """
        Sanitizes text by replacing unverified citations with honest general descriptions,
        preventing citation hallucinations while preserving the core logic.
        """
        unverified = self.detect_unverified_citations(text, citation_type)
        unverified_items = unverified.get(citation_type, [])
        if not unverified_items:
            return text

        pattern = CITATION_PATTERNS.get(citation_type)
        if not pattern:
            return text

        sanitized = text
        for item in unverified_items:
            # Replace occurrences of this specific unverified item
            item_regex = re.compile(re.escape(item), re.IGNORECASE)
            sanitized = item_regex.sub(fallback_phrase, sanitized)

        return sanitized

    @classmethod
    def detect_absolute_guarantees(cls, text: str) -> List[Dict[str, Any]]:
        """Audits text for absolute guarantee violations (Judicial/Clinical Discretion Gate)."""
        violations = []
        for pat in PROHIBITED_ABSOLUTE_GUARANTEES:
            for match in pat.finditer(text):
                violations.append({
                    "matched_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "rule": "Judicial / Clinical Discretion Gate: Prohibited absolute certainty guarantee"
                })
        return violations

    def audit_response(self, text: str) -> Dict[str, Any]:
        """Comprehensive grounding and discretion audit."""
        unverified = self.detect_unverified_citations(text)
        guarantees = self.detect_absolute_guarantees(text)
        has_violations = bool(unverified or guarantees)

        return {
            "passed": not has_violations,
            "has_unverified_citations": bool(unverified),
            "unverified_citations": unverified,
            "guarantee_violations": guarantees,
            "total_issues": sum(len(v) for v in unverified.values()) + len(guarantees),
            "summary": "Passed Grounding Oracle and Discretion Gate" if not has_violations
                       else f"Detected issues: {len(unverified)} unverified citation types, {len(guarantees)} guarantee violations."
        }
