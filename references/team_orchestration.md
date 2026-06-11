# Team 编排指南 — Story Studio v2.0

## 概述

本文档描述如何用 WorkBuddy 的 Team 功能真正并行运行 Story Studio 的12个Agent。阅读前提：已读完 SKILL.md 的"Team 并行模式"章节。

---

## 一、Agent清单与初始化参数

每个Agent需要加载的文件：

| Agent | Prompt文件 | 上下文文件 | 模式 |
|-------|-----------|-----------|------|
| 因果律 | references/agent_prompts/karma_engine.md | world_bible.md, volume{N}_blueprint.md, logs/decisions.md | 读写 |
| 世界模型 | references/agent_prompts/world_model.md | world_bible.md | 只读（严格模式） |
| 现场监理 | references/agent_prompts/现场监理.md | characters/*/timeline.md, world_bible.md, 当前Spec | 读写 |
| 总导演 | references/agent_prompts/director.md | 当前Spec, characters/*/state.md, world_bible.md | 读写 |
| 角色导演 | references/agent_prompts/角色导演.md | world_bible.md, volume{N}_blueprint.md | 读写 |
| 人物创作者 | references/agent_prompts/character_creator.md | world_bible.md | 只读 |
| 审查官 | references/agent_prompts/审查官.md | world_bible.md, characters/*/profile.md, chapters/*.md, tracker/*.md | 读写 |
| 摄影 | references/agent_prompts/摄影.md | 当前场景Spec | 只写 |
| 剪辑 | references/agent_prompts/剪辑.md | scenes/（素材） | 读写 |
| 特效 | references/agent_prompts/特效.md | 剪辑输出 | 读写 |
| 主角Agent | characters/{角色名}/agent.md | characters/{角色名}/state.md, characters/{角色名}/memories.md | 只读自己的文件 |

---

## 二、Phase 1：创世（Team模式）

### 创建Team
```
TeamCreate("天宫-剧组")
```

### 启动核心Agent
```
# 因果律 — 创世会议的主持人
因果律: 你是Story Studio的因果律引擎。当前Phase=WORLD_BUILDING。
请与制片人(用户)开"创世会议"，确定：
1. 小说类型 2. 核心主题 3. 规模 4. 基调 5. 一句话卖点
完成后，输出项目大纲。

# 世界模型 — 等待因果律确定框架后建立world_bible
世界模型: 你是世界模型（严格模式）。等待因果律确定大纲后，
与制片人交互建立world_bible.md。只能记录确认的事实，不编造。
```

### 用户与因果律的交互
用户在主对话中直接回复因果律的问题。因果律整理后通知世界模型。

---

## 三、Phase 2：卷前筹备

```
# 因果律 → 卷前会议
因果律: Phase=VOLUME_PLANNING。请与制片人开卷前会议：
1. 本卷核心事件 2. 感情线 3. 终点 4. 特殊要求
确认后生成 volume1_blueprint.md。

# 角色导演 → 选角
角色导演: 读取volume1_blueprint.md，分析角色需求。
需要以下类型角色：[列表]。请人物创作者生成候选。

# 人物创作者 → 生成候选
人物创作者: 收到需求。为以下类型各生成3个候选：
[类型列表]。输出完整7维度档案。

# 角色导演 → 决策
角色导演: 候选已阅。选定以下角色：
[角色A] — 重要角色(Agent) | [角色B] — 重要角色(Agent)
请制片人确认。

# 因果律 → 生成timeline
因果律: 为每个选定角色生成 characters/{角色名}/timeline.md
```

---

## 四、Phase 3：场景执行（核心循环）

### 场景启动消息序列

```
Step 1: 总导演发布Scene Spec
总导演 → broadcast: 
  "Phase=SCENE_EXECUTION。第1卷第1幕。
   场景 scene_001：{标题}
   Spec已保存至 specs/scene_001.yaml
   请现场监理执行入场许可检查。"

Step 2: 现场监理入场许可
现场监理 → 世界模型: 
  "请求核查 scene_001——
   时间：2078.3.15 22:30 → world_bible是否有记录？
   地点：北京海淀区公寓 → §四.1是否有记录？
   道具：干扰器 → 是否有记录？"

世界模型 → 现场监理:
  "核查结果：
   时间 ✅ world_bible §一时间线范围内
   地点 ✅ world_bible §四.1 周远公寓
   道具 ✅ world_bible + characters/周远/state.md"

现场监理 → 总导演:
  "入场许可：通过 ✅
   A.出场许可 ✅ B.世界核查 ✅ C.状态一致 ✅ D.锚点完整 ✅"

Step 3: 总导演宣布场景
总导演 → broadcast:
  "scene_001 开始。在场角色：[周远]。POV：周远。
   
   === 锚点约束 ===
   时间：2078年3月15日 22:30
   地点：北京海淀区公寓
   知识已知：天宫通知已收到、追踪48h内启动
   知识未知：医疗报告被修改、陈念存在
   物理：胰腺癌晚期，不能剧烈运动
   禁止：遇见其他角色、使用暴力、提及'天宫'
   === 回合开始 ==="

总导演 → 周远:
  "周远，场景已开始。请执行回合1。"

Step 4: 角色Agent回合制
周远 → 总导演:
  "回合1 — 观察：茶几上的通知书蓝光渐暗...
   思考：三天了。他们以为我会感激...
   行动：从沙发起身，走向书架，取出金属盒子
   对话：（无）
   目标：检查装备"

审查官 → 总导演:  # 回合间隙检查（静默）
  "回合1间隙检查：✅ OOC检查通过，✅ 无AI味，✅ 知识边界内"

总导演 → 周远:
  "回合1确认。情境更新：金属盒子在茶几上。继续。"

周远 → 总导演:
  "回合2 — ..."

... (继续直到 must_happen 全部达成)

Step 5: 场景结束
总导演 → broadcast:
  "scene_001 结束。must_happen全部达成。
   正在更新角色状态..."

总导演 → 周远/state.md:
  "更新周远state：位置=公寓，情绪=警觉，发现物=医疗报告异常"

总导演 → broadcast:
  "Phase=SCENE_END。摄影请传递素材。"
```

### 角色Agent休眠指令

```
# 场景中只有周远时，陈念处于休眠
总导演 → 陈念:
  shutdown_request: "本场景你不出场。保存当前state后休眠。"

陈念 → 总导演:
  shutdown_response: "已保存。state.md已更新。休眠。"
```

---

## 五、Phase 4：章节生成

```
摄影 → 剪辑:
  "原始素材：scenes/scene_001.md, scene_002.md, scene_003.md
   共10回合，3场戏。请编排为第1章。"

剪辑 → 特效:
  "第1章已编排。chapters/chapter_001_draft.md
   标注：[特效]处需要润色（3处感官描写、1处动词升级）"

特效 → 审查官:
  "第1章特效完成。提交审查。"

审查官 → 总导演:
  "审查完成：P0=0, P1=1, P2=0。评分：88/100。
   建议：保留，等候5角色评审。"

# 5角色评审由主AI执行（或单独Agent）
审查官 → broadcast:
  "第1章评审通过 ✅ 88/100 — 优秀"
```

---

## 六、Team管理

### 创建Team
```
TeamCreate("天宫-剧组")
```
所有Agent的SendMessage通信范围限制在Team内。

### 查看Agent状态
通过TaskList查看各Agent的活跃状态。

### 关闭Team
```
# 卷末复盘完成后
TeamDelete("天宫-剧组")
```
删除前确保所有Agent已完成输出并保存状态。

---

## 七、故障处理

| 情况 | 处理 |
|------|------|
| Agent偏离指令 | 总导演SendMessage提醒。连续3次偏离→通知用户 |
| 角色Agent OOC | 审查官标记→总导演发OOC警告→角色修正或用户裁决 |
| 现场监理拒绝入场 | 总导演修改Spec后重新提交，或通知用户仲裁 |
| 审查官P0>0 | 总导演暂停场景→要求修改→重新提交审查 |
| Agent无响应 | 检查Agent是否休眠。必要时重新启动Agent并加载state |
