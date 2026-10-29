# Functional Analysis Skill

把系统、微服务或模块的实现整理成可核对、易理解的功能说明文档。

This portable Agent Skill turns source code and supplied design materials into evidence-based functional descriptions. It explains capabilities, triggers, business rules, data/state changes, failure behavior, and integration boundaries in the user's language.

## 能力与文档风格

文档按业务能力组织，先说明职责与范围，再解释功能链路和处理结果。复杂功能展开前置条件、正常步骤、异常分支、数据变化与后续动作；关键结论关联源码证据。技术标识符保持原样，正文使用自然、准确的语言。

Skill 特别区分当前实现、文档意图、推断和未确认行为。不会仅凭方法名判断逻辑删除、凭注解判断跨服务事务，也不会因为没找到消息发送就推断存在 CDC。

适用请求示例：

```text
使用 $functional-analysis 分析 <仓库路径> 中的 <系统/服务/模块>，
生成当前实现的中文功能说明，保存到 <输出目录>。
说明功能入口、业务规则、状态变化、异常分支和系统协作，并提供源码证据。
```

```text
Use $functional-analysis to document the current behavior of <module> in <repository>.
Explain its capabilities, important flows, rules, state changes, errors and dependencies.
Write in English and cite the source evidence. Save the result to <output directory>.
```

输入只有需求或设计资料时，也可以梳理功能描述，但文档会注明它描述的是资料中的意图，尚未核验实现。

## 可移植范围

技能遵循 [Agent Skills specification](https://agentskills.io/specification)：入口为 `SKILL.md`，详细方法、模板和可选脚本随同分发。核心流程不依赖 Codex、Claude、特定操作系统、Python、MCP、网络或付费接口。具备读取资料与写入文档能力的 agent 可以读取入口并按相对链接使用资源。

自动发现路径由各个客户端决定，不能承诺任意 agent 自动加载某个全机目录。支持 Agent Skills 的客户端使用其技能目录；其他 agent 可显式读取 `skills/functional-analysis/SKILL.md`。脚本支持 Windows、macOS、Linux，使用 Python 3.10+ 标准库。

| 使用范围 | 安装位置或方式 |
| --- | --- |
| 当前用户 Codex / generic | `~/.agents/skills/functional-analysis/` |
| 当前用户 Claude Code | `~/.claude/skills/functional-analysis/` |
| 项目协作 | `<project>/.agents/skills/` 或 `<project>/.claude/skills/` |
| 自定义或组织共享目录 | `--dest <技能父目录>`；再由客户端或管理员配置发现路径 |
| 无技能发现机制的 agent | 显式读取 `SKILL.md`，并使同目录资源可访问 |

仓库与发布包不含作者个人用户路径。任何系统用户都可按自己的主目录独立安装；全机所有用户自动可用，需要管理员按客户端的组织级能力或用户部署机制接入，单独复制一个共享文件夹不能实现这一点。不要共享含凭据和会话的整个 agent 主目录。

## 安装

克隆源码仓库，或下载 [GitHub Releases](https://github.com/DreamWalkerJK/functional-analysis-skill/releases) 中的源码包并解压：

```sh
git clone https://github.com/DreamWalkerJK/functional-analysis-skill.git
cd functional-analysis-skill
python scripts/install.py --agent codex
python scripts/install.py --agent codex --apply
python scripts/install.py --agent claude --apply
```

第一条安装命令仅预览；`--apply` 才创建目标。也可安装到项目或共享目录：

```sh
python scripts/install.py --agent generic --scope project --project <project-path> --apply
python scripts/install.py --dest <shared-skills-directory> --apply
```

安装器遇到相同内容会保持原文件及时间戳；遇到冲突、额外文件或已有空目录会停止，不覆盖用户内容。它拒绝源与目标路径组件中的符号链接和 Windows junction。当前版本不自动升级或卸载：保留已有安装并选择新的目标，或核对备份后手动替换。

独立 Skill ZIP 可直接解压，将其中的 `functional-analysis/` 目录复制到客户端技能目录；保留全部相对资源。没有 Python 时使用该方式。新安装将在客户端下一次刷新技能时可用；Codex 中通常在下一轮对话可用。若当前会话没有刷新，显式读取安装目录中的 `SKILL.md` 即可执行。

如使用 Codex 自带的 skill-installer，可指定：

```text
仓库：DreamWalkerJK/functional-analysis-skill
路径：skills/functional-analysis
版本：v0.1.0
```

## 内容布局

```text
skills/functional-analysis/
  SKILL.md                         通用入口与约束
  references/analysis-method.md    调查方法与证据边界
  references/writing-guide.md      技术化、通顺的写作标准
  references/evidence-format.md    可选机器可验的证据格式
  assets/functional-description.md 可调整的中文文档模板
  scripts/verify_evidence.py        可选源码锚点完整性校验
scripts/install.py                 跨平台安装器
scripts/package_release.py         基于 Git 已提交内容打包
```

模板按系统、服务、模块三个粒度调整；输出语言遵循用户请求，无需保留中文标题。证据脚本检查引用文件和行区间是否匹配捕获的哈希，不判断业务解释是否正确，也不代替应用测试。

## 开发、验证与发布

```sh
python -m unittest discover -s tests -v
python scripts/package_release.py
```

发布打包要求工作区干净，只包含 Git 已跟踪并提交的内容。`dist/` 中生成独立 Skill ZIP、源码 ZIP 和 SHA-256 校验清单。CI 在 Windows、macOS、Linux 上运行测试；推送与 `VERSION` 相符的 `v*` 标签后，测试通过才创建 GitHub Release。

私有项目的验证文档应写入用户指定的本地输出目录。公共仓库只收录通用说明、合成样例和不含私有细节的验证方法，不收录私有源码、业务资料、环境配置或凭据。

## License

[MIT](LICENSE)
