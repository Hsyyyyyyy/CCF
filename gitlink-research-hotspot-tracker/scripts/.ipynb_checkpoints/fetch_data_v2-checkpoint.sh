
(base) root@autodl-container-fac242a21a-fa2e640a:~/autodl-tmp/gitlink-research-hotspot-tracker# for repo in "Supercomputing/alphafold" "NSCCN/AlphaFill" "NSCCN/RoseTTAFold" "scnc/openfold"; do
    owner=$(echo $repo | cut -d/ -f1)
    name=$(echo $repo | cut -d/ -f2)
    echo "========== $repo =========="
    echo "--- mirror & counts ---"
    gitlink-cli repo +info --owner $owner --repo $name --format json | grep -E '"mirror"|"issues_count"|"pull_requests_count"|"full_name"'
    echo "--- issues ---"
    gitlink-cli issue +list --owner $owner --repo $name --format json | head -5
    echo "--- prs ---"
    gitlink-cli pr +list --owner $owner --repo $name --format json | head -5
done
========== Supercomputing/alphafold ==========
--- mirror & counts ---
    "full_name": "Supercomputing/alphafold",
    "issues_count": 0,
    "mirror": true,
    "pull_requests_count": 0,
--- issues ---
{
  "ok": true,
  "data": {
    "closed_count": 0,
    "complete_count": null,
--- prs ---
{
  "ok": true,
  "data": {
    "pulls": [],
    "total_count": 0
========== NSCCN/AlphaFill ==========
--- mirror & counts ---
    "full_name": "NSCCN/AlphaFill",
    "issues_count": 0,
    "mirror": true,
    "pull_requests_count": 0,
--- issues ---
{
  "ok": true,
  "data": {
    "closed_count": 0,
    "complete_count": null,
--- prs ---
{
  "ok": true,
  "data": {
    "pulls": [],
    "total_count": 0
========== NSCCN/RoseTTAFold ==========
--- mirror & counts ---
    "full_name": "NSCCN/RoseTTAFold",
    "issues_count": 0,
    "mirror": true,
    "pull_requests_count": 0,
--- issues ---
{
  "ok": true,
  "data": {
    "closed_count": 0,
    "complete_count": null,
--- prs ---
{
  "ok": true,
  "data": {
    "pulls": [],
    "total_count": 0
========== scnc/openfold ==========
--- mirror & counts ---
    "full_name": "scnc/openfold",
    "issues_count": 0,
    "mirror": true,
    "pull_requests_count": 0,
--- issues ---
{
  "ok": true,
  "data": {
    "closed_count": 0,
    "complete_count": null,
--- prs ---
{
  "ok": true,
  "data": {
    "pulls": [],
    "total_count": 0
(base) root@autodl-container-fac242a21a-fa2e640a:~/autodl-tmp/gitlink-research-hotspot-tracker# # 1. 代码统计
gitlink-cli repo +code-stats --owner NSCCN --repo AlphaFold3 --format json

# 2. 贡献者统计
gitlink-cli repo +contributor-stats --owner NSCCN --repo AlphaFold3 --format json

# 3. README 内容
gitlink-cli repo +readme --owner NSCCN --repo AlphaFold3

# 4. 语言统计
gitlink-cli repo +languages --owner NSCCN --repo AlphaFold3 --format json

# 5. 文件树（看目录结构）
gitlink-cli repo +tree --owner NSCCN --repo AlphaFold3 --format json

# 6. 贡献者列表
gitlink-cli repo +contributors --owner NSCCN --repo AlphaFold3 --format json

# 7. 仓库列表（看看NSCCN组织下还有哪些科研仓库）
gitlink-cli repo +list --owner NSCCN --format json | head -20
{
  "ok": true,
  "data": {
    "additions": 83809,
    "author_count": 14,
    "authors": [
      {
        "additions": 79026,
        "author": {
          "email": "augustinzidek@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/A/233_155_153/120.png",
          "login": "Augustin Zidek",
          "name": "Augustin Zidek",
          "type": null
        },
        "commits": 206,
        "deletions": 12252
      },
      {
        "additions": 470,
        "author": {
          "email": "jabramson@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/J/165_135_246/120.png",
          "login": "Josh Abramson",
          "name": "Josh Abramson",
          "type": null
        },
        "commits": 11,
        "deletions": 326
      },
      {
        "additions": 155,
        "author": {
          "email": "jamessspencer@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/J/188_135_35/120.png",
          "login": "James Spencer",
          "name": "James Spencer",
          "type": null
        },
        "commits": 9,
        "deletions": 67
      },
      {
        "additions": 188,
        "author": {
          "email": "jacobjinkelly@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/J/240_72_133/120.png",
          "login": "Jacob Kelly",
          "name": "Jacob Kelly",
          "type": null
        },
        "commits": 7,
        "deletions": 159
      },
      {
        "additions": 3,
        "author": {
          "email": "akvi@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/A/159_195_72/120.png",
          "login": "Akvile Zemgulyte",
          "name": "Akvile Zemgulyte",
          "type": null
        },
        "commits": 2,
        "deletions": 1
      },
      {
        "additions": 5,
        "author": {
          "email": "mlbileschi@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/M/226_116_189/120.png",
          "login": "mlbileschi",
          "name": "mlbileschi",
          "type": null
        },
        "commits": 1,
        "deletions": 4
      },
      {
        "additions": 15,
        "author": {
          "email": "vanderplas@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/J/186_135_57/120.png",
          "login": "Jake VanderPlas",
          "name": "Jake VanderPlas",
          "type": null
        },
        "commits": 1,
        "deletions": 2
      },
      {
        "additions": 34,
        "author": {
          "email": "noreply@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/D/231_155_135/120.png",
          "login": "DeepMind",
          "name": "DeepMind",
          "type": null
        },
        "commits": 1,
        "deletions": 8
      },
      {
        "additions": 1,
        "author": {
          "email": "bchetioui@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/B/130_221_137/120.png",
          "login": "Benjamin Chetioui",
          "name": "Benjamin Chetioui",
          "type": null
        },
        "commits": 1,
        "deletions": 0
      },
      {
        "additions": 10,
        "author": {
          "email": "vwbaker@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/T/187_206_136/120.png",
          "login": "Tori Baker",
          "name": "Tori Baker",
          "type": null
        },
        "commits": 1,
        "deletions": 10
      },
      {
        "additions": 1,
        "author": {
          "email": "aliia@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/A/88_244_199/120.png",
          "login": "Aliia Khasanova",
          "name": "Aliia Khasanova",
          "type": null
        },
        "commits": 1,
        "deletions": 1
      },
      {
        "additions": 72,
        "author": {
          "email": "koretadaniel@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/F/173_120_149/120.png",
          "login": "Foromo Daniel Soromou",
          "name": "Foromo Daniel Soromou",
          "type": null
        },
        "commits": 1,
        "deletions": 6
      },
      {
        "additions": 1,
        "author": {
          "email": "cowie@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/A/127_238_163/120.png",
          "login": "Andrew Cowie",
          "name": "Andrew Cowie",
          "type": null
        },
        "commits": 1,
        "deletions": 1
      },
      {
        "additions": 3828,
        "author": {
          "email": "rpachauri@google.com",
          "id": null,
          "image_url": "system/lets/letter_avatars/2/R/69_222_172/120.png",
          "login": "Ryan Pachauri",
          "name": "Ryan Pachauri",
          "type": null
        },
        "commits": 1,
        "deletions": 3168
      }
    ],
    "change_files": null,
    "commit_count": 244,
    "commit_count_in_all_branches": 246,
    "deletions": 16005
  }
}
[-1] 获取贡献者(代码行)失败！
{
  "ok": true,
  "data": null
}
{
  "ok": true,
  "data": {
    "C++": "14.0%",
    "CMake": "0.2%",
    "Dockerfile": "0.3%",
    "Python": "85.1%",
    "Shell": "0.4%"
  }
}
[-2] 你访问的文件不存在
{
  "ok": true,
  "data": {
    "list": [
      {
        "contribution_perc": "60.59%",
        "contributions": 206,
        "email": "augustinzidek@google.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/A/233_155_153/120.png",
        "login": null,
        "name": "augustin zidek",
        "type": null
      },
      {
        "contribution_perc": "4.71%",
        "contributions": 16,
        "email": "49699333+dependabot[bot]@users.noreply.github.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/D/241_157_191/120.png",
        "login": null,
        "name": "dependabot[bot]",
        "type": null
      },
      {
        "contribution_perc": "3.24%",
        "contributions": 11,
        "email": "jabramson@google.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/J/165_135_246/120.png",
        "login": null,
        "name": "josh abramson",
        "type": null
      },
      {
        "contribution_perc": "2.65%",
        "contributions": 9,
        "email": "jamessspencer@google.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/J/188_135_35/120.png",
        "login": null,
        "name": "james spencer",
        "type": null
      },
      {
        "contribution_perc": "2.06%",
        "contributions": 7,
        "email": "jacobjinkelly@google.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/J/240_72_133/120.png",
        "login": null,
        "name": "jacob kelly",
        "type": null
      },
      {
        "contribution_perc": "1.18%",
        "contributions": 4,
        "email": "ashutoshkumarsingh0x@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/A/142_220_202/120.png",
        "login": null,
        "name": "ashutosh0x",
        "type": null
      },
      {
        "contribution_perc": "1.18%",
        "contributions": 4,
        "email": "rocklover88@proton.me",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/L/180_135_251/120.png",
        "login": null,
        "name": "linchimingrocks",
        "type": null
      },
      {
        "contribution_perc": "1.18%",
        "contributions": 4,
        "email": "pasqmigl97@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/P/59_195_89/120.png",
        "login": null,
        "name": "pasqm",
        "type": null
      },
      {
        "contribution_perc": "0.88%",
        "contributions": 3,
        "email": "ccoulombe@users.noreply.github.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/C/219_200_69/120.png",
        "login": null,
        "name": "charles coulombe",
        "type": null
      },
      {
        "contribution_perc": "0.88%",
        "contributions": 3,
        "email": "j.j.carpenter@bham.ac.uk",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/J/174_177_222/120.png",
        "login": null,
        "name": "james carpenter (advanced research computing)",
        "type": null
      },
      {
        "contribution_perc": "0.88%",
        "contributions": 3,
        "email": "zohaibshahid7035@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/Z/142_125_214/120.png",
        "login": null,
        "name": "zohaib shahid",
        "type": null
      },
      {
        "contribution_perc": "0.88%",
        "contributions": 3,
        "email": "ook077358@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/O/233_192_237/120.png",
        "login": null,
        "name": "ook077358-lab",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "akvi@google.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/A/159_195_72/120.png",
        "login": null,
        "name": "akvile zemgulyte",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "alex.morehead@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/A/220_77_167/120.png",
        "login": null,
        "name": "alex morehead",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "avisinha1711@gmail.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/A/195_119_88/120.png",
        "login": null,
        "name": "avi sinha",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "53904580+dailypartita@users.noreply.github.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/D/169_173_189/120.png",
        "login": null,
        "name": "dp",
        "type": null
      },
      {
        "contribution_perc": "0.88%",
        "contributions": 3,
        "email": "90102437+dibyx@users.noreply.github.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/D/235_202_125/120.png",
        "login": null,
        "name": "debasish",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "o.kenway@ucl.ac.uk",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/D/124_142_87/120.png",
        "login": null,
        "name": "dr owain kenway",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/O/74_243_75/120.png",
        "login": null,
        "name": "ojas shelke",
        "type": null
      },
      {
        "contribution_perc": "0.59%",
        "contributions": 2,
        "email": "48257736+pasqm@users.noreply.github.com",
        "id": null,
        "image_url": "system/lets/letter_avatars/2/P/74_243_75/120.png",
        "login": null,
        "name": "pasquale miglionico",
        "type": null
      }
    ],
    "total_count": 63
  },
  "meta": {
    "total_count": 63
  }
}
{
  "ok": true,
  "data": {
    "projects": [
      {
        "author": {
          "image_url": "system/lets/letter_avatars/2/A/185_229_243/120.png",
          "login": "Arcelyth",
          "name": "Arcelyth",
          "type": "User"
        },
        "category": null,
        "description": "轻量级、高性能的响应式web框架",
        "forked_count": 0,
        "forked_from_project_id": null,
        "full_last_update_time": "2026-07-05T21:40:59.000+08:00",
        "has_dataset": false,
        "id": 1547578,
        "identifier": "aitne",
        "is_public": true,
(base) root@autodl-container-fac242a21a-fa2e640a:~/autodl-tmp/gitlink-research-hotspot-tracker# 