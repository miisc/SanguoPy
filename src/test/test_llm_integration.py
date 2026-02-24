#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM集成架构测试
验证LLM集成的核心功能是否正常工作
"""

import unittest
from game.llm_integration import LLMIntegration, get_llm_instance, ContextManager


class TestLLMIntegration(unittest.TestCase):
    """测试LLM集成类"""
    
    def setUp(self):
        """设置测试环境"""
        self.llm = LLMIntegration()
    
    def test_initialization(self):
        """测试初始化功能"""
        self.assertIsInstance(self.llm, LLMIntegration)
        self.assertEqual(self.llm.model_name, "llama3")
    
    def test_get_available_models(self):
        """测试获取可用模型列表"""
        models = self.llm.available_models
        self.assertIsInstance(models, list)
    
    def test_generate(self):
        """测试文本生成功能"""
        prompt = "你好，请简单介绍一下自己"
        response = self.llm.generate(prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_generate_with_system_prompt(self):
        """测试带系统提示词的文本生成"""
        system_prompt = "你是一名三国时期的谋士，说话风格古雅，知识渊博。"
        user_prompt = "请分析当前的天下大势"
        response = self.llm.generate_with_system_prompt(system_prompt, user_prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_get_context_manager(self):
        """测试获取上下文管理器"""
        context_manager = self.llm.get_context_manager("test_context")
        self.assertIsInstance(context_manager, ContextManager)
    
    def test_context_manager(self):
        """测试上下文管理器功能"""
        context_manager = ContextManager()
        context_manager.add_message("user", "你好")
        context_manager.add_message("assistant", "你好，有什么可以帮助你的？")
        context = context_manager.get_context()
        self.assertEqual(len(context), 2)
        context_manager.clear()
        self.assertEqual(len(context_manager.get_context()), 0)
    
    def test_generate_for_npc(self):
        """测试为NPC生成文本"""
        npc_id = "zhuge_liang"
        prompt = "请你对当前的军事形势发表看法"
        system_prompt = "你是诸葛亮，三国时期蜀汉丞相，足智多谋，忠诚勤勉。说话风格谨慎，考虑周全。"
        context = "当前刘备刚刚占据益州，与曹操、孙权形成三足鼎立之势。"
        response = self.llm.generate_for_npc(npc_id, prompt, system_prompt, context)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_batch_generate(self):
        """测试批量生成功能"""
        prompts = ["你好", "今天天气如何", "再见"]
        system_prompt = "你是一名友好的助手，回答简洁明了。"
        responses = self.llm.batch_generate(prompts, system_prompt)
        self.assertEqual(len(responses), 3)
        for response in responses:
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
    
    def test_get_llm_instance(self):
        """测试获取全局LLM实例"""
        instance1 = get_llm_instance()
        instance2 = get_llm_instance()
        self.assertIs(instance1, instance2)
        self.assertIsInstance(instance1, LLMIntegration)


if __name__ == "__main__":
    unittest.main()