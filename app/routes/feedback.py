from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_session
from app.models.feedback import Feedback, FeedbackStatus, FeedbackType
from app.models.user import Role, User

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    """创建反馈请求"""
    feedback_type: str = Field(..., description="反馈类型: bug/feature/question/other")
    title: str = Field(..., min_length=1, max_length=200, description="反馈标题")
    content: str = Field(..., min_length=1, max_length=2000, description="反馈内容")


class FeedbackReply(BaseModel):
    """管理员回复请求"""
    reply: str = Field(..., min_length=1, max_length=1000, description="回复内容")
    status: Optional[str] = Field(None, description="更新状态: pending/processed/archived")


@router.post("")
def create_feedback(
    payload: FeedbackCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    提交意见反馈
    
    所有登录用户都可以提交反馈
    """
    # 验证反馈类型
    try:
        feedback_type = FeedbackType(payload.feedback_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的反馈类型: {payload.feedback_type}，可选: bug/feature/question/other"
        )
    
    feedback = Feedback(
        user_id=current_user.id,
        feedback_type=feedback_type,
        title=payload.title,
        content=payload.content,
        status=FeedbackStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    
    return {
        "success": True,
        "message": "反馈提交成功，感谢您的意见！",
        "data": {
            "id": feedback.id,
            "title": feedback.title,
            "status": feedback.status.value
        }
    }


@router.get("/my/list")
def list_my_feedback(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    查询我提交的反馈列表
    """
    stmt = select(Feedback).where(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc())
    
    feedbacks = session.exec(stmt).all()
    
    return [
        {
            "id": f.id,
            "feedback_type": f.feedback_type.value,
            "title": f.title,
            "content": f.content,
            "status": f.status.value,
            "admin_reply": f.admin_reply,
            "created_at": f.created_at.isoformat(),
            "updated_at": f.updated_at.isoformat()
        }
        for f in feedbacks
    ]


# ==================== 管理员接口 ====================

@router.get("/admin/list")
def admin_list_feedback(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
    status_filter: Optional[str] = None,
) -> List[Dict]:
    """
    查询所有反馈列表（管理员专用）
    
    参数：
    - status_filter: 状态过滤（pending/processed/archived）
    """
    stmt = select(Feedback).order_by(Feedback.created_at.desc())
    
    if status_filter:
        try:
            filter_status = FeedbackStatus(status_filter)
            stmt = stmt.where(Feedback.status == filter_status)
        except ValueError:
            pass  # 忽略无效的状态过滤
    
    feedbacks = session.exec(stmt).all()
    
    result = []
    for f in feedbacks:
        # 获取用户信息
        user = session.get(User, f.user_id)
        result.append({
            "id": f.id,
            "user_id": f.user_id,
            "username": user.username if user else None,
            "real_name": user.real_name if user else None,
            "user_role": user.role.value if user else None,
            "feedback_type": f.feedback_type.value,
            "title": f.title,
            "content": f.content,
            "status": f.status.value,
            "admin_reply": f.admin_reply,
            "created_at": f.created_at.isoformat(),
            "updated_at": f.updated_at.isoformat()
        })
    
    return result


@router.get("/admin/stats")
def admin_feedback_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    获取反馈统计数据（管理员专用）
    """
    all_feedbacks = session.exec(select(Feedback)).all()
    
    total = len(all_feedbacks)
    pending = len([f for f in all_feedbacks if f.status == FeedbackStatus.PENDING])
    processed = len([f for f in all_feedbacks if f.status == FeedbackStatus.PROCESSED])
    archived = len([f for f in all_feedbacks if f.status == FeedbackStatus.ARCHIVED])
    
    # 按类型统计
    by_type = {}
    for f in all_feedbacks:
        type_key = f.feedback_type.value
        by_type[type_key] = by_type.get(type_key, 0) + 1
    
    return {
        "total": total,
        "pending": pending,
        "processed": processed,
        "archived": archived,
        "by_type": by_type
    }


@router.put("/admin/{feedback_id}")
def admin_update_feedback(
    feedback_id: int,
    payload: FeedbackReply,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    回复/更新反馈（管理员专用）
    """
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    # 更新回复
    feedback.admin_reply = payload.reply
    feedback.updated_at = datetime.utcnow()
    
    # 更新状态
    if payload.status:
        try:
            feedback.status = FeedbackStatus(payload.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态: {payload.status}"
            )
    else:
        # 如果没有指定状态，自动设为已处理
        feedback.status = FeedbackStatus.PROCESSED
    
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    
    return {
        "success": True,
        "message": "反馈已回复",
        "data": {
            "id": feedback.id,
            "status": feedback.status.value,
            "admin_reply": feedback.admin_reply
        }
    }


@router.delete("/admin/{feedback_id}")
def admin_delete_feedback(
    feedback_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    删除反馈（管理员专用）
    """
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    session.delete(feedback)
    session.commit()
    
    return {
        "success": True,
        "message": "反馈已删除"
    }







