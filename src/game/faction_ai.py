#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FactionAI — 非玩家势力月度自动决策
每月为指定势力随机选取一个议题，按其立场（alignment）选择对应选项，
将 dimension_effects 应用到 faction_dimensions，不影响玩家维度。
"""
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_model import GameModel


class FactionAI:
    """为非玩家势力执行月度朝会决策。"""

    # alignment → 偏好 option index（与官员个性化系统保持一致）
    _ALIGNMENT_INDEX = {"hawk": 0, "pragmatist": 1, "dove": 2}

    def __init__(self, game_model: "GameModel"):
        self._model = game_model

    def run_monthly_decision(self, faction_id: str) -> dict:
        """为 `faction_id` 随机选题并按立场自动决策，应用 dimension_effects。

        Returns:
            {"faction": ..., "topic_id": ..., "option_id": ..., "effects": ...}
        """
        from game.court_topic_loader import CourtTopicLoader

        topics = CourtTopicLoader.load_topics()
        topic = random.choice(topics)

        alignment = (
            self._model.game_data["factions"]
            .get(faction_id, {})
            .get("alignment", "pragmatist")
        )
        index = self._ALIGNMENT_INDEX.get(alignment, 1)
        index = min(index, len(topic["options"]) - 1)
        option = topic["options"][index]

        effects = option.get("dimension_effects", {})
        self._apply_faction_dimension_effects(faction_id, effects)

        return {
            "faction": faction_id,
            "topic_id": topic["id"],
            "option_id": option["id"],
            "effects": effects,
        }

    def _apply_faction_dimension_effects(self, faction_id: str, effects: dict):
        """将 dimension_effects 写入该势力的 faction_dimensions，裁剪到 [0, 100]。"""
        valid_keys = {"military", "economy", "technology", "public_order", "diplomacy"}
        dims = self._model.game_data.setdefault(
            "faction_dimensions", {}
        ).setdefault(
            faction_id,
            {k: 50 for k in valid_keys}
        )
        for key, delta in effects.items():
            if key in valid_keys:
                dims[key] = max(0, min(100, dims.get(key, 50) + delta))
