# -*- coding: utf-8 -*-
"""测试保存功能"""
import json
import os

stats_rules_file = r"C:\Users\50319\Desktop\n8n\templates\stats_rules.json"

print(f"Test file: {stats_rules_file}")
print(f"File exists: {os.path.exists(stats_rules_file)}")

# 读取
with open(stats_rules_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

print(f"Current rules: {len(config.get('stats_sheets', {}))}")

# 添加测试规则
test_rule = {
    "description": "Test Rule",
    "type": "kpi",
    "enabled": True,
    "metrics": [
        {"field": "销售额", "agg": "sum", "alias": "总销售额"}
    ]
}

config['stats_sheets']['AI_Test_Rule'] = test_rule
print(f"After add: {len(config.get('stats_sheets', {}))}")

# 保存
with open(stats_rules_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("Save OK!")

# 验证
with open(stats_rules_file, 'r', encoding='utf-8') as f:
    verify = json.load(f)

print(f"Verify: {len(verify.get('stats_sheets', {}))} rules")
print(f"Rules: {list(verify.get('stats_sheets', {}).keys())}")

if 'AI_Test_Rule' in verify.get('stats_sheets', {}):
    print("TEST PASSED!")
else:
    print("TEST FAILED!")
