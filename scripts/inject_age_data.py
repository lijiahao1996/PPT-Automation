# -*- coding: utf-8 -*-
"""
数据注入脚本 - 添加客户年龄段字段
用于测试散点图配置
"""
import pandas as pd
import random
import numpy as np

# 读取现有数据
df = pd.read_excel('output/帆软销售明细.xlsx')

print(f'原始数据：{len(df)} 行')
print(f'原始字段：{df.columns.tolist()}')

# 添加客户年龄段字段
# 根据订单金额和客户类型模拟年龄段
def generate_age_group(row):
    """根据销售额和客户类型生成年龄段"""
    sales = float(str(row['销售额']).replace(',', ''))
    customer_type = row['客户属性']
    
    # 老客更可能是中年客户，新客更可能是年轻客户
    if customer_type == '老客':
        age_groups = ['25-30 岁', '31-35 岁', '36-40 岁', '41-45 岁', '46-50 岁']
        weights = [0.15, 0.25, 0.30, 0.20, 0.10]  # 老客集中在 31-45 岁
    else:  # 新客
        age_groups = ['25-30 岁', '31-35 岁', '36-40 岁', '41-45 岁', '46-50 岁']
        weights = [0.35, 0.30, 0.20, 0.10, 0.05]  # 新客集中在 25-35 岁
    
    # 高金额订单更可能是中年客户
    if sales > 5000:
        weights = [0.10, 0.20, 0.35, 0.25, 0.10]
    elif sales < 1000:
        weights = [0.40, 0.30, 0.15, 0.10, 0.05]
    
    return np.random.choice(age_groups, p=weights)

# 设置随机种子，保证可重复性
np.random.seed(42)

# 添加年龄段字段
df['客户年龄段'] = df.apply(generate_age_group, axis=1)

print(f'\n注入后数据：{len(df)} 行')
print(f'新增字段：客户年龄段')
print(f'\n年龄段分布:')
print(df['客户年龄段'].value_counts().sort_index())

print(f'\n年龄段 x 客户类型 分布:')
print(pd.crosstab(df['客户年龄段'], df['客户属性']))

print(f'\n年龄段 x 销售额 统计:')
# 转换销售额为数字
df['销售额_num'] = df['销售额'].astype(str).str.replace(',', '').astype(float)
age_sales = df.groupby('客户年龄段')['销售额_num'].agg(['sum', 'mean', 'count'])
age_sales.columns = ['总销售额', '平均客单价', '订单数']
print(age_sales)

# 保存回 Excel（移除临时字段）
df_to_save = df.drop(columns=['销售额_num'])
df_to_save.to_excel('output/帆软销售明细.xlsx', index=False)
print('\nOK: Data saved to output/帆软销售明细.xlsx')

# 同时更新统计汇总文件
summary_path = 'output/销售统计汇总.xlsx'
try:
    with pd.ExcelWriter(summary_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # 添加客户年龄分布统计
        age_dist = df.groupby(['客户年龄段', '客户类型']).agg({
            '销售额_num': ['sum', 'count', 'mean']
        }).reset_index()
        age_dist.columns = ['年龄段', '客户类型', '总销售额', '订单数', '客单价']
        age_dist.to_excel(writer, sheet_name='客户年龄分布', index=False)
        print('OK: Added sheet: 客户年龄分布')
except Exception as e:
    print(f'Warning: Update summary failed: {e}')
    print('   Re-run Run.bat to regenerate summary')
