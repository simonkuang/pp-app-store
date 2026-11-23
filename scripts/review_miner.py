#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立开发者“差评寻宝”分析器 (Review Miner)
从 App Store 差评中提取高频槽点、未被满足的需求与新功能切入点。
内置速率控制与重试退避机制，严格遵守苹果公共接口频控策略。
"""

import sys
import json
import subprocess
import argparse
import time
from collections import Counter
import re

def run_command_with_retry(cmd, max_retries=3, delay_sec=2.0):
    for attempt in range(1, max_retries + 1):
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return p.stdout
        except subprocess.CalledProcessError as e:
            err = e.stderr or ""
            # 检测是否触发 429 或限流
            if "429" in err or "rate limit" in err.lower():
                wait = delay_sec * (2 ** (attempt - 1))
                sys.stderr.write(f"[WARN] 触发速率限制 (429/RateLimit)，第 {attempt} 次重试，退避等待 {wait:.1f} 秒...\n")
                time.sleep(wait)
            else:
                sys.stderr.write(f"[ERROR] 命令执行失败: {' '.join(cmd)}\n{err}\n")
                if attempt == max_retries:
                    return None
                time.sleep(delay_sec)
    return None

def analyze_reviews(app_id, country="cn", limit=100, max_rating=2, rate_limit="0.5"):
    cmd = [
        "app-store-pp-cli", "reviews", str(app_id),
        "--country", country,
        "--limit", str(limit),
        "--rate-limit", str(rate_limit),
        "--agent"
    ]
    out = run_command_with_retry(cmd)
    if not out:
        return

    try:
        data = json.loads(out)
    except Exception as e:
        sys.stderr.write(f"JSON 解析失败: {e}\n原始输出: {out[:200]}\n")
        return

    reviews = data.get("results", {}).get("reviews", [])
    if not reviews and isinstance(data.get("results"), list):
        reviews = data.get("results")

    negative_reviews = []
    for r in reviews:
        score = r.get("rating", 5)
        if score <= max_rating:
            negative_reviews.append({
                "rating": score,
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "version": r.get("version", "unknown"),
                "date": r.get("date", "")
            })

    print(f"\n=======================================================")
    print(f"📊 差评痛点挖掘报告 (App ID: {app_id} | 市场: {country})")
    print(f"总拉取评论数: {len(reviews)} | 筛选低星差评 (≤{max_rating}星): {len(negative_reviews)}")
    print(f"=======================================================\n")

    if not negative_reviews:
        print("未提取到符合条件的低星差评，产品口碑较为平稳或评论样本偏少。")
        return

    text_corpus = " ".join([f"{r['title']} {r['body']}" for r in negative_reviews])
    words = re.findall(r'[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}', text_corpus)
    stop_words = {"这个", "一个", "什么", "怎么", "没有", "不是", "还是", "觉得", "就是", "感觉", "真的", "现在", "因为", "所以", "软件", "应用", "app"}
    filtered_words = [w for w in words if w not in stop_words]
    common_words = Counter(filtered_words).most_common(12)

    print("🔥 高频吐槽关键词 TOP 12:")
    for w, count in common_words:
        print(f"  • {w}: 出现 {count} 次")
    print("")

    print(f"💬 典型痛点原声反馈（精选最多 6 条）:")
    for i, r in enumerate(negative_reviews[:6], 1):
        print(f"  [{i}] ({r['rating']}星 | v{r['version']}) {r['title']}")
        print(f"      “{r['body'].strip()[:100]}...”")
        print("")

    print("💡 独立开发者切入机会建议:")
    print("  1. 体验修复型机会：检查上述差评是否集中在性能/闪退/强制全屏广告，做极致轻量、体验克制的产品可迅速吸纳流失用户。")
    print("  2. 定价破局型机会：若高频词含'收费'、'贵'、'扣费'，可考虑提供一次性买断 (Lifetime) 或更轻巧的亲民阶梯。")
    print("  3. 需求补完型机会：针对用户高频抱怨'缺少XX功能'，在自己的产品中作为首发核心差异点。")

def main():
    parser = argparse.ArgumentParser(description="App Store 竞品差评痛点寻宝工具 (带速率控制)")
    parser.add_argument("app_id", help="目标应用 App ID (如 989673964)")
    parser.add_argument("--country", default="cn", help="Storefront 国家代码 (默认 cn)")
    parser.add_argument("--limit", type=int, default=100, help="获取评论样本量 (默认 100)")
    parser.add_argument("--max-rating", type=int, default=2, help="最高星级过滤 (默认 2星)")
    parser.add_argument("--rate-limit", default="0.5", help="每秒最大请求数 (默认 0.5 即 2秒/次，防止触碰苹果限频)")
    args = parser.parse_args()

    analyze_reviews(args.app_id, args.country, args.limit, args.max_rating, args.rate_limit)

if __name__ == "__main__":
    main()
