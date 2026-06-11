#!/usr/bin/env python3
"""
Story Studio MVP 工作流
简化版，使用3个核心Agent验证概念
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MVPSession:
    """
    MVP 会话管理器
    
    核心三人组：
    - 因果律Agent：掌控主线
    - 主角合体Agent：代表所有角色
    - 作家Agent：记录+剪辑+特效
    """
    
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.world_bible: Optional[str] = None
        self.blueprint: Optional[str] = None
        self.characters: Dict[str, str] = {}
        
        self.turns: List[Dict] = []
        self.current_act: int = 0
        
        # 创建子目录
        (self.session_path / "scenes").mkdir(exist_ok=True)
        (self.session_path / "chapters").mkdir(exist_ok=True)
    
    def save_world_bible(self, content: str):
        """保存世界圣经"""
        self.world_bible = content
        path = self.session_path / "world_bible.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    
    def save_blueprint(self, content: str):
        """保存卷蓝图"""
        self.blueprint = content
        path = self.session_path / "volume1_blueprint.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    
    def save_character(self, name: str, profile: str):
        """保存角色档案"""
        self.characters[name] = profile
        path = self.session_path / f"character_{name}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(profile)
        return path
    
    def add_turn(self, context: str, karma_action: str, 
                 character_response: str, writer_output: str):
        """
        添加一个回合
        
        Args:
            context: 当前情境
            karma_action: 因果律的行动（天意/事件）
            character_response: 角色的反应
            writer_output: 作家生成的文本
        """
        turn = {
            "turn_num": len(self.turns) + 1,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "karma_action": karma_action,
            "character_response": character_response,
            "writer_output": writer_output
        }
        
        self.turns.append(turn)
        
        # 保存回合记录
        self._save_turn(turn)
        
        return turn
    
    def _save_turn(self, turn: Dict):
        """保存单个回合"""
        path = self.session_path / "scenes" / f"turn_{turn['turn_num']:03d}.md"
        
        content = f"""# 回合 {turn['turn_num']}
**时间**：{turn['timestamp']}

## 情境
{turn['context']}

## 因果律
{turn['karma_action']}

## 角色反应
{turn['character_response']}

## 作家输出
{turn['writer_output']}
"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def compile_chapter(self, chapter_num: int, turn_range: tuple) -> str:
        """
        编译章节
        
        Args:
            chapter_num: 章节号
            turn_range: (开始回合, 结束回合)
        """
        start, end = turn_range
        selected_turns = self.turns[start-1:end]
        
        # 合并作家输出
        chapter_content = f"# 第{chapter_num}章\n\n"
        
        for turn in selected_turns:
            chapter_content += turn['writer_output'] + "\n\n"
        
        # 保存章节
        path = self.session_path / "chapters" / f"chapter_{chapter_num:02d}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(chapter_content)
        
        return str(path)
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        return {
            "session_path": str(self.session_path),
            "world_bible": self.world_bible is not None,
            "blueprint": self.blueprint is not None,
            "characters": list(self.characters.keys()),
            "total_turns": len(self.turns),
            "current_act": self.current_act
        }
    
    def export_full_story(self) -> str:
        """导出完整故事"""
        # 收集所有章节
        chapters = sorted(
            (self.session_path / "chapters").glob("chapter_*.md")
        )
        
        full_story = f"""# {self.session_path.name}

## 世界设定
{self.world_bible or "（未设置）"}

---

"""
        
        for chapter_file in chapters:
            with open(chapter_file, "r", encoding="utf-8") as f:
                full_story += f.read() + "\n\n---\n\n"
        
        # 保存完整故事
        path = self.session_path / "full_story.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_story)
        
        return str(path)


# 快捷函数，供skill调用
def create_session(project_name: str, base_path: str = "./story_projects") -> MVPSession:
    """创建新会话"""
    session_path = Path(base_path) / project_name
    return MVPSession(str(session_path))


def load_session(project_name: str, base_path: str = "./story_projects") -> Optional[MVPSession]:
    """加载已有会话"""
    session_path = Path(base_path) / project_name
    if not session_path.exists():
        return None
    return MVPSession(str(session_path))


if __name__ == "__main__":
    # 测试代码
    session = create_session("test_project")
    print(f"Created session at: {session.session_path}")
    print(f"Summary: {session.get_session_summary()}")
