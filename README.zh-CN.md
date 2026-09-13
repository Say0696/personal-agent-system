# Personal Agent System

一套面向 Codex 的个人成长型 Skill 系统：每个项目任务先做本地 Skill 检查，再检索对应领域记忆，保护参考文件排版，并把经过验证的问题修正为可复用规则。

## 目录

- `skills/personal-project-router`：任务预检、Skill 搜索、路由、证据和问题回收。
- `skills/personal-memory`：带作用域的记忆，以及 candidate/validated/applied 状态。
- `skills/math-profile`：数学内容的格式和验收规则。
- `skills/document-fidelity`：保持参考文件排版的文档流程。
- `skills/computer-development`：计算机和软件项目流程。
- `references/skill-registry.yaml`：已安装和推荐 Skill 清单。
- `memory/rules.example.yaml`：用户本地规则的空白示例。个人要求不会放进这个公开仓库。
- `scripts/memory_cli.py`：只操作本地记忆的新增、查询和状态更新工具。
- `scripts/privacy_check.py`：发布前检查暂存区是否包含个人内容。
- `scripts/route.py`：只读的任务分类、Skill 和本地记忆路由工具。
- `scripts/install.ps1`、`scripts/update.ps1`、`scripts/uninstall.ps1`：Windows 安装、更新和卸载辅助脚本。
- `scripts/route.py`：只读的项目预检和领域 Skill 路由器。
- `scripts/install.ps1` / `update.ps1` / `uninstall.ps1`：安装、更新和移除 Skill；更新前会备份已有 Skill。

## 安装和路由

在 PowerShell 中运行（仓库目录内）：

```powershell
.\scripts\install.ps1
python .\scripts\route.py "创建一份数学练习题"
python .\scripts\route.py --json "修复代码并运行测试"
```

安装器只复制通用 Skill，并在 `$CODEX_HOME/personal-agent-system/memory/rules.yaml` 创建本地空白记忆；已有记忆不会覆盖。`route.py` 是只读预检，不会自动安装、修改记忆或发布外部内容。更新使用 `update.ps1`，它会先备份已安装的 Skill；`uninstall.ps1` 只移除清单中的 Skill，并保留个人记忆。

## 成长机制

新经验先记录为 `candidate`；经过代表性任务或专项检查后才变为 `validated`；只有明确写入一个长期负责人后才变为 `applied`。每条记录保留适用范围、证据、示例、验证时间和回滚方式。

公开仓库只提供空白结构。用户自己的数学、计算机、文档等要求保存在本机的被忽略文件中，不会自动上传到 GitHub。

规则冲突时按“当前请求 > 系统和开发者指令 > 项目规则 > 本地已验证记忆 > 通用 Skill”处理。每次规则发生变化，都应保留一个最小回归检查，确认新规则确实生效。

运行本地脚本前安装依赖：`python -m pip install -r requirements.txt`；运行测试则安装 `requirements-dev.txt`。

## 核心原则

- 先查本地 Skill；本地没有合适的再搜索 GitHub/skills.sh。
- 推荐外部 Skill 前检查来源、口碑、许可证、更新时间和实际说明文件。
- 不捏造缺失要求；证据不足时询问或明确标记不确定。
- 参考文件的排版默认是约束；先分析再修改，除非用户要求重新设计。
- 数学产物使用真正的数学排版，例如用 `\\frac{a}{b}` 表示上下分式。
- 汇报时分开说明实时证据、源码检查、旧日志和推测。

## 状态

版本 0.2.0。这是一个有意保持空白的起点。用户的规则只在本机根据真实纠正逐步成长，不会发布到这里。

发布流程和参考的开源项目做法见 [PUBLISHING.md](PUBLISHING.md)。
