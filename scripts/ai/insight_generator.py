# -*- coding: utf-8 -*-
"""
AI 洞察生成器 - 调用 Qwen API 生成商业洞察
集成 data-insight Skill 规范
"""
import json
import os
import requests
from typing import Dict, List, Optional
import logging
import configparser

logger = logging.getLogger(__name__)


class InsightGenerator:
    """AI 洞察生成器"""
    
    def __init__(self, base_dir: str = None):
        # 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
        self.base_dir = os.environ.get('EXE_WORK_DIR') or base_dir or os.path.dirname(os.path.dirname(__file__))
        
        # 加载配置
        self.config = self._load_config()
        
        # API 配置
        self.api_key = self.config.get('api_keys', 'qwen_api_key', fallback='')
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-plus"
        
        # 加载 Skill 规范
        self.skill_prompt = self._load_skill_prompt()
    
    def _load_config(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_dir, 'config.ini')
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        return config
    
    def _load_skill_prompt(self) -> Optional[str]:
        """加载 data-insight Skill 规范"""
        skill_path = os.path.join(self.base_dir, 'skills', 'data-insight', 'SKILL.md')
        if os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def generate(self, data_summary: Dict, output_path: str = None) -> List[str]:
        """
        生成 AI 洞察
        
        Args:
            data_summary: 统计数据字典 {sheet_name: DataFrame}
            output_path: 保存洞察 JSON 的路径
        
        Returns:
            List[str]: 10 条洞察
        """
        logger.info("开始生成 AI 洞察...")
        
        # 构建数据上下文
        data_context = self._build_data_context(data_summary)
        
        # 构建 Prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(data_context)
        
        # 调用 API
        response = self._call_api(system_prompt, user_prompt)
        
        if not response:
            raise RuntimeError(
                "AI 洞察生成失败：Qwen API 调用无响应\n"
                "请检查：\n"
                "1. config.ini 中的 qwen_api_key 是否正确\n"
                "2. 网络连接是否正常\n"
                "3. API 额度是否充足"
            )
        
        # 解析响应
        insights = self._parse_response(response)
        
        # 保存洞察
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, ensure_ascii=False, indent=2)
            logger.info(f"洞察已保存：{output_path}")
        
        logger.info(f"生成 {len(insights)} 条洞察")
        return insights
    
    def _build_data_context(self, data_summary: Dict) -> str:
        """构建数据上下文（支持 DataFrame）"""
        import pandas as pd
        context = []
        
        if '核心 KPI' in data_summary:
            kpi = data_summary['核心 KPI']
            context.append("【核心指标】")
            for _, row in kpi.iterrows():
                context.append(f"  - {row['指标']}: {row['数值']}{row['单位']}")
        
        if '销售员业绩' in data_summary:
            context.append("\n【销售员业绩 TOP5】")
            df = data_summary['销售员业绩']
            for _, row in df.head(5).iterrows():
                context.append(f"  - {row['销售员']}: 销售额{row['总销售额']:,.0f}元，客单价{row['客单价']:,.0f}元")
        
        if '产品占比' in data_summary:
            context.append("\n【产品销售占比】")
            df = data_summary['产品占比']
            for _, row in df.iterrows():
                context.append(f"  - {row['产品']}: {row['占比']}%")
        
        if '城市排名' in data_summary:
            context.append("\n【城市业绩 TOP5】")
            df = data_summary['城市排名']
            for _, row in df.head(5).iterrows():
                context.append(f"  - {row['城市']}: 销售额{row['总销售额']:,.0f}元")
        
        if '客户类型' in data_summary:
            context.append("\n【客户类型对比】")
            df = data_summary['客户类型']
            for _, row in df.iterrows():
                context.append(f"  - {row['客户属性']}: 销售额{row['总销售额']:,.0f}元，占比{row['占比']}%")
        
        if '月度趋势' in data_summary:
            context.append("\n【月度销售趋势】")
            df = data_summary['月度趋势']
            for _, row in df.iterrows():
                context.append(f"  - {row['年月']}: 销售额{row['总销售额']:,.0f}元")
        
        if '季度对比' in data_summary:
            context.append("\n【季度对比】")
            df = data_summary['季度对比']
            for _, row in df.iterrows():
                context.append(f"  - {row['季度']}: 销售额{row['总销售额']:,.0f}元，占比{row['占比']}%")
        
        if '异常订单' in data_summary and len(data_summary['异常订单']) > 0:
            context.append("\n【异常订单】")
            df = data_summary['异常订单']
            for _, row in df.head(5).iterrows():
                context.append(f"  - {row['销售员']}: {row['销售额']:,.0f}元")
        
        return '\n'.join(context)
    
    def _build_system_prompt(self) -> str:
        """构建系统 Prompt - 完全依赖 SKILL.md 规范"""
        if not self.skill_prompt:
            raise FileNotFoundError(
                "Skill 规范文件不存在：skills/data-insight/SKILL.md\n"
                "请确保 Skill 文件存在，AI 洞察生成依赖此规范。"
            )
        
        return f"""你是一位专业的商业数据分析师，专门为销售分析报告生成 PPT 洞察文案。

请严格遵循以下 SKILL 规范生成洞察：

{self.skill_prompt[:10000]}

【重要】直接输出 JSON 数组，不要任何其他文字。"""
    
    def _build_user_prompt(self, data_context: str) -> str:
        """构建用户 Prompt"""
        return f"""请根据以下销售数据，生成 10 条符合上述规范的商业洞察。

数据摘要:
{data_context}

记住：JSON 数组中每条只包含纯洞察内容，不要任何前缀！"""
    
    def _call_api(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用 Qwen API"""
        if not self.api_key:
            logger.error("API Key 未配置")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            logger.info("正在调用 Qwen API...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"API 响应：{content[:200]}...")
                return content
            else:
                logger.error(f"API 返回异常：{result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 调用失败：{e}")
            return None
    
    def _parse_response(self, response: str) -> List[str]:
        """解析 API 响应（处理嵌套数组）"""
        import re
        
        try:
            # 提取 JSON 数组
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                insights_raw = json.loads(json_match.group())
            else:
                insights_raw = json.loads(response)
            
            logger.info(f"AI 返回原始数据：{len(insights_raw)} 项")
            
            # 展平嵌套数组 - 确保 10 条洞察
            insights = []
            for i, item in enumerate(insights_raw):
                if isinstance(item, list):
                    # 列表式洞察（第 5-11 页）：用换行符连接 3 条
                    item_text = '\n'.join(item)
                    insights.append(item_text)
                    logger.info(f"第{i+1}条：列表式洞察，{len(item)} 条")
                elif isinstance(item, str):
                    # 字符串洞察
                    insights.append(item)
                    logger.info(f"第{i+1}条：字符串洞察")
                else:
                    logger.warning(f"第{i+1}条：未知类型 {type(item)}")
            
            # 确保返回 10 条
            if len(insights) != 10:
                raise ValueError(
                    f"AI 返回的洞察数量异常：期望 10 条，实际{len(insights)}条\n"
                    f"原始返回：{insights_raw[:2]}...\n"
                    "请检查 API 配置或联系管理员。"
                )
            
            logger.info(f"解析后洞察数量：{len(insights)}")
            return insights
            
        except json.JSONDecodeError as e:
            raise ValueError(
                f"AI 返回的 JSON 格式无效：{e}\n"
                f"原始响应：{response[:200]}...\n"
                "请检查 API 配置或联系管理员。"
            )
    
    # 如果 API 失败，直接抛出异常
