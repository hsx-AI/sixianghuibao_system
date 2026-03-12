from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Dict, Any

from app.database import get_session
from app.models import User, Role, Report, ReportStatus
from app.services import report_service

router = APIRouter(prefix="/integration", tags=["OA Integration"])

@router.get("/oa/todos", summary="查询OA待办事项")
def get_oa_todos(
    username: str = Query(..., description="OA系统用户名"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    供OA系统调用的接口，查询指定用户的待办事项数量。
    
    返回字段说明：
    - username: 查询的用户名
    - pending_reviews: 待审批数量（针对审核人员）
    - returned_reports: 被退回报告数量（针对提交人员）
    - total: 总待办数量
    """
    # 1. 查找用户
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"用户 {username} 不存在"
        )
    
    pending_reviews = 0
    returned_reports = 0
    
    # 2. 如果是审核人员，查询待审核报告
    # 培养人、组织委员、支部书记、总支书
    if user.role in [Role.PYR, Role.ZZWY, Role.ZBSJ, Role.ZZS]:
        # 使用现有的服务函数查询待审核列表
        # 注意：这里不传时间筛选参数，查询所有待办
        reports = report_service.list_pending_reports_for_reviewer(session, user)
        pending_reviews = len(reports)
        
    # 3. 如果是积极分子，查询被退回的报告
    if user.role == Role.ACTIVIST:
        stmt = select(Report).where(
            Report.user_id == user.id,
            Report.status == ReportStatus.REJECTED
        )
        reports = session.exec(stmt).all()
        returned_reports = len(reports)
        
    return {
        "username": username,
        "pending_reviews": pending_reviews,
        "returned_reports": returned_reports,
        "total": pending_reviews + returned_reports
    }
