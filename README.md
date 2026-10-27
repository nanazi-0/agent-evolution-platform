# Agent Evolution Platform

一个可运行、厂商中立的受治理 RSI（Recursive Self-Improvement）闭环。系统从评测失败中提出候选修改，在隔离工作区中验证 Prompt、Skill、记忆规则或 Agent Harness，只有独立留出评测、安全策略和外部质量门禁全部通过后才允许进入人工审批；所有代际、证据、晋升和回滚均可审计。

## 实现边界

本项目以 L5 为方向，但采用分层证据而不是营销标签。默认可运行部分实现当前可工程化的 **bounded RSI / harness evolution**，并提供后继模型训练适配器：

- 持久修改 Prompt、Skill、记忆规则和声明式工作流；
- 根据失败反馈生成下一代候选；
- 根据历代候选的增益和失败更新“改进器策略”，让改进方法本身参与递归学习；
- 候选之间具有父子谱系；
- 使用候选不可见的留出集评测；
- 将优胜候选提交给独立的 `agent-quality-security` 控制面；
- 默认要求具名人工批准；
- 支持非破坏性回滚和哈希审计链。
- 可调用隔离的训练、蒸馏或合成数据流水线产生后继模型，并要求至少两个留出领域的能力提升证据。

当后继模型、多领域留出集、递归改进器、外部安全门禁和自主研究闭环同时通过时，系统会标记为“bounded L5-oriented experiment”。这仍不等于已经证明开放式通用 RSI，也不会默认在宿主机执行模型生成的代码或自动修改模型权重。

## 快速开始

```powershell
cd D:\Portfolio\agent-evolution-platform
.\scripts\setup.ps1
.\scripts\demo.ps1
```

演示会运行完整链路，但停在 `eligible`，不会冒充人类自动批准：

```powershell
.\.venv\Scripts\python.exe evolutionctl.py status
.\.venv\Scripts\python.exe evolutionctl.py approve --run-id latest --actor "你的名字" --reason "已审查证据"
.\.venv\Scripts\python.exe evolutionctl.py rollback --actor "你的名字" --reason "回归异常"
.\.venv\Scripts\python.exe evolutionctl.py audit-verify
```

## 使用真实模型提出修改

核心无第三方 Python 依赖。模型调用使用 OpenAI-compatible HTTP 接口：

```powershell
$env:EVOLUTION_API_KEY = "..."
$env:EVOLUTION_BASE_URL = "https://your-provider.example/v1"
$env:EVOLUTION_MODEL = "your-model"
.\.venv\Scripts\python.exe evolutionctl.py run --config configs/llm-example.toml
```

API Key 只从环境变量读取，不写入数据库、报告或候选目录。

## 核心安全边界

```text
可变区：targets/<agent>/baseline 中声明允许的 Prompt / Skill / JSON Harness
不可变区：评测集、治理策略、评估器、审批规则、质量安全控制面
```

候选只写入 `.runtime/candidates/`。批准后生成不可变版本快照和 `releases/current.json` 指针，不覆盖基线。完整设计见 `docs/ARCHITECTURE.md`，真实接入步骤见 `docs/ADOPTION.md`。

## 与现有验收平台的关系

`agent-evolution-platform` 是选手和实验管理员；`agent-quality-security` 是独立裁判。演示将每代优胜者的标准结果信封提交给后者的 `Generic CI` 适配器，并由后者生成证据哈希和审计记录。生产接入时，应把真实目标智能体的全量十大门禁命令配置为外部质量命令，不能仅使用演示评估器。

## 参考实现思想

- Darwin Gödel Machine / HyperAgents：代际谱系和 Harness 自修改；
- Google RRSI：编辑预算、历史约束与留出集防过拟合；
- MLflow/GEPA：评测驱动的 Prompt 优化和版本比较；
- openJiuwen：工程化执行、评测、记忆和安全隔离；
- Microsoft Agentic Innovation：受限、可验证、可逆的修改。

具体链接与采用/未采用范围见 `docs/SOURCES.md`。
