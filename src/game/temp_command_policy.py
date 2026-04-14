#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时指令白名单策略加载器

从 docs/design/TEMP_COMMAND_POLICY_MVP.json 加载白名单配置，
为运行时提供指令合法性、触发条件、费用与冷却的查询接口。
"""

import json
import os
from typing import Dict, Optional, Any, Set


class TempCommandPolicy:
    """从 JSON 策略文件加载并查询临时指令白名单规则。"""

    DEFAULT_PATH = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "design", "TEMP_COMMAND_POLICY_MVP.json")
    )

    def __init__(self, policy_path: Optional[str] = None):
        path = policy_path or self.DEFAULT_PATH
        with open(path, "r", encoding="utf-8") as f:
            self._policy: Dict[str, Any] = json.load(f)

        self._whitelist: Dict[str, Dict[str, Any]] = {
            cmd["command_id"]: cmd for cmd in self._policy.get("whitelist", [])
        }
        global_limits = self._policy.get("global_limits", {})
        self.cost_per_command: int = global_limits.get("cost_per_command", 10)

    def is_whitelisted(self, command_id: str) -> bool:
        """指令 ID 是否在白名单中。"""
        return command_id in self._whitelist

    def get_command_config(self, command_id: str) -> Optional[Dict[str, Any]]:
        """返回指令的完整配置字典，不在白名单中则返回 None。"""
        return self._whitelist.get(command_id)

    def get_command_cost(self, command_id: str) -> int:
        """返回指令的诏令权威消耗（默认 cost_per_command）。"""
        cmd = self._whitelist.get(command_id)
        if cmd is None:
            return self.cost_per_command
        return cmd.get("cost", self.cost_per_command)

    def get_command_cooldown(self, command_id: str) -> int:
        """返回指令的同类型冷却旬数（默认 1）。"""
        cmd = self._whitelist.get(command_id)
        if cmd is None:
            return 1
        return cmd.get("cooldown_xun", 1)

    def is_trigger_met(self, command_id: str, active_event_codes: Set[str]) -> bool:
        """当前激活事件集合是否满足该指令的触发条件（any_of 语义）。"""
        cmd = self._whitelist.get(command_id)
        if cmd is None:
            return False
        any_of = cmd.get("trigger_rules", {}).get("any_of", [])
        if not any_of:
            return True  # 无触发约束，视为满足
        return bool(active_event_codes & set(any_of))
