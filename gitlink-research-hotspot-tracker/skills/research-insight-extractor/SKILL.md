---
name: research-insight-extractor
version: 1.0.0
description: "从 GitLink 科研仓库的 commit 历史、README 文档、代码变更中自动提炼研究思路、技术迭代脉络、创新点，辅助科研复盘与新 Idea 生成；支持 OpenClaw、Claude Code、Cursor 等 Agent 自动触发。"
license: MulanPSL-2.0
metadata:
  requires:
    bins_any: ["gitlink-cli"]
    bins_note: "依赖 gitlink-cli 获取 commit 日志、README 内容等，需配置 GITLINK_TOKEN 环境鉴权变量"
  cliHelp: "gitlink-cli repo --help"
  platforms:
    agents:
      - openclaw
      - claude-code
      - cursor
      - generic-agent
    backends:
      - id: gitlink
        cli: gitlink-cli
        url_template: "https://www.gitlink.org.cn/{owner}/{repo}"
        raw_template: "https://www.gitlink.org.cn/{owner}/{repo}/raw/master/{path}"
        api_base: "https://www.gitlink.org.cn/api/v1"
        auth_env: GITLINK_TOKEN
        default: true
---
# research-insight-extractor 科研思路提炼 Skill
## **CRITICAL — 所有仓库查询执行前必须校验 gitlink-cli 鉴权状态，GITLINK_TOKEN 缺失/失效直接终止流程并提示用户配置环境变量。**
## **CRITICAL — 本技能仅读取仓库公开数据（commit 历史、README、文件树），不进行任何写入操作，无需用户确认步骤。**

## 功能概述
本 Skill 为 C1 纯文档模式，Agent 直接按内置流程执行：
1. 解析用户指令，提取仓库 `owner/repo` 及分析范围（如最近 N 次 commit、特定版本区间）；
2. 调用 gitlink-cli 拉取 commit 历史、README 内容、文件树；
3. 使用 AI 语义分析技术，从 commit 消息、文档变更中提取：
   - **研究思路**：项目要解决的科学问题、方法论选择
   - **技术迭代脉络**：关键版本演进、算法替换、架构调整
   - **创新点**：区别于同类工作的新方法、新特性
4. 输出结构化科研洞悉报告，为科研复盘与新 Idea 生成提供直接参考。

## 触发场景
用户输入包含以下关键词/意图时激活：
- “提炼XX仓库的研究思路”
- “分析XX项目的技术迭代脉络”
- “找出XX的创新点”
- “科研复盘XX仓库”
- “从XX仓库生成研究灵感”

## 输入提取规则
从用户语句中拆分仓库标识 `owner/repo`，同时可选提取：
- `--since` 起始日期
- `--until` 结束日期
- `--max-commits` 最大分析提交数（默认 100）

## 内置计算判定规则
1. 技术迭代节点判定：commit 消息包含 replace/migrate/refactor/upgrade 关键词，标记为架构迭代节点；
2. 创新模块判定：commit 消息包含 add/introduce/new/support 关键词，标记为新增创新功能；
3. 实验演进识别：目录树内 experiments/、scripts/、configs/ 文件新增/修改，判定为实验策略调整；
4. 过滤规则：自动忽略仅修改注释、依赖版本、文档排版、测试用例的无科研价值commit；
5. 报告输出规则：至少保留3个以上有效技术迭代节点，不足时在表格备注仓库历史数据有限。

## 执行流程
1. 从用户输入提取 owner、repo、时间范围参数。
2. 依次执行以下命令获取原始数据（若 commit 命令不支持 --since，则先拉取全部最近提交，后续由 Agent 按时间过滤）：
   ```bash
   gitlink-cli repo +readme --owner <owner> --repo <repo>
   gitlink-cli repo +tree --owner <owner> --repo <repo>
   gitlink-cli commit list --repo <owner>/<repo> --format json --limit <max> --since <date> --until <date>
   ```
3. 解析 commit 消息，结合 README 和目录结构，提炼：
    核心研究问题：从 README 标题、描述、commit 中高频词提取。
    技术路线变化：commit 里出现“replace”“migrate”“refactor”“upgrade”等关键词对应的变更。
    创新功能引入：commit 里出现“add”“introduce”“new”“support”等关键词对应的新模块。
    实验策略演进：目录树中 experiments/、scripts/、configs/ 下新增或修改的文件。
4. 生成科研洞悉报告（严格按输出模板）。

## 输出模板
### 项目核心研究问题
[从 README 与高频 commit 主题中总结出 1-2 句话，点明该项目要解决的科学问题]

### 技术迭代脉络
按时间顺序列出关键版本或重要提交节点：

| 时间 | 版本/提交 | 技术变化 | 影响 |
|------|-----------|----------|------|
| YYYY-MM-DD | [commit hash 或 tag] | [简述变更，如“模型从 ResNet 替换为 Transformer”] | [对性能、实验的影响] |
（至少列出 3-5 个关键节点，若数据不足则注明“镜像仓库历史有限”）			

### 核心创新点
[创新点 1]：[简要描述 + 在代码中的体现（文件名或模块）]
[创新点 2]：[例如：提出新的损失函数、引入多模态数据等]
（提取 2-4 个创新点，每个附 evidence）

### 研究思路总结
[用一段话概括该项目的研究范式：从问题定义 → 方法论选择 → 实验验证 → 迭代优化，突出其科研逻辑]

### 新 Idea 启发
基于以上分析，为研究者提供 2-3 个可延伸的研究方向或改进思路：
[例如：将项目中方法应用于另一领域]
[例如：针对已知局限性的改进方案]
[例如：结合其他技术的交叉创新]

## 使用示例
用户：提炼 NSCCN/AlphaFold3 的技术迭代脉络和创新点，分析最近 100 次提交
Agent 行为：
1. 解析 owner=NSCCN, repo=AlphaFold3, max-commits=100
2. 执行命令获取 README、文件树、commit 历史
3. 假设从 commit 中发现：
    早期提交大量引入 Evoformer 模块
    中期 commit 消息“refactor: replace Pairformer with simplified pairformer”
    后期新增“diffusion_head”目录
    README 强调“accurate protein complex prediction”
4. 生成报告：

### 项目核心研究问题
本项目致力于利用深度学习实现高精度的蛋白质及其复合物三维结构预测，核心科学问题是“如何从序列和进化信息中推断三维折叠结构”。

### 技术迭代脉络
| 时间 | 版本/提交 | 技术变化 | 影响 |
|------|-----------|----------|------|
| 2024-05 | a1b2c3d | 引入 AlphaFold2 的 Evoformer 作为初始编码器 | 建立基线 | 
| 2024-11 | e4f5g6h | 将 Pairformer 模块简化为轻量版本 | 推理速度提升 30% |
| 2025-02 | i7j8k9l | 新增 Diffusion Head 用于结构精修 | 复合体预测精度提高 5% |
| 2025-06 | m0n1o2p | 增加多链复合体训练数据支持 | 扩展应用范围 |

### 核心创新点
扩散模型精修：在传统结构预测后增加扩散去噪步骤，显著提高侧链坐标精度（见 diffusion_head/）。
轻量化 Pairformer：通过去除冗余交互路径，在几乎不损失精度的情况下降低显存占用。
多链复合体建模：支持蛋白质-蛋白、蛋白-核酸等复合体一键预测，突破原有单体限制。

### 研究思路总结
该项目遵循“序列特征提取 → 配对表示优化 → 三维结构生成 → 精修”的技术路线，以 AlphaFold2 为基础，重点攻关结构精修与多链泛化，体现了工程优化与科学问题结合的研究范式。

### 新 Idea 启发
将扩散精修模块独立出来，作为后处理插件用于其他结构预测工具（如 RoseTTAFold）。
探索将 ESM 等语言模型嵌入 MSA 构建过程，减少对多序列比对的依赖。
基于多链复合体预测结果，设计界面结合亲和力预测的端到端模型。