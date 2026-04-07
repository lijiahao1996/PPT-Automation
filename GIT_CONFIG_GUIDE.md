# Git 配置指南

> 📋 如何安全地管理配置文件和敏感信息  
> **最后更新**: 2026-04-07

---

## 🔐 敏感信息保护

### 不提交的文件

以下文件包含敏感信息，**不应提交到 Git**：

| 文件 | 原因 |
|------|------|
| `config.ini` | 包含 API Key、密码 |
| `.env` | 环境变量（可能包含密钥） |
| `*.key`, `*.pem` | 私钥文件 |
| `output/*.pptx` | 生成的报告（可能包含商业数据） |
| `output/*.xlsx` | 导出的数据 |
| `artifacts/*` | 临时文件 |
| `logs/*.log` | 日志文件 |

---

## 📝 配置步骤

### 首次使用（克隆项目后）

**方法 1：自动创建（推荐）**

```bash
# 直接运行，会自动从模板创建
.\启动器.bat
```

如果 `config.ini` 不存在，程序会：
1. ✅ 自动从 `config.ini.example` 复制
2. ✅ 提示你填写必要信息
3. ✅ 等待你填写后再次运行

**方法 2：手动创建**

```bash
# 1. 复制模板
copy config.ini.example config.ini

# 2. 编辑 config.ini，填写：
#    - [fanruan] password
#    - [api_keys] qwen_api_key

# 3. 运行
.\启动器.bat
```

---

## 📦 Git 提交清单

### ✅ 应该提交的文件

```
n8n/
├── .gitignore
├── config.ini.example          ⭐ 配置模板
├── README.md
├── 启动器.bat
├── Run.ps1
├── PPT 生成.exe                 ⭐ 可选（8MB）
│
├── scripts/                     ⭐ 所有脚本
├── templates/                   ⭐ PPT 模板和配置
├── skills/                      ⭐ AI 规范
├── docs/                        ⭐ 文档
│
├── artifacts/.gitkeep           ⭐ 目录占位符
├── logs/.gitkeep                ⭐ 目录占位符
└── output/.gitkeep              ⭐ 目录占位符
```

### ❌ 不应提交的文件

```
n8n/
├── config.ini                   ❌ 包含密码和 API Key
├── output/*.pptx                ❌ 生成的报告
├── output/*.xlsx                ❌ 导出的数据
├── artifacts/*                  ❌ 临时文件（除.gitkeep）
├── logs/*.log                   ❌ 日志文件
├── __pycache__/                 ❌ Python 缓存
└── *.pyc                        ❌ Python 字节码
```

---

## 🚀 快速开始（给新用户）

### 1. 克隆项目

```bash
git clone <repository-url>
cd n8n
```

### 2. 配置

**方式 A：自动（推荐）**
```bash
# 直接运行，会自动提示配置
.\启动器.bat
```

**方式 B：手动**
```bash
# 复制模板
copy config.ini.example config.ini

# 编辑 config.ini，填写：
# 1. 帆软密码
# 2. Qwen API Key
```

### 3. 运行

```bash
# 方式 1：BAT 启动器
.\启动器.bat

# 方式 2：PowerShell
.\Run.ps1

# 方式 3：EXE（如果已打包）
.\PPT 生成.exe
```

---

## 💡 最佳实践

### 1. 使用环境变量（可选）

对于更安全的配置，可以使用环境变量：

```ini
[api_keys]
qwen_api_key = ${QWEN_API_KEY}
```

然后在系统中设置：
```bash
setx QWEN_API_KEY "sk-your-actual-key"
```

### 2. 定期更新模板

当添加新配置项时：
1. ✅ 更新 `config.ini.example`
2. ✅ 在 README 中说明
3. ❌ 不要提交真实的 `config.ini`

### 3. 团队共享

**分享项目时**：
- ✅ 确保 `config.ini.example` 是最新的
- ✅ README 中有清晰的配置说明
- ✅ 运行一次测试，确保模板可用

**接收项目时**：
- ✅ 首先复制 `config.ini.example` → `config.ini`
- ✅ 填写必要的配置
- ✅ 测试运行

---

## 🔍 常见问题

### Q1: 为什么 config.ini 不能提交？

**A**: 包含敏感信息：
- 帆软账号密码
- Qwen API Key（按量计费）

提交会导致：
- ❌ 密码泄露
- ❌ API Key 被盗用
- ❌ 产生额外费用

### Q2: 别人下载项目后怎么配置？

**A**: 按照以下步骤：
1. 复制 `config.ini.example` → `config.ini`
2. 填写帆软密码和 API Key
3. 运行 `.\启动器.bat`

### Q3: 如何确认哪些文件应该提交？

**A**: 使用 `git status` 查看：
```bash
git status
```

绿色 = 已暂定提交  
红色 = 未暂定（需要判断）

不确定的文件，查看 `.gitignore`。

### Q4: config.ini.example 和 config.ini 有什么区别？

| 文件 | 用途 | 是否提交 |
|------|------|---------|
| `config.ini.example` | 模板，示例配置 | ✅ 提交 |
| `config.ini` | 实际配置，包含真实密码 | ❌ 不提交 |

---

## 📚 相关文档

- [README.md](README.md) - 项目说明
- [config.ini.example](config.ini.example) - 配置模板
- [.gitignore](.gitignore) - Git 忽略规则

---

**最后更新**: 2026-04-07  
**版本**: 1.0
