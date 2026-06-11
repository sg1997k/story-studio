# Story Studio v2.1

> 多 Agent 小说创作剧组 — 模仿影视剧组工作机制的 AI 小说创作系统

[![Version](https://img.shields.io/badge/version-2.1-blue)](SKILL.md)
[![Darwin Score](https://img.shields.io/badge/darwin_score-88.5%2F100-brightgreen)](SKILL.md)

## 这是什么

Story Studio 是一个 **WorkBuddy Skill**，它将小说创作组织成一个 12 人影视剧组的协作流程。不是"AI 帮你写小说"，而是"AI 扮演一个完整的创作团队"。

### 剧组构成

| 角色 | 职责 |
|------|------|
| 🎬 **总导演** | 场景调度、Scene Spec 生成、节奏控制 |
| 📋 **统筹** | 卷结构规划、角色出场协调、Team 通信 |
| ⚖️ **因果律** | 主线守护、天意干预、偏离检测 |
| 🌍 **世界模型** | 世界观一致性、设定查询（严格只读模式） |
| 👤 **角色导演** | 选角分析、角色需求匹配 |
| ✍️ **人物创作者** | 角色档案生成、背景故事 |
| 🛡️ **现场监理** | 入场许可检查（4 项：出场/世界/状态/锚点） |
| 🎭 **主角 Agent** | 主角自主决策和互动 |
| 👥 **杂鱼 Agent** | NPC 批量处理 |
| 🔍 **审查官** | 三时机检查（回合间/场景结束/章节完成）P0/P1/P2 分级 |
| ✂️ **剪辑** | 场景编译为章节 |
| 🎨 **特效** | 文风润色、节奏调整 |

### 核心机制

- **Scene Spec 驱动** — 每场戏有结构化 YAML 规格（before_state / must_happen / tension_curve / forbidden / anchors）
- **锚点约束系统** — 5 类锚点（时间/地点/知识/物理/禁止）防止角色即兴失控
- **开放世界模式** — 角色自主决策 + 因果律隐性引导
- **Codemap 系统** — PROJECT_MAP.md 自描述项目状态，支持中断恢复
- **Team 并行** — 每个 Agent 独立进程运行，角色真实博弈

## 快速开始

### 安装

将整个 `story-studio/` 文件夹放入 WorkBuddy 的 skills 目录：

```
~/.workbuddy/skills/story-studio/
```

### 启动

```
"启动剧组"                   # 串行模拟模式（快速原型）
"启动剧组 Team模式"          # 完整 12 Agent 并行模式
"恢复《书名》"               # 从 PROJECT_MAP.md 恢复进度
```

详细说明见 [QUICKSTART.md](QUICKSTART.md)。

## 目录结构

```
story-studio/
├── SKILL.md                    # 主 Skill 定义（~900行）
├── QUICKSTART.md               # 快速启动指南
├── README.md                   # 本文件
├── test-prompts.json           # 内置测试 Prompt
├── .gitignore
├── references/
│   ├── agent_prompts/          # 12 个 Agent 的角色 Prompt
│   │   ├── director.md         #   总导演
│   │   ├── karma_engine.md     #   因果律
│   │   ├── world_model.md      #   世界模型
│   │   ├── character_creator.md #  人物创作者
│   │   ├── character_agent.md  #   主角 Agent
│   │   ├── 角色导演.md          #   角色导演
│   │   ├── 现场监理.md          #   现场监理
│   │   ├── 审查官.md            #   审查官
│   │   ├── 杂鱼Agent.md         #   杂鱼 Agent
│   │   ├── 摄影.md              #   摄影
│   │   ├── 剪辑.md              #   剪辑
│   │   └── 特效.md              #   特效
│   ├── anchor_system.md        # 锚点约束系统详解
│   ├── codemap_spec.md         # Codemap 自描述系统
│   ├── review_criteria.md      # 5 角色评审标准
│   ├── team_orchestration.md   # Team 并行编排
│   └── open_world_architecture.md # 开放世界模式架构
├── templates/                  # 项目模板
│   ├── PROJECT_MAP.md          #   Codemap 模板
│   ├── scene_spec.yaml         #   Scene Spec 模板
│   ├── appearance_permit.md    #   入场许可模板
│   ├── character_folder/       #   角色文件夹模板
│   └── project_structure/      #   项目目录模板
└── scripts/                    # Python 辅助脚本
    ├── workflow.py             #   v2.0 完整工作流（StoryStudioV2 类）
    └── mvp_workflow.py         #   MVP 简化版（3 Agent）
```

## Darwin 质量评分

经过 Darwin Skill Optimizer 两轮共 6 次优化：

```
71.3 ──[Pass 1]──→ 81.5 ──[Pass 2]──→ 88.5 / 100
```

| 维度 | 得分 |
|------|------|
| Frontmatter 质量 | 8/10 |
| 工作流清晰度 | 9/10 |
| 边界条件覆盖 | 8.5/10 |
| 检查点设计 | 8/10 |
| 指令具体性 | 8.5/10 |
| 资源整合度 | 8.5/10 |
| 整体架构 | 8.5/10 |
| 实测表现 | 8.5/10 |
| 反例黑名单 | 7/10 |

## 创作理念

> "小说不是被写出来的，是被演出来的。"
> 
> 传统的 AI 写作是"一个人写完全文"。Story Studio 的做法是：先让角色"活过来"，在结构化约束下自主互动，再从互动素材中剪辑成文。
>
> 这更接近真实创作——金庸不会先写好所有对话再让人物出场，他让人物在情境中自己说话。

## 适合谁

- **网文作者** — 超长篇连载的上下文一致性管理
- **创意写作者** — 需要一个"虚拟写作室"来 brainstorm 和推演剧情
- **AI 研究者** — 多 Agent 协作 + 约束系统的参考实现
- **WorkBuddy 用户** — 想看看一个复杂的 Skill 能长什么样

## 许可

MIT License — 随便用，署名 appreciated 但不强制。

---

*Made with ❤️ and a lot of Darwin optimization rounds.*
