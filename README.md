# PPT 报告生成系统

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 5.0 Web 版  
> **最后更新**: 2026-04-11

---

## 🚀 快速开始

### 方式 1: Web 界面（推荐）

1. **启动服务**
   ```bash
   cd C:\Users\50319\Desktop\n8n
   python -m streamlit run scripts/config_tool/app.py --server.port 8501
   ```

2. **访问界面**
   - 打开浏览器：http://localhost:8501/

3. **使用流程**
   - **Tab 1** 📋 统计规则配置 → 上传 Excel，配置统计规则
   - **Tab 2** 📈 图表配置 → 配置图表
   - **Tab 7** ⚙️ 项目配置 → 配置 API Key 等
   - **Tab 8** 🚀 生成 PPT 报告 → 一键生成

### 方式 2: 命令行

```bash
cd C:\Users\50319\Desktop\n8n
.\Run.bat
```

---

## 📁 目录结构

```
n8n/
├── scripts/                 # 核心脚本
│   ├── config_tool/         # Web 配置工具
│   ├── core/                # 核心引擎
│   ├── ai/                  # AI 模块
│   └── fanruan/             # 帆软模块
├── templates/               # PPT 模板
├── skills/                  # AI Skill
├── docs/                    # 文档
├── resources/               # 资源文件
├── output/                  # 输出目录
├── artifacts/               # 临时文件
├── logs/                    # 日志目录
├── config.ini               # 配置文件
├── Run.bat                  # 一键运行
└── README.md                # 项目文档
```

---

## ⚙️ 配置说明

### 通过 Web 界面配置（推荐）

1. 访问 http://localhost:8501/
2. 进入 **"⚙️ 项目配置"** 页签
3. 配置以下内容：
   - **API Key 配置** - Qwen API Key（用于 AI 洞察）
   - **路径配置** - 一般使用默认值即可
   - **高级配置** - 会话有效期、日志级别

### 配置文件

`config.ini` 已通过 Web 界面管理，无需手动编辑。

**必要配置**:
- `qwen_api_key` - 阿里云百炼 Qwen API Key

**可选配置**:
- `output_dir` - 输出目录（默认：output）
- `logs_dir` - 日志目录（默认：logs）

---

## 📊 使用流程

### 1. 上传数据
进入 **"📋 统计规则配置"** 页签，上传 Excel 数据文件。

### 2. 配置统计规则
添加需要的统计规则（KPI、排名、占比等）。

### 3. 配置图表
进入 **"📈 图表配置"** 页签，为每个统计配置图表。

### 4. 配置 AI 洞察
进入 **"💡 洞察配置"** 页签，配置每个图表的 AI 分析维度。

### 5. 生成 PPT
进入 **"🚀 生成 PPT 报告"** 页签，点击"▶️ 开始生成 PPT 报告"。

---

## 🔑 获取 API Key

1. 访问：https://bailian.console.aliyun.com/
2. 登录阿里云账号
3. 创建 API Key
4. 在 Web 界面的 **"⚙️ 项目配置"** 中填写

---

## 📝 日志查看

日志文件位置：`logs/ppt_YYYYMMDD.log`

例如：`logs/ppt_20260411.log`

---

## ❓ 常见问题

**Q: Web 界面无法启动？**  
A: 确保已安装 Streamlit：`pip install streamlit`

**Q: API Key 在哪里获取？**  
A: 阿里云百炼控制台：https://bailian.console.aliyun.com/

**Q: 日志文件在哪里？**  
A: `logs/` 目录下，按日期命名

**Q: 如何修改配置？**  
A: 通过 Web 界面的 **"⚙️ 项目配置"** 页签

---

**最后更新**: 2026-04-11  
**版本**: 5.0 Web 版  
**状态**: ✅ 生产就绪
