# 项目 Codemap 体系

## 设计理念

Story Studio 管理的是"世界"——每个小说项目是一个独立的世界实例。Codemap 体系解决三个问题：

1. **新对话恢复**：打开新对话时，Skill 能瞬间读懂世界的完整状态
2. **项目交接**：任何人都可以拿到项目文件夹，通过 PROJECT_MAP.md 理解并继续
3. **工具互操作**：不同工具（workflow.py / 手动 / AI）操作同一项目时，状态一致

## PROJECT_MAP.md — 项目自描述清单

**定位**：项目根目录的索引文件，Skill 打开项目的第一个读取目标。

**内容设计**：三层信息——元数据（不变）→ 进度（变化）→ 恢复指令（操作）

### 第一层：元数据（创建时确定，基本不变）
- 项目名称、类型、主题、基调、卷数
- 世界观文档路径
- 创建时间和最后修改时间

### 第二层：当前进度（每阶段更新）
- 当前处于哪个 Phase（创世/卷前/场景执行/章节生成/卷末复盘）
- 卷号、章号、场景ID
- 活跃Agent列表、休眠Agent列表
- 待处理P0问题数

### 第三层：快速恢复指令（检查点时更新）
- 从哪个检查点恢复
- 下一个待执行的场景
- 上次中断的位置和原因

## 目录约定

所有项目遵循统一目录结构。Skill 初始化项目时从 `templates/project_structure/` 复制骨架。已有项目的路径偏差记录在 PROJECT_MAP.md 的"自定义路径"节。

## 文件命名约定

| 类别 | 命名规则 | 示例 |
|------|----------|------|
| 卷蓝图 | volume{N}_blueprint.md | volume1_blueprint.md |
| Scene Spec | scene_{ddd}.yaml | scene_001.yaml |
| 场景素材 | scene_{ddd}.md | scene_001.md |
| 章节 | chapter_{ddd}.md | chapter_001.md |
| 评审报告 | chapter_{ddd}_review.md | chapter_001_review.md |
| 入场许可 | {scene_id}_permit.md | scene_001_permit.md |
| 状态检查点 | YYYYMMDD_HHMMSS/ | 20260526_173000/ |
| 角色目录 | characters/{角色名}/ | characters/周远/ |

## 状态机

项目按 Phase 流转，字段 `project_phase` 记录当前位置：

```
INITIALIZED → WORLD_BUILDING → VOLUME_PLANNING → SCENE_EXECUTION → CHAPTER_GENERATION → VOLUME_REVIEW
                                          ↑                                                        │
                                          └────────────────────────────────────────────────────────┘
                                          (下一卷循环)
```

每个 Phase 有进入条件和完成条件，记录在 PROJECT_MAP.md 的"当前Phase"节。
