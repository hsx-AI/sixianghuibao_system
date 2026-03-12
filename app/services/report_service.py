from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.report import CurrentStep, Report, ReportStatus
from app.models.review import Review, ReviewStatus
from app.models.user import Role, User


# 审核流程步骤映射：定义审核流转顺序
# 积极分子 → 培养人 → 组织委员 → 支部书记 → 总支书（不审批，只查看）
WORKFLOW_MAP = {
    CurrentStep.PYR: CurrentStep.ZZWY,
    CurrentStep.ZZWY: CurrentStep.ZBSJ,
    CurrentStep.ZBSJ: CurrentStep.ZZS,  # 支部书记审核后流转到总支书查看
}

# 步骤对应的审核角色
STEP_ROLE_MAP = {
    CurrentStep.PYR: Role.PYR,
    CurrentStep.ZZWY: Role.ZZWY,
    CurrentStep.ZBSJ: Role.ZBSJ,
    CurrentStep.ZZS: Role.ZZS,
}

# 反向映射：用于退回时恢复上一级步骤
REVERSE_WORKFLOW_MAP = {
    CurrentStep.ZZWY: CurrentStep.PYR,
    CurrentStep.ZBSJ: CurrentStep.ZZWY,
    CurrentStep.ZZS: CurrentStep.ZBSJ,
    CurrentStep.PYR: CurrentStep.PYR,  # 培养人是第一步，退回仍为培养人
}


def _normalize_person_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    normalized = name.strip()
    return normalized or None


def _normalize_zhibu(zhibu: Optional[str]) -> Optional[str]:
    if not zhibu:
        return None
    normalized = zhibu.strip()
    return normalized or None


def list_assigned_trainer_names(user: User) -> List[str]:
    names = [_normalize_person_name(user.pyr1), _normalize_person_name(user.pyr2)]
    unique = {name for name in names if name}
    return sorted(unique)


def check_pyr_assignment(session: Session, report: Report, reviewer: User) -> None:
    if report.current_step != CurrentStep.PYR:
        return

    author = session.get(User, report.user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"æäº¤äºº ID {report.user_id} ä¸å­˜åœ¨"
        )

    reviewer_name = _normalize_person_name(reviewer.real_name)
    if not reviewer_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="æ— æ³•è¯†åˆ«å®¡æ ¸äººå§“åï¼Œä¸èƒ½å®¡æ ¸è¯¥æŠ¥å‘Š"
        )

    if reviewer_name not in list_assigned_trainer_names(author):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="è¯¥æ€æƒ³æ±‡æŠ¥æœªåˆ†é…ç»™æ‚¨å®¡æ ¸"
        )


def check_zhibu_scope(session: Session, report: Report, reviewer: User) -> None:
    if reviewer.role not in {Role.ZZWY, Role.ZBSJ}:
        return
    if report.current_step not in {CurrentStep.ZZWY, CurrentStep.ZBSJ}:
        return

    reviewer_zhibu = _normalize_zhibu(reviewer.zhibu)
    if not reviewer_zhibu:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户未设置所属支部，无法审核支部级思想汇报",
        )

    author = report.author or session.get(User, report.user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交人不存在，无法审核此思想汇报",
        )

    author_zhibu = _normalize_zhibu(author.zhibu)
    if not author_zhibu:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="提交人未设置所属支部，无法审核此思想汇报",
        )

    if reviewer_zhibu != author_zhibu:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权审核非本支部思想汇报",
        )


def create_report(
    session: Session,
    user_id: int,
    year: int,
    month: int,
    file_path: str,
    title: Optional[str] = None,
    original_filename: Optional[str] = None
) -> Report:
    """
    创建新的思想汇报
    
    Args:
        session: 数据库会话
        user_id: 提交人ID
        year: 年份
        month: 月份
        file_path: 文件路径
        title: 汇报标题（可选）
        original_filename: 原始文件名（可选，用于下载时显示）
        
    Returns:
        Report: 创建的报告对象
    """
    author = session.get(User, user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"提交人 ID {user_id} 不存在"
        )

    trainer_names = list_assigned_trainer_names(author)
    if not trainer_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未设置培养人（PYR1/PYR2），无法提交思想汇报"
        )

    missing_trainers: List[str] = []
    for trainer_name in trainer_names:
        stmt = select(User.id).where(User.real_name == trainer_name)
        if session.exec(stmt).first() is None:
            missing_trainers.append(trainer_name)
    if missing_trainers:
        missing_str = "，".join(missing_trainers)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"培养人不存在：{missing_str}"
        )

    report = Report(
        user_id=user_id,
        title=title,
        year=year,
        month=month,
        file_path=file_path,
        original_filename=original_filename,
        uploaded_time=datetime.utcnow(),
        current_step=CurrentStep.PYR,  # 初始步骤：培养人审核
        status=ReportStatus.PENDING,
        updated_at=datetime.utcnow()
    )
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return report


def get_report_by_id(session: Session, report_id: int) -> Report:
    """
    根据ID查询报告
    
    Args:
        session: 数据库会话
        report_id: 报告ID
        
    Returns:
        Report: 报告对象
        
    Raises:
        HTTPException: 报告不存在时抛出404
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"报告 ID {report_id} 不存在"
        )
    return report


def check_reviewer_permission(report: Report, reviewer: User) -> None:
    """
    检查审核人是否有权限审核当前步骤
    
    Args:
        report: 报告对象
        reviewer: 审核人对象
        
    Raises:
        HTTPException: 无权限时抛出403
    """
    if report.current_step == CurrentStep.PYR:
        return

    expected_role = STEP_ROLE_MAP.get(report.current_step)
    if reviewer.role != expected_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"当前步骤需要 {expected_role.value} 角色审核，您的角色是 {reviewer.role.value}"
        )


def review_report(
    session: Session,
    report_id: int,
    reviewer_id: int,
    review_status: str,
    comment: Optional[str] = None,
    reject_file_path: Optional[str] = None,
    reject_original_filename: Optional[str] = None
) -> Dict:
    """
    审核思想汇报
    
    审核流程：积极分子 → 培养人 → 组织委员 → 支部书记 → 总支书
    - 通过(approved)：流转到下一步，最后一步则标记为已通过
    - 退回(rejected)：恢复到上一级步骤，状态改为已驳回
    
    Args:
        session: 数据库会话
        report_id: 报告ID
        reviewer_id: 审核人ID
        review_status: 审核状态 ('approved' 或 'rejected')
        comment: 审核意见（可选）
        reject_file_path: 驳回时上传的批注文件路径（可选）
        
    Returns:
        Dict: 包含审核结果的JSON格式数据
        
    Raises:
        HTTPException: 各种业务异常（报告不存在、审核人不存在、无权限等）
    """
    # 1. 验证审核状态参数
    if review_status not in ['approved', 'rejected']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="审核状态必须是 'approved' 或 'rejected'"
        )
    
    # 2. 查询报告和审核人
    report = get_report_by_id(session, report_id)
    reviewer = session.get(User, reviewer_id)
    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"审核人 ID {reviewer_id} 不存在"
        )
    
    # 3. 检查报告是否已经完成审核
    if report.status == ReportStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该报告已经完成全部审核流程"
        )
    
    # 4. 检查审核人权限
    check_reviewer_permission(report, reviewer)
    check_pyr_assignment(session, report, reviewer)
    check_zhibu_scope(session, report, reviewer)

    # 5. 记录当前步骤（用于记录）
    current_step_before_review = report.current_step
    
    # 6. 根据审核结果更新报告状态
    if review_status == 'approved':
        # 检查是否满足流转条件
        should_advance = True
        
        # 特殊处理：培养人审核阶段需要所有分配的培养人一致通过
        if report.current_step == CurrentStep.PYR:
            author = report.author or session.get(User, report.user_id)
            trainer_names = list_assigned_trainer_names(author)
            
            # 获取所有培养人的ID
            required_reviewer_ids = set()
            if trainer_names:
                stmt = select(User.id).where(User.real_name.in_(trainer_names))
                required_reviewer_ids = set(session.exec(stmt).all())
            
            # 获取已有的审核通过记录（当前步骤）
            existing_reviews = session.exec(
                select(Review)
                .where(
                    Review.report_id == report_id,
                    Review.role == Role.PYR,
                    Review.status == ReviewStatus.APPROVED
                )
            ).all()
            
            approved_reviewer_ids = {r.reviewer_id for r in existing_reviews}
            approved_reviewer_ids.add(reviewer_id)  # 加上当前的审核人
            
            # 检查是否所有培养人都已通过
            if not required_reviewer_ids.issubset(approved_reviewer_ids):
                should_advance = False
                message = "您已审核通过，等待其他培养人审核"
        
        if should_advance:
            # 通过：流转到下一步
            next_step = WORKFLOW_MAP.get(report.current_step)
            if next_step is None:
                # 已经是最后一步，标记为最终通过
                report.status = ReportStatus.APPROVED
                message = "报告已通过全部审核流程"
            else:
                # 流转到下一步
                report.current_step = next_step
                report.status = ReportStatus.PENDING
                message = f"报告已通过当前审核，流转至 {next_step.value} 步骤"
    
    else:  # rejected
        # 退回：恢复到上一级步骤
        previous_step = REVERSE_WORKFLOW_MAP.get(report.current_step)
        report.current_step = previous_step
        report.status = ReportStatus.REJECTED
        message = f"报告被退回，返回至 {previous_step.value} 步骤"
    
    # 7. 更新报告的更新时间
    report.updated_at = datetime.utcnow()
    
    # 8. 创建审核记录
    # 修正：确定记录审核记录时的角色身份
    # 核心问题解决：当高等级角色（如ZBSJ/ZZWY）兼任培养人（PYR）时，
    # 如果直接使用 reviewer.role，会导致审核记录的角色为 ZBSJ/ZZWY，
    # 从而导致后续检查"是否所有培养人都已审核"（查询 Role.PYR）时遗漏该记录，造成死循环。
    # 因此，这里必须根据当前审核步骤(current_step)来确定记录的角色身份。
    review_role = STEP_ROLE_MAP.get(report.current_step, reviewer.role)

    review = Review(
        report_id=report_id,
        reviewer_id=reviewer_id,
        role=review_role,
        status=ReviewStatus.APPROVED if review_status == 'approved' else ReviewStatus.REJECTED,
        comment=comment,
        reject_file_path=reject_file_path if review_status == 'rejected' else None,
        reject_original_filename=reject_original_filename if review_status == 'rejected' else None,
        review_time=datetime.utcnow()
    )
    
    # 9. 保存到数据库
    session.add(review)
    session.add(report)
    session.commit()
    session.refresh(report)
    session.refresh(review)
    
    # 10. 返回JSON格式结果
    return {
        "success": True,
        "message": message,
        "data": {
            "report_id": report.id,
            "current_step": report.current_step.value,
            "status": report.status.value,
            "updated_at": report.updated_at.isoformat(),
            "review": {
                "id": review.id,
                "reviewer_id": reviewer.id,
                "reviewer_name": reviewer.real_name,
                "reviewer_role": reviewer.role.value,
                "status": review.status.value,
                "comment": review.comment,
                "review_time": review.review_time.isoformat()
            }
        }
    }


def list_reports_by_user(
    session: Session,
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None
) -> List[Report]:
    """
    查询用户提交的报告列表
    
    Args:
        session: 数据库会话
        user_id: 用户ID
        year: 年份过滤（可选）
        month: 月份过滤（可选）
        status_filter: 状态过滤（可选）
        
    Returns:
        List[Report]: 报告列表
    """
    stmt = select(Report).where(Report.user_id == user_id).options(
        selectinload(Report.author),
        selectinload(Report.reviews)
    )
    
    if year:
        stmt = stmt.where(Report.year == year)
    if month:
        stmt = stmt.where(Report.month == month)
    if status_filter:
        if status_filter == ReportStatus.APPROVED:
            stmt = stmt.where(or_(Report.status == ReportStatus.APPROVED, Report.current_step == CurrentStep.ZZS))
        elif status_filter == ReportStatus.PENDING:
            stmt = stmt.where(and_(Report.status == ReportStatus.PENDING, Report.current_step != CurrentStep.ZZS))
        else:
            stmt = stmt.where(Report.status == status_filter)
    
    stmt = stmt.order_by(Report.uploaded_time.desc())
    return list(session.exec(stmt).all())


def list_pending_reports_for_reviewer(
    session: Session,
    reviewer: User,
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> List[Report]:
    """
    查询待当前审核人审核的报告列表
    
    Args:
        session: 数据库会话
        reviewer: 审核人对象
        year: 年份过滤（可选）
        month: 月份过滤（可选）
        quarter: 季度过滤（可选）
        
    Returns:
        List[Report]: 待审核报告列表
    """
    # 根据审核人角色确定应该审核的步骤
    reviewer_name = _normalize_person_name(reviewer.real_name)
    pyr_reports: List[Report] = []
    
    # 辅助函数：应用时间过滤器
    def apply_filters(stmt):
        if year:
            stmt = stmt.where(Report.year == year)
        if month:
            stmt = stmt.where(Report.month == month)
        elif quarter:
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            stmt = stmt.where(Report.month >= start_month, Report.month <= end_month)
        return stmt

    if reviewer_name:
        stmt_pyr = (
            select(Report)
            .where(
                Report.current_step == CurrentStep.PYR,
                Report.status == ReportStatus.PENDING,
            )
            .options(selectinload(Report.author))
            .order_by(Report.uploaded_time.asc())
        )
        stmt_pyr = apply_filters(stmt_pyr)
        pyr_reports = list(session.exec(stmt_pyr).all())
        pyr_reports = [
            report
            for report in pyr_reports
            if report.author and reviewer_name in list_assigned_trainer_names(report.author)
        ]
        
        # 过滤掉当前审核人已经审核通过的报告
        if pyr_reports:
            pyr_report_ids = [r.id for r in pyr_reports]
            reviewed_stmt = select(Review.report_id).where(
                Review.report_id.in_(pyr_report_ids),
                Review.reviewer_id == reviewer.id,
                Review.role == Role.PYR,
                Review.status == ReviewStatus.APPROVED
            )
            reviewed_ids = set(session.exec(reviewed_stmt).all())
            pyr_reports = [r for r in pyr_reports if r.id not in reviewed_ids]

    target_step = None
    for step, role in STEP_ROLE_MAP.items():
        if role == reviewer.role:
            target_step = step
            break
    
    if target_step is None:
        return pyr_reports

    if target_step == CurrentStep.PYR:
        return pyr_reports
    
    # 查询处于该步骤且状态为待审核的报告，并预加载作者信息
    stmt = select(Report).where(
        Report.current_step == target_step,
        Report.status == ReportStatus.PENDING
    ).options(selectinload(Report.author)).order_by(Report.uploaded_time.asc())
    
    stmt = apply_filters(stmt)

    role_reports = list(session.exec(stmt).all())
    if target_step in {CurrentStep.ZZWY, CurrentStep.ZBSJ} and reviewer.role in {Role.ZZWY, Role.ZBSJ}:
        reviewer_zhibu = _normalize_zhibu(reviewer.zhibu)
        role_reports = [
            report
            for report in role_reports
            if reviewer_zhibu
            and report.author
            and _normalize_zhibu(report.author.zhibu) == reviewer_zhibu
        ]
    if not pyr_reports:
        return role_reports
    if target_step == CurrentStep.PYR:
        return pyr_reports

    by_id = {report.id: report for report in role_reports}
    for report in pyr_reports:
        by_id[report.id] = report
    return sorted(by_id.values(), key=lambda r: r.uploaded_time)


def get_report_reviews(session: Session, report_id: int) -> List[Review]:
    """
    查询报告的所有审核记录
    
    Args:
        session: 数据库会话
        report_id: 报告ID
        
    Returns:
        List[Review]: 审核记录列表，按时间顺序排列
    """
    stmt = select(Review).where(Review.report_id == report_id).order_by(Review.review_time.asc())
    return list(session.exec(stmt).all())


def list_all_reports(
    session: Session,
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None
) -> List[Report]:
    """
    查询所有报告列表（供总支书查看）
    
    Args:
        session: 数据库会话
        year: 年份过滤（可选）
        month: 月份过滤（可选）
        quarter: 季度过滤（可选）
        status_filter: 状态过滤（可选）
        
    Returns:
        List[Report]: 报告列表
    """
    stmt = select(Report).options(selectinload(Report.author))
    
    if year:
        stmt = stmt.where(Report.year == year)
    if month:
        stmt = stmt.where(Report.month == month)
    elif quarter:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        stmt = stmt.where(Report.month >= start_month, Report.month <= end_month)
    if status_filter:
        if status_filter == ReportStatus.APPROVED:
            stmt = stmt.where(or_(Report.status == ReportStatus.APPROVED, Report.current_step == CurrentStep.ZZS))
        elif status_filter == ReportStatus.PENDING:
            stmt = stmt.where(and_(Report.status == ReportStatus.PENDING, Report.current_step != CurrentStep.ZZS))
        else:
            stmt = stmt.where(Report.status == status_filter)
    
    stmt = stmt.order_by(Report.uploaded_time.desc())
    return list(session.exec(stmt).all())


def delete_report(session: Session, report_id: int, user_id: int) -> Dict:
    """
    删除思想汇报（包括数据库记录和文件）
    
    Args:
        session: 数据库会话
        report_id: 报告ID
        user_id: 当前用户ID（用于权限验证）
        
    Returns:
        Dict: 删除结果
        
    Raises:
        HTTPException: 报告不存在或无权限删除
    """
    # 查询报告
    report = get_report_by_id(session, report_id)
    
    # 权限检查：只有报告作者可以删除自己的报告
    if report.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此报告"
        )
    
    # 删除关联的审核记录
    stmt = select(Review).where(Review.report_id == report_id)
    reviews = session.exec(stmt).all()
    for review in reviews:
        session.delete(review)
    
    # 删除文件
    from pathlib import Path
    from app.config import settings
    
    file_path = settings.data_dir / report.file_path
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # 文件删除失败不影响数据库记录删除
            print(f"删除文件失败: {file_path}, 错误: {e}")
    
    # 删除数据库记录
    session.delete(report)
    session.commit()
    
    return {
        "success": True,
        "message": "报告已成功删除",
        "data": {
            "report_id": report_id
        }
    }


def get_zzs_report_stats(
    session: Session,
    year: int,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> Dict:
    """
    获取总支书统计数据
    """
    activists = list(session.exec(select(User).where(User.role == Role.ACTIVIST)).all())

    user_id_to_zhibu: Dict[int, str] = {}
    activists_by_zhibu: Dict[str, int] = defaultdict(int)
    for user in activists:
        zhibu = _normalize_zhibu(user.zhibu) or "未设置"
        user_id_to_zhibu[user.id] = zhibu
        activists_by_zhibu[zhibu] += 1

    submitted_report_count = 0
    approved_report_count = 0
    submitted_user_ids: set[int] = set()
    approved_user_ids: set[int] = set()
    submitted_reports_by_zhibu: Dict[str, int] = defaultdict(int)
    approved_reports_by_zhibu: Dict[str, int] = defaultdict(int)

    stmt_reports = (
        select(
            Report.user_id,
            func.lower(Report.status).label("status_lc"),
            User.zhibu,
            Report.current_step,
        )
        .join(User, User.id == Report.user_id)
        .where(
            User.role == Role.ACTIVIST,
            Report.year == year,
        )
    )

    if month:
        stmt_reports = stmt_reports.where(Report.month == month)
    elif quarter:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        stmt_reports = stmt_reports.where(Report.month >= start_month, Report.month <= end_month)

    for user_id, status_lc, zhibu_raw, current_step in session.exec(stmt_reports).all():
        submitted_report_count += 1
        submitted_user_ids.add(user_id)
        zhibu = _normalize_zhibu(zhibu_raw) or "未设置"
        submitted_reports_by_zhibu[zhibu] += 1

        if status_lc == "approved" or current_step == CurrentStep.ZZS:
            approved_report_count += 1
            approved_user_ids.add(user_id)
            approved_reports_by_zhibu[zhibu] += 1

    missing_list = []
    missing_by_zhibu: Dict[str, int] = defaultdict(int)
    for user in activists:
        if user.id in submitted_user_ids:
            continue
        zhibu = user_id_to_zhibu.get(user.id, "未设置")
        missing_by_zhibu[zhibu] += 1
        # 获取培养联系人
        trainers = []
        if user.pyr1:
            trainers.append(user.pyr1)
        if user.pyr2:
            trainers.append(user.pyr2)
        missing_list.append(
            {
                "id": user.id,
                "real_name": user.real_name,
                "zhibu": zhibu,
                "trainers": "、".join(trainers) if trainers else "-",
            }
        )

    zhibu_summary = []
    for zhibu in sorted(activists_by_zhibu.keys()):
        zhibu_summary.append(
            {
                "zhibu": zhibu,
                "activist_count": activists_by_zhibu[zhibu],
                "submitted_reports": submitted_reports_by_zhibu.get(zhibu, 0),
                "approved_reports": approved_reports_by_zhibu.get(zhibu, 0),
                "missing_activists": missing_by_zhibu.get(zhibu, 0),
            }
        )

    return {
        "year": year,
        "month": month,
        "quarter": quarter,
        "overall": {
            "activist_count": len(activists),
            "submitted_reports": submitted_report_count,
            "submitted_activists": len(submitted_user_ids),
            "approved_reports": approved_report_count,
            "approved_activists": len(approved_user_ids),
            "missing_activists": len(activists) - len(submitted_user_ids),
        },
        "by_zhibu": zhibu_summary,
        "missing_list": sorted(missing_list, key=lambda x: (x["zhibu"], x["real_name"])),
    }


def get_zhibu_report_stats(
    session: Session,
    zhibu: str,
    year: int,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> Dict:
    """
    获取指定支部的统计数据
    """
    normalized_zhibu = _normalize_zhibu(zhibu)
    if not normalized_zhibu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="支部名称不能为空"
        )
    
    activists = list(
        session.exec(
            select(User).where(
                User.role == Role.ACTIVIST,
                User.zhibu == normalized_zhibu
            )
        ).all()
    )
    
    submitted_report_count = 0
    approved_report_count = 0
    submitted_user_ids: set[int] = set()
    approved_user_ids: set[int] = set()
    
    stmt_reports = (
        select(
            Report.user_id,
            func.lower(Report.status).label("status_lc"),
            Report.current_step,
        )
        .join(User, User.id == Report.user_id)
        .where(
            User.role == Role.ACTIVIST,
            User.zhibu == normalized_zhibu,
            Report.year == year,
        )
    )

    if month:
        stmt_reports = stmt_reports.where(Report.month == month)
    elif quarter:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        stmt_reports = stmt_reports.where(Report.month >= start_month, Report.month <= end_month)
    
    for user_id, status_lc, current_step in session.exec(stmt_reports).all():
        submitted_report_count += 1
        submitted_user_ids.add(user_id)
        
        if status_lc == "approved" or current_step == CurrentStep.ZZS:
            approved_report_count += 1
            approved_user_ids.add(user_id)
    
    missing_list = []
    for user in activists:
        if user.id not in submitted_user_ids:
            # 获取培养联系人
            trainers = []
            if user.pyr1:
                trainers.append(user.pyr1)
            if user.pyr2:
                trainers.append(user.pyr2)
            missing_list.append({
                "id": user.id,
                "real_name": user.real_name,
                "zhibu": normalized_zhibu,
                "trainers": "、".join(trainers) if trainers else "-",
            })
    
    return {
        "year": year,
        "month": month,
        "quarter": quarter,
        "zhibu": normalized_zhibu,
        "overall": {
            "activist_count": len(activists),
            "submitted_reports": submitted_report_count,
            "submitted_activists": len(submitted_user_ids),
            "approved_reports": approved_report_count,
            "approved_activists": len(approved_user_ids),
            "missing_activists": len(activists) - len(submitted_user_ids),
        },
        "missing_list": sorted(missing_list, key=lambda x: x["real_name"]),
    }


def list_zhibu_reports(
    session: Session,
    zhibu: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None
) -> List[Report]:
    """
    查询指定支部的所有报告列表
    """
    normalized_zhibu = _normalize_zhibu(zhibu)
    if not normalized_zhibu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="支部名称不能为空"
        )
    
    stmt = (
        select(Report)
        .join(User, User.id == Report.user_id)
        .where(
            User.role == Role.ACTIVIST,
            User.zhibu == normalized_zhibu
        )
        .options(selectinload(Report.author))
    )
    
    if year:
        stmt = stmt.where(Report.year == year)
    if month:
        stmt = stmt.where(Report.month == month)
    elif quarter:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        stmt = stmt.where(Report.month >= start_month, Report.month <= end_month)
    if status_filter:
        stmt = stmt.where(Report.status == status_filter)
    
    stmt = stmt.order_by(Report.uploaded_time.desc())
    return list(session.exec(stmt).all())
