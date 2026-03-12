import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings


def _get_unique_filename(dest_dir: Path, original_name: str) -> str:
    """
    获取唯一文件名，保留原始文件名
    如果文件已存在，则添加时间戳后缀
    
    Args:
        dest_dir: 目标目录
        original_name: 原始文件名
        
    Returns:
        str: 唯一的文件名
    """
    if not original_name:
        # 如果没有原始文件名，使用 UUID
        return f"{uuid4().hex}.docx"
    
    target = dest_dir / original_name
    if not target.exists():
        return original_name
    
    # 文件已存在，添加时间戳
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix or ".docx"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{stem}_{timestamp}{suffix}"


async def save_upload_file(upload_file: UploadFile, year: int, month: int) -> str:
    """
    保存上传的文件，保留原始文件名
    
    Args:
        upload_file: 上传的文件
        year: 年份
        month: 月份
        
    Returns:
        str: 相对文件路径（相对于 data_dir）
    """
    # 创建目录结构: reports/年份/月份/
    dest_dir = settings.data_dir / "reports" / str(year) / f"{month:02d}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # 保留原始文件名，必要时添加时间戳避免冲突
    original_name = upload_file.filename or ""
    unique_name = _get_unique_filename(dest_dir, original_name)
    target = dest_dir / unique_name
    
    # 保存文件
    with target.open("wb") as buffer:
        content = await upload_file.read()
        buffer.write(content)
    
    # 返回相对路径
    relative_path = f"reports/{year}/{month:02d}/{unique_name}"
    return relative_path
