# pp-app-store 📱
> Apple App Store 商业情报挖掘与竞品分析 Agent 技能库（独立开发者增强版）

[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)](#-通用系统兼容与一键安装)
[![Architecture](https://img.shields.io/badge/Arch-x86__64%20%7C%20arm64%20%7C%20Apple%20Silicon-green.svg)](#-通用系统兼容与一键安装)
[![Design](https://img.shields.io/badge/Design-Positive%20Prompt%20Only-brightgreen.svg)](#-设计哲学正向驱动--下沉防护)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

专为 **AI Coding Agent** 与 **独立开发者（Indie Hacker / OPC 一人公司）** 封装的 Apple App Store 市场挖掘与情报分析套件。

底层基于高性能独立 Go 二进制 `app-store-pp-cli`（出自开源项目 [mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)），**无需 Apple 开发者账号、免 API Key 鉴权**，原生内置 SQLite 历史数据库。

---

## 💡 设计哲学：正向驱动 · 下沉防护

在 Agent 技能设计中，**过多的负向禁令（“不要做 X”、“严禁触发 429”、“必须等待”）容易污染 Agent 上下文，导致能力一般的模型产生注意力漂移或过度防御**。

本项目严格遵循**“正向指令上浮，防护逻辑下沉”**的工程规范：
* **`SKILL.md` 纯正向导向**：只告诉 Agent 面对什么需求该调用什么指令、输出什么格式的报告，上下文零噪音。
* **防护逻辑静默下沉**：苹果免鉴权接口的频率控制（默认 2s 间隔平滑）、HTTP 429 指数退避、错误重试、本地 SQLite 缓存等所有复杂防御逻辑，**全部封装在脚本和底层 CLI 内部无感执行**。
* **解耦的 `status` 状态查询**：提供专用的状态检查接口，在 Agent 或用户主动查询前，上层完全无需感知限频细节；需要排查时可随时查看当前的执行阶段与频控冷却状态。

---

## ✨ 核心优势

* 🚀 **零外部环境负担**：单文件 Go 二进制，秒级冷启动，免去复杂的浏览器模拟。
* 🔑 **免认证即开即用**：直接调用 Apple 官方公开接口，无账户封禁或密钥过期困扰。
* 🚦 **透明的 `status` 状态探针**：一键掌握上游 API 连通性、当前 Rate Limit 频控状态与 SQLite 缓存数据规模。
* 🗄️ **通用 SQLite 本地时序库**：所有查询自动落盘（通用路径：`~/.local/data/pp-app-store.db` 或标准 XDG 路径），无任何特定机器路径依赖。
* 🤖 **原生 Agent 友好**：所有命令原生支持 `--agent` 标志，输出结构化 JSON，无终端染色字符。

---

## 💻 通用系统兼容与一键安装

本安装程序采用纯通用路径规范，安装二进制至用户本地目录（`~/.local/bin`），技能规范直接安装到通用的 Agent 技能根目录（`~/.agents/skills/pp-app-store`）。

### 1. macOS & Linux 一键安装

```bash
chmod +x install.sh
./install.sh
```

**支持的环境变量自定义**：
* `BIN_DIR`：自定义二进制存放路径（默认：`~/.local/bin`）
* `DATA_DIR`：自定义 SQLite 数据目录（默认：`~/.local/data`）
* `AGENTS_SKILLS_DIR`：自定义技能安装根目录（默认：`~/.agents/skills`）
* `GITHUB_MIRROR`：GitHub 加速代理（如 `GITHUB_MIRROR="https://ghproxy.net"`）

### 2. Windows 一键安装

* **CMD / 批处理**：直接运行 `install.cmd`
* **PowerShell**：
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\install.ps1
  ```

---

## 🎯 独立开发者专属增强脚本

在基础 CLI 之外，本项目在 `scripts/` 目录下提供了专为独立开发者痛点设计的分析工具（已内嵌透明控速与退避）：

### 1. 运行状态与频控检测 (`status.py`)
* **作用**：检查苹果上游 API 连通性、当前 Rate Limit 频控健康度（距上次发包间隔、冷却状态）及 SQLite 缓存统计（支持 `--json`）。
* **用法**：
  ```bash
  python3 scripts/status.py
  ```

### 2. “差评寻宝”分析器 (`review_miner.py`)
* **作用**：自动过滤竞品 ≤2 星差评，提取高频痛点词与用户求而不得的功能点，提炼差异化切入清单。
* **用法**：
  ```bash
  python3 scripts/review_miner.py <APP_ID> --country cn
  ```

### 3. 商业化内购定价拆解器 (`iap_analyzer.py`)
* **作用**：抓取并拆解目标应用 Top 10 内购项（周期订阅、终身买断、代币），输出定价阶梯建议。
* **用法**：
  ```bash
  python3 scripts/iap_analyzer.py <APP_ID> --country cn
  ```

### 4. ASO 黄金标题生成器 (`aso_builder.py`)
* **作用**：输入核心业务词，自动结合下拉联想与竞品词频，生成符合苹果 ≤30 字符硬约束的推荐标题。
* **用法**：
  ```bash
  python3 scripts/aso_builder.py "<核心词>" --country cn --brand "<产品名>"
  ```

---

## 📖 基础原子命令速查

| 调研场景 | CLI 命令示例 | 说明 |
| :--- | :--- | :--- |
| **实时榜单大盘** | `app-store-pp-cli top --country cn --genre 6014 --limit 50 --agent` | 拉取分类（如 6014 游戏）免费榜 |
| **单品完整画像** | `app-store-pp-cli app 989673964 --country cn --agent` | 获取应用基础信息、评分概况与副标题 |
| **App Store 搜索** | `app-store-pp-cli search-store "收纳" --country cn --limit 30 --agent` | 检索关键词排名靠前的应用列表 |
| **竞品同台横向比** | `app-store-pp-cli compare 989673964 1321803705 --country cn --agent` | 评分、价格、安装包体积侧面对比 |
| **跨国冲榜黑马** | `app-store-pp-cli breakouts --genre 6014 --min-markets 2 --since 7d --agent` | 查找 7 天内多国同时上升的黑马 |

---

## 📁 项目目录结构

```text
.
├── .gitignore          # 排除本地 SQLite、临时缓存与开发产物
├── README.md           # 项目综合说明文档（本文件）
├── SKILL.md            # Agent 专用的正向技能指令与任务流程规范
├── install.sh          # Linux & macOS 跨平台通用自动安装脚本
├── install.ps1         # Windows PowerShell 通用自动安装脚本
├── install.cmd         # Windows 批处理双击安装向导
└── scripts/            # 独立开发者专属复合工作流脚本
    ├── status.py       # 状态探针与 Rate Limit 频控检测器
    ├── review_miner.py # 差评寻宝与痛点提取器
    ├── iap_analyzer.py # 商业化内购定价梯队测算器
    └── aso_builder.py  # ASO 黄金标题与关键词矩阵构建器
```

---

## 📜 鸣谢与上游说明

* 核心 CLI 二进制源自开源项目：[mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)
* 本技能遵循 MIT 开源许可。
