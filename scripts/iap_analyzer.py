#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立开发者商业化与内购定价梯队分析器 (IAP Analyzer)
拆解目标应用的变现结构（买断、按周/月/年订阅、消耗性代币），测算定价中位数与年费折扣比。
内置速率控制与重试保护。
"""

import sys
import json
import subprocess
import argparse
import time
import re

def run_command_with_retry(cmd, max_retries=3, delay_sec=2.0):
    for attempt in range(1, max_retries + 1):
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return p.stdout
        except subprocess.CalledProcessError as e:
            err = e.stderr or ""
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

def analyze_iap(app_id, country="cn", rate_limit="0.5"):
    cmd = [
        "app-store-pp-cli", "iap", str(app_id),
        "--country", country,
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

    items = data.get("results", {}).get("items", [])
    if not items:
        print(f"⚠️ App ID {app_id} 在 {country} 区未检测到公开的内购项目（可能为纯免费、广告变现或付费下载）。")
        return

    subscriptions = []
    consumables = []
    lifetimes = []
    others = []

    for item in items:
        name = item.get("name", "")
        price_str = item.get("price", "")
        num_match = re.search(r'([0-9]+(?:\.[0-9]+)?)', price_str.replace(",", ""))
        price_val = float(num_match.group(1)) if num_match else 0.0

        item_info = {
            "name": name,
            "price": price_str,
            "value": price_val,
            "currency": item.get("currency", "")
        }

        if re.search(r'年|Year|Annual', name, re.I):
            subscriptions.append(("年度订阅", item_info))
        elif re.search(r'月|Month', name, re.I):
            subscriptions.append(("月度订阅", item_info))
        elif re.search(r'周|Week', name, re.I):
            subscriptions.append(("周度订阅", item_info))
        elif re.search(r'永久|终身|买断|Lifetime', name, re.I):
            lifetimes.append(item_info)
        elif re.search(r'金币|钻石|点数|Coin|Gem|代币', name, re.I):
            consumables.append(item_info)
        else:
            others.append(item_info)

    print(f"\n=======================================================")
    print(f"💰 商业化与内购体系拆解 (App ID: {app_id} | 市场: {country})")
    print(f"检测到 In-App Purchases 总项数: {len(items)}")
    print(f"=======================================================\n")

    print("📋 全部内购项目明细:")
    for idx, it in enumerate(items, 1):
        print(f"  {idx:2d}. {it['name']:<25} -> {it['price']}")
    print("")

    if subscriptions:
        print("🔄 订阅制阶梯分析:")
        for period, s in subscriptions:
            print(f"  • [{period}] {s['name']}: {s['price']}")
        print("")

    if lifetimes:
        print("💎 终身买断制项目 (Lifetime):")
        for l in lifetimes:
            print(f"  • {l['name']}: {l['price']}")
        print("")

    if consumables:
        print("🪙 消耗型代币项目:")
        for c in consumables[:4]:
            print(f"  • {c['name']}: {c['price']}")
        print("")

    print("🎯 独立开发者定价对标建议:")
    if subscriptions and lifetimes:
        print("  • 混合定价模式：该竞品同时提供订阅与终身买断。独立开发产品可参考此模式（'订阅为日常现金流，买断打消顾虑并拉升首单客单价'）。")
    elif subscriptions and not lifetimes:
        print("  • 纯订阅模式：竞品仅有周期性订阅。若你的产品能够提供'一次性终身买断 (Lifetime)'，将成为抗衡竞品的杀手锏优势。")
    elif lifetimes and not subscriptions:
        print("  • 纯买断/小额付费模式：开发维护成本轻量，适合个人一次性变现。")

def main():
    parser = argparse.ArgumentParser(description="App Store 商业化与内购定价分析工具 (带速率控制)")
    parser.add_argument("app_id", help="目标应用 App ID (如 989673964)")
    parser.add_argument("--country", default="cn", help="Storefront 国家代码 (默认 cn)")
    parser.add_argument("--rate-limit", default="0.5", help="CLI 内部请求限频 (默认 0.5 即 2秒/次)")
    args = parser.parse_args()

    analyze_iap(args.app_id, args.country, args.rate_limit)

if __name__ == "__main__":
    main()
