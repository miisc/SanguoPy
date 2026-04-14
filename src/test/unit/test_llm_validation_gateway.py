"""
Tests for LlmValidationGateway (F5).
Validation order: schema → numeric (magnitude) → balance → historical (MVP placeholder).
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from game.llm_validation_gateway import LlmValidationGateway

TEMPLATE_EFFECTS = {"military": 5, "economy": -3, "technology": 0, "public_order": 0, "diplomacy": 0}

VALID_PROPOSAL = {
    "proposal_id": "p001",
    "proposal_type": "military",
    "title": "增兵北伐",
    "background": "边境紧张",
    "options": [
        {"option_id": "A", "label": "大规模增兵", "effects": {"military": 10, "economy": -8}},
        {"option_id": "B", "label": "维持现状", "effects": {"military": 0, "economy": 0}},
    ],
    "base_effects": {},
    "constraints": [],
    "source_tag": "template",
}


class TestLlmValidationGateway:
    def setup_method(self):
        self.gw = LlmValidationGateway()

    def test_schema_violation_falls_back(self):
        """Proposal missing required fields → schema failure → fallback to template."""
        incomplete_proposal = {"proposal_type": "military"}  # missing 7 required fields
        llm_effects = {"military": 5, "economy": -3, "technology": 0, "public_order": 0, "diplomacy": 0}
        result = self.gw.apply_with_fallback(llm_effects, TEMPLATE_EFFECTS, proposal=incomplete_proposal)
        assert result["fallback_applied"] is True
        assert "schema" in result["audit_log"]["failed_rules"]
        assert result["effects"] == TEMPLATE_EFFECTS

    def test_magnitude_violation_falls_back(self):
        """Single dimension delta > 15 → magnitude failure → fallback to template."""
        llm_effects = {"military": 20, "economy": -5, "technology": 0, "public_order": 0, "diplomacy": 0}
        result = self.gw.apply_with_fallback(llm_effects, TEMPLATE_EFFECTS)
        assert result["fallback_applied"] is True
        assert "magnitude" in result["audit_log"]["failed_rules"]
        assert result["effects"] == TEMPLATE_EFFECTS

    def test_balance_violation_falls_back(self):
        """All non-negative effects (no tradeoff) → balance failure → fallback to template."""
        llm_effects = {"military": 5, "economy": 3, "technology": 0, "public_order": 0, "diplomacy": 0}
        result = self.gw.apply_with_fallback(llm_effects, TEMPLATE_EFFECTS)
        assert result["fallback_applied"] is True
        assert "balance" in result["audit_log"]["failed_rules"]
        assert result["effects"] == TEMPLATE_EFFECTS

    def test_valid_effects_pass_and_audit_logged(self):
        """Effects within all bounds with tradeoff → pass, use LLM values, audit log complete."""
        llm_effects = {"military": 8, "economy": -5, "technology": 3, "public_order": 0, "diplomacy": 0}
        result = self.gw.apply_with_fallback(llm_effects, TEMPLATE_EFFECTS, proposal=VALID_PROPOSAL)
        assert result["fallback_applied"] is False
        assert result["effects"] == llm_effects
        audit = result["audit_log"]
        assert audit["validation_result"] == "passed"
        required_fields = [
            "request_id", "proposal_id", "template_effects", "llm_effects",
            "validation_result", "failed_rules", "fallback_applied", "timestamp",
        ]
        for field in required_fields:
            assert field in audit, f"audit_log missing field: {field}"
