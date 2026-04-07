"""
帆软社区登录脚本
- 登录成功后将会话状态（cookies 等）保存到 fanruan_session.json
- 之后运行 fanruan_scrape.py 即可免登录抓数据
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import sys
import configparser

# ========== 加载配置 ==========
# 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
WORK_DIR = os.environ.get('EXE_WORK_DIR') or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config_path = os.path.join(WORK_DIR, "config.ini")
config.read(config_path, encoding='utf-8')

# 从配置文件读取
YOUR_PHONE = config.get('fanruan', 'username', fallback='13021020077')
YOUR_PASSWORD = config.get('fanruan', 'password', fallback='')

OUTPUT_DIR = config.get('paths', 'output_dir', fallback=os.path.join(WORK_DIR, "output"))
ARTIFACTS_DIR = config.get('paths', 'artifacts_dir', fallback=os.path.join(WORK_DIR, "artifacts"))

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

SESSION_FILE = os.path.join(ARTIFACTS_DIR, "fanruan_session.json")  # 保存到 artifacts
# ============================


def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. 打开登录页
            print("正在打开登录页...")
            page.goto("https://fanruanclub.com/login/signin", wait_until="networkidle")
            page.wait_for_timeout(2000)

            # 2. 切换到「密码登录」
            try:
                tab = page.locator("text=密码登录").first
                if tab.is_visible():
                    tab.click()
                    print("已切换到密码登录")
                    page.wait_for_timeout(1000)
            except Exception:
                print("默认已是密码登录")

            # 3. 输入手机号
            print("正在输入手机号...")
            all_inputs = page.locator("input.bi-input:visible").all()
            print(f"  找到 {len(all_inputs)} 个可见输入框")
            if len(all_inputs) < 2:
                raise Exception("输入框数量不足，请检查截图 error_general.png")

            all_inputs[0].click()
            all_inputs[0].fill(YOUR_PHONE)
            print(f"已输入手机号：{YOUR_PHONE[:3]}****{YOUR_PHONE[-4:]}")
            
            # 等待 1 秒，让页面反应一下（防止输入太快被限制）
            page.wait_for_timeout(1000)

            # 4. 输入密码
            print("正在输入密码...")
            
            # 尝试多种方式找到密码输入框
            pw_input = None
            try:
                # 方式 1: 使用 placeholder 定位
                pw_input = page.locator("input[placeholder*='密码']:visible").first
                if not pw_input.is_visible():
                    pw_input = None
            except Exception:
                pass
            
            if not pw_input:
                try:
                    # 方式 2: 使用 type='password' 定位
                    pw_input = page.locator("input[type='password']:visible").first
                    if not pw_input.is_visible():
                        pw_input = None
                except Exception:
                    pass
            
            if not pw_input:
                try:
                    # 方式 3: 使用第二个输入框定位
                    pw_input = all_inputs[1]
                except Exception as e:
                    print(f"无法找到密码输入框：{e}")
                    page.screenshot(path=os.path.join(WORK_DIR, "error_password.png"))
                    raise Exception("无法找到密码输入框，请检查截图 error_password.png")
            
            # 点击密码框
            pw_input.click()
            page.wait_for_timeout(500)
            
            # 使用 JavaScript 直接设置值（绕过反自动化检测）
            print(f"正在输入密码（{len(YOUR_PASSWORD)} 位）...")
            
            # 方式 A: 尝试使用 type 逐个字符输入（模拟真实打字）
            try:
                for char in YOUR_PASSWORD:
                    pw_input.type(char, delay=50)  # 每个字符间隔 50ms
                print("已输入密码（type 逐字输入）")
            except Exception as e1:
                # 方式 B: 使用 JavaScript 直接设置值
                try:
                    pw_input.evaluate(f"(el) => {{ el.value = '{YOUR_PASSWORD}'; el.dispatchEvent(new Event('input', {{ bubbles: true }})); el.dispatchEvent(new Event('change', {{ bubbles: true }})); }}")
                    print("已输入密码（JavaScript 注入）")
                except Exception as e2:
                    # 方式 C: 使用 fill
                    try:
                        pw_input.fill(YOUR_PASSWORD)
                        print("已输入密码（fill）")
                    except Exception as e3:
                        print(f"所有密码输入方式都失败：{e1}, {e2}, {e3}")
                        page.screenshot(path=os.path.join(WORK_DIR, "error_password.png"))
                        raise Exception("密码输入失败，请检查截图 error_password.png")

            # 5. 处理验证码
            print("检查是否有验证码...")
            try:
                captcha = page.locator("#aliyunCaptcha-captcha-body, .nc_wrapper, [id*='captcha']").first
                if captcha.is_visible(timeout=3000):
                    print("=" * 50)
                    print("检测到验证码！请在浏览器中手动完成滑块验证")
                    print("你有 15 秒时间...")
                    print("=" * 50)
                    page.wait_for_timeout(15000)
            except Exception:
                print("没有检测到验证码")

            # 6. 点击登录按钮
            print("正在点击登录按钮...")
            btn_info = page.evaluate("""() => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent.trim();
                    const rect = el.getBoundingClientRect();
                    if (text === '登录' && rect.width > 80 && rect.height > 20 && rect.height < 60) {
                        const childText = Array.from(el.children).map(c => c.textContent.trim()).join('');
                        if (childText === '登录' || childText === '' || el.children.length <= 2) {
                            return { tag: el.tagName, className: el.className,
                                     width: rect.width, height: rect.height };
                        }
                    }
                }
                return null;
            }""")

            if btn_info:
                print(f"  找到登录按钮：{btn_info['tag']}, 尺寸={btn_info['width']:.0f}x{btn_info['height']:.0f}")
                page.evaluate("""() => {
                    const all = document.querySelectorAll('*');
                    for (const el of all) {
                        const text = el.textContent.trim();
                        const rect = el.getBoundingClientRect();
                        if (text === '登录' && rect.width > 80 && rect.height > 20 && rect.height < 60) {
                            const childText = Array.from(el.children).map(c => c.textContent.trim()).join('');
                            if (childText === '登录' || childText === '' || el.children.length <= 2) {
                                el.click(); return;
                            }
                        }
                    }
                }""")
                print("已点击登录按钮")
            else:
                raise Exception("未找到登录按钮")

            # 7. 等待登录成功
            print("等待登录成功...")
            login_ok = False
            try:
                page.wait_for_url(lambda url: "login" not in url, timeout=20000)
                login_ok = True
                print(f"登录成功！已跳转到：{page.url}")
            except Exception:
                pass

            if not login_ok:
                try:
                    page.locator(".user-info, .avatar, [class*='user-name']").first.wait_for(timeout=10000)
                    login_ok = True
                    print("登录成功！（检测到用户信息）")
                except Exception:
                    pass

            if not login_ok:
                page.screenshot(path=os.path.join(WORK_DIR, "login_failed.png"))
                print("登录可能失败，已截图到 login_failed.png")
                return

            # 8. 保存会话状态
            context.storage_state(path=SESSION_FILE)
            print("=" * 50)
            print(f"登录成功！会话已保存到：{SESSION_FILE}")
            print("现在可以运行 fanruan_scrape.py 抓取数据了")
            print("=" * 50)

        except PlaywrightTimeoutError as e:
            print(f"\n超时错误：{e}")
            page.screenshot(path=os.path.join(WORK_DIR, "error_timeout.png"))
        except Exception as e:
            print(f"\n发生错误：{e}")
            page.screenshot(path=os.path.join(WORK_DIR, "error_general.png"))
        finally:
            browser.close()


if __name__ == "__main__":
    login()
    # 根据会话文件是否存在判断成功失败
    if os.path.exists(SESSION_FILE):
        sys.exit(0)
    else:
        sys.exit(1)
