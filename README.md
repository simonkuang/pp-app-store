# pp-app-store 📱
> Apple App Store 商业情报挖掘与竞品分析 Agent 技能库（独立开发者增强版）

[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)](#-通用系统兼容与一键安装)
[![Architecture](https://img.shields.io/badge/Arch-x86__64%20%7C%20arm64%20%7C%20Apple%20Silicon-green.svg)](#-通用系统兼容与一键安装)
[![Target](https://img.shields.io/badge/Agents-Universal%20%28~%2F.agents%2Fskills%29-purple.svg)](#-通用系统兼容与一键安装)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

专为 **AI Coding Agent** 与 **独立开发者（Indie Hacker / OPC 一人公司）** 封装的 Apple App Store 市场挖掘与情报分析套件。

底层基于由 Go 语言编写的高性能独立二进制 `app-store-pp-cli`（出自开源项目 [mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)），**无需 Apple 开发者账号、免 API Key 鉴权**，原生内置 SQLite 历史数据库。本技能项目在此基础上，进一步引申并封装了专为独立开发者设计的**差评需求挖掘、内购定价对标、ASO 黄金词阵生成**等实战工作流。

---

## ✨ 核心优势

* 🚀 **零外部运行时依赖**：单文件 Go 编译产物，秒级冷启动，免去复杂的 Python/Node 环境搭建。
* 🔑 **免认证即开即用**：直接调用 Apple 官方公开接口，无账户封禁或密钥过期困扰。
* 🗄️ **通用 SQLite 本地时序库**：所有查询自动落盘（通用路径：`~/.local/data/pp-app-store.db` 或标准 XDG 数据目录），无任何特定机器路径依赖，支持时序排名异动（`movers`）、拉力评估（`traction`）与重大更新影响分析（`impact`）。
* 🤖 **原生 Agent 友好**：所有命令原生支持 `--agent` 标志，输出结构化 JSON，无终端染色字符或交互式阻塞。
* 🛠️ **独立开发者专项增强**：内置开箱即用的高价值工作流脚本（差评寻宝、IAP 定价测算、ASO 词库构建）。

---

## 💻 通用系统兼容与一键安装

本安装程序采用纯通用路径规范，安装二进制至用户本地目录（`~/.local/bin`），技能规范直接安装到通用的 Agent 技能根目录（`~/.agents/skills/pp-app-store`），不捆绑任何特定 Agent 的专属软链接。

### 1. macOS & Linux 一键安装

```bash
# 克隆或下载本仓库后，进入目录执行：
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

## 🎯 独立开发者 5 大高价值实战工作流

除了基础的 API 接口调用外，本项目针对独立开发者的核心痛点，引申并封装了 5 大专属工作流（配有即用型扩展脚本）：

### 1. “差评寻宝”需求挖掘法 (Negative Review Feature Mining)
* **痛点**：做新产品不知道做什么功能，大厂竞品大而全但留有体验死角。
* **做法**：专门筛选竞品 `rating <= 2` 的低星差评，聚类提取用户反复抱怨的“痛点词”与“未满足诉求”。
* **即用脚本**：
  ```bash
  python3 scripts/review_miner.py <APP_ID> --country cn --limit 100 --max-rating 2
  ```

### 2. 商业化模式与内购定价梯队测算 (IAP Pricing Ladder)
* **痛点**：该定多少钱？在中国区推年订阅还是推终身买断 (Lifetime)？
* **做法**：抓取目标应用的 Top 10 内购项，自动解析周期订阅与非消耗型买断，测算折扣率与定价中位数。
* **即用脚本**：
  ```bash
  python3 scripts/iap_analyzer.py <APP_ID> --country cn
  ```

### 3. ASO 黄金标题与关键词矩阵生成 (ASO Keyword Matrix)
* **痛点**：零买量预算，完全靠自然搜索流量，如何把苹果标题的 30 个字符打满？
* **做法**：输入核心种子词，自动通过 `suggest` 获取高搜索意图下拉词，同时扫描前 10 竞品的主副标题高频词，生成符合苹果 30 字符硬约束的方案。
* **即用脚本**：
  ```bash
  python3 scripts/aso_builder.py "<核心词>" --country cn --brand "<产品名>"
  ```

### 4. 蓝海细分赛道与独立黑马探测 (Indie Niche & Blue Ocean Scan)
* **做法**：扫描二级细分类别（如 `7012` 益智、`6007` 效率）前 100 榜单，过滤大厂发行商，锁定评分高于 4.6 且评价数在 500~5000 之间的中小型独立应用。
* **命令**：
  ```bash
  app-store-pp-cli top --country cn --genre 7012 --chart top-free --limit 100 --agent
  ```

### 5. 跨地区出海潜力与客单价套利 (Global Market Arbitrage)
* **做法**：横向比对中国区 (`cn`)、美国区 (`us`)、日本区 (`jp`) 的内购定价与评价热度，测算海外市场的客单价倍数。
* **命令**：
  ```bash
  app-store-pp-cli iap <APP_ID> --country cn --agent
  app-store-pp-cli iap <APP_ID> --country us --agent
  app-store-pp-cli iap <APP_ID> --country jp --agent
  ```

---

## 📖 基础原子命令速查

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

## 📁 项目目录结构

```text
.
├── .gitignore          # 排除本地 SQLite、临时缓存与开发产物
├── README.md           # 项目综合说明文档（本文件）
├── SKILL.md            # Agent 专用的结构化技能定义与 Prompt 调度规范
├── install.sh          # Linux & macOS 跨平台通用自动安装脚本
├── install.ps1         # Windows PowerShell 通用自动安装脚本
├── install.cmd         # Windows 批处理双击安装向导
└── scripts/            # 独立开发者专属复合工作流脚本
    ├── review_miner.py # 差评寻宝与痛点提取器
    ├── iap_analyzer.py # 商业化内购定价梯队测算器
    └── aso_builder.py  # ASO 黄金标题与关键词矩阵构建器
```

---

## 📜 鸣谢与上游说明

* 核心 CLI 二进制源自开源项目：[mvanhorn/printing-press-library](https://github.com/mvanhorn/printing-press-library)
* 本技能遵循 MIT 开源许可。
