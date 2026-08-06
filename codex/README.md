# Codex 版本

本目录是 8 个 `vedic-*` skill 的 Codex 原生版本（`agents/openai.yaml` 为 Codex 适配元数据）。

## ⚠️ 安装 skill 后必须安装 codex-patch

本目录只有 skill 引擎。Codex 用户装完 `codex/skills/vedic-*` 后，**还必须**安装仓库
根目录的 `codex-patch/` 执行规则补丁（全局路由器 + UC 证据防火墙 + 表达/产物/校准等
按需模块），否则 skill 无法正确联动。

```bash
# 1. 安装 8 个 skill（引擎）
cp -r codex/skills/vedic-* ~/.codex/skills/

# 2. 安装 codex-patch（执行规则，必须！）
cp -r codex-patch/vedic_*.md ~/.codex/
# AGENTS.md 的合并规则见 codex-patch/README.md，不要直接覆盖已有的 ~/.codex/AGENTS.md
```

安装与使用说明：**`codex-patch/README.md`**（仓库根目录）。

> Agent 提示：本仓库同时包含 `claude-code/`、`antigravity/`、`codex/` 三个版本目录。
> 被要求下载 "Codex 版本" 时，应安装 `codex/skills/vedic-*` 全部 8 个 skill，
> **并同步安装 `codex-patch/`**，两者缺一不可。
