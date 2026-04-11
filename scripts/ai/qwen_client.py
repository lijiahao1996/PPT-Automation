# -*- coding: utf-8 -*-
"""
千问 API 客户端
提供统一的 AI 调用接口
"""
import os
import json
import requests
import configparser
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class QwenClient:
    """千问 API 客户端"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(__file__))
        self.api_key = self._load_api_key()
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-plus"
    
    def _load_api_key(self) -> str:
        """从 config.ini 加载 API Key"""
        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_dir, 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
            return config.get('api_keys', 'qwen_api_key', fallback='')
        return ''
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str, 
             temperature: float = 0.3,
             max_tokens: int = 2000,
             json_mode: bool = False) -> Optional[str]:
        """
        调用千问 API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度（0-1，越低越稳定）
            max_tokens: 最大 token 数
            json_mode: 是否要求 JSON 输出
        
        Returns:
            AI 响应内容，失败返回 None
        """
        if not self.api_key:
            logger.warning("Qwen API Key 未配置")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if json_mode:
            messages[0]["content"] += "\n\n请严格输出 JSON 格式，不要任何其他文字。"
        
        messages.append({"role": "user", "content": user_prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                logger.error(f"API 返回异常：{result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 调用失败：{e}")
            return None
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析 JSON 格式的响应"""
        import re
        
        if not response:
            return None
        
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return None
    
    def is_available(self) -> bool:
        """检查 AI 是否可用"""
        return bool(self.api_key)
