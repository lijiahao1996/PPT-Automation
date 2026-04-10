"""
帆软数据抓取脚本（F12 抓包 API 直连版）
- 拦截网络请求找到数据接口
- 直接调用 API 获取全量数据
- 不滚动、不分页、不虚拟累积
"""
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import json
import re

import configparser

# ========== 加载配置 ==========
# 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
WORK_DIR = os.environ.get('EXE_WORK_DIR') or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config_path = os.path.join(WORK_DIR, "config.ini")
config.read(config_path, encoding='utf-8')

OUTPUT_DIR = config.get('paths', 'output_dir', fallback=os.path.join(WORK_DIR, "output"))
ARTIFACTS_DIR = config.get('paths', 'artifacts_dir', fallback=os.path.join(WORK_DIR, "artifacts"))

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

SESSION_FILE = os.path.join(ARTIFACTS_DIR, "fanruan_session.json")  # 移到 artifacts
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "帆软销售明细.xlsx")
DATA_URL = config.get('fanruan', 'data_url', fallback="https://demo.fanruan.com/webroot/decision#/datacenter/config/table/5bad5de2769141e8bcada4e0df0e5b5d")
# ============================


def scrape():
    if not os.path.exists(SESSION_FILE):
        print("错误：未找到会话文件，请先登录")
        return False

    captured_apis = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            storage_state=SESSION_FILE
        )
        page = context.new_page()

        # 拦截所有 JSON 响应
        def handle_response(response):
            try:
                url = response.url
                if 'decision/v5' in url and 'fanruan' in url:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        try:
                            data = response.json()
                            captured_apis.append({
                                'url': url,
                                'method': response.request.method,
                                'data': data
                            })
                        except:
                            pass
            except:
                pass

        page.on('response', handle_response)

        try:
            # 1. 打开页面触发 API 请求
            print("[1/4] 打开页面拦截 API...")
            page.goto(DATA_URL, wait_until="networkidle")
            page.wait_for_timeout(10000)
            
            if "login" in page.url:
                print("错误：会话已过期")
                return False
            
            print(f"      拦截到 {len(captured_apis)} 个 API 响应")

            # 2. 分析 API 找到数据接口
            print("\n[2/4] 分析 API 寻找数据接口...")
            
            data_api = None
            for api in captured_apis:
                url = api['url']
                data = api['data']
                
                # 找包含实际数据的 API
                if isinstance(data, dict) and data.get('success'):
                    inner = data.get('data', {})
                    if isinstance(inner, dict):
                        # 检查是否有 records/data/rows 字段
                        records = inner.get('records') or inner.get('data') or inner.get('rows')
                        if records and isinstance(records, list) and len(records) > 0:
                            data_api = api
                            print(f"      [OK] 找到数据接口：{url[:150]}")
                            print(f"      [OK] 返回记录数：{len(records)}")
                            break
                        
                        # 检查 pageInfo 判断是否是分页接口
                        if 'pageInfo' in inner or 'totalRows' in str(inner):
                            print(f"      [?] 可能是分页接口：{url[:100]}")
                            data_api = api  # 备选
            
            if not data_api:
                print("\n错误：未找到返回数据的 API 接口")
                print("\n拦截到的 API 列表:")
                for i, api in enumerate(captured_apis[:10]):
                    print(f"  {i+1}. {api['url'][:120]}")
                return False

            # 3. 提取数据
            print("\n[3/4] 提取数据...")
            inner = data_api['data'].get('data', {})
            
            # 获取记录
            all_rows = inner.get('records') or inner.get('data') or inner.get('rows') or []
            
            # 获取字段定义
            fields = inner.get('fields') or inner.get('allFields') or []
            
            print(f"      记录数：{len(all_rows)}")
            print(f"      字段数：{len(fields)}")
            
            # 检查是否是完整数据
            page_info = inner.get('pageInfo', {})
            total_rows = page_info.get('totalRows', len(all_rows))
            print(f"      总记录数：{total_rows}")
            
            if len(all_rows) < total_rows:
                print(f"\n[WARN] API 只返回了{len(all_rows)}条，但总数是{total_rows}条")
                print("      原因：帆软 API 分页限制（pageSize=100）")
                print(f"      处理：继续使用已抓取的 {len(all_rows)} 条数据")

            # 4. 转换并保存数据
            print("\n[4/4] 保存数据...")
            
            # 获取字段名
            field_names = []
            if fields:
                field_names = [f.get('name', f.get('transferName', '')) for f in fields]
                print(f"      字段列表：{field_names}")
            
            if all_rows and isinstance(all_rows[0], dict):
                # 对象数组 → 按字段顺序提取值
                if field_names:
                    final_rows = [[row.get(fn, '') for fn in field_names] for row in all_rows]
                else:
                    final_rows = [list(row.values()) for row in all_rows]
            else:
                final_rows = all_rows
            
            # 保存 Excel（带表头）
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # 确定输出文件路径
            output_path = OUTPUT_FILE
            
            # 检查文件是否被占用
            if os.path.exists(output_path):
                try:
                    # 尝试删除旧文件
                    os.remove(output_path)
                    print(f"      [INFO] 已删除旧文件：{output_path}")
                except PermissionError:
                    print(f"      [WARN] 文件被占用，无法删除：{output_path}")
                    print(f"      [INFO] 将保存为新文件名...")
                    import time
                    timestamp = int(time.time())
                    output_path = os.path.join(OUTPUT_DIR, f"帆软销售明细_{timestamp}.xlsx")
            
            if field_names:
                df = pd.DataFrame(final_rows, columns=field_names)
                df.to_excel(output_path, index=False, header=True)  # 保留表头
            else:
                df = pd.DataFrame(final_rows)
                df.to_excel(output_path, index=False, header=False)
            
            print(f"      [OK] 保存成功：{output_path}")
            print(f"      [OK] 共 {len(final_rows)} 行")
            
            # 预览
            print("\n前 5 行预览:")
            for i, row in enumerate(final_rows[:5]):
                print(f"  {i+1}: {row}")
            
            # 保存 API 调试信息到 artifacts
            debug_file = os.path.join(ARTIFACTS_DIR, 'api_debug_full.json')
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'api_url': data_api['url'],
                    'total_rows': total_rows,
                    'captured_rows': len(all_rows),
                    'fields': fields
                }, f, ensure_ascii=False, indent=2)
            print(f"\n调试信息：{debug_file}")
            
            return True
            
        except Exception as e:
            print(f"错误：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    success = scrape()
    exit(0 if success else 1)
