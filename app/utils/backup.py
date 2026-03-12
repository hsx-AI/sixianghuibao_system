import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import List

from app.config import settings


def get_backup_dir() -> Path:
    """获取备份目录，如果不存在则创建"""
    backup_dir = settings.data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def clean_old_backups(backup_dir: Path, max_backups: int = 30) -> None:
    """
    清理旧的备份文件，只保留最近的 max_backups 个
    
    Args:
        backup_dir: 备份目录
        max_backups: 保留的最大备份数量
    """
    # 获取所有备份文件，按修改时间排序
    backups: List[Path] = sorted(
        backup_dir.glob("app.db.*.bak"),
        key=os.path.getmtime,
        reverse=True
    )
    
    # 如果备份数量超过限制，删除旧的备份
    if len(backups) > max_backups:
        for backup in backups[max_backups:]:
            try:
                os.remove(backup)
                print(f"已清理旧备份: {backup.name}")
            except OSError as e:
                print(f"清理备份失败 {backup.name}: {e}")


def backup_database() -> None:
    """
    执行数据库备份
    策略：
    1. 每天只备份一次
    2. 保留最近30天的备份
    """
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    if not db_path.exists():
        print("数据库文件不存在，跳过备份")
        return

    backup_dir = get_backup_dir()
    today = datetime.now().strftime("%Y%m%d")
    backup_filename = f"app.db.{today}.bak"
    backup_path = backup_dir / backup_filename

    # 检查今天是否已经备份过
    if backup_path.exists():
        print(f"今日已备份，跳过: {backup_filename}")
        return

    try:
        # 执行备份
        shutil.copy2(db_path, backup_path)
        print(f"数据库备份成功: {backup_path}")
        
        # 清理旧备份
        clean_old_backups(backup_dir)
        
    except Exception as e:
        print(f"数据库备份失败: {e}")