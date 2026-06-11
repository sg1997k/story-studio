# Story Studio v2.1

> Multi-Agent Novel Writing Studio — AI fiction creation modeled after a real film production crew

[![Version](https://img.shields.io/badge/version-2.1-blue)](SKILL.md)
[![Darwin Score](https://img.shields.io/badge/darwin_score-88.5%2F100-brightgreen)](SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What Is This

Story Studio is a **WorkBuddy Skill** that organizes novel writing as a 12-person film crew's collaborative workflow. It's not "AI writes a novel for you" — it's "AI plays an entire creative team."

### The Crew

| Role | Responsibility |
|------|---------------|
| 🎬 **Director** | Scene orchestration, Scene Spec generation, pacing |
| 📋 **Coordinator** | Volume structure, character appearance coordination, Team comms |
| ⚖️ **Karma Engine** | Main plot guardianship, divine intervention, deviation detection |
| 🌍 **World Model** | Worldbuilding consistency, setting queries (strict read-only mode) |
| 👤 **Character Director** | Casting analysis, character requirement matching |
| ✍️ **Character Creator** | Character profile generation, backstory |
| 🛡️ **Stage Manager** | Admission checkpoint (4 checks: appearance / world / state / anchor) |
| 🎭 **Protagonist Agent** | Autonomous protagonist decisions and interactions |
| 👥 **Extra Agent** | Batch NPC processing |
| 🔍 **Reviewer** | Triple-timing inspection (inter-turn / scene-end / chapter-end) with P0/P1/P2 tiering |
| ✂️ **Editor** | Scene-to-chapter compilation |
| 🎨 **VFX** | Prose polishing, rhythm adjustment |

### Core Mechanisms

- **Scene Spec Driven** — Every scene has a structured YAML spec (before_state / must_happen / tension_curve / forbidden / anchors)
- **Anchor Constraint System** — 5 anchor types (time / location / knowledge / physics / prohibition) preventing character improvisation from going off the rails
- **Open World Mode** — Characters make autonomous decisions with Karma Engine providing subtle guidance
- **Codemap System** — PROJECT_MAP.md as a self-describing project state, enabling interruption recovery
- **Team Parallel Execution** — Each Agent runs as an independent process, enabling true character interactions

## Quick Start

### Installation

Copy the entire `story-studio/` folder into WorkBuddy's skills directory:

```
~/.workbuddy/skills/story-studio/
```

### Launch

```
"Launch the crew"                    # Serial simulation mode (rapid prototyping)
"Launch the crew Team mode"          # Full 12-Agent parallel mode
"Resume <Title>"                     # Recover from PROJECT_MAP.md
```

See [QUICKSTART.md](QUICKSTART.md) (Chinese) for detailed instructions.

## Directory Structure

```
story-studio/
├── SKILL.md                    # Main Skill definition (~900 lines)
├── QUICKSTART.md               # Quick start guide (Chinese)
├── README.md                   # This file (English)
├── README.md                   # Chinese README
├── test-prompts.json           # Built-in test prompts
├── .gitignore
├── references/
│   ├── agent_prompts/          # 12 Agent role prompts
│   │   ├── director.md         #   Director
│   │   ├── karma_engine.md     #   Karma Engine
│   │   ├── world_model.md      #   World Model
│   │   ├── character_creator.md #  Character Creator
│   │   ├── character_agent.md  #   Protagonist Agent
│   │   ├── 角色导演.md          #   Character Director
│   │   ├── 现场监理.md          #   Stage Manager
│   │   ├── 审查官.md            #   Reviewer
│   │   ├── 杂鱼Agent.md         #   Extra Agent
│   │   ├── 摄影.md              #   Cinematographer
│   │   ├── 剪辑.md              #   Editor
│   │   └── 特效.md              #   VFX
│   ├── anchor_system.md        # Anchor constraint system details
│   ├── codemap_spec.md         # Codemap self-describing system
│   ├── review_criteria.md      # 5-role review criteria
│   ├── team_orchestration.md   # Team parallel orchestration
│   └── open_world_architecture.md # Open world mode architecture
├── templates/                  # Project templates
│   ├── PROJECT_MAP.md          #   Codemap template
│   ├── scene_spec.yaml         #   Scene Spec template
│   ├── appearance_permit.md    #   Admission permit template
│   ├── character_folder/       #   Character folder template
│   └── project_structure/      #   Project directory template
└── scripts/                    # Python helper scripts
    ├── workflow.py             #   v2.0 full workflow (StoryStudioV2 class)
    └── mvp_workflow.py         #   MVP simplified version (3 Agents)
```

## Darwin Quality Score

After 2 passes (6 rounds) of Darwin Skill Optimizer:

```
71.3 ──[Pass 1]──→ 81.5 ──[Pass 2]──→ 88.5 / 100
```

| Dimension | Score |
|-----------|-------|
| Frontmatter Quality | 8/10 |
| Workflow Clarity | 9/10 |
| Boundary Coverage | 8.5/10 |
| Checkpoint Design | 8/10 |
| Instruction Specificity | 8.5/10 |
| Resource Integration | 8.5/10 |
| Overall Architecture | 8.5/10 |
| Practical Performance | 8.5/10 |
| Anti-pattern Blacklist | 7/10 |

## Design Philosophy

> "A novel is not written. It is performed."
>
> Traditional AI writing is "one person writes everything." Story Studio's approach: let characters "come alive," interact autonomously within structured constraints, then edit the interaction material into prose.
>
> This is closer to how real creation works — J.K. Rowling didn't script every dialogue before putting Harry in a scene. She let the character speak in the moment.

## Who Is This For

- **Web novel authors** — Context consistency management for ultra-long serials
- **Creative writers** — A "virtual writers' room" for brainstorming and plot simulation
- **AI researchers** — A reference implementation of multi-agent collaboration + constraint systems
- **WorkBuddy users** — Curious about what a complex Skill looks like

## Acknowledgments

This project is deeply influenced by two open-source projects:

### 🧬 [Nuwa · Skill Creation](https://github.com/alchaincyf/nuwa-skill)

Nuwa defined the methodology for "distilling how a person thinks into a runnable cognitive operating system." All 12 Agent role prompts in Story Studio (Director, Karma Engine, World Model, Reviewer, etc.) follow Nuwa's persona skill framework — each agent has independent mental models, decision heuristics, expression DNA, anti-patterns, and honesty boundaries. Without Nuwa, these "living" creative agents wouldn't exist.

> "What you can't write into it — that's your real moat." — Nuwa

### 🔬 [Darwin · Skill Optimizer](https://github.com/alchaincyf/darwin-skill)

Darwin performed 2 passes (6 rounds) of optimization on Story Studio using a 9-dimension rubric, raising the quality score from **71.3 to 88.5** (+24%). Key contributions:
- Structured YAML frontmatter (bilingual triggers)
- 5 critical checkpoints (Genesis confirmation, Volume blueprint, Review failure decisions, etc.)
- 12-tiered anti-pattern blacklist (P0/P1/P2)
- 7 fault recovery scenarios + golden rules
- Complete Scene Spec YAML example

> "If it's not graded, it's not improved." — Darwin

## License

MIT License — use freely, attribution appreciated but not required.

---

*Made with Nuwa's methodology and a lot of Darwin optimization rounds.*
