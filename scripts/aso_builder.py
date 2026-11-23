#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立开发者 ASO 黄金标题与关键词矩阵构建器 (ASO Builder)
基于 App Store 搜索联想与竞品标题拆解，生成符合 30 字符硬约束的爆款标题方案。
内置跨请求节奏控制 (Pacing)，避免短时间内突发请求触发苹果风控。
"""

import sys
import json
import subprocess
import argparse
import time
import re
from collections import Counter

def run_command(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return p.stdout
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Command failed: {' '.join(cmd)}\n{e.stderr}\n")
        return None

def build_aso_matrix(seed_keyword, country="cn", brand_name="", delay_sec=1.5, rate_limit="0.5"):
    print(f"\n=======================================================")
    print(f"🔍 ASO 关键词矩阵与标题生成器 (种子词: '{seed_keyword}' | 市场: {country})")
    print(f"=======================================================\n")

    # 1. 抓取联想词 (Suggest)
    cmd_suggest = [
        "app-store-pp-cli", "suggest", seed_keyword,
        "--country", country,
        "--rate-limit", str(rate_limit),
        "--agent"
    ]
    out_suggest = run_command(cmd_suggest)
    suggestions = []
    if out_suggest:
        try:
            data = json.loads(out_suggest)
            suggestions = data.get("results", {}).get("suggestions", [])
            if not suggestions and isinstance(data.get("results"), list):
                suggestions = data.get("results")
        except Exception:
            pass

    print("💡 1. App Store 搜索下拉联想词 (高意图搜索词):")
    if suggestions:
        for idx, s in enumerate(suggestions[:10], 1):
            term = s if isinstance(s, str) else s.get("term", str(s))
            print(f"   [{idx:2d}] {term}")
    else:
        print("   (未获取到联想词)")
    print("")

    # 速率平滑控制：多步抓取之间强制沉睡，遵守苹果经验速率
    if delay_sec > 0:
        time.sleep(delay_sec)

    # 2. 搜索前排竞品 (Search-Store) 提取标题词频
    cmd_search = [
        "app-store-pp-cli", "search-store", seed_keyword,
        "--country", country,
        "--limit", "15",
        "--rate-limit", str(rate_limit),
        "--agent"
    ]
    out_search = run_command(cmd_search)
    competitor_titles = []
    if out_search:
        try:
            data = json.loads(out_search)
            apps = data.get("results", [])
            for a in apps[:10]:
                title = a.get("title", "")
                subtitle = a.get("subtitle", "")
                competitor_titles.append((title, subtitle))
        except Exception:
            pass

    print("🏆 2. 头部竞品主标题与副标题参考 (前 5 名):")
    for idx, (t, st) in enumerate(competitor_titles[:5], 1):
        sub_str = f" - {st}" if st else ""
        print(f"   [{idx}] {t}{sub_str}")
    print("")

    # 3. 分词提取核心热词
    corpus = " ".join([f"{t} {st}" for t, st in competitor_titles])
    tokens = re.findall(r'[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}', corpus)
    stop = {seed_keyword, "游戏", "软件", "应用", "专业", "正版", "官方"}
    hot_keywords = [k for k, _ in Counter([w for w in tokens if w not in stop]).most_common(8)]

    print(f"🔥 3. 竞品覆盖核心高频修饰词: {', '.join(hot_keywords)}")
    print("")

    # 4. 生成建议标题（严格遵守 30 字符上限）
    brand = brand_name if brand_name else "我的应用"
    print("✨ 4. 独立开发者 ASO 推荐组合方案 (严格 ≤30 字符):")
    
    plan_a_title = f"{brand} - {seed_keyword}"
    if hot_keywords:
        plan_a_sub = f"{hot_keywords[0]}与{hot_keywords[1] if len(hot_keywords) > 1 else '工具'}的首选"
    else:
        plan_a_sub = f"简单好用的{seed_keyword}助手"

    print(f"   • 方案 A (功能直觉型):")
    print(f"     - 主标题: {plan_a_title[:30]} (字符数: {len(plan_a_title)})")
    print(f"     - 副标题: {plan_a_sub[:30]} (字符数: {len(plan_a_sub)})")

    if hot_keywords and len(hot_keywords) >= 2:
        plan_b_title = f"{brand}: {seed_keyword}{hot_keywords[0]}"
        plan_b_sub = f"轻量{hot_keywords[1]}·无广告无后台"
    else:
        plan_b_title = f"{brand}：极简{seed_keyword}"
        plan_b_sub = f"轻量不占内存·随开随用"

    print(f"   • 方案 B (独立卖点型):")
    print(f"     - 主标题: {plan_b_title[:30]} (字符数: {len(plan_b_title)})")
    print(f"     - 副标题: {plan_b_sub[:30]} (字符数: {len(plan_b_sub)})")

def main():
    parser = argparse.ArgumentParser(description="App Store 独立开发者 ASO 矩阵生成器 (带速率平滑控制)")
    parser.add_argument("keyword", help="核心种子关键词 (如 '背单词', '收纳', '记账')")
    parser.add_argument("--country", default="cn", help="Storefront 国家代码 (默认 cn)")
    parser.add_argument("--brand", default="", help="自有品牌名或产品名预设 (可选)")
    parser.add_argument("--delay", type=float, default=1.5, help="请求间平滑等待秒数 (默认 1.5s)")
    parser.add_argument("--rate-limit", default="0.5", help="CLI 内部请求限频 (默认 0.5 即 2秒/次)")
    args = parser.parse_args()

    build_aso_matrix(args.keyword, args.country, args.brand, args.delay, args.rate_limit)

if __name__ == "__main__":
    main()
