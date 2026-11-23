---
name: pp-app-store
description: Apple App Store data mining, market intelligence, competitor teardown, ASO tracking, and user feedback analysis using app-store-pp-cli. Use this skill when researching App Store rankings, analyzing app traction and ratings, conducting ASO keyword research, benchmarking competitor IAP prices, reading user review sentiment, or discovering breakout apps across any regional storefront.
---

# App Store 商业情报与数据挖掘指南 (`pp-app-store`)

本技能为 Agent 提供完整的 Apple App Store 市场挖掘与情报分析能力。所有网络请求已在底层脚本中自动完成了频率控制、智能重试与数据缓存，Agent 仅需专注执行上层任务与报告产出。

---

## 一、核心推荐指令速查

针对最常见的调研需求，优先使用已封装好的高阶分析脚本或 CLI 原生指令：

| 调研目标 | 推荐执行指令 | 输出效果 |
| :--- | :--- | :--- |
| **查询环境与频控状态** | `python3 ~/.agents/skills/pp-app-store/scripts/status.py` | 查看苹果接口连通性、当前 Rate Limit 状态与 SQLite 缓存规模 |
| **挖掘竞品差评痛点** | `python3 ~/.agents/skills/pp-app-store/scripts/review_miner.py <APP_ID> --country cn` | 自动筛选低星评价，聚类核心吐槽词与新功能机会点 |
| **拆解内购定价模型** | `python3 ~/.agents/skills/pp-app-store/scripts/iap_analyzer.py <APP_ID> --country cn` | 拆解周/月/年订阅及终身买断，给出定价阶梯建议 |
| **生成 ASO 标题方案** | `python3 ~/.agents/skills/pp-app-store/scripts/aso_builder.py "<关键词>" --country cn` | 提取联想词与竞品词频，生成 ≤30 字符的主副标题组合 |
| **查询单品完整信息** | `app-store-pp-cli app <APP_ID> --country cn --agent` | 获取应用基础信息、评分概况、开发者与副标题 |
| **搜索 App Store 应用** | `app-store-pp-cli search-store "<关键词>" --country cn --agent` | 检索关键词排名靠前的应用列表与 App ID |
| **查询分类实时榜单** | `app-store-pp-cli top --country cn --genre 6014 --limit 30 --agent` | 拉取游戏类（6014）或其他分类的免费榜大盘 |
| **对比两款同类竞品** | `app-store-pp-cli compare <APP_1> <APP_2> --country cn --agent` | 横向对比两款应用的价格、评分、体积与版本更新 |

> 提示：
> 1. 上述指令在执行时已完全内置频率保护，Agent 无需额外干预底层速率。
> 2. `--country` 参数默认对应目标地区（中国区用 `cn`，美国区用 `us`，日本区用 `jp`）。CLI 命令添加 `--agent` 可获得标准紧凑 JSON。

---

## 二、标准任务作业流程 (Task Recipes)

### 任务 1：竞品深度体检调研
当用户需要全面调研某款应用（如“帮我分析一下《我在古代有座城》怎么样”）时：
1. **获取 App ID**：若用户未提供 ID，先运行 `app-store-pp-cli search-store "<应用名>" --country cn --agent` 查得 `appId`。
2. **提取商业化与口碑**：
   - 运行 `python3 ~/.agents/skills/pp-app-store/scripts/iap_analyzer.py <APP_ID> --country cn`
   - 运行 `python3 ~/.agents/skills/pp-app-store/scripts/review_miner.py <APP_ID> --country cn`
3. **结构化输出**：汇报该应用定位、评分情况、主要变现手段（纯内购/订阅/广告），以及用户最集中的差评诉求。

---

### 任务 2：细分赛道选品与机会发掘
当用户需要寻找市场机会（如“最近微信小游戏或收纳类游戏有什么好方向”）时：
1. **扫描大盘**：运行 `app-store-pp-cli top --country cn --genre <GENRE_ID> --limit 50 --agent` 查看榜单（益智游戏类 genre 为 `7012`，效率工具类为 `6007`）。
2. **定位代表竞品**：从中挑出 2~3 款排名靠前且评分较高的小团队/独立产品。
3. **寻找差异化空缺**：调用 `review_miner.py` 查阅其低星差评，找出竞品未做好的功能死角。

---

### 任务 3：新产品 ASO 命名与关键词规划
当用户希望为新应用起名或优化 App Store 搜索权重时：
1. **生成推荐词阵**：运行 `python3 ~/.agents/skills/pp-app-store/scripts/aso_builder.py "<核心业务词>" --country cn --brand "<预设品牌名>"`。
2. **提供两套策略方案**：
   - **功能直觉型**：品牌名 + 核心功能词 + 场景，提升自然搜索命中率。
   - **卖点突出型**：品牌名 + 核心差异点（如极简、无广告、买断），吸引高意向用户点击。

---

### 任务 4：环境体检与缓存状态查询
当用户询问当前数据挖掘工具是否正常工作，或查询本地缓存了多少应用数据时：
1. 直接运行：`python3 ~/.agents/skills/pp-app-store/scripts/status.py`
2. 根据输出简要向用户反馈 API 连通性、当前频控健康度与本地数据库统计。

---

## 三、报告交付模板

在向用户汇报调研结论时，优先采用以下结构组织回复：

```markdown
### 1. 基础画像与市场定位
- **应用名称**：[产品名]（ID: [App ID]）
- **分类与排位**：[如：游戏-益智榜第 3 名]
- **用户评分**：[评分] 星（基于 [评价数] 条评价）

### 2. 商业化与变现模式
- **核心模式**：[如：免费下载 + 订阅制 / 终身买断制]
- **代表定价梯队**：[列举月费、年费或主要充值档位]
- **对标启示**：[独立开发者适用的定价建议]

### 3. 用户口碑与真实痛点（机会点）
- **高频吐槽**：[用户最集中的 2~3 个抱怨，如缺少数据导出、付费提示过于频繁]
- **功能机会**：[做新产品时可以直接作为核心亮点的功能点]

### 4. 行动建议
- [具体的 1~2 条落地动作建议]
```
