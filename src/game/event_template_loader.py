#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件模板加载器

从 docs/design/EVENT_TEMPLATES_MVP.json 加载重大事件模板，
并将其转换为 CourtMeetingSystem 所需的议题格式。
"""

import json
import os
from typing import Dict, Any, Optional

_TEMPLATE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "docs", "design", "EVENT_TEMPLATES_MVP.json")
)


class EventTemplateLoader:
    """按需加载并索引 EVENT_TEMPLATES_MVP.json，提供转换接口。"""

    _index: Optional[Dict[str, Any]] = None

    @classmethod
    def _load(cls) -> Dict[str, Any]:
        if cls._index is None:
            with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._index = {e["event_id"]: e for e in data["events"]}
        return cls._index

    @classmethod
    def get_template(cls, event_id: str) -> Optional[Dict[str, Any]]:
        """返回原始事件模板，未找到则返回 None。"""
        return cls._load().get(event_id)

    @classmethod
    def to_court_topic(cls, template: Dict[str, Any]) -> Dict[str, Any]:
        """将事件模板转换为 CourtMeetingSystem 议题格式。"""
        options = [
            {
                "id": opt["option_id"],
                "title": opt["label"],
                "description": opt["label"],
                "effects": {},
                "dimension_effects": opt["effects"],
            }
            for opt in template.get("options", [])
        ]
        return {
            "id": template["event_id"],
            "title": template["title"],
            "options": options,
        }
