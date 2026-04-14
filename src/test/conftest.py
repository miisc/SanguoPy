#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest fixtures for SanguoPy tests
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# 将 src 目录加入搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def game_model():
    """返回干净的 GameModel 实例（不读取磁盘文件）"""
    from game.game_model import GameModel
    with patch("game.game_model.os.path.exists", return_value=False):
        model = GameModel()
    return model


@pytest.fixture
def court_meeting_system(game_model):
    """返回绑定了 game_model 的 CourtMeetingSystem（无 Qt 事件循环依赖）"""
    from game.court_meeting import CourtMeetingSystem

    # PyQt5 信号在测试中需要 QApplication 存在；用 mock 规避
    system = CourtMeetingSystem.__new__(CourtMeetingSystem)
    system.game_model = game_model
    system.current_meeting = None
    system.meeting_active = False
    system.topic_templates = []

    # 载入真实模板（从父类 __init__ 复制）
    real = CourtMeetingSystem(game_model)
    system.topic_templates = real.topic_templates
    return system


@pytest.fixture
def mock_llm():
    """返回 LLMIntegration 实例，OLLAMA 调用被完整 mock"""
    with patch("game.llm_integration.ollama") as mock_ollama:
        mock_ollama.list.return_value = {"models": [{"name": "llama3"}]}
        mock_ollama.generate.return_value = {"response": "测试回复文本"}
        from game.llm_integration import LLMIntegration
        llm = LLMIntegration(model_name="llama3")
        yield llm, mock_ollama
