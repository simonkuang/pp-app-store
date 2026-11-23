---
name: pp-app-store
description: Apple App Store data mining, market intelligence, competitor teardown, ASO tracking, and user feedback analysis using app-store-pp-cli. Use this skill when researching App Store rankings, analyzing app traction and ratings, conducting ASO keyword research, benchmarking competitor IAP prices, reading user review sentiment, or discovering breakout apps across any regional storefront.
---

# App Store 数据挖掘与竞品情报指南 (`pp-app-store`)

本技能指导 Agent 利用单文件 Go 二进制工具 `app-store-pp-cli`（别名 `pp-app-store`，默认安装于 `~/.local/bin/`），免开发者账号与 API Key、直接调用 Apple App Store 公开接口完成深度的市场情报挖掘。

---

## 一、核心原则与通用环境规范

1. **二进制与通用目录**：
   - 二进制路径：`~/.local/bin/app-store-pp-cli`（别名 `pp-app-store`）。
   - 技能项目路径：通用 Agent 技能目录 `~/.agents/skills/pp-app-store/`。
   - 若系统未检测到该工具，请提示用户运行本技能目录下的 `./install.sh`（Linux/macOS）或 `install.cmd`（Windows）一键安装。

2. **通用 SQLite 数据存储规范**：
   - 默认存储：CLI 默认将时序数据存储于跨平台的标准数据目录中。
   - 自定义通用路径：若需要指定通用数据库文件，建议统一使用 `--db ~/.local/data/pp-app-store.db`，**严禁在命令中硬编码任何特定用户的机器绝对路径**。

3. **强制使用 `--agent` 参数**：
   - 对任何子命令添加 `--agent` 标志，会自动启用 `--json --compact --no-input --no-color`，以结构化 JSON 输出结果，杜绝交互式提示与终端染色代码。

4. **国家地区 Storefront (`--country`)**：
   - 默认国家代码为 `us`（美国区）。
   - 分析国内市场或特定区域时，**务必显式指定国家代码**，如中国区 `--country cn`、日本区 `--country jp`、韩国区 `--country kr`、英国区 `--country gb`。

---

## 二、基础原子接口速查 (Native Primitives)

```bash
# 1. 榜单与分类
app-store-pp-cli top --country cn --genre 6014 --chart top-free --limit 50 --agent
app-store-pp-cli categories list
app-store-pp-cli categories games

# 2. 单品画像与元数据
app-store-pp-cli app <APP_ID> --country cn --agent
app-store-pp-cli app <APP_ID> --full --country cn --agent
app-store-pp-cli ratings <APP_ID> --histogram --country cn --agent

# 3. 商业化与版本
app-store-pp-cli iap <APP_ID> --country cn --agent
app-store-pp-cli versions <APP_ID> --country cn --agent

# 4. 评价挖掘
app-store-pp-cli review-digest <APP_ID> --country cn --agent
app-store-pp-cli reviews <APP_ID> --country cn --limit 50 --agent

# 5. ASO 与搜索
app-store-pp-cli search-store "<KEYWORD>" --country cn --limit 30 --agent
app-store-pp-cli suggest "<KEYWORD>" --country cn --agent
app-store-pp-cli keyword-rank "<KEYWORD>" --app <APP_ID> --country cn --agent

# 6. 时序异动与黑马发现 (依赖本地 SQLite 历史)
app-store-pp-cli movers --country cn --genre 6014 --agent
app-store-pp-cli breakouts --genre 6014 --min-markets 2 --since 7d --agent
app-store-pp-cli traction <APP_ID> --period monthly --country cn --agent
app-store-pp-cli compare <APP_1> <APP_2> --country cn --agent
```

---

## 三、独立开发者深度衍生工作流 (Indie Workflows)

结合独立开发者（Indie Hacker / OPC 一人公司）的实际立项与商业化痛点，本技能在基础接口之上引申并封装了以下 5 个高价值综合工作流：

### 1. “差评寻宝”需求挖掘法 (Negative Review Feature Mining)
* **痛点场景**：做新产品不知道做什么功能，大厂成熟竞品功能繁杂但留有死角。
* **衍生逻辑**：拉取竞品评论，专门过滤出 `rating <= 2` 的低星差评，聚类提取用户反复抱怨的“核心痛点”、“收费太黑”与“未满足功能请求”。
* **执行命令**：
  ```bash
  # 直接调用技能内置扩展脚本：
  python3 ~/.agents/skills/pp-app-store/scripts/review_miner.py <APP_ID> --country cn --limit 100 --max-rating 2
  ```
* **产出物**：
  - 高频吐槽词 TOP 榜（如闪退、强制广告、贵、缺少导入功能）。
  - 典型痛点原声反馈（提炼做差异化新产品的首发功能清单）。

---

### 2. 商业化模式与内购定价梯队测算 (IAP Pricing Ladder)
* **痛点场景**：不知道该定多少钱，是在中国区推年订阅还是推终身买断？
* **衍生逻辑**：抓取目标应用的 Top 10 内购项，自动解析周期性订阅（周/月/年）与非消耗型买断（Lifetime），计算年费折扣率与客单价中位数。
* **执行命令**：
  ```bash
  # 直接调用技能内置扩展脚本：
  python3 ~/.agents/skills/pp-app-store/scripts/iap_analyzer.py <APP_ID> --country cn
  ```
* **产出物**：
  - 变现模型判定（纯订阅型 / 订阅+终身买断混合型 / 消耗性代币型）。
  - 独立开发者定价对标建议（如何用“买断制”击穿纯订阅竞品的护城河）。

---

### 3. ASO 黄金标题与关键词矩阵生成 (ASO Keyword Matrix)
* **痛点场景**：没有买量预算，完全依赖自然搜索流量，如何把苹果标题的 30 个字符打满？
* **衍生逻辑**：输入核心种子词，自动通过 `suggest` 获取高搜索意图联想词，同时扫描前 10 名竞品的主副标题高频词，组装出符合苹果字符硬约束的推荐方案。
* **执行命令**：
  ```bash
  # 直接调用技能内置扩展脚本：
  python3 ~/.agents/skills/pp-app-store/scripts/aso_builder.py "<核心词>" --country cn --brand "<品牌名>"
  ```
* **产出物**：
  - 搜索下拉高价值长尾词列表。
  - 严格限制在 30 字符以内的「功能直觉型」与「独立卖点型」标题 + 副标题组合。

---

### 4. 蓝海细分赛道与独立黑马探测 (Indie Niche & Blue Ocean Scan)
* **痛点场景**：如何避开买量大厂，找到小团队做出来的轻量级、高口碑黑马产品？
* **衍生逻辑**：
  1. 调用 `top` 拉取细分二级分类（如 `7012` 益智、`6007` 效率、`6017` 教育）的免费或付费榜前 100 名。
  2. 过滤掉大厂（腾讯、网易、字节等），锁定评分高于 4.6 且评价数在 500~5000 之间的中小型独立应用。
  3. 通过 `traction` 与 `movers` 验证其近期是否有持续增长。
* **执行命令**：
  ```bash
  app-store-pp-cli top --country cn --genre 7012 --chart top-free --limit 100 --agent
  ```

---

### 5. 跨地区出海潜力与客单价套利 (Global Market Arbitrage)
* **痛点场景**：同一款产品在国内变现难，在海外能否卖出 5~10 倍单价？
* **衍生逻辑**：横向比对目标应用在中国区 (`cn`)、美国区 (`us`)、日本区 (`jp`) 的内购定价与评价热度，测算各地区实际客单价。
* **执行命令**：
  ```bash
  # 对比各地区定价
  app-store-pp-cli iap <APP_ID> --country cn --agent
  app-store-pp-cli iap <APP_ID> --country us --agent
  app-store-pp-cli iap <APP_ID> --country jp --agent
  ```

---

## 四、Agent 执行交付规范

当用户询问 App Store 竞品调研或赛道分析时，Agent 应遵循以下流程产出深度分析报告：

1. **确定目标**：通过 `search-store` 确认目标产品的 `appId`。
2. **多维数据组合调用**：
   - 基础画像：`app --agent` + `ratings --histogram --agent`
   - 商业化梯队：`iap_analyzer.py` 或 `iap --agent`
   - 差评寻宝：`review_miner.py` 或 `reviews --agent`
3. **交付报告标准模块**：
   - **基础画像与当前大盘**（包体大小、最新版本、当前榜单排名）
   - **商业化模式解析**（订阅周期、定价梯度、是否存在买断机会）
   - **用户真实口碑与致命痛点**（竞品做得很烂、用户在差评里求的功能）
   - **独立开发者破局建议**（功能取舍建议、定价策略、ASO 命名参考）
