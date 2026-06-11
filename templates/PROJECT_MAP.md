# {项目名称} — PROJECT_MAP

> ⚠️ 此文件是项目的自描述清单。
> Skill 打开项目时首先读取此文件以理解当前状态。
> 每次项目状态变化时更新。不要删除。

---

## 项目元数据

| 字段 | 值 |
|------|-----|
| **书名** | {书名} |
| **类型** | {玄幻/科幻/都市/历史/悬疑/其他} |
| **核心主题** | {一句话} |
| **卷数** | {n}卷 |
| **基调** | {黑暗/温暖/悬疑/热血/黑色幽默/文艺} |
| **创建时间** | {ISO 8601} |
| **最后更新** | {ISO 8601} |
| **项目版本** | v{version} |

---

## 当前进度

| 字段 | 值 |
|------|-----|
| **Phase** | {INITIALIZED / WORLD_BUILDING / VOLUME_PLANNING / SCENE_EXECUTION / CHAPTER_GENERATION / VOLUME_REVIEW} |
| **当前卷** | 第{n}卷 |
| **当前幕** | 第{n}幕 |
| **当前场景** | {scene_id 或 '-'} |
| **当前章节** | 第{n}章 |
| **总字数** | {n}字 |

### Phase 进入条件检查

| Phase | 条件 | 状态 |
|-------|------|------|
| INITIALIZED | project_info.json 存在 | ✅ |
| WORLD_BUILDING | world_bible.md 存在 | {✅/❌} |
| VOLUME_PLANNING | volume{N}_blueprint.md 存在 | {✅/❌} |
| SCENE_EXECUTION | 至少1个 Scene Spec 通过入场许可 | {✅/❌} |
| CHAPTER_GENERATION | 至少1个场景已完成 | {✅/❌} |
| VOLUME_REVIEW | 本卷所有章节已完成 | {✅/❌} |

---

## 目录索引

```
{项目路径}/
├── PROJECT_MAP.md           ← 本文件（自描述清单）
├── project_info.json        ← 项目元数据（JSON）
├── world_bible.md           ← 世界圣经（世界模型维护）
│
├── volumes/                 ← 卷蓝图
│   ├── volume1_blueprint.md
│   └── volume{N}_blueprint.md
│
├── characters/              ← 角色管理
│   ├── INDEX.md             ← 所有角色状态汇总
│   ├── {主角A}/             ← 重要角色（独立Agent）
│   │   ├── profile.md       ←   固定档案（7维度角色卡）
│   │   ├── agent.md         ←   Agent System Prompt
│   │   ├── state.md         ←   实时状态（每场戏后更新）
│   │   ├── timeline.md      ←   出场时间表
│   │   └── memories.md      ←   角色记忆（渐进追加）
│   └── NPCs/                ← 次要角色（批量处理）
│       └── batch.md
│
├── specs/                   ← Scene Spec（YAML）
│   ├── scene_001.yaml
│   └── scene_{ddd}.yaml
│
├── scenes/                  ← 场景原始素材（摄影记录）
│   └── scene_{ddd}.md
│
├── chapters/                ← 成品章节（剪辑+特效后）
│   └── chapter_{ddd}.md
│
├── reviews/                 ← 评审报告
│   └── chapter_{ddd}_review.md
│
├── tracker/                 ← 追踪器
│   ├── state.json           ←   全局进度
│   ├── foreshadowing.md     ←   伏笔埋入/回收
│   ├── conflicts.md         ←   冲突记录
│   └── feedback.md          ←   读者/用户反馈
│
├── logs/                    ← 运行日志
│   ├── events.jsonl         ←   事件流
│   ├── decisions.md         ←   关键决策
│   ├── ooc_warnings.md      ←   OOC警告记录
│   └── admission/           ←   入场许可记录
│       └── {scene_id}_permit.md
│
└── checkpoints/             ← 状态快照（回溯用）
    └── YYYYMMDD_HHMMSS/
        ├── characters/      ←   角色状态快照
        └── global_state.json ←  全局快照
```

### 自定义路径（如有偏离标准目录的，在此记录）

| 内容 | 标准路径 | 实际路径 | 原因 |
|------|----------|----------|------|
| （无偏离） | - | - | - |

---

## Agent 状态

| Agent | 状态 | 备注 |
|-------|------|------|
| 因果律 | {活跃/休眠} | {当前任务或休眠原因} |
| 世界模型 | {活跃/休眠} | |
| 角色导演 | {活跃/休眠} | |
| 人物创作者 | {活跃/休眠} | |
| 现场监理 | {活跃/休眠} | |
| 总导演 | {活跃/休眠} | |
| 审查官 | {活跃/休眠} | |
| 5角色评审团 | {活跃/休眠} | |
| 摄影 | {活跃/休眠} | |
| 剪辑 | {活跃/休眠} | |
| 特效 | {活跃/休眠} | |

### 角色Agent状态

| 角色 | 状态 | 当前位置 | 上次出场 |
|------|------|----------|----------|
| {角色A} | {活跃/休眠/未登场} | {位置} | {场景ID} |
| {角色B} | {活跃/休眠/未登场} | {位置} | {场景ID} |

---

## 待处理清单

### P0 问题（阻塞项）
- [ ] {问题描述}（{来源场景/章节}）

### 待生成 Scene Spec
- [ ] scene_{ddd}：{幕}幕，{简述}

### 待回收伏笔
- [ ] {伏笔内容}（埋于{场景}，预计回收于{场景}）

---

## 快速恢复

### 如果从本次会话中断恢复
```
1. 读取本文件确认当前 Phase 和进度
2. 如果 Phase = SCENE_EXECUTION：
   - 读取当前场景的 Scene Spec
   - 读取在场角色 state.md
   - 加载 world_bible.md 相关章节
   - 加载角色 agent.md
3. 如果 Phase = CHAPTER_GENERATION：
   - 收集待编译的场景ID列表
   - 运行剪辑+特效+评审
4. 最近检查点：{checkpoint_path 或 '无'}
```

### 上次中断原因
{如果中断，记录原因和时间}

---

---

## 维护说明

- **何时更新**：每次 Phase 切换、场景完成、角色状态变化时更新
- **谁更新**：Skill 自动维护（workflow.py 或 AI Agent）
- **不要手动编辑**：除非项目处于离线维护状态

---

*PROJECT_MAP.md — Story Studio v2.0 Codemap System*
