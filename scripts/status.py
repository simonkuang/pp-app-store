#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pp-app-store 运行状态与速率限制 (Rate Limit) 状态检测器
透明提供：当前执行状态、网络连通性、本地 SQLite 缓存规模、最近请求与频控健康度。
支持人类可读表格与 --json 结构化输出。
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

def get_home_dir():
    return Path(os.environ.get("HOME", "~")).expanduser()

def run_cmd(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return p.stdout
    except Exception:
        return None

def get_sqlite_stats(db_path):
    stats = {
        "exists": False,
        "size_kb": 0,
        "tracked_apps": 0,
        "chart_snapshots": 0,
        "stored_reviews": 0,
        "stored_iaps": 0
    }
    if not db_path.exists():
        return stats

    stats["exists"] = True
    stats["size_kb"] = round(db_path.stat().st_size / 1024, 1)

    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        
        c.execute("SELECT COUNT(DISTINCT app_id) FROM app_snapshots")
        stats["tracked_apps"] = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM chart_snapshots")
        stats["chart_snapshots"] = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM reviews")
        stats["stored_reviews"] = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM iap_prices")
        stats["stored_iaps"] = c.fetchone()[0]

        conn.close()
    except Exception:
        pass

    return stats

def parse_iso_time(s):
    try:
        # 兼容带时区 ISO 格式
        return datetime.fromisoformat(s)
    except Exception:
        return None

def check_status(as_json=False):
    home = get_home_dir()
    data_dir = home / ".local/share/app-store-pp-cli"
    state_dir = home / ".local/state/app-store-pp-cli"
    db_path = data_dir / "data.db"
    governor_path = state_dir / "appstore-governor.json"

    # 1. 检查 CLI 连通性与版本
    doctor_out = run_cmd(["app-store-pp-cli", "doctor", "--agent"])
    cli_version = "unknown"
    api_reachable = False
    base_url = "https://itunes.apple.com"

    if doctor_out:
        try:
            doc_data = json.loads(doctor_out)
            res = doc_data.get("results", {})
            cli_version = res.get("version", "unknown")
            api_reachable = (res.get("api") == "reachable")
            base_url = res.get("base_url", base_url)
        except Exception:
            pass

    # 2. 检查 SQLite 本地时序缓存
    db_stats = get_sqlite_stats(db_path)

    # 3. 检查速率限制与请求 Governor
    governor_data = {}
    last_any_str = None
    seconds_since_last_req = None
    rate_limit_health = "🟢 正常空闲 (Idle & Healthy)"
    cooldown_suggested = False

    if governor_path.exists():
        try:
            governor_data = json.loads(governor_path.read_text(encoding="utf-8"))
            last_any_str = governor_data.get("lastAny")
            if last_any_str:
                dt = parse_iso_time(last_any_str)
                if dt:
                    now = datetime.now(dt.tzinfo)
                    diff = (now - dt).total_seconds()
                    seconds_since_last_req = max(0.0, round(diff, 1))
                    if seconds_since_last_req < 2.0:
                        rate_limit_health = f"🟡 刚完成请求 ({seconds_since_last_req}s 前，频控平滑中)"
                        cooldown_suggested = True
                    else:
                        rate_limit_health = f"🟢 正常就绪 (距上次请求 {seconds_since_last_req}s，冷却充分)"
        except Exception:
            pass

    payload = {
        "status": "ok" if api_reachable else "degraded",
        "cli": {
            "name": "app-store-pp-cli",
            "version": cli_version,
            "api_endpoint": base_url,
            "api_reachable": api_reachable
        },
        "rate_limiting": {
            "health": rate_limit_health,
            "in_cooldown": cooldown_suggested,
            "seconds_since_last_request": seconds_since_last_req,
            "last_request_time": last_any_str,
            "safe_threshold": "≤ 20~30 requests/min (min interval: 2.0s)",
            "pacing_mode": "Transparent (Auto Pacing & Backoff handled in scripts)"
        },
        "storage": {
            "sqlite_db": str(db_path),
            "size_kb": db_stats["size_kb"],
            "tracked_apps_count": db_stats["tracked_apps"],
            "chart_snapshots_count": db_stats["chart_snapshots"],
            "stored_reviews_count": db_stats["stored_reviews"],
            "stored_iaps_count": db_stats["stored_iaps"]
        }
    }

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    # 人类可读格式
    print("=======================================================")
    print("🚦 pp-app-store 运行环境与速率状态 (Status)")
    print("=======================================================")
    print(f"• CLI 版本: {cli_version}")
    print(f"• 苹果 API 连通性: {'✅ 畅通 (Reachable)' if api_reachable else '❌ 无法连接'}")
    print(f"• 上游基础地址: {base_url}")
    print("")
    print("⏱️ 速率限制状态 (Rate Limit & Pacing):")
    print(f"• 当前健康度: {rate_limit_health}")
    if seconds_since_last_req is not None:
        print(f"• 距上一次发包: {seconds_since_last_req} 秒前")
    print(f"• 建议安全速率: 单 IP ≤ 20~30次/分 (单次间隔 ≥ 2.0s，脚本已内置无感平滑)")
    print("")
    print("🗄️ 本地 SQLite 缓存状态 (Local Cache):")
    print(f"• 数据库文件: {db_path} ({db_stats['size_kb']} KB)")
    print(f"• 已记录 App 档案: {db_stats['tracked_apps']} 款")
    print(f"• 沉淀榜单快照: {db_stats['chart_snapshots']} 份")
    print(f"• 离线评论缓存: {db_stats['stored_reviews']} 条")
    print(f"• 跟踪内购商品: {db_stats['stored_iaps']} 项")
    print("=======================================================")

def main():
    parser = argparse.ArgumentParser(description="pp-app-store 运行状态与频控检测工具")
    parser.add_argument("--json", action="store_true", help="以结构化 JSON 输出结果")
    args = parser.parse_args()

    check_status(args.json)

if __name__ == "__main__":
    main()
