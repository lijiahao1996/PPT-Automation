FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    N8N_SCRIPTS_BASE_DIR=/app

# 使用清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖（中文字体、Playwright 依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install --with-deps chromium 2>/dev/null || true

# 复制应用代码
COPY scripts/ ./scripts/
COPY templates/ ./templates/
COPY skills/ ./skills/
COPY artifacts/stats_rules.json ./artifacts/stats_rules.json
COPY artifacts/placeholders.json ./artifacts/placeholders.json
COPY config.ini.example ./config.ini

# 创建必要目录
RUN mkdir -p output/report output/summary output/uploaded artifacts/temp logs resources

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["python", "-m", "streamlit", "run", "scripts/config_tool/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
