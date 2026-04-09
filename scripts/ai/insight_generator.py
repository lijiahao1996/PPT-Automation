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
    
    def _load_charts_config(self) -> Optional[Dict]:
        """动态加载图表配置"""
        placeholders_path = os.path.join(self.base_dir, 'templates', 'placeholders.json')
        if os.path.exists(placeholders_path):
            with open(placeholders_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('placeholders', {}).get('charts', {})
        return None
    
    def _load_insights_config(self) -> Optional[Dict]:
        """动态加载洞察配置"""
        placeholders_path = os.path.join(self.base_dir, 'templates', 'placeholders.json')
        if os.path.exists(placeholders_path):
            with open(placeholders_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('placeholders', {}).get('insights', {})
        return None
    
    def _load_special_insights_config(self) -> Optional[Dict]:
        """加载特殊洞察配置（结论 & 策略）"""
        placeholders_path = os.path.join(self.base_dir, 'templates', 'placeholders.json')
        if os.path.exists(placeholders_path):
            with open(placeholders_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('special_insights', {})
        return None
    
    def generate(self, data_summary: Dict, output_path: str = None) -> List[str]:
        """
        生成 AI 洞察
        
        Args:
            data_summary: 统计数据字典 {sheet_name: DataFrame}
            output_path: 保存洞察 JSON 的路径
        
        Returns:
            List[str]: 洞察列表
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
        """构建数据上下文（动态支持所有统计表）"""
        import pandas as pd
        context = []
        
        # 动态遍历所有可用的统计表
        for sheet_name, df in data_summary.items():
            if df is None or len(df) == 0:
                continue
            
            context.append(f"\n【{sheet_name}】")
            
            # 显示前 5 行数据
            for idx, row in df.head(5).iterrows():
                row_data = []
                for col in df.columns:
                    val = row[col]
                    if isinstance(val, (int, float)):
                        row_data.append(f"{col}: {val:,.0f}")
                    else:
                        row_data.append(f"{col}: {val}")
                context.append("  - " + "，".join(row_data))
            
            if len(df) > 5:
                context.append(f"  ... 共{len(df)}行数据")
        
        return '\n'.join(context)
    
    def _build_system_prompt(self) -> str:
        """构建系统 Prompt - 完全依赖 SKILL.md 规范"""
        if not self.skill_prompt:
            raise FileNotFoundError(
                "Skill 规范文件不存在：skills/data-insight/SKILL.md\n"
                "请确保 Skill 文件存在，AI 洞察生成依赖此规范。"
            )
        
        # 动态加载图表和洞察配置
        charts_config = self._load_charts_config()
        insights_config = self._load_insights_config()
        chart_count = len(charts_config) if charts_config else 0
        insight_count = len(insights_config) if insights_config else chart_count
        
        return f"""你是一位专业的商业数据分析师，专门为销售分析报告生成 PPT 洞察文案。

请严格遵循以下 SKILL 规范生成洞察：

{self.skill_prompt[:10000]}

【重要】
1. 直接输出 JSON 数组，不要任何其他文字
2. JSON 数组的元素数量 = 洞察配置数量 +2（当前{insight_count}个洞察 + 结论 + 策略 = 共{insight_count+2}条）
3. 每条洞察对应一个图表/数据表，按配置顺序输出
4. 洞察内容必须基于提供的数据，不能虚构"""
    
    def _build_user_prompt(self, data_context: str) -> str:
        """构建用户 Prompt（支持洞察配置 + 结论策略）"""
        # 动态加载图表配置
        charts_config = self._load_charts_config()
        insights_config = self._load_insights_config()
        special_insights_config = self._load_special_insights_config()
        
        chart_info = "\n\n【图表配置】\n"
        if charts_config:
            for i, (chart_key, chart_cfg) in enumerate(charts_config.items(), 1):
                chart_info += f"{i}. {chart_key}: {chart_cfg.get('title', '')} (数据源：{chart_cfg.get('data_source', '')})\n"
        
        # 添加洞察配置
        insight_config_info = ""
        if insights_config:
            insight_config_info = "\n\n【洞察配置】\n"
            for chart_key, insight_cfg in insights_config.items():
                insight_config_info += f"\n### {chart_key}\n"
                insight_config_info += f"- 分析维度：{', '.join(insight_cfg.get('dimensions', []))}\n"
                insight_config_info += f"- 关键指标：{', '.join(insight_cfg.get('metrics', []))}\n"
                insight_config_info += f"- 对比基准：{insight_cfg.get('baseline', '无')}\n"
                insight_config_info += f"- 洞察风格：{insight_cfg.get('style', '平衡型')}\n"
                insight_config_info += f"- 字数要求：{insight_cfg.get('word_count', 150)}字\n"
                if insight_cfg.get('custom_prompt'):
                    insight_config_info += f"- 自定义提示：{insight_cfg.get('custom_prompt')}\n"
        
        # 添加特殊洞察配置（结论 & 策略）
        special_config_info = ""
        if special_insights_config:
            special_config_info = "\n\n【特殊洞察配置】\n"
            
            conclusion_cfg = special_insights_config.get('conclusion', {})
            if conclusion_cfg:
                special_config_info += f"\n### 核心结论\n"
                special_config_info += f"- 分析维度：{', '.join(conclusion_cfg.get('dimensions', []))}\n"
                special_config_info += f"- 洞察风格：{conclusion_cfg.get('style', '数据驱动')}\n"
                special_config_info += f"- 字数要求：{conclusion_cfg.get('word_count', 300)}字\n"
                if conclusion_cfg.get('custom_prompt'):
                    special_config_info += f"- 自定义提示：{conclusion_cfg.get('custom_prompt')}\n"
            
            strategy_cfg = special_insights_config.get('strategy', {})
            if strategy_cfg:
                special_config_info += f"\n### 落地策略\n"
                special_config_info += f"- 策略维度：{', '.join(strategy_cfg.get('dimensions', []))}\n"
                special_config_info += f"- 洞察风格：{strategy_cfg.get('style', '建议导向')}\n"
                special_config_info += f"- 字数要求：{strategy_cfg.get('word_count', 400)}字\n"
                if strategy_cfg.get('custom_prompt'):
                    special_config_info += f"- 自定义提示：{strategy_cfg.get('custom_prompt')}\n"
        
        # 使用 insights 配置数量（包括 kpi_summary, abnormal 等额外洞察）
        insight_count = len(insights_config) if insights_config else len(charts_config)
        total_count = insight_count + 2  # +2 为结论和策略
        
        return f"""请根据以下销售数据，生成符合上述规范的商业洞察。

数据摘要:
{data_context}
{chart_info}
{insight_config_info}
{special_config_info}
记住：
1. JSON 数组中每条只包含纯洞察内容，不要任何前缀
2. 洞察数量 = 洞察配置数量 +2（当前{insight_count}个洞察 + 结论 + 策略 = 共{total_count}条）
3. 前{insight_count}条：每条洞察对应一个图表/数据表，按配置顺序分析
4. 第{insight_count + 1}条：核心结论（4 条结构化洞察，用\\n\\n 分隔）
5. 第{insight_count + 2}条：落地策略（4 条结构化策略，用\\n\\n 分隔）
6. 根据配置的洞察配置生成对应内容"""
    
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
            
            # 动态加载洞察配置，确定期望的洞察数量
            insights_config = self._load_insights_config()
            insight_count = len(insights_config) if insights_config else 0
            expected_count = insight_count + 2  # 洞察 + 结论 + 策略
            
            # 展平嵌套数组
            insights = []
            for i, item in enumerate(insights_raw):
                if isinstance(item, list):
                    # 列表式洞察：用换行符连接
                    item_text = '\n'.join(item)
                    insights.append(item_text)
                    logger.info(f"第{i+1}条：列表式洞察，{len(item)} 条")
                elif isinstance(item, str):
                    # 字符串洞察
                    insights.append(item)
                    logger.info(f"第{i+1}条：字符串洞察")
                else:
                    logger.warning(f"第{i+1}条：未知类型 {type(item)}")
            
            # 动态检查洞察数量
            if len(insights) < insight_count:
                raise ValueError(
                    f"AI 返回的洞察数量异常：期望至少{insight_count}条，实际{len(insights)}条\n"
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
