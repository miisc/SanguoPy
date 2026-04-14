#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM集成架构
为NPC拟人化提供核心引擎，支持智能对话生成和决策模拟
"""

import ollama
import json
import time
from typing import Dict, List, Optional, Any


class ContextManager:
    """上下文管理类，维护对话历史和状态"""
    
    def __init__(self, max_length: int = 2000):
        """初始化上下文管理器
        
        Args:
            max_length: 上下文最大长度
        """
        self.messages = []
        self.max_length = max_length
    
    def add_message(self, role: str, content: str):
        """添加消息到上下文
        
        Args:
            role: 消息角色 (system, user, assistant)
            content: 消息内容
        """
        self.messages.append({"role": role, "content": content})
        self._trim_context()
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取当前上下文
        
        Returns:
            上下文消息列表
        """
        return self.messages
    
    def clear(self):
        """清空上下文"""
        self.messages = []
    
    def _trim_context(self):
        """裁剪上下文长度，确保不超过最大长度"""
        total_length = sum(len(msg["content"]) for msg in self.messages)
        while total_length > self.max_length and len(self.messages) > 1:
            # 移除最早的非系统消息
            for i, msg in enumerate(self.messages):
                if msg["role"] != "system":
                    removed_length = len(msg["content"])
                    self.messages.pop(i)
                    total_length -= removed_length
                    break


class LLMIntegration:
    """LLM集成类，提供文本生成和管理功能"""
    
    def __init__(self, model_name: str = "llama3"):
        """初始化LLM集成
        
        Args:
            model_name: 使用的模型名称
        """
        self.model_name = model_name
        self.context_managers = {}
        self._ollama_available = True  # 首次连接失败后置 False，短路后续调用
        self.available_models = self._get_available_models()
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9
        }
    
    def _get_available_models(self) -> List[str]:
        """获取可用模型列表
        
        Returns:
            可用模型名称列表
        """
        try:
            models = ollama.list()
            # 适配不同版本的OLLAMA API响应格式
            if isinstance(models, list):
                return [model.get("name", "") for model in models if model.get("name")]
            elif isinstance(models, dict) and "models" in models:
                return [model.get("name", "") for model in models["models"] if model.get("name")]
            else:
                return []
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            self._ollama_available = False
            return []
    
    def generate(self, prompt: str, context: Optional[List[Dict[str, str]]] = None, 
                 params: Optional[Dict[str, Any]] = None) -> str:
        """生成文本
        
        Args:
            prompt: 用户提示词
            context: 上下文消息列表
            params: 生成参数
            
        Returns:
            生成的文本
        """
        try:
            if not self._ollama_available:
                raise ConnectionError("Ollama unavailable (short-circuit)")
            # 构建请求参数
            request_params = self.default_params.copy()
            if params:
                request_params.update(params)
            
            # 构建完整的提示词
            full_prompt = prompt
            if context:
                # 将上下文转换为文本格式
                context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
                full_prompt = f"{context_text}\n\nuser: {prompt}"
            
            # 调用OLLAMA生成文本
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options=request_params
            )
            
            # 适配不同版本的OLLAMA API响应格式
            if isinstance(response, dict):
                return response.get("response", "")
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            self._ollama_available = False
            print(f"生成文本失败: {e}")
            return "抱歉，我无法理解你的意思。"
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, 
                                   params: Optional[Dict[str, Any]] = None) -> str:
        """使用系统提示词生成文本
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            params: 生成参数
            
        Returns:
            生成的文本
        """
        try:
            if not self._ollama_available:
                raise ConnectionError("Ollama unavailable (short-circuit)")
            # 构建请求参数
            request_params = self.default_params.copy()
            if params:
                request_params.update(params)
            
            # 构建完整的提示词
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # 调用OLLAMA生成文本
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options=request_params
            )
            
            # 适配不同版本的OLLAMA API响应格式
            if isinstance(response, dict):
                return response.get("response", "")
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            self._ollama_available = False
            print(f"生成文本失败: {e}")
            return "抱歉，我无法理解你的意思。"
    
    def set_model(self, model_name: str) -> bool:
        """切换模型
        
        Args:
            model_name: 新的模型名称
            
        Returns:
            是否切换成功
        """
        if model_name in self.available_models:
            self.model_name = model_name
            return True
        else:
            # 尝试加载模型
            try:
                ollama.pull(model_name)
                self.model_name = model_name
                self.available_models.append(model_name)
                return True
            except Exception as e:
                print(f"切换模型失败: {e}")
                return False
    
    def get_context_manager(self, context_id: str) -> ContextManager:
        """获取上下文管理器
        
        Args:
            context_id: 上下文ID
            
        Returns:
            上下文管理器
        """
        if context_id not in self.context_managers:
            self.context_managers[context_id] = ContextManager()
        return self.context_managers[context_id]
    
    def generate_for_npc(self, npc_id: str, prompt: str, system_prompt: str, 
                        context: Optional[str] = None) -> str:
        """为NPC生成文本
        
        Args:
            npc_id: NPC ID
            prompt: 用户提示词
            system_prompt: 系统提示词
            context: 额外上下文
            
        Returns:
            生成的文本
        """
        # 构建完整的提示词
        full_prompt = f"当前情境：\n{context}\n\n{prompt}"
        
        # 生成文本
        return self.generate_with_system_prompt(system_prompt, full_prompt)
    
    def batch_generate(self, prompts: List[str], system_prompt: str, 
                      params: Optional[Dict[str, Any]] = None) -> List[str]:
        """批量生成文本
        
        Args:
            prompts: 提示词列表
            system_prompt: 系统提示词
            params: 生成参数
            
        Returns:
            生成的文本列表
        """
        results = []
        for prompt in prompts:
            result = self.generate_with_system_prompt(system_prompt, prompt, params)
            results.append(result)
            # 避免请求过快
            time.sleep(0.1)
        return results


# 全局LLM实例
_llm_instance = None


def get_llm_instance(model_name: str = "llama3") -> LLMIntegration:
    """获取LLM实例
    
    Args:
        model_name: 使用的模型名称
        
    Returns:
        LLM集成实例
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMIntegration(model_name)
    elif _llm_instance.model_name != model_name:
        _llm_instance.set_model(model_name)
    return _llm_instance