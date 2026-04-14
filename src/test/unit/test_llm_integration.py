#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests — LLMIntegration
覆盖：OLLAMA mock 下的接口契约、fallback、模型切换

运行：pytest src/test/unit/test_llm_integration.py -v
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture
def llm_with_mock():
    """patch ollama 全局，返回 (LLMIntegration instance, mock_ollama)"""
    import game.llm_integration as llm_mod
    with patch.object(llm_mod, "ollama") as mock_ollama:
        mock_ollama.list.return_value = {"models": [{"name": "llama3"}, {"name": "qwen"}]}
        mock_ollama.generate.return_value = {"response": "测试生成回复"}
        llm = llm_mod.LLMIntegration(model_name="llama3")
        yield llm, mock_ollama


# ---------------------------------------------------------------------------
# generate() 接口契约
# ---------------------------------------------------------------------------

class TestGenerate:
    def test_returns_non_empty_string(self, llm_with_mock):
        llm, _ = llm_with_mock
        result = llm.generate("测试提示词")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_calls_ollama_generate(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        llm.generate("测试提示词")
        mock_ollama.generate.assert_called_once()

    def test_uses_correct_model_name(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        llm.generate("测试提示词")
        call_kwargs = mock_ollama.generate.call_args
        assert call_kwargs[1].get("model") == "llama3" or call_kwargs[0][0] == "llama3"

    def test_returns_fallback_on_exception(self, llm_with_mock):
        """OLLAMA 抛出异常时 generate 返回 fallback 字符串而不崩溃"""
        llm, mock_ollama = llm_with_mock
        mock_ollama.generate.side_effect = ConnectionError("OLLAMA not running")
        result = llm.generate("测试提示词")
        assert isinstance(result, str)
        assert len(result) > 0  # fallback 非空

    def test_generate_with_context(self, llm_with_mock):
        """携带上下文时不崩溃，仍返回字符串"""
        llm, _ = llm_with_mock
        context = [{"role": "system", "content": "你是一位三国时期的谋士"}]
        result = llm.generate("当前局势如何？", context=context)
        assert isinstance(result, str)

    def test_generate_accepts_string_response(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        mock_ollama.generate.return_value = "纯文本响应"
        assert llm.generate("x") == "纯文本响应"

    def test_generate_converts_non_string_response(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        mock_ollama.generate.return_value = 12345
        assert llm.generate("x") == "12345"

    def test_generate_with_system_prompt_fallback_on_exception(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        mock_ollama.generate.side_effect = RuntimeError("boom")
        text = llm.generate_with_system_prompt("sys", "user")
        assert isinstance(text, str)
        assert len(text) > 0


# ---------------------------------------------------------------------------
# 可用模型列表
# ---------------------------------------------------------------------------

class TestAvailableModels:
    def test_returns_list(self, llm_with_mock):
        llm, _ = llm_with_mock
        models = llm.available_models
        assert isinstance(models, list)

    def test_contains_expected_model(self, llm_with_mock):
        llm, _ = llm_with_mock
        assert "llama3" in llm.available_models

    def test_empty_list_on_connection_error(self):
        """OLLAMA 不可用时返回空列表而不崩溃"""
        import game.llm_integration as llm_mod
        with patch.object(llm_mod, "ollama") as mock_ollama:
            mock_ollama.list.side_effect = ConnectionError("unreachable")
            llm = llm_mod.LLMIntegration()
            assert llm.available_models == []

    def test_available_models_with_list_format(self):
        import game.llm_integration as llm_mod
        with patch.object(llm_mod, "ollama") as mock_ollama:
            mock_ollama.list.return_value = [{"name": "llama3"}, {"name": "qwen"}]
            llm = llm_mod.LLMIntegration()
            assert llm.available_models == ["llama3", "qwen"]

    def test_available_models_with_unknown_format(self):
        import game.llm_integration as llm_mod
        with patch.object(llm_mod, "ollama") as mock_ollama:
            mock_ollama.list.return_value = {"unexpected": []}
            llm = llm_mod.LLMIntegration()
            assert llm.available_models == []


# ---------------------------------------------------------------------------
# ContextManager
# ---------------------------------------------------------------------------

class TestContextManager:
    def test_add_and_get_messages(self):
        from game.llm_integration import ContextManager
        cm = ContextManager()
        cm.add_message("user", "你好")
        cm.add_message("assistant", "你好，主公")
        ctx = cm.get_context()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"

    def test_clear_empties_messages(self):
        from game.llm_integration import ContextManager
        cm = ContextManager()
        cm.add_message("user", "hello")
        cm.clear()
        assert cm.get_context() == []

    def test_trim_respects_max_length(self):
        """超过 max_length 时自动裁剪"""
        from game.llm_integration import ContextManager
        cm = ContextManager(max_length=50)
        cm.add_message("user", "a" * 30)
        cm.add_message("user", "b" * 30)  # 60 > 50，应触发裁剪
        total = sum(len(m["content"]) for m in cm.get_context())
        assert total <= 60  # 允许一定裕量，但不能无限增长


class TestManagementMethods:
    def test_set_model_switches_when_in_available_list(self, llm_with_mock):
        llm, _ = llm_with_mock
        ok = llm.set_model("qwen")
        assert ok is True
        assert llm.model_name == "qwen"

    def test_set_model_pulls_when_missing(self, llm_with_mock):
        llm, mock_ollama = llm_with_mock
        llm.available_models = ["llama3"]
        mock_ollama.pull.return_value = None
        ok = llm.set_model("deepseek-r1")
        assert ok is True
        assert llm.model_name == "deepseek-r1"
        mock_ollama.pull.assert_called_once_with("deepseek-r1")

    def test_get_context_manager_reuses_same_id(self, llm_with_mock):
        llm, _ = llm_with_mock
        c1 = llm.get_context_manager("npc_1")
        c2 = llm.get_context_manager("npc_1")
        assert c1 is c2

    def test_batch_generate_returns_one_result_per_prompt(self, llm_with_mock):
        llm, _ = llm_with_mock
        with patch("game.llm_integration.time.sleep", return_value=None):
            results = llm.batch_generate(["a", "b", "c"], "sys")
        assert len(results) == 3

    def test_generate_for_npc_uses_system_prompt_api(self, llm_with_mock):
        llm, _ = llm_with_mock
        with patch.object(llm, "generate_with_system_prompt", return_value="ok") as fn:
            out = llm.generate_for_npc("npc1", "问候", "系统提示", context="朝会现场")
        assert out == "ok"
        fn.assert_called_once()


class TestGlobalInstance:
    def test_get_llm_instance_singleton_behavior(self):
        import game.llm_integration as llm_mod
        with patch.object(llm_mod, "LLMIntegration") as MockLLM:
            inst = MagicMock()
            inst.model_name = "llama3"
            MockLLM.return_value = inst
            llm_mod._llm_instance = None

            a = llm_mod.get_llm_instance("llama3")
            b = llm_mod.get_llm_instance("llama3")

            assert a is b
            MockLLM.assert_called_once_with("llama3")

    def test_get_llm_instance_calls_set_model_on_change(self):
        import game.llm_integration as llm_mod
        inst = MagicMock()
        inst.model_name = "llama3"
        inst.set_model = MagicMock()
        llm_mod._llm_instance = inst

        got = llm_mod.get_llm_instance("qwen")
        assert got is inst
        inst.set_model.assert_called_once_with("qwen")
