"""
帆软数据分析脚本（企业版）
- 读取原始数据
- 数据质量校验
- 数据清洗 -> 销售分析数据.xlsx
- 二次统计 -> 销售统计汇总.xlsx
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging
import configparser

# 导入核心模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
from data_loader import DataLoader
from validator import DataValidator, PresetValidators, DataQualityError
from stats_engine import StatsEngine

# ========== 加载配置 ==========
# 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
WORK_DIR = os.environ.get('EXE_WORK_DIR') or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config_path = os.path.join(WORK_DIR, "config.ini")
config.read(config_path, encoding='utf-8')

# 从 config.ini 读取路径（如果配置了），否则使用相对路径
OUTPUT_DIR = config.get('paths', 'output_dir', fallback=os.path.join(WORK_DIR, "output"))
ARTIFACTS_DIR = config.get('paths', 'artifacts_dir', fallback=os.path.join(WORK_DIR, "artifacts"))
LOGS_DIR = config.get('paths', 'logs_dir', fallback=os.path.join(WORK_DIR, "logs"))

# 自动检测 output 目录中的原始数据文件
# 优先使用 config.ini 配置，如果没有则查找第一个 xlsx 文件
RAW_DATA_FILE_NAME = config.get('paths', 'raw_data_file', fallback='')

if not RAW_DATA_FILE_NAME or not os.path.exists(os.path.join(OUTPUT_DIR, RAW_DATA_FILE_NAME)):
    # 自动查找 output 目录中的第一个 xlsx 文件（排除统计汇总文件）
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
            RAW_DATA_FILE_NAME = f
            break

if not RAW_DATA_FILE_NAME:
    RAW_DATA_FILE_NAME = '帆软销售明细.xlsx'

# 统计汇总文件名：基于原始数据文件名 + _统计汇总
if RAW_DATA_FILE_NAME.endswith('.xlsx'):
    SUMMARY_FILE_NAME = RAW_DATA_FILE_NAME.replace('.xlsx', '_统计汇总.xlsx')
else:
    SUMMARY_FILE_NAME = RAW_DATA_FILE_NAME + '_统计汇总.xlsx'

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ========== 统一日志配置 ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOGS_DIR, f'analyze_{datetime.now().strftime("%Y%m%d")}.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

RAW_FILE = os.path.join(OUTPUT_DIR, RAW_DATA_FILE_NAME)
ANALYSIS_FILE = os.path.join(ARTIFACTS_DIR, "销售分析数据.xlsx")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, SUMMARY_FILE_NAME)
# ============================


def clean_and_analyze():
    print("=" * 60)
    print("帆软数据分析 - 清洗 + 统计")
    print("=" * 60)
    
    # 1. 读取原始数据
    if not os.path.exists(RAW_FILE):
        logger.error(f"未找到原始数据文件：{RAW_FILE}")
        return False
    
    logger.info("\n[1/6] 读取原始数据...")
    df = pd.read_excel(RAW_FILE, header=0)
    logger.info(f"      原始数据：{len(df)} 行")
    logger.info(f"      列名：{list(df.columns)}")
    
    # 2. 数据质量校验
    logger.info("\n[2/6] 数据质量校验...")
    validator = PresetValidators.sales_data_validator(df)
    try:
        validator.validate(df)
        logger.info("      [OK] 数据校验通过")
        if validator.warnings:
            for warn in validator.warnings:
                logger.warning(f"      [WARN] {warn}")
    except DataQualityError as e:
        logger.error(f"      [ERROR] 数据校验失败：{e}")
        return False
    
    # 3. 基础清洗
    logger.info("\n[3/6] 基础数据清洗...")
    logger.info(f"      销售额列原始类型：{df['销售额'].dtype}")
    df['销售额'] = df['销售额'].apply(lambda x: float(str(x).replace(',', '').strip()) if pd.notna(x) else 0.0)
    logger.info(f"      [OK] 销售额列已转换为数字 (移除千位分隔符)")
    
    df['年月'] = pd.to_datetime(df['订单时间']).dt.to_period('M').astype(str)
    df['月份'] = pd.to_datetime(df['订单时间']).dt.month
    df['季度'] = pd.to_datetime(df['订单时间']).dt.quarter
    df['星期'] = pd.to_datetime(df['订单时间']).dt.dayofweek
    
    weekday_map = {0:'周一', 1:'周二', 2:'周三', 3:'周四', 4:'周五', 5:'周六', 6:'周日'}
    df['星期'] = df['星期'].map(weekday_map)
    
    logger.info(f"      [OK] 时间维度提取完成")
    
    # 4. 保存清洗数据
    logger.info("\n[4/6] 保存清洗数据...")
    clean_df = df[['订单时间', '销售员', '产品', '城市', '客户属性', '销售员工号', '销售额', '年月', '季度', '星期']].copy()
    clean_df.to_excel(ANALYSIS_FILE, index=False)
    logger.info(f"      [OK] 清洗数据：{ANALYSIS_FILE}")
    
    # 5. 二次统计计算（使用配置化统计引擎）
    logger.info("\n[5/6] 二次统计计算（配置化）...")
    
    # 执行统计引擎
    results = {}
    try:
        engine = StatsEngine(base_dir=WORK_DIR)
        results = engine.run_all(df, output_path=None)  # 先不保存，手动保存
        logger.info(f"      [OK] 统计引擎执行完成，生成 {len(results)} 个统计表")
    except Exception as e:
        logger.error(f"      [ERROR] 统计引擎执行失败：{e}")
        logger.info(f"      [INFO] 回退到硬编码统计模式...")
        results = None  # 标记需要使用硬编码后备
    
    # 6. 保存统计汇总
    logger.info("\n[6/6] 保存统计汇总...")
    
    # 使用统计引擎的结果保存
    if results is not None and len(results) > 0:
        with pd.ExcelWriter(SUMMARY_FILE) as writer:
            for sheet_name, df_result in results.items():
                # Excel Sheet 名称长度限制 31 字符
                safe_name = sheet_name[:31]
                df_result.to_excel(writer, sheet_name=safe_name, index=False)
        logger.info(f"      [OK] 统计汇总：{SUMMARY_FILE}")
        logger.info(f"      [OK] 共 {len(results)} 个 Sheet")
    else:
        # 后备方案：硬编码统计逻辑
        logger.info(f"      [INFO] 使用硬编码统计模式...")
        
        # 核心 KPI
        kpi_data = {
            '指标': ['总销售额', '总订单数', '平均客单价', '最高单额', '最低单额'],
            '数值': [
                df['销售额'].sum(),
                len(df),
                df['销售额'].mean(),
                df['销售额'].max(),
                df['销售额'].min()
            ],
            '单位': ['元', '单', '元', '元', '元']
        }
        kpi_df = pd.DataFrame(kpi_data)
        
        # 销售员业绩
        sales_by_person = df.groupby('销售员').agg({
            '销售额': ['sum', 'count', 'mean']
        }).reset_index()
        sales_by_person.columns = ['销售员', '总销售额', '订单数', '客单价']
        sales_by_person = sales_by_person.sort_values('总销售额', ascending=False)
        
        # 产品占比
        product_stats = df.groupby('产品')['销售额'].sum().reset_index()
        product_stats['占比'] = (product_stats['销售额'] / product_stats['销售额'].sum() * 100).round(1)
        product_stats = product_stats.sort_values('销售额', ascending=False)
        
        # 城市排名
        city_stats = df.groupby('城市').agg({
            '销售额': 'sum',
            '销售员': 'count'
        }).reset_index()
        city_stats.columns = ['城市', '总销售额', '订单数']
        city_stats = city_stats.sort_values('总销售额', ascending=False)
        
        # 客户类型
        customer_stats = df.groupby('客户属性').agg({
            '销售额': 'sum',
            '销售员': 'count'
        }).reset_index()
        customer_stats.columns = ['客户属性', '总销售额', '订单数']
        customer_stats['客单价'] = (customer_stats['总销售额'] / customer_stats['订单数']).round(0)
        
        # 月度趋势
        monthly_stats = df.groupby('年月').agg({
            '销售额': 'sum',
            '销售员': 'count'
        }).reset_index()
        monthly_stats.columns = ['年月', '总销售额', '订单数']
        monthly_stats = monthly_stats.sort_values('年月')
        
        # 保存
        with pd.ExcelWriter(SUMMARY_FILE) as writer:
            kpi_df.to_excel(writer, sheet_name='核心 KPI', index=False)
            sales_by_person.to_excel(writer, sheet_name='销售员业绩', index=False)
            product_stats.to_excel(writer, sheet_name='产品占比', index=False)
            city_stats.to_excel(writer, sheet_name='城市排名', index=False)
            customer_stats.to_excel(writer, sheet_name='客户类型', index=False)
            monthly_stats.to_excel(writer, sheet_name='月度趋势', index=False)
        
        logger.info(f"      [OK] 统计汇总：{SUMMARY_FILE} (硬编码模式)")
        logger.info(f"      [OK] 共 6 个 Sheet")
        
        # 更新 results 用于后续打印
        results = {
            '核心 KPI': kpi_df,
            '销售员业绩': sales_by_person,
            '产品占比': product_stats,
            '城市排名': city_stats,
            '客户类型': customer_stats,
            '月度趋势': monthly_stats
        }
    
    # 打印关键指标
    logger.info(f"\n{'='*60}")
    logger.info("核心 KPI:")
    if results and '核心 KPI' in results:
        kpi_df = results['核心 KPI']
        for _, row in kpi_df.iterrows():
            logger.info(f"  {row['指标']}: {row['数值']:,.2f}{row.get('单位', '')}")
    logger.info(f"{'='*60}")
    
    return True


if __name__ == "__main__":
    success = clean_and_analyze()
    exit(0 if success else 1)



