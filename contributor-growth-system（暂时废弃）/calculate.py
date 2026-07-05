#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贡献者成长体系 - 核心计算模块
功能：获取数据 → 计算分数 → 生成报告
新增：代码提交维度（基于 repo +contributors）
优化：用户名提取使用显示名称（name），内部用 login 作为键
"""

import json
import subprocess
import os
import re
from collections import defaultdict
from datetime import datetime

# ============ 配置 ============
TARGET_REPO = "Gitlink/gitlink-cli"
OWNER, REPO_NAME = TARGET_REPO.split("/")
OUTPUT_DIR = "output"
PR_LIMIT = 50
ISSUE_LIMIT = 50

# 权重配置（可根据需要调整）
WEIGHT_PR = 10           # 每个 PR 合并
WEIGHT_BUG = 5           # 每个 Bug 修复（额外）
WEIGHT_ISSUE_CREATE = 3  # 创建 Issue
WEIGHT_ISSUE_CLOSE = 5   # 关闭 Issue
WEIGHT_REVIEW = 4        # 每次代码审查
WEIGHT_COMMENT = 0.1     # 每10字评论 = 1分 → 每个字 0.1分
WEIGHT_MENTION = 2       # 被提及
WEIGHT_COMMIT = 1        # ⭐ 新增：每次代码提交

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

def safe_get(data, *keys, default=None):
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

def extract_user_info(obj):
    """
    从对象中提取用户登录名和显示名
    返回: (login, name) 元组，如果都取不到则返回 (None, None)
    """
    login = None
    name = None

    # 尝试直接字段
    for key in ["login", "username"]:
        if key in obj and obj[key]:
            login = obj[key]
            break
    for key in ["name", "full_name", "display_name", "nickname"]:
        if key in obj and obj[key]:
            name = obj[key]
            break

    # 如果直接字段没有，尝试嵌套在 user/author/creator/assignee 中
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

# ============ 数据获取 ============
def fetch_prs():
    """获取已合并的 PR 列表"""
    print("📥 获取已合并的 PR...")
    raw_data = run_cli_command([
        "pr", "+list",
        "--state", "merged",
        "--limit", str(PR_LIMIT),
        "--format", "json"
    ])

    if not raw_data:
        return []

    if isinstance(raw_data, dict):
        data_field = raw_data.get("data")
        if isinstance(data_field, dict):
            for key in ["pulls", "items", "list", "records", "prs"]:
                if key in data_field and isinstance(data_field[key], list):
                    print(f"   [DEBUG] 找到 {len(data_field[key])} 个 PR")
                    return data_field[key]
    return []

def fetch_issues():
    """获取已关闭的 Issue 列表"""
    print("📥 获取已关闭的 Issue...")
    raw_data = run_cli_command([
        "issue", "+list",
        "--state", "closed",
        "--limit", str(ISSUE_LIMIT),
        "--format", "json"
    ])

    if not raw_data:
        return []

    if isinstance(raw_data, dict):
        data_field = raw_data.get("data")
        if isinstance(data_field, dict):
            for key in ["issues", "items", "list", "records"]:
                if key in data_field and isinstance(data_field[key], list):
                    print(f"   [DEBUG] 找到 {len(data_field[key])} 个 Issue")
                    return data_field[key]
    return []

def fetch_reviews(pr_id):
    """获取单个 PR 的 Review 评论"""
    data = run_cli_command([
        "pr", "+reviews",
        "--id", str(pr_id),
        "--format", "json"
    ])
    if isinstance(data, dict):
        data_field = data.get("data")
        if isinstance(data_field, dict):
            for key in ["items", "list", "records", "reviews"]:
                if key in data_field and isinstance(data_field[key], list):
                    return data_field[key]
        elif isinstance(data_field, list):
            return data_field
    return [] if not isinstance(data, list) else data

def fetch_all_reviews(prs):
    """遍历所有 PR，获取 Review 数据"""
    print("📥 获取代码审查数据...")
    all_reviews = []
    if not isinstance(prs, list):
        return []
    total = len(prs)
    for idx, pr in enumerate(prs, 1):
        if not isinstance(pr, dict):
            continue
        pr_id = pr.get("id")
        if not pr_id:
            continue
        if idx % 10 == 0 or idx == total:
            print(f"  进度: {idx}/{total}")
        reviews = fetch_reviews(pr_id)
        if reviews:
            for r in reviews:
                r["pr_id"] = pr_id
            all_reviews.extend(reviews)
    return all_reviews

def fetch_contributors():
    """获取基于提交次数的贡献者数据，返回 {login: {'commits': n, 'name': name}}"""
    print("📥 获取代码提交数据...")
    raw_data = run_cli_command([
        "repo", "+contributors",
        "--format", "json"
    ])

    if not raw_data:
        return {}

    if isinstance(raw_data, dict):
        data_field = raw_data.get("data")
        if isinstance(data_field, dict):
            for key in ["contributors", "items", "list", "records"]:
                if key in data_field and isinstance(data_field[key], list):
                    print(f"   [DEBUG] 找到 {len(data_field[key])} 位贡献者")
                    result = {}
                    for c in data_field[key]:
                        login, name = extract_user_info(c)
                        if not login:
                            continue
                        commits = safe_get(c, "commits", default=0)
                        result[login] = {
                            "commits": commits,
                            "name": name or login  # 如果没 name，用 login 代替
                        }
                    return result
    return {}

def save_data(prs, issues, reviews, contributors):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(f"{OUTPUT_DIR}/pr_data.json", "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=2, ensure_ascii=False)
    with open(f"{OUTPUT_DIR}/issue_data.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    with open(f"{OUTPUT_DIR}/reviews_data.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    with open(f"{OUTPUT_DIR}/contributors_data.json", "w", encoding="utf-8") as f:
        json.dump(contributors, f, indent=2, ensure_ascii=False)

# ============ 分数计算 ============
def extract_mentions(text):
    if not text:
        return []
    pattern = r"@([a-zA-Z0-9_-]+)"
    return re.findall(pattern, text)

def calculate_scores(prs, issues, reviews, contributors):
    stats = defaultdict(lambda: {
        "pr_merged": 0,
        "bug_fixes": 0,
        "issue_created": 0,
        "issue_closed": 0,
        "review_count": 0,
        "review_comments": 0,
        "mentioned": 0,
        "commits": 0,
        "score": 0
    })
    user_name_map = {}

    def process_user(obj):
        """提取 login 和 name，更新映射，返回 login"""
        login, name = extract_user_info(obj)
        if login:
            if name:
                user_name_map[login] = name
            else:
                # 如果没取到 name，先用 login 占位，后续可能被覆盖
                user_name_map.setdefault(login, login)
        return login

    # ---- 1. 代码贡献：PR 合并数 ----
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        # 作者可能在 issue.author 或直接 author
        author_obj = pr.get("issue", {}) or pr
        login = process_user(author_obj)
        if not login:
            continue
        stats[login]["pr_merged"] += 1
        title = pr.get("title", "").lower()
        if "fix" in title or "bug" in title:
            stats[login]["bug_fixes"] += 1

    # ---- 2. 任务协作：Issue 创建与关闭 ----
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        # 创建者
        creator_obj = issue.get("creator", {}) or issue
        login = process_user(creator_obj)
        if login:
            stats[login]["issue_created"] += 1
        # 指派人（关闭者）
        assignee_obj = issue.get("assignee", {})
        login2 = process_user(assignee_obj)
        if login2:
            stats[login2]["issue_closed"] += 1

    # ---- 3. 协作贡献：代码审查 ----
    for review in reviews:
        if not isinstance(review, dict):
            continue
        reviewer_obj = review.get("user", {}) or review
        login = process_user(reviewer_obj)
        if not login:
            continue
        stats[login]["review_count"] += 1
        body = review.get("body", "")
        stats[login]["review_comments"] += len(body.split())

    # ---- 4. 影响力：被提及次数 ----
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        body = issue.get("body", "")
        for m in extract_mentions(body):
            stats[m]["mentioned"] += 1
            # 被提及的用户可能没有 name，先存 login，后面如果有其他数据映射则会覆盖
            if m not in user_name_map:
                user_name_map[m] = m

    # ---- 5. 代码提交次数 ----
    for login, info in contributors.items():
        stats[login]["commits"] = info.get("commits", 0)
        if info.get("name"):
            user_name_map[login] = info["name"]

    # ---- 6. 计算总分 ----
    for user, data in stats.items():
        score = (
            data["pr_merged"] * WEIGHT_PR +
            data["bug_fixes"] * WEIGHT_BUG +
            data["issue_created"] * WEIGHT_ISSUE_CREATE +
            data["issue_closed"] * WEIGHT_ISSUE_CLOSE +
            data["review_count"] * WEIGHT_REVIEW +
            data["review_comments"] * WEIGHT_COMMENT +
            data["mentioned"] * WEIGHT_MENTION +
            data["commits"] * WEIGHT_COMMIT
        )
        data["score"] = int(score)

    return stats, user_name_map

# ============ 报告生成 ============
def generate_report(stats, user_name_map, output_path):
    sorted_users = sorted(stats.items(), key=lambda x: x[1]["score"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 🏆 贡献者成长体系 - 排行榜\n\n")
        f.write(f"> 📅 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 📊 贡献者综合排名\n\n")
        f.write("| 排名 | 贡献者 | 总分 | PR数 | 提交数 | Bug修复 | 创建Issue | 关闭Issue | 审查次数 | 被提及 |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")

        for idx, (user, data) in enumerate(sorted_users, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
            display_name = user_name_map.get(user, user)  # 使用显示名称，若无则用 login
            f.write(
                f"| {medal} | @{display_name} | **{data['score']}** | "
                f"{data['pr_merged']} | {data['commits']} | "
                f"{data['bug_fixes']} | {data['issue_created']} | "
                f"{data['issue_closed']} | {data['review_count']} | "
                f"{data['mentioned']} |\n"
            )

        f.write("\n## 📈 分数构成说明\n\n")
        f.write("| 贡献类型 | 权重分 | 说明 |\n")
        f.write("| :--- | :---: | :--- |\n")
        f.write("| 合并 PR | 10分/个 | 成功合并的 Pull Request |\n")
        f.write("| 提交代码 | 1分/次 | 直接代码提交（Commit） |\n")
        f.write("| 修复 Bug | +5分/个 | PR 标题含 fix/bug |\n")
        f.write("| 创建 Issue | 3分/个 | 创建并关闭的 Issue |\n")
        f.write("| 关闭 Issue | 5分/个 | 作为指派人关闭 Issue |\n")
        f.write("| 代码审查 | 4分/次 | 参与 PR Review |\n")
        f.write("| 评论活跃 | 1分/10字 | Review 评论字数 |\n")
        f.write("| 被提及 | 2分/次 | Issue 中被 @ 提及 |\n")
        f.write("\n> 🤖 本报告由自动化工作流自动生成，数据来源：`gitlink-cli`\n")

# ============ 等级划分 ============
def generate_badges(stats):
    """根据总分自动划分等级"""
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

# ============ 主函数 ============
def main():
    print("=" * 50)
    print(" 贡献者成长体系 - 自动化工作流")
    print("=" * 50)

    prs = fetch_prs()
    issues = fetch_issues()
    reviews = fetch_all_reviews(prs)
    contributors = fetch_contributors()

    print(f"✅ 获取到 PR: {len(prs)} 个，Issue: {len(issues)} 个，Review: {len(reviews)} 条，提交者: {len(contributors)} 位")

    save_data(prs, issues, reviews, contributors)
    print("✅ 原始数据已保存至 output/ 目录")

    stats, user_name_map = calculate_scores(prs, issues, reviews, contributors)
    print(f"✅ 计算完成，共 {len(stats)} 位贡献者")

    badges = generate_badges(stats)
    print("✅ 等级划分完成")

    output_file = f"{OUTPUT_DIR}/CONTRIBUTORS.md"
    generate_report(stats, user_name_map, output_file)
    print(f"✅ 报告已生成: {output_file}")

    # 打印 Top 5
    sorted_users = sorted(stats.items(), key=lambda x: x[1]["score"], reverse=True)
    print("\n🏆 Top 5 贡献者:")
    for idx, (user, data) in enumerate(sorted_users[:5], 1):
        display = user_name_map.get(user, user)
        print(f"   {idx}. @{display}: {data['score']} 分 ({badges.get(user, '')})")

    print("=" * 50)
    print("🎉 全部步骤完成！")

if __name__ == "__main__":
    main()