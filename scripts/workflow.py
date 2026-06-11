#!/usr/bin/env python3
"""
Story Studio v2.0 核心工作流脚本
完整12 Agent剧组架构，支持超长篇连载
"""

import json
import os
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


# ============================================================
# 数据类
# ============================================================

class CharacterStatus(Enum):
    ACTIVE = "active"      # 在场，可行动
    DORMANT = "dormant"    # 不在场，冻结
    ABSENT = "absent"      # 尚未登场或已退场


class SceneStatus(Enum):
    PLANNING = "planning"       # Spec已生成，等待入场许可
    APPROVED = "approved"       # 入场许可通过，等待开始
    ACTIVE = "active"           # 正在执行
    COMPLETED = "completed"     # 已完成
    REJECTED = "rejected"       # 入场许可被拒
    PAUSED = "paused"           # 暂停


class IssueSeverity(Enum):
    P0 = "P0"  # 硬伤，必须修正，流水线暂停
    P1 = "P1"  # 问题，建议修正
    P2 = "P2"  # 优化，可选


@dataclass
class Anchor:
    """场景锚点"""
    time: str = ""                  # 精确时间
    location: str = ""              # 精确地点
    visible_range: str = ""         # 可见范围
    movable_range: str = ""         # 可移动范围
    time_pressure: str = ""         # 时间紧迫感
    known_info: List[str] = field(default_factory=list)     # 角色知道的事
    unknown_info: List[str] = field(default_factory=list)   # 角色不知道的事
    physical_state: str = ""        # 身体状态
    physical_limits: str = ""       # 能力限制
    forbidden: List[str] = field(default_factory=list)      # 禁止行为


@dataclass
class CharacterState:
    """角色实时状态"""
    name: str
    location: str = ""
    health: str = ""
    emotion: str = ""
    current_goal: str = ""
    carries: List[str] = field(default_factory=list)
    known_info: List[str] = field(default_factory=list)
    last_scene: str = ""
    status: CharacterStatus = CharacterStatus.ABSENT


@dataclass
class SceneSpec:
    """场景规格（YAML驱动）"""
    scene_id: str
    chapter: int
    act: int
    title: str = ""
    summary: str = ""
    before_state: Dict = field(default_factory=dict)
    after_state: Dict = field(default_factory=dict)
    must_happen: List[str] = field(default_factory=list)
    tension_curve: List[Dict] = field(default_factory=list)
    key_scenes: List[str] = field(default_factory=list)
    new_hooks: List[str] = field(default_factory=list)
    forbidden: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    pov: str = ""


@dataclass
class AdmissionPermit:
    """入场许可"""
    scene_id: str
    approved: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class TurnRecord:
    """回合记录"""
    turn_num: int
    character: str
    observation: str = ""
    thought: str = ""
    action: str = ""
    dialogue: str = ""
    goal: str = ""
    timestamp: str = ""


@dataclass
class ReviewResult:
    """评审结果"""
    score: int = 0
    reader_score: int = 0      # 阅读者
    editor_score: int = 0      # 编审
    storyteller_score: int = 0 # 故事家
    literary_score: int = 0    # 文学顾问
    critic_score: int = 0      # 毒舌读者
    p0_issues: List[str] = field(default_factory=list)
    p1_issues: List[str] = field(default_factory=list)
    p2_issues: List[str] = field(default_factory=list)
    passed: bool = False


# ============================================================
# 主控制器
# ============================================================

class ProjectPhase(Enum):
    INITIALIZED = "INITIALIZED"
    WORLD_BUILDING = "WORLD_BUILDING"
    VOLUME_PLANNING = "VOLUME_PLANNING"
    SCENE_EXECUTION = "SCENE_EXECUTION"
    CHAPTER_GENERATION = "CHAPTER_GENERATION"
    VOLUME_REVIEW = "VOLUME_REVIEW"


class StoryStudioV2:
    """Story Studio v2.0 主控制器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.characters: Dict[str, CharacterState] = {}
        self.scenes: List[SceneSpec] = []
        self.current_scene: Optional[SceneSpec] = None
        self.current_scene_turns: List[TurnRecord] = []
        self.checkpoint: Optional[Dict] = None
        self.project_info: Dict = {}
        self.phase: ProjectPhase = ProjectPhase.INITIALIZED

        self._ensure_directories()

        # 尝试加载已有项目
        map_path = self.project_path / "PROJECT_MAP.md"
        if map_path.exists():
            self._load_project_map()

    def _ensure_directories(self):
        """创建项目目录结构"""
        dirs = [
            "volumes", "characters", "NPCs",
            "specs", "scenes", "chapters", "reviews",
            "tracker", "logs", "checkpoints"
        ]
        for d in dirs:
            (self.project_path / d).mkdir(parents=True, exist_ok=True)

    # ---- Phase 1: 创世 ----

    def init_project(self, title: str, genre: str, theme: str,
                     volumes: int, tone: str) -> Dict:
        """初始化项目 + 生成 PROJECT_MAP.md"""
        info = {
            "title": title,
            "genre": genre,
            "theme": theme,
            "total_volumes": volumes,
            "tone": tone,
            "created_at": datetime.now().isoformat(),
            "current_volume": 0,
            "current_chapter": 0,
            "current_scene": "",
            "total_words": 0,
            "status": "initialized"
        }
        self.project_info = info
        self.phase = ProjectPhase.INITIALIZED
        self._save_json("project_info.json", info)

        # 生成 PROJECT_MAP.md
        self._generate_project_map()

        return info

    # ---- Codemap 系统 ----

    def _generate_project_map(self):
        """生成/更新 PROJECT_MAP.md"""
        info = self.project_info

        # Phase 进入条件检查
        phase_checks = {
            "INITIALIZED": (self.project_path / "project_info.json").exists(),
            "WORLD_BUILDING": (self.project_path / "world_bible.md").exists(),
            "VOLUME_PLANNING": any(
                (self.project_path / "volumes").glob("volume*_blueprint.md")
            ),
            "SCENE_EXECUTION": any(
                (self.project_path / "scenes").glob("scene_*.md")
            ),
            "CHAPTER_GENERATION": any(
                (self.project_path / "chapters").glob("chapter_*.md")
            ),
            "VOLUME_REVIEW": False  # 手动标记
        }

        # 角色Agent状态
        char_table = ""
        for name, state in self.characters.items():
            char_table += f"| {name} | {state.status.value} | {state.location or '-'} | {state.last_scene or '-'} |\n"

        # 场景计数
        scene_count = len(list((self.project_path / "scenes").glob("scene_*.md")))
        chapter_count = len(list((self.project_path / "chapters").glob("chapter_*.md")))
        spec_count = len(list((self.project_path / "specs").glob("scene_*.yaml")))

        map_content = f"""# {info.get('title', '未命名')} — PROJECT_MAP

> ⚠️ 此文件是项目的自描述清单。
> Skill 打开项目时首先读取此文件以理解当前状态。
> 每次项目状态变化时更新。不要删除。

---

## 项目元数据

| 字段 | 值 |
|------|-----|
| **书名** | {info.get('title', '未命名')} |
| **类型** | {info.get('genre', '-')} |
| **核心主题** | {info.get('theme', '-')} |
| **卷数** | {info.get('total_volumes', '-')}卷 |
| **基调** | {info.get('tone', '-')} |
| **创建时间** | {info.get('created_at', '-')} |
| **最后更新** | {datetime.now().isoformat()} |
| **项目版本** | v{info.get('version', '1.0')} |

---

## 当前进度

| 字段 | 值 |
|------|-----|
| **Phase** | {self.phase.value} |
| **当前卷** | 第{info.get('current_volume', 0)}卷 |
| **当前场景** | {info.get('current_scene', '-')} |
| **当前章节** | 第{info.get('current_chapter', 0)}章 |
| **场景进度** | {scene_count}场景已完成 / {spec_count}场景已规划 |
| **章节进度** | {chapter_count}章已生成 |

### Phase 进入条件

| Phase | 条件 | 状态 |
|-------|------|------|
| INITIALIZED | project_info.json 存在 | {'✅' if phase_checks['INITIALIZED'] else '❌'} |
| WORLD_BUILDING | world_bible.md 存在 | {'✅' if phase_checks['WORLD_BUILDING'] else '❌'} |
| VOLUME_PLANNING | volume蓝图存在 | {'✅' if phase_checks['VOLUME_PLANNING'] else '❌'} |
| SCENE_EXECUTION | 场景素材存在 | {'✅' if phase_checks['SCENE_EXECUTION'] else '❌'} |
| CHAPTER_GENERATION | 章节存在 | {'✅' if phase_checks['CHAPTER_GENERATION'] else '❌'} |
| VOLUME_REVIEW | 本卷完成 | {'✅' if phase_checks['VOLUME_REVIEW'] else '❌'} |

---

## 目录索引

```
（项目根目录）/
├── PROJECT_MAP.md           ← 本文件
├── project_info.json
├── world_bible.md           {'✅' if phase_checks['WORLD_BUILDING'] else '❌'}
├── volumes/                 （{len(list((self.project_path/'volumes').glob('*.md')))}个蓝图）
├── characters/              （{len(self.characters)}个角色）
├── specs/                   （{spec_count}个Scene Spec）
├── scenes/                  （{scene_count}个场景素材）
├── chapters/                （{chapter_count}个成品章节）
├── reviews/                 
├── tracker/
├── logs/
└── checkpoints/
```

---

## 角色Agent状态

| 角色 | 状态 | 当前位置 | 上次出场 |
|------|------|----------|----------|
{char_table if char_table else '| （尚无角色） | - | - | - |'}

---

## 快速恢复

### 当前 Phase：{self.phase.value}

{self._recovery_instructions()}

### 最近检查点
{self._latest_checkpoint()}

---

*最后更新：{datetime.now().isoformat()}*
"""
        map_path = self.project_path / "PROJECT_MAP.md"
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(map_content)

    def _recovery_instructions(self) -> str:
        """生成快速恢复指令"""
        if self.phase == ProjectPhase.INITIALIZED:
            return "项目刚初始化。开始创世会议——与世界模型一起建立 world_bible.md。"
        elif self.phase == ProjectPhase.WORLD_BUILDING:
            return "世界设定已完成。与因果律开启卷前会议生成 volume{N}_blueprint.md。"
        elif self.phase == ProjectPhase.VOLUME_PLANNING:
            return "蓝图已就绪。角色导演开始选角，总导演生成 Scene Specs。"
        elif self.phase == ProjectPhase.SCENE_EXECUTION:
            sid = self.project_info.get('current_scene', '')
            return f"当前场景：{sid}。读取 spec/{sid}.yaml，加载在场角色 agent.md + state.md，继续回合制互动。"
        elif self.phase == ProjectPhase.CHAPTER_GENERATION:
            return "场景已完成。运行剪辑→特效→审查→评审生成章节。"
        elif self.phase == ProjectPhase.VOLUME_REVIEW:
            return "本卷完成。与因果律进行卷末复盘，创建检查点。"
        return "未知状态，请检查 PROJECT_MAP.md。"

    def _latest_checkpoint(self) -> str:
        """获取最近检查点"""
        cp_dir = self.project_path / "checkpoints"
        if not cp_dir.exists():
            return "无"
        cps = sorted(cp_dir.iterdir(), reverse=True)
        return str(cps[0].name) if cps else "无"

    def _load_project_map(self):
        """从 PROJECT_MAP.md 恢复项目状态"""
        map_path = self.project_path / "PROJECT_MAP.md"
        if not map_path.exists():
            return
        content = map_path.read_text(encoding="utf-8")

        # 尝试读取 project_info.json
        info_path = self.project_path / "project_info.json"
        if info_path.exists():
            with open(info_path, "r", encoding="utf-8") as f:
                self.project_info = json.load(f)

        # 尝试恢复角色状态
        chars_dir = self.project_path / "characters"
        if chars_dir.exists():
            for char_dir in chars_dir.iterdir():
                if char_dir.is_dir() and char_dir.name != "NPCs":
                    state_path = char_dir / "state.md"
                    name = char_dir.name
                    cs = CharacterState(name=name)
                    if state_path.exists():
                        # 简单解析 state.md
                        state_text = state_path.read_text(encoding="utf-8")
                        for line in state_text.split("\n"):
                            if "**当前位置**" in line:
                                cs.location = line.split("：")[-1].strip() if "：" in line else ""
                            if "上次出场" in line:
                                cs.last_scene = line.split("：")[-1].strip() if "：" in line else ""
                    self.characters[name] = cs

        # 推断当前 Phase
        if (self.project_path / "chapters").exists() and any(
            (self.project_path / "chapters").glob("chapter_*.md")
        ):
            self.phase = ProjectPhase.CHAPTER_GENERATION
        elif (self.project_path / "scenes").exists() and any(
            (self.project_path / "scenes").glob("scene_*.md")
        ):
            self.phase = ProjectPhase.SCENE_EXECUTION
        elif (self.project_path / "volumes").exists() and any(
            (self.project_path / "volumes").glob("volume*_blueprint.md")
        ):
            self.phase = ProjectPhase.VOLUME_PLANNING
        elif (self.project_path / "world_bible.md").exists():
            self.phase = ProjectPhase.WORLD_BUILDING
        else:
            self.phase = ProjectPhase.INITIALIZED

    def update_phase(self, new_phase: ProjectPhase):
        """更新项目Phase并同步PROJECT_MAP"""
        self.phase = new_phase
        self._generate_project_map()
        self._log("phase_change", {"new_phase": new_phase.value})

    def create_world_bible(self, content: str, version: str = "1.0"):
        """创建/更新世界圣经"""
        path = self.project_path / "world_bible.md"
        header = f"# {self._get_project_title()} 世界圣经 v{version}\n\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + content)
        self.update_phase(ProjectPhase.WORLD_BUILDING)
        self._log("world_bible_created", {"version": version, "path": str(path)})

    # ---- Phase 2: 卷前筹备 ----

    def save_volume_blueprint(self, volume_num: int, content: str):
        """保存卷蓝图"""
        path = self.project_path / "volumes" / f"volume{volume_num}_blueprint.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.project_info["current_volume"] = volume_num
        self.update_phase(ProjectPhase.VOLUME_PLANNING)

    def register_character(self, name: str) -> Path:
        """注册角色——创建角色文件夹"""
        char_dir = self.project_path / "characters" / name
        char_dir.mkdir(parents=True, exist_ok=True)

        # 创建模板文件
        for fname in ["profile.md", "agent.md", "state.md",
                       "timeline.md", "memories.md"]:
            (char_dir / fname).touch()

        # 初始化状态
        self.characters[name] = CharacterState(
            name=name,
            status=CharacterStatus.ABSENT
        )

        # 更新索引
        self._update_character_index()

        return char_dir

    def _update_character_index(self):
        """更新角色总索引"""
        index_path = self.project_path / "characters" / "INDEX.md"
        lines = ["# 角色索引\n\n"]
        lines.append(f"| 角色 | 状态 | 当前位置 | 上次出场 |\n")
        lines.append(f"|------|------|----------|----------|\n")
        for name, state in self.characters.items():
            lines.append(
                f"| {name} | {state.status.value} | "
                f"{state.location or '-'} | {state.last_scene or '-'} |\n"
            )
        with open(index_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # ---- Phase 3: 场景生成与检查 ----

    def load_scene_spec(self, scene_id: str) -> Optional[SceneSpec]:
        """加载场景Spec"""
        spec_path = self.project_path / "specs" / f"{scene_id}.yaml"
        if not spec_path.exists():
            return None
        with open(spec_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return SceneSpec(
            scene_id=data.get("scene_id", scene_id),
            chapter=data.get("chapter", 0),
            act=data.get("act", 0),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            before_state=data.get("before_state", {}),
            after_state=data.get("after_state", {}),
            must_happen=data.get("must_happen", []),
            tension_curve=data.get("tension_curve", []),
            key_scenes=data.get("key_scenes", []),
            new_hooks=data.get("new_hooks", []),
            forbidden=data.get("forbidden", []),
            characters=data.get("出场角色", []),
            pov=data.get("POV", "")
        )

    def save_scene_spec(self, spec: SceneSpec):
        """保存场景Spec"""
        spec_path = self.project_path / "specs" / f"{spec.scene_id}.yaml"
        data = asdict(spec)
        with open(spec_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def admit_scene(self, spec: SceneSpec) -> AdmissionPermit:
        """
        现场监理：入场许可检查
        返回 AdmissionPermit（通过/拒绝 + 原因）
        """
        issues = []
        checks = {
            "appearance": True,    # 出场许可
            "world_check": True,   # 世界设定
            "state_consistency": True,  # 状态一致
            "anchor_complete": True     # 锚点完整
        }

        # A. 出场许可检查
        for char_name in spec.characters:
            char_state = self.characters.get(char_name)
            if not char_state:
                issues.append(f"角色'{char_name}'未在characters/INDEX.md中注册")
                checks["appearance"] = False
                continue

            # 检查 timeline.md
            timeline_path = self.project_path / "characters" / char_name / "timeline.md"
            if not timeline_path.exists():
                issues.append(f"角色'{char_name}'缺少timeline.md")
                checks["appearance"] = False

        # C. 状态一致性
        for char_name in spec.characters:
            char_state = self.characters.get(char_name)
            if char_state and char_state.last_scene:
                before_loc = char_state.location
                spec_loc = spec.before_state.get("characters", [])
                for c in spec_loc:
                    if c.get("name") == char_name:
                        if c.get("location") != before_loc:
                            issues.append(
                                f"角色'{char_name}'位置不一致："
                                f"上次在'{before_loc}'，本次在'{c.get('location')}'"
                            )
                            checks["state_consistency"] = False

        # D. 锚点完整性（必须有 forbidden）
        if not spec.forbidden:
            issues.append("场景缺少forbidden锚点（禁止行为列表）")
            checks["anchor_complete"] = False

        approved = all(checks.values())

        permit = AdmissionPermit(
            scene_id=spec.scene_id,
            approved=approved,
            checks=checks,
            issues=issues,
            reason="所有检查通过" if approved else "; ".join(issues)
        )

        # 存档
        self._save_permit(permit)

        return permit

    def _save_permit(self, permit: AdmissionPermit):
        """存档入场许可"""
        permit_dir = self.project_path / "logs" / "admission"
        permit_dir.mkdir(exist_ok=True)
        path = permit_dir / f"{permit.scene_id}_permit.md"
        status = "✅ 通过" if permit.approved else "❌ 拒绝"
        content = f"# 入场许可 - {permit.scene_id} - {status}\n\n"
        content += f"**检查项**：\n"
        for check, result in permit.checks.items():
            content += f"- {check}: {'✅' if result else '❌'}\n"
        content += f"\n**原因**：{permit.reason}\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def start_scene(self, spec: SceneSpec) -> Dict:
        """总导演：宣布场景开始"""
        self.current_scene = spec
        self.current_scene_turns = []
        self.project_info["current_scene"] = spec.scene_id
        self.update_phase(ProjectPhase.SCENE_EXECUTION)

        # 激活在场角色
        for char_name in spec.characters:
            if char_name in self.characters:
                self.characters[char_name].status = CharacterStatus.ACTIVE

        # 生成锚点
        anchor = self._generate_anchor(spec)

        return {
            "scene_id": spec.scene_id,
            "title": spec.title,
            "pov": spec.pov,
            "characters": spec.characters,
            "must_happen": spec.must_happen,
            "anchor": asdict(anchor),
            "forbidden": spec.forbidden
        }

    def _generate_anchor(self, spec: SceneSpec) -> Anchor:
        """生成场景锚点"""
        anchor = Anchor()

        # 从 before_state 提取
        bs = spec.before_state
        anchor.time = bs.get("time", "")
        anchor.location = bs.get("scene_location", "")

        # 从角色 state.md 读取
        for char_name in spec.characters:
            char_state = self.characters.get(char_name)
            if char_state:
                anchor.physical_state = char_state.health
                anchor.physical_limits = "正常"
                anchor.known_info = char_state.known_info.copy()
                break  # 先取第一个角色的（后续可细化）

        anchor.forbidden = spec.forbidden.copy()
        anchor.time_pressure = "正常节奏"

        return anchor

    def add_turn(self, character: str, observation: str, thought: str,
                 action: str, dialogue: str, goal: str) -> TurnRecord:
        """记录回合"""
        turn = TurnRecord(
            turn_num=len(self.current_scene_turns) + 1,
            character=character,
            observation=observation,
            thought=thought,
            action=action,
            dialogue=dialogue,
            goal=goal,
            timestamp=datetime.now().isoformat()
        )
        self.current_scene_turns.append(turn)
        self._save_turn(turn)
        return turn

    def _save_turn(self, turn: TurnRecord):
        """保存回合到场景文件"""
        if not self.current_scene:
            return
        scene_path = self.project_path / "scenes" / f"{self.current_scene.scene_id}.md"
        # 首次创建文件头
        if not scene_path.exists():
            header = f"# {self.current_scene.scene_id}：{self.current_scene.title}\n\n"
            header += f"**POV**：{self.current_scene.pov}\n\n---\n\n"
            with open(scene_path, "w", encoding="utf-8") as f:
                f.write(header)

        # 追加回合
        turn_md = f"## 回合 {turn.turn_num} — {turn.character}\n\n"
        turn_md += f"**观察**：{turn.observation}\n\n"
        if turn.thought:
            turn_md += f"**思考**：{turn.thought}\n\n"
        turn_md += f"**行动**：{turn.action}\n\n"
        if turn.dialogue:
            turn_md += f"**对话**：{turn.dialogue}\n\n"
        turn_md += f"**目标**：{turn.goal}\n\n---\n\n"

        with open(scene_path, "a", encoding="utf-8") as f:
            f.write(turn_md)

    def end_scene(self) -> Dict:
        """总导演：场景结束 + 状态更新"""
        if not self.current_scene:
            return {}

        # 更新角色状态
        updates = {}
        after_state = self.current_scene.after_state
        for char_data in after_state.get("characters", []):
            name = char_data.get("name", "")
            if name in self.characters:
                self.characters[name].location = char_data.get("location", "")
                self.characters[name].last_scene = self.current_scene.scene_id
                updates[name] = self.characters[name]
                # 保存 state.md
                self._save_character_state(name)

        # 休眠离场角色
        for char_name in self.characters:
            if char_name not in self.current_scene.characters:
                self.characters[char_name].status = CharacterStatus.DORMANT

        # 更新索引
        self._update_character_index()

        # 更新全局状态
        self._update_global_state()

        # 同步 PROJECT_MAP
        self._generate_project_map()

        result = {
            "scene_id": self.current_scene.scene_id,
            "must_happen_done": True,  # 由AI判断
            "character_updates": {k: asdict(v) for k, v in updates.items()}
        }

        self.current_scene = None
        self.current_scene_turns = []

        return result

    def _save_character_state(self, name: str):
        """保存单个角色状态"""
        state = self.characters.get(name)
        if not state:
            return
        path = self.project_path / "characters" / name / "state.md"
        content = f"""# {name} 实时状态

**最后更新**：{datetime.now().isoformat()}

## 位置
- **当前位置**：{state.location}

## 身体状态
- **健康**：{state.health}

## 情绪
- **当前情绪**：{state.emotion}

## 目标
- **当前目标**：{state.current_goal}

## 持有物品
{chr(10).join(f'- {item}' for item in state.carries) if state.carries else '- 无'}

## 已知信息
{chr(10).join(f'- {info}' for info in state.known_info) if state.known_info else '- 无'}

## 出场记录
- 上次出场：{state.last_scene}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _update_global_state(self):
        """更新全局state.json"""
        state = {
            "last_updated": datetime.now().isoformat(),
            "total_characters": len(self.characters),
            "total_scenes": len(self.scenes),
            "active_characters": [
                name for name, s in self.characters.items()
                if s.status == CharacterStatus.ACTIVE
            ]
        }
        self._save_json("tracker/state.json", state)

    # ---- Phase 4: 章节生成 ----

    def compile_chapter(self, chapter_num: int, scene_ids: List[str]) -> str:
        """剪辑+特效：编译章节"""
        chapter_md = f"# 第{chapter_num}章\n\n"
        for sid in scene_ids:
            scene_path = self.project_path / "scenes" / f"{sid}.md"
            if scene_path.exists():
                chapter_md += scene_path.read_text(encoding="utf-8")
                chapter_md += "\n\n---\n\n"

        chapter_path = self.project_path / "chapters" / f"chapter_{chapter_num:03d}.md"
        with open(chapter_path, "w", encoding="utf-8") as f:
            f.write(chapter_md)

        return str(chapter_path)

    def save_review(self, chapter_num: int, result: ReviewResult):
        """保存评审报告"""
        review_path = self.project_path / "reviews" / f"chapter_{chapter_num:03d}.md"
        status = "✅ 通过" if result.passed else "❌ 未通过"
        content = f"""# 第{chapter_num}章评审报告

## 综合得分：{result.score}/100 — {status}

| 角色 | 得分 |
|------|------|
| 阅读者 | {result.reader_score}/100 |
| 编审 | {result.editor_score}/100 |
| 故事家 | {result.storyteller_score}/100 |
| 文学顾问 | {result.literary_score}/100 |
| 毒舌读者 | {result.critic_score}/100 |

## P0问题（必须改）
{chr(10).join(f'- {i}' for i in result.p0_issues) if result.p0_issues else '无'}

## P1问题（建议改）
{chr(10).join(f'- {i}' for i in result.p1_issues) if result.p1_issues else '无'}

## P2优化（可选）
{chr(10).join(f'- {i}' for i in result.p2_issues) if result.p2_issues else '无'}
"""
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(content)

    # ---- Phase 5: 卷末复盘 ----

    def create_checkpoint(self):
        """创建状态检查点"""
        cp_dir = self.project_path / "checkpoints" / datetime.now().strftime("%Y%m%d_%H%M%S")
        cp_dir.mkdir(parents=True, exist_ok=True)

        # 备份所有角色状态
        chars_dir = cp_dir / "characters"
        chars_dir.mkdir(exist_ok=True)
        for name, state in self.characters.items():
            with open(chars_dir / f"{name}_state.json", "w", encoding="utf-8") as f:
                json.dump(asdict(state), f, ensure_ascii=False, indent=2)

        # 备份全局状态
        self._save_json(str(cp_dir / "global_state.json"), {
            "checkpoint_time": datetime.now().isoformat(),
            "current_scene": self.current_scene.scene_id if self.current_scene else None,
            "total_turns_in_scene": len(self.current_scene_turns)
        })

        self._log("checkpoint_created", {"path": str(cp_dir)})
        return str(cp_dir)

    # ---- 工具方法 ----

    def _save_json(self, rel_path: str, data: Dict):
        """保存JSON文件"""
        path = self.project_path / rel_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_project_title(self) -> str:
        """获取项目标题"""
        info_path = self.project_path / "project_info.json"
        if info_path.exists():
            with open(info_path, "r", encoding="utf-8") as f:
                return json.load(f).get("title", "未命名")
        return "未命名"

    def _log(self, event_type: str, data: Dict):
        """记录事件"""
        log_path = self.project_path / "logs" / "events.jsonl"
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def get_status(self) -> Dict:
        """获取项目状态"""
        return {
            "project_path": str(self.project_path),
            "total_characters": len(self.characters),
            "active_characters": [
                n for n, s in self.characters.items()
                if s.status == CharacterStatus.ACTIVE
            ],
            "current_scene": self.current_scene.scene_id if self.current_scene else None,
            "current_turns": len(self.current_scene_turns),
            "total_scenes": len(list((self.project_path / "scenes").glob("*.md"))),
            "total_chapters": len(list((self.project_path / "chapters").glob("*.md")))
        }


# ============================================================
# 快捷函数
# ============================================================

def create_session(project_name: str, base_path: str = ".") -> StoryStudioV2:
    """创建新项目"""
    session_path = Path(base_path) / project_name
    return StoryStudioV2(str(session_path))


def load_session(project_name: str, base_path: str = ".") -> Optional[StoryStudioV2]:
    """加载已有项目"""
    session_path = Path(base_path) / project_name
    if not session_path.exists():
        return None
    return StoryStudioV2(str(session_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Story Studio v2.0")
    parser.add_argument("--project", "-p", required=True, help="项目路径")
    parser.add_argument("--command", "-c", choices=["init", "status", "checkpoint"],
                       help="命令")
    args = parser.parse_args()

    studio = StoryStudioV2(args.project)

    if args.command == "status":
        import json as j
        print(j.dumps(studio.get_status(), ensure_ascii=False, indent=2))
    elif args.command == "checkpoint":
        cp = studio.create_checkpoint()
        print(f"检查点已创建：{cp}")
