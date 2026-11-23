# pp-app-store 📱
> Apple App Store 数据挖掘与竞品情报 Agent 技能库

[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)](#系统兼容与安装)
[![Architecture](https://img.shields.io/badge/Arch-x86__64%20%7C%20arm64%20%7C%20Apple%20Silicon-green.svg)](#系统兼容与安装)
[![Agent](https://img.shields.io/badge/Agent-Gemini%20%7C%20Codex%20%7C%20WorkBuddy%20%7C%20ZCode%20%7C%20Claude-purple.svg)](#多-agent-生态无缝集成)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

专为 **AI Coding Agent**（Google Gemini / Antigravity、OpenAI Codex CLI、WorkBuddy、ZCode、Claude Code）与自动化终端工作流封装的 Apple App Store 公开数据挖掘套件。

底层基于由 Go 语言编写的高性能独立单文件二进制 `app-store-pp-cli`（出自开源项目 [mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)），**无需 Apple 开发者账号、免 API Key 鉴权**，且自带本地 SQLite 历史时序库，支持随时比对两次抓取之间的排名波动、热度牵引与差评沉淀。

---

## ✨ 核心优势

* 🚀 **零依赖与极速冷启动**：单文件 Go 编译产物，无需 Node.js / Python 运行时或沉重的无头浏览器。
* 🔑 **免认证即开即用**：直接调用 Apple 官方公开接口，无账户封禁或密钥过期困扰。
* 📊 **内置 SQLite 本地时序库**：所有查询自动缓存到本地数据库（`~/.local/share/app-store-pp-cli/data.db`），支持时序排名异动（`movers`）、拉力评估（`traction`）与重大更新影响分析（`impact`）。
* 🤖 **原生 Agent 友好**：所有命令原生支持 `--agent` 标志，输出结构化 JSON，无任何终端染色字符或阻塞式交互。
* 🌐 **多地区 Storefront 覆盖**：原生支持切换全球任意 App Store 市场（如 `--country cn`、`--country us`、`--country jp` 等）。

---

## 🛠️ 系统兼容与安装

本仓库自带针对 macOS、Linux 与 Windows 的全自动化安装器，自动识别系统与 CPU 架构，从 GitHub Releases 官方发布渠道拉取最新稳定版二进制。

### 1. macOS & Linux 一键安装

```bash
# 进入技能目录执行
chmod +x install.sh
./install.sh
```

或指定安装路径（默认 `~/.local/bin`）：
```bash
BIN_DIR=/usr/local/bin ./install.sh
```

> **注**：若在特定网络环境下访问 GitHub 较慢，可指定代理镜像变量，如：
> `GITHUB_MIRROR="https://ghproxy.net" ./install.sh`

### 2. Windows 一键安装

* **CMD / 批处理**：直接双击或在终端运行 `install.cmd`
* **PowerShell**：
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\install.ps1
  ```

---

## 🔗 多 Agent 生态无缝集成

通过标准软链接机制，一份技能可在本机所有主流 Agent 环境中实现统一管理与实时热更新：

```bash
# 通用技能根目录
~/.agents/skills/pp-app-store/

# 自动建立软连接到各 Agent：
├── ~/.gemini/config/skills/pp-app-store -> ~/.agents/skills/pp-app-store
├── ~/.codex/skills/pp-app-store        -> ~/.agents/skills/pp-app-store
├── ~/.workbuddy/skills/pp-app-store    -> ~/.agents/skills/pp-app-store
└── ~/.zcode/skills/pp-app-store        -> ~/.agents/skills/pp-app-store
```

`install.sh` / `install.ps1` 运行时会自动检测上述 Agent 路径，若检测到宿主目录存在将**自动完成软链接挂载**。

---

## 📖 核心命令与实战速查

安装完成后，命令行已提供 `app-store-pp-cli` 及别名 `pp-app-store`：

| 挖掘场景 | CLI 命令示例 | 说明 |
| :--- | :--- | :--- |
| **实时榜单大盘** | `app-store-pp-cli top --country cn --genre 6014 --limit 50 --agent` | 拉取分类（如 6014 游戏）免费榜 |
| **竞品全景拆解** | `app-store-pp-cli app 989673964 --country cn --full --agent` | 完整元数据、截图、隐私与权限 |
| **Top 10 内购价格** | `app-store-pp-cli iap 989673964 --country cn --agent` | 获取商业化内购梯队与定价货币 |
| **星级评分直方图** | `app-store-pp-cli ratings 989673964 --histogram --country cn --agent` | 1~5 星精准占比与总体评价量 |
| **版本迭代日志** | `app-store-pp-cli versions 989673964 --country cn --agent` | 提取近 25 个版本更新日志 |
| **智能评价摘要** | `app-store-pp-cli review-digest 989673964 --country cn --agent` | 各版本好评差评走势与高频负面词 |
| **ASO 联想词扩展**| `app-store-pp-cli suggest "小游戏" --country cn --agent` | 模拟搜索下拉词挖掘长尾词 |
| **关键词排位跟踪** | `app-store-pp-cli keyword-rank "收纳" --app 989673964 --country cn --agent` | 追踪指定 App 在搜索结果里的实时顺位 |
| **多品同台横向比** | `app-store-pp-cli compare 989673964 1321803705 --country cn --agent` | 评分、价格、安装包体积侧面对比 |
| **跨国冲榜黑马** | `app-store-pp-cli breakouts --genre 6014 --min-markets 2 --since 7d --agent` | 查找 7 天内多国同时上升的黑马 |

---

## 📁 目录结构

```text
.
├── .gitignore          # 忽略本地 SQLite、缓存及临时构建产物
├── README.md           # 项目综合说明文档（本文件）
├── SKILL.md            # Agent 专用的结构化技能定义与 Prompt 调度规范
├── install.sh          # Linux & macOS 跨平台自动安装脚本
├── install.ps1         # Windows PowerShell 自动安装脚本
└── install.cmd         # Windows 批处理入口向导
```

---

## 📜 鸣谢与上游说明

* 二进制核心与数据解析能力源自开源项目：[mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)
* 本技能遵循 MIT 开源许可。
