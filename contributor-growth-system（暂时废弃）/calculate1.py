#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贡献者成长体系 - 核心计算模块（不去重版本）
功能：获取所有状态的 PR 和 Issue，不分页去重，直接累加各状态数据
- PR 状态：open, merged, closed（每个状态分别计数，不合并）
- Issue 状态：open, closed（每个状态分别计数，不合并）
- 关闭者：仅通过 journals 精确获取
- 自动分页拉取全部数据，但不做 ID 去重
"""

import json
import subprocess
import os
from collections import defaultdict
from datetime import datetime

# ============ 配置 ============
TARGET_REPO = "Gitlink/gitlink-cli"
OWNER, REPO_NAME = TARGET_REPO.split("/")
OUTPUT_DIR = "output"

# 每页数量
PAGE_SIZE = 100

# 权重配置
WEIGHT_PR = 10           # 每个 PR 合并
WEIGHT_BUG = 5           # 每个 Bug 修复（额外）
WEIGHT_ISSUE_CREATE = 3  # 创建 Issue
WEIGHT_ISSUE_CLOSE = 5   # 关闭 Issue

# 是否启用 journals 获取实际关闭者
USE_JOURNALS_FOR_CLOSER = True

# ============ 工具函数 ============
def run_cli_command(args):
    """执行 gitlink-cli 命令并返回 JSON 结果"""
    filtered_args = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--owner", "--repo"):
            skip_next = True
            continue
        filtered_args.append(arg)

    full_cmd = ["gitlink-cli", "--owner", OWNER, "--repo", REPO_NAME] + filtered_args

    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
        stdout = result.stdout.strip()
        if not stdout:
            return None
        return json.loads(stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ 命令执行失败: {' '.join(full_cmd)}")
        print(f"   stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️ 返回数据不是有效 JSON: {' '.join(full_cmd)}")
        print(f"   原始输出前200字符: {stdout[:200] if stdout else '(空)'}")
        return None

def extract_list_from_response(raw_data):
    """从响应中提取列表"""
    if not raw_data:
        return []
    if isinstance(raw_data, list):
        return raw_data
    if isinstance(raw_data, dict):
        data_field = raw_data.get("data")
        if isinstance(data_field, dict):
            for key in ["issues", "items", "list", "records", "pulls", "prs"]:
                if key in data_field and isinstance(data_field[key], list):
                    return data_field[key]
        for key in ["issues", "items", "list", "records", "pulls", "prs"]:
            if key in raw_data and isinstance(raw_data[key], list):
                return raw_data[key]
    return []

def extract_user_info(obj):
    """提取用户登录名和显示名"""
    login = None
    name = None
    for key in ["login", "username"]:
        if key in obj and obj[key]:
            login = obj[key]
            break
    for key in ["name", "full_name", "display_name", "nickname"]:
        if key in obj and obj[key]:
            name = obj[key]
            break
    if not login or not name:
        for parent in ["user", "author", "creator", "assignee"]:
            if parent in obj and isinstance(obj[parent], dict):
                sub = obj[parent]
                if not login:
                    for key in ["login", "username"]:
                        if key in sub and sub[key]:
                            login = sub[key]
                            break
                if not name:
                    for key in ["name", "full_name", "display_name", "nickname"]:
                        if key in sub and sub[key]:
                            name = sub[key]
                            break
                if login and name:
                    break
    return login, name

# ============ 数据获取（不去重）============
def fetch_prs():
    """获取所有状态的 PR（open, merged, closed），分页，但不进行去重"""
    print("📥 获取 PR（所有状态：open, merged, closed）- 不去重")
    all_prs = []

    states = ["open", "merged", "closed"]

    for state in states:
        print(f"   → 获取状态: {state}")
        page = 1
        while True:
            raw_data = run_cli_command([
                "pr", "+list",
                "--state", state,
                "--page", str(page),
                "--limit", str(PAGE_SIZE),
                "--format", "json"
            ])
            if not raw_data:
                break

            items = extract_list_from_response(raw_data)
            if not items:
                break

            # 直接添加，不做任何去重
            all_prs.extend(items)

            print(f"      本次获取 {len(items)} 条，累计（含重复） {len(all_prs)} 条")
            if len(items) < PAGE_SIZE:
                break
            page += 1

    print(f"✅ 总共获取 PR 条数（各状态累计，含重复）: {len(all_prs)}")
    return all_prs

def fetch_issue_journals(issue_id):
    """获取单个 Issue 的 journals"""
    data = run_cli_command([
        "issue", "+journals",
        "--id", str(issue_id),
        "--format", "json"
    ])
    if not data:
        return []
    if isinstance(data, dict):
        journals = data.get("data", {}).get("journals")
        if isinstance(journals, list):
            return journals
        journals = data.get("journals")
        if isinstance(journals, list):
            return journals
    elif isinstance(data, list):
        return data
    return []

def get_closer_from_journals(journals):
    """从 journals 中提取关闭者 login"""
    if not journals:
        return None
    sorted_journals = sorted(journals, key=lambda j: j.get("created_unix", 0))
    for journal in sorted_journals:
        status = None
        if "status" in journal:
            status = journal["status"]
        elif "new_status" in journal:
            status = journal["new_status"]
        elif "change" in journal and isinstance(journal["change"], dict):
            change = journal["change"]
            if "status" in change:
                status = change["status"]
            elif "new_status" in change:
                status = change["new_status"]
        if status in ("closed", "close", "1", 1, "已关闭"):
            user = journal.get("user", {})
            if isinstance(user, dict):
                return user.get("login")
            return journal.get("user_login")
    return None

def fetch_issues():
    """获取所有状态的 Issue（open, closed），分页，不去重，补充 _closer（仅对 closed）"""
    print("📥 获取 Issue（所有状态：open, closed）- 不去重")
    all_issues = []

    states = ["open", "closed"]

    for state in states:
        print(f"   → 获取状态: {state}")
        page = 1
        while True:
            raw_data = run_cli_command([
                "issue", "+list",
                "--state", state,
                "--page", str(page),
                "--limit", str(PAGE_SIZE),
                "--format", "json"
            ])
            if not raw_data:
                break

            items = extract_list_from_response(raw_data)
            if not items:
                break

            all_issues.extend(items)

            print(f"      本次获取 {len(items)} 条，累计（含重复） {len(all_issues)} 条")
            if len(items) < PAGE_SIZE:
                break
            page += 1

    print(f"✅ 总共获取 Issue 条数（各状态累计，含重复）: {len(all_issues)}")

    # ---- 通过 journals 获取关闭者（仅对 closed 状态） ----
    if USE_JOURNALS_FOR_CLOSER:
        print("   🔍 正在获取 Issue 操作记录（journals），以确定关闭者...")
        # 注意：一个 Issue 可能在 open 和 closed 状态中都出现，但我们只对状态为 closed 的条目获取关闭者
        # 这里我们遍历所有条目，但只对 state == "closed" 的处理
        closed_items = [i for i in all_issues if i.get("state") == "closed"]
        total = len(closed_items)
        for idx, issue in enumerate(closed_items, 1):
            if idx % 10 == 0 or idx == total:
                print(f"      进度: {idx}/{total}")
            issue_id = issue.get("id")
            if not issue_id:
                continue
            journals = fetch_issue_journals(issue_id)
            closer = get_closer_from_journals(journals)
            if closer:
                issue["_closer"] = closer

    return all_issues

def save_data(prs, issues):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(f"{OUTPUT_DIR}/pr_data.json", "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=2, ensure_ascii=False)
    with open(f"{OUTPUT_DIR}/issue_data.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

# ============ 分数计算 ============
def calculate_scores(prs, issues):
    stats = defaultdict(lambda: {
        "pr_open": 0,
        "pr_merged": 0,
        "pr_closed": 0,
        "bug_fixes": 0,
        "issue_created": 0,
        "issue_closed": 0,
        "issue_open": 0,
        "score": 0
    })
    user_name_map = {}

    def process_user(obj):
        login, name = extract_user_info(obj)
        if login:
            if name:
                user_name_map[login] = name
            else:
                user_name_map.setdefault(login, login)
        return login

    # ---- 1. PR 统计（不去重，每个状态独立计数） ----
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        author_obj = pr.get("issue", {}) or pr
        login = process_user(author_obj)
        if not login:
            continue

        state = pr.get("state", "").lower()
        is_merged = pr.get("merged_at") is not None

        if state == "open":
            stats[login]["pr_open"] += 1
        elif state == "merged" or is_merged:
            stats[login]["pr_merged"] += 1
            title = pr.get("title", "").lower()
            if "fix" in title or "bug" in title:
                stats[login]["bug_fixes"] += 1
        elif state == "closed":
            stats[login]["pr_closed"] += 1
        else:
            # 未知状态，根据 merged_at 判断
            if is_merged:
                stats[login]["pr_merged"] += 1
                title = pr.get("title", "").lower()
                if "fix" in title or "bug" in title:
                    stats[login]["bug_fixes"] += 1
            else:
                stats[login]["pr_closed"] += 1

    # ---- 2. Issue 统计（不去重） ----
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        creator_obj = issue.get("creator", {}) or issue
        login = process_user(creator_obj)
        if login:
            stats[login]["issue_created"] += 1
            if issue.get("state") == "open":
                stats[login]["issue_open"] += 1

        # 关闭者：仅当状态为 closed 且 _closer 存在
        if issue.get("state") == "closed" and USE_JOURNALS_FOR_CLOSER:
            closer_login = issue.get("_closer")
            if closer_login:
                if closer_login not in user_name_map:
                    user_name_map[closer_login] = closer_login
                stats[closer_login]["issue_closed"] += 1

    # ---- 3. 计算总分 ----
    for user, data in stats.items():
        score = (
            data["pr_merged"] * WEIGHT_PR +
            data["bug_fixes"] * WEIGHT_BUG +
            data["issue_created"] * WEIGHT_ISSUE_CREATE +
            data["issue_closed"] * WEIGHT_ISSUE_CLOSE
        )
        data["score"] = int(score)

    return stats, user_name_map

# ============ 报告生成 ============
def generate_report(stats, user_name_map, output_path):
    sorted_users = sorted(stats.items(), key=lambda x: x[1]["score"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 🏆 贡献者成长体系 - 排行榜（不去重版本）\n\n")
        f.write(f"> 📅 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        if USE_JOURNALS_FOR_CLOSER:
            f.write("> 📌 关闭者统计方式：仅基于 journals 操作记录，无降级回退\n\n")
        else:
            f.write("> ⚠️ 关闭者统计已禁用（USE_JOURNALS_FOR_CLOSER = False）\n\n")
        f.write("> ⚠️ 注意：本报告对 PR 和 Issue 的不同状态分别计数，**未进行去重**，因此同一项可能出现在多个状态计数中。\n\n")

        f.write("## 📊 贡献者综合排名（基于 PR 和 Issue）\n\n")
        f.write("| 排名 | 贡献者 | 总分 | 开启PR | 合并PR | 关闭PR(拒绝) | 创建Issue | 关闭Issue |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")

        for idx, (user, data) in enumerate(sorted_users, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
            display_name = user_name_map.get(user, user)
            f.write(
                f"| {medal} | @{display_name} | **{data['score']}** | "
                f"{data['pr_open']} | {data['pr_merged']} | {data['pr_closed']} | "
                f"{data['issue_created']} | {data['issue_closed']} |\n"
            )

        f.write("\n## 📈 分数构成说明\n\n")
        f.write("| 贡献类型 | 权重分 | 说明 |\n")
        f.write("| :--- | :---: | :--- |\n")
        f.write("| 合并 PR | 10分/个 | 成功合并的 Pull Request |\n")
        f.write("| 修复 Bug | +5分/个 | PR 标题含 fix/bug（仅合并的 PR） |\n")
        f.write("| 创建 Issue | 3分/个 | 创建的 Issue（不限状态） |\n")
        f.write("| 关闭 Issue | 5分/个 | 仅当 journals 能确定关闭者时计分 |\n")
        f.write("\n> 🤖 本报告统计了所有状态的 PR 和 Issue，但仅对合并 PR 和关闭 Issue 给予贡献分。由于不去重，同一项可能同时出现在多个状态中，但这不影响总分计算（仅合并PR和关闭Issue计分）。\n")

def generate_badges(stats):
    badges = {}
    for user, data in stats.items():
        score = data["score"]
        if score >= 500:
            badges[user] = "⭐⭐⭐⭐ 核心 (Core)"
        elif score >= 200:
            badges[user] = "⭐⭐⭐ 常客 (Regular)"
        elif score >= 50:
            badges[user] = "⭐⭐ 贡献者 (Contributor)"
        else:
            badges[user] = "⭐ 访客 (Visitor)"
    return badges

def main():
    print("=" * 50)
    print(" 贡献者成长体系 - 不去重版本")
    print("=" * 50)

    prs = fetch_prs()
    issues = fetch_issues()

    print(f"✅ 获取到 PR（含重复）: {len(prs)} 条，Issue（含重复）: {len(issues)} 条")

    save_data(prs, issues)
    print("✅ 原始数据已保存至 output/ 目录")

    stats, user_name_map = calculate_scores(prs, issues)
    print(f"✅ 计算完成，共 {len(stats)} 位贡献者")

    badges = generate_badges(stats)
    print("✅ 等级划分完成")

    output_file = f"{OUTPUT_DIR}/CONTRIBUTORS.md"
    generate_report(stats, user_name_map, output_file)
    print(f"✅ 报告已生成: {output_file}")

    sorted_users = sorted(stats.items(), key=lambda x: x[1]["score"], reverse=True)
    print("\n🏆 Top 5 贡献者:")
    for idx, (user, data) in enumerate(sorted_users[:5], 1):
        display = user_name_map.get(user, user)
        print(f"   {idx}. @{display}: {data['score']} 分 ({badges.get(user, '')})")

    print("=" * 50)
    print("🎉 全部步骤完成！")

if __name__ == "__main__":
    main()