---
name: pp-app-store
description: Apple App Store data mining, market intelligence, competitor teardown, ASO tracking, and user feedback analysis using app-store-pp-cli. Use this skill when researching App Store rankings, analyzing app traction and ratings, conducting ASO keyword research, benchmarking competitor IAP prices, reading user review sentiment, or discovering breakout apps across any regional storefront.
---

# App Store 数据挖掘与竞品情报指南 (`pp-app-store`)

本技能指导 Agent 利用本地单文件 Go 二进制工具 `app-store-pp-cli`（别名 `pp-app-store`，默认安装于 `~/.local/bin/`），免开发者账号与 API Key、直接调用 Apple App Store 公开接口完成深度的市场情报挖掘。

---

## 一、核心原则与调用规范

1. **二进制路径与别名**：
   - 默认安装路径：`~/.local/bin/app-store-pp-cli`
   - 兼容别名：`~/.local/bin/pp-app-store`
   - 若系统未检测到该工具，请提示用户运行本技能目录下的 `./install.sh`（Linux/macOS）或 `install.cmd`（Windows）一键安装。

2. **强制使用 `--agent` 参数**：
   - 对任何子命令添加 `--agent` 标志，会自动启用 `--json --compact --no-input --no-color`，以结构化 JSON 输出结果，杜绝交互式提示与终端染色代码。

3. **国家地区 Storefront (`--country`)**：
   - 默认国家代码为 `us`（美国区）。
   - 分析国内市场或特定区域时，**务必显式指定国家代码**，如中国区 `--country cn`、日本区 `--country jp`、韩国区 `--country kr`、英国区 `--country gb`。

4. **本地 SQLite 自动落盘与时序分析**：
   - 工具运行产生的数据会自动缓存在本地 SQLite 数据库（`~/.local/share/app-store-pp-cli/data.db`）。
   - 连续抓取后，可直接调用 `movers`（排名异动）、`traction`（增长拉力）、`impact`（更新影响）进行时序对比。

---

## 二、高频挖掘场景与命令配方 (Playbooks)

### 场景 1：竞品全景拆解（Listing / 商业化 / 评分）

当需要对某款竞品应用（已知 App ID，如微信 `414478124` 或王者荣耀 `989673964`）进行全方位体检时：

```bash
# 1. 基础元数据、副标题、开发者与实时榜单排名
app-store-pp-cli app <APP_ID> --country cn --agent

# 2. 深度全景（包含应用描述、截图、隐私标签、应用能力、内购价格）
app-store-pp-cli app <APP_ID> --full --country cn --agent

# 3. 商业化分析：抓取前 10 大内购项目（IAP）与定价梯度
app-store-pp-cli iap <APP_ID> --country cn --agent

# 4. 用户口碑：星级分布直方图与真实评分量
app-store-pp-cli ratings <APP_ID> --histogram --country cn --agent

# 5. 更新节奏：获取最近 25 次版本更新日志与发布时间
app-store-pp-cli versions <APP_ID> --country cn --agent
```

---

### 场景 2：用户评价挖掘与差评痛点分析 (Voice of Customer)

通过用户真实反馈洞察核心抱怨、功能缺陷及需求痛点：

```bash
# 1. 评论智能摘要：生成星级分布、按版本的评分走势及高频投诉词
app-store-pp-cli review-digest <APP_ID> --country cn --agent

# 2. 抓取最新与最有价值评论（自动去重并入库）
app-store-pp-cli reviews <APP_ID> --country cn --limit 50 --agent

# 3. 本地离线检索已落盘的评论（支持关键词检索，如闪退、卡顿、扣费）
app-store-pp-cli search "闪退" --country cn
```

---

### 场景 3：大盘榜单扫描与黑马产品发现 (Charts & Breakouts)

挖掘细分赛道正处于上升期的潜力产品：

```bash
# 1. 查询分类及其 Genre ID（游戏类：6014，动作类：7001，益智类：7012，效率类：6007 等）
app-store-pp-cli categories list
app-store-pp-cli categories games

# 2. 拉取特定分类实时榜单（支持 top-free / top-paid / top-grossing，默认最多 200 条）
app-store-pp-cli top --country cn --genre 6014 --chart top-free --limit 50 --agent

# 3. 榜单异动扫描（对比最近两次快照的进榜、掉榜、攀升应用）
app-store-pp-cli movers --country cn --genre 6014 --agent

# 4. 全球跨市场黑马发现（查找同时在多个国家/地区冲榜的产品）
app-store-pp-cli breakouts --genre 6014 --min-markets 2 --since 7d --agent

# 5. 查看 Today 标签页精选故事与被推荐应用
app-store-pp-cli featured --country cn --agent
```

---

### 场景 4：ASO 搜索优化与关键词情报 (ASO & Keyword Intelligence)

```bash
# 1. 模拟 App Store 搜索下拉联想词（获取高价值长尾词）
app-store-pp-cli suggest "小游戏" --country cn --agent

# 2. 按关键词进行 App Store 实况搜索
app-store-pp-cli search-store "收纳" --country cn --limit 30 --agent

# 3. 查询特定应用在关键词搜索结果中的实时排名位置，并落盘跟踪
app-store-pp-cli keyword-rank "消除" --app <APP_ID> --country cn --agent

# 4. 查看某个关键词在历史跟踪中的排名变动趋势
app-store-pp-cli keyword-history "消除" --country cn --agent
```

---

### 场景 5：增长趋势与竞品横向对比 (Traction & Comparison)

```bash
# 1. 评估需求拉力（基于评分新增速率、榜单排名等综合代理指标，按月/年汇总）
app-store-pp-cli traction <APP_ID> --period monthly --country cn --agent

# 2. 版本重大更新/改名/调价前后的效果对比（Impact 分析）
app-store-pp-cli impact <APP_ID> --date 2026-11-01 --country cn --agent

# 3. 多款同类竞品同台横向对比（对比评分、价格、包体大小、版本）
app-store-pp-cli compare <APP_ID_1> <APP_ID_2> --country cn --agent

# 4. 查看苹果官方算法推荐的“类似应用”列表
app-store-pp-cli similar <APP_ID> --country cn --agent
```

---

## 三、Agent 执行产出规范

当用户要求做 App Store 调研或竞品分析时，Agent 应遵循以下流程交付结构化报告：

1. **定位产品**：先通过 `search-store` 确认目标产品的 `appId` 及官方名称。
2. **多维提取**：组合 `app`（基础信息）、`iap`（商业化模式）、`ratings`/`review-digest`（用户口碑），必要时用 `similar` 找齐 2-3 款主要竞品。
3. **输出报告结构建议**：
   - **基础画像**：应用名、副标题、开发者、当前榜单排位、上线及更新日期。
   - **商业化模型**：内购项价格分布（免费内购/订阅制/买断制），定价策略分析。
   - **用户口碑洞察**：评分分布健康度，正面评价焦点 vs 负面吐槽/痛点诉求。
   - **ASO 与获客策略**：主副标题关键词覆盖度、相关搜索排名表现。
   - **机会与建议**：基于竞品缺陷提炼差异化切入点。
