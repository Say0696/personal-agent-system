# Personal Agent System

[![许可证：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![测试](https://img.shields.io/badge/tests-6%20passed-brightgreen.svg)](tests)

一套本地优先、保护隐私的个人 Agent Skill 起始系统。它负责路由项目任务，读取匹配的本地记忆，发现用户自己添加的 Skill，并把经过确认的问题修正沉淀为有作用域的规则，帮助以后类似任务减少重复纠正。

这个仓库有意保持领域无关。公开仓库只提供两个通用核心 Skill；数学、编程、写作、视频、科研或其他领域的 Skill，都由用户在需要时保存在本机。

> English: [README.md](README.md)

## 功能

- 为多步骤项目任务执行轻量预检。
- 从 Codex 主目录和当前项目动态发现 Skill，不写死领域目录。
- 只读取与任务作用域匹配、状态为 `validated` 或 `applied` 的本地记忆。
- 让个人记忆留在公开仓库之外。
- 任务结束后先征得同意，再保存可复用要求。
- 管理记忆候选、验证、应用、回滚、备份和搜索。
- 在 Windows 上安装、更新、回滚和卸载通用核心 Skill。
- 检查暂存区或已跟踪内容中的个人路径、本地记忆、环境文件和常见 Token。

## 架构

```text
用户任务 -> personal-project-router -> 本地记忆和 Skill 发现
                                      -> 用户按需添加的领域 Skill
                                      -> 执行和验收
                                      -> 询问是否保存
                                      -> 本地候选规则
                                      -> 验证 -> 已应用规则
```

核心系统不假设固定领域。只要目录中有 `SKILL.md`，就可以被路由器动态发现。

## Windows 快速开始

在仓库目录的 PowerShell 中运行：

```powershell
python -m pip install -r requirements.txt
.\scripts\install.ps1
python .\scripts\route.py --json "创建一个项目文件"
```

安装器只复制两个通用核心 Skill，并在文件不存在时创建本地记忆：

```text
%CODEX_HOME%\personal-agent-system\memory\rules.yaml
```

已有本地记忆会保留。具体领域 Skill 需要时再在本机添加。

## 运行流程

1. 多步骤任务开始时，宿主支持隐式 Skill 选择就加载总控；`scripts/route.py` 提供确定性的手动入口。
2. 总控检查当前项目、项目规则、Git 状态和本地 Skill 清单。
3. 只读取匹配任务的 `validated` 和 `applied` 本地记忆。
4. 有合适的本地 Skill 就选择；没有时，用户可以搜索 GitHub 或 `skills.sh`，查看实际 `SKILL.md` 后决定是否安装。
5. 在授权范围内执行任务，再做最小而有意义的验收。
6. 汇报时分开说明实时证据、源码检查、旧日志和推测。
7. 如果出现可复用纠正，总控会询问保存范围：仅本次任务、当前项目、同类项目、所有项目或不保存。

Skill 是否自动加载取决于宿主。全局 `AGENTS.md` 会要求 Codex 在项目任务开始时预检；总控不会静默安装、发布或发送外部消息。

## 本地记忆生命周期

个人记录不会进入公开目录。常用命令：

```powershell
python scripts/memory_cli.py add --scope writing --rule "使用指定的写作风格" --evidence "用户确认的偏好"
python scripts/memory_cli.py list --scope writing
python scripts/memory_cli.py search "写作风格"
python scripts/memory_cli.py validate <id> --note "代表性任务通过" --evidence-file .\evidence.txt
python scripts/memory_cli.py apply <id> --owner writing-skill --change-ref "skill:writing-skill@abc123"
python scripts/memory_cli.py rollback <id> --reason "该偏好已经不再适用"
```

规则通过受保护的状态流转：

```text
candidate -> validated -> applied
     |          |           |
  rejected   rejected   superseded / rolled_back
```

验证必须提供非空说明，以及证据文件或 SHA-256 摘要。写入前会备份，并使用原子替换。`export` 需要显式确认，因为导出的记忆可能包含个人偏好。

## 在本机添加领域 Skill

创建一个包含简洁 `SKILL.md` 的本地目录：

```text
%CODEX_HOME%\skills\my-domain-skill\SKILL.md
```

使用 Agent Skills 格式，填写唯一名称和适用场景。个人示例和个人偏好放在本地记忆，不要放进公开 Skill 仓库。路由器在下次预检时会发现它。

## 更新和恢复

```powershell
.\scripts\update.ps1
.\scripts\rollback.ps1
.\scripts\uninstall.ps1
```

更新前会备份已安装的核心 Skill；回滚会恢复最近备份；卸载只移除安装清单中的 Skill，并保留本地记忆。

## 验证和开发

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
.\scripts\check.ps1
```

检查脚本会验证 Skill 结构、编译 Python 脚本、运行测试，并扫描已跟踪内容中的个人数据。`python scripts/privacy_check.py` 检查暂存文件；加上 `--all` 检查所有已跟踪文件。

## 隐私和设计边界

- 公开文件只包含通用流程和空白记忆结构。
- 个人规则、私有项目事实、聊天记录、凭据和本地覆盖配置留在用户自己的 Codex 目录。
- 一次纠正只有在用户确认后才会成为候选规则；不回应不会产生长期记忆。
- 当前用户要求始终优先于旧记忆。采用外部 Skill 前要检查实际内容。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
