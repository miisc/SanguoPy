"""
LLM Proposal Validation Gateway (F5).
Validates LLM-modified proposal effects against LLM_VALIDATION_POLICY_MVP.json.
Validation order: schema → numeric (magnitude) → balance → historical (MVP placeholder).
On failure: fallback to template_effects and record audit log.
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional


class LlmValidationGateway:
    _DEFAULT_POLICY_PATH = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "design", "LLM_VALIDATION_POLICY_MVP.json")
    )

    def __init__(self, policy_path: str = None):
        path = policy_path or self._DEFAULT_POLICY_PATH
        with open(path, "r", encoding="utf-8") as f:
            self._policy = json.load(f)

    def validate(
        self,
        llm_effects: Dict[str, int],
        template_effects: Dict[str, int],
        proposal: Optional[Dict] = None,
    ) -> Dict:
        """
        Run validation pipeline. Returns {valid, failed_rules, audit_log}.
        proposal is optional; when provided, schema validation runs first.
        """
        failed_rules: List[str] = []

        # 1. Schema validation
        if proposal is not None:
            required = self._policy["schema"]["required_fields"]
            missing = [f for f in required if f not in proposal]
            if missing:
                failed_rules.append("schema")

        # 2. Numeric (magnitude) validation
        numeric = self._policy["numeric_rules"]
        values = list(llm_effects.values())
        magnitude_fail = (
            any(abs(v) > numeric["single_dimension_delta_abs_max"] for v in values)
            or sum(v for v in values if v > 0) > numeric["sum_positive_delta_max"]
            or abs(sum(v for v in values if v < 0)) > numeric["sum_negative_delta_abs_max"]
            or (numeric["reject_if_all_dimensions_zero"] and all(v == 0 for v in values))
        )
        if magnitude_fail:
            failed_rules.append("magnitude")

        # 3. Balance validation — require at least one positive AND one negative
        if self._policy["balance_rules"]["require_tradeoff"]:
            has_pos = any(v > 0 for v in values)
            has_neg = any(v < 0 for v in values)
            if not (has_pos and has_neg):
                failed_rules.append("balance")

        # 4. Historical validation — MVP placeholder, not blocking
        #    (defers to Sanguozhi source; implement when historical DB is available)

        valid = len(failed_rules) == 0
        audit_log = {
            "request_id": str(uuid.uuid4()),
            "proposal_id": (proposal or {}).get("proposal_id", "unknown"),
            "template_effects": template_effects,
            "llm_effects": llm_effects,
            "validation_result": "passed" if valid else "failed",
            "failed_rules": failed_rules,
            "fallback_applied": not valid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return {"valid": valid, "failed_rules": failed_rules, "audit_log": audit_log}

    def apply_with_fallback(
        self,
        llm_effects: Dict[str, int],
        template_effects: Dict[str, int],
        proposal: Optional[Dict] = None,
    ) -> Dict:
        """
        Validate and apply. Returns {effects, fallback_applied, audit_log}.
        On failure: effects = template_effects. On success: effects = llm_effects.
        """
        result = self.validate(llm_effects, template_effects, proposal)
        effects = llm_effects if result["valid"] else template_effects
        return {
            "effects": effects,
            "fallback_applied": not result["valid"],
            "audit_log": result["audit_log"],
        }
