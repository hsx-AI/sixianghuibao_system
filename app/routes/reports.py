from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, require_roles
from app.config import settings
from app.database import get_session
from app.models.report import CurrentStep, Report, ReportStatus
from app.models.review import Review, ReviewStatus
from app.models.user import Role, User
from app.services import report_service
from app.utils.file_utils import save_upload_file
from app.utils.preview_utils import convert_word_to_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRead(BaseModel):
    id: int
    user_id: int
    year: int
    month: int
    file_path: str
    uploaded_time: str
    current_step: CurrentStep
    status: ReportStatus
    updated_at: str
    submitted_by: Optional[str] = None  # 提交人姓名

    class Config:
        orm_mode = True


class ReviewRequest(BaseModel):
    """审核请求模型"""
    status: str = Field(..., description="审核状态: approved 或 rejected")
    comment: Optional[str] = Field(None, description="审核意见")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "approved",
                "comment": "审核通过，内容详实"
            }
        }


class ReviewResponse(BaseModel):
    """审核响应模型"""
    id: int
    reviewer_id: int
    reviewer_name: str
    reviewer_role: str
    status: str
    comment: Optional[str]
    review_time: str


@router.post("")
async def submit_report(
    file: UploadFile = File(...),
    title: str = Form(None),
    period: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ACTIVIST))
) -> Report:
    """
    提交思想汇报
    
    参数：
    - file: 上传的文件（Word文档）
    - title: 标题（可选，暂不使用）
    - period: 期间（格式：YYYY-MM）
    
    返回：
    - 创建的报告对象
    """
    # 检查文件类型
    if not file.filename or not file.filename.endswith(('.doc', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 Word 文档格式（.doc 或 .docx）"
        )
    
    # 解析 period（格式：YYYY-MM）
    try:
        year_str, month_str = period.split('-')
        year = int(year_str)
        month = int(month_str)
        if not (1 <= month <= 12):
            raise ValueError("月份必须在 1-12 之间")
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"期间格式错误，应为 YYYY-MM 格式，例如：2024-03"
        )
    
    # 保存文件
    file_path = await save_upload_file(file, year, month)
    
    # 创建报告记录，保存原始文件名
    report = report_service.create_report(
        session=session,
        user_id=current_user.id,
        year=year,
        month=month,
        file_path=file_path,
        title=title,
        original_filename=file.filename  # 保存原始文件名用于下载
    )
    
    return report


@router.get("/my/list")
def list_my_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    year: Optional[int] = None,
    month: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None,
) -> List[Dict]:
    """
    查询当前用户提交的报告列表
    
    参数：
    - year: 年份过滤（可选）
    - month: 月份过滤（可选）
    - status_filter: 状态过滤（可选）
    
    返回：
    - 报告列表
    """
    reports = report_service.list_reports_by_user(
        session=session,
        user_id=current_user.id,
        year=year,
        month=month,
        status_filter=status_filter
    )
    
    # 添加提交人姓名和最新驳回意见
    result = []
    for report in reports:
        # 获取最新的驳回意见（如果状态是已驳回）
        reject_comment = None
        reject_review_id = None
        reject_has_file = False
        if report.status == ReportStatus.REJECTED and report.reviews:
            # 找到最新的驳回记录
            rejected_reviews = [r for r in report.reviews if r.status.value == 'rejected']
            if rejected_reviews:
                latest_reject = max(rejected_reviews, key=lambda r: r.review_time)
                reject_comment = latest_reject.comment
                reject_review_id = latest_reject.id
                reject_has_file = bool(latest_reject.reject_file_path)
        
        # 获取当前审批人信息
        current_reviewer_names = _get_current_reviewer_names(session, report, current_user)
        
        # 获取审批历史（用于显示每个步骤的审批人）
        review_history = _get_review_history(report)
        
        report_dict = {
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "year": report.year,
            "month": report.month,
            "file_path": report.file_path,
            "uploaded_time": report.uploaded_time.isoformat(),
            "current_step": report.current_step,
            "status": report.status,
            "updated_at": report.updated_at.isoformat(),
            "submitted_by": report.author.real_name if report.author else None,
            "reject_comment": reject_comment,
            "reject_review_id": reject_review_id,
            "reject_has_file": reject_has_file,
            "current_reviewer_names": current_reviewer_names,  # 当前审批人姓名列表
            "review_history": review_history  # 审批历史
        }
        result.append(report_dict)
    
    return result


def _get_current_reviewer_names(session: Session, report: Report, author: User) -> List[str]:
    """获取当前步骤的审批人姓名列表"""
    if report.status == ReportStatus.APPROVED:
        return []  # 已通过，无需审批
    
    if report.status == ReportStatus.REJECTED:
        return []  # 已驳回，等待重新提交
    
    current_step = report.current_step
    reviewer_names = []
    
    if current_step == CurrentStep.PYR:
        # 培养人步骤：获取用户的培养人
        if author.pyr1:
            reviewer_names.append(author.pyr1)
        if author.pyr2 and author.pyr2 != author.pyr1:
            reviewer_names.append(author.pyr2)
    
    elif current_step == CurrentStep.ZZWY:
        # 组织委员步骤：获取同支部的组织委员
        if author.zhibu:
            stmt = select(User).where(
                User.role == Role.ZZWY,
                User.zhibu == author.zhibu
            )
            zzwy_users = session.exec(stmt).all()
            reviewer_names = [u.real_name for u in zzwy_users if u.real_name]
    
    elif current_step == CurrentStep.ZBSJ:
        # 支部书记步骤：获取同支部的支部书记
        if author.zhibu:
            stmt = select(User).where(
                User.role == Role.ZBSJ,
                User.zhibu == author.zhibu
            )
            zbsj_users = session.exec(stmt).all()
            reviewer_names = [u.real_name for u in zbsj_users if u.real_name]
    
    elif current_step == CurrentStep.ZZS:
        # 党总支步骤：获取党总支角色的人
        stmt = select(User).where(User.role == Role.ZZS)
        zzs_users = session.exec(stmt).all()
        reviewer_names = [u.real_name for u in zzs_users if u.real_name]
    
    return reviewer_names


def _get_review_history(report: Report) -> List[Dict]:
    """获取审批历史，按步骤整理"""
    history = []
    
    if not report.reviews:
        return history
    
    # 按审核时间排序
    sorted_reviews = sorted(report.reviews, key=lambda r: r.review_time)
    
    for review in sorted_reviews:
        history.append({
            "step": review.role.value,  # 审核人角色即为审核步骤
            "reviewer_name": review.reviewer.real_name if review.reviewer else None,
            "status": review.status.value,
            "comment": review.comment,
            "review_time": review.review_time.isoformat()
        })
    
    return history


@router.get("/{report_id}")
def get_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Report:
    """
    查询报告详情
    
    参数：
    - report_id: 报告ID
    
    返回：
    - 报告详情
    """
    report = report_service.get_report_by_id(session, report_id)
    
    # 权限检查：只有报告作者和审核人员可以查看
    if report.user_id != current_user.id and current_user.role == Role.ACTIVIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此报告"
        )
    
    return report


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """
    下载报告文件
    
    参数：
    - report_id: 报告ID
    
    返回：
    - 报告文件
    """
    report = report_service.get_report_by_id(session, report_id)
    
    # 权限检查
    if report.user_id != current_user.id and current_user.role == Role.ACTIVIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权下载此报告"
        )
    
    file_path = settings.data_dir / report.file_path
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 优先使用原始文件名，如果没有则使用磁盘文件名
    download_filename = report.original_filename or file_path.name
    
    return FileResponse(path=file_path, filename=download_filename)


@router.get("/{report_id}/preview")
def preview_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    在线预览思想汇报（Word -> PDF）

    说明：需要本机安装 LibreOffice，并提供 `soffice` 命令。
    """
    report = report_service.get_report_by_id(session, report_id)

    # 权限检查（与下载一致）：积极分子只能预览自己的报告
    if report.user_id != current_user.id and current_user.role == Role.ACTIVIST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权预览此报告")

    input_path = settings.data_dir / report.file_path
    if not input_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    preview_dir = settings.data_dir / "previews"
    preview_path = preview_dir / f"report_{report.id}.pdf"

    try:
        if not preview_path.exists() or preview_path.stat().st_mtime < input_path.stat().st_mtime:
            convert_word_to_pdf(input_path, preview_path)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    headers = {"Content-Disposition": f'inline; filename="report_{report.id}.pdf"'}
    return FileResponse(path=preview_path, media_type="application/pdf", headers=headers)


@router.post("/{report_id}/review")
def review_report(
    report_id: int,
    payload: ReviewRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    审核思想汇报
    
    审核流程：积极分子 → 培养人 → 组织委员 → 支部书记 → 总支书
    - 通过(approved)：流转到下一步，最后一步则标记为已通过
    - 退回(rejected)：恢复到上一级步骤
    
    参数：
    - report_id: 报告ID
    - status: 审核状态 (approved/rejected)
    - comment: 审核意见（可选）
    
    返回：
    - JSON格式的审核结果，包含报告最新状态和审核记录
    """
    result = report_service.review_report(
        session=session,
        report_id=report_id,
        reviewer_id=current_user.id,
        review_status=payload.status,
        comment=payload.comment
    )
    return result


@router.post("/{report_id}/reject-with-file")
async def reject_report_with_file(
    report_id: int,
    comment: str = Form(...),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    驳回思想汇报（支持上传批注文件）
    
    参数：
    - report_id: 报告ID
    - comment: 驳回意见（必填）
    - file: 批注文件（可选，支持Word文档）
    
    返回：
    - JSON格式的审核结果
    """
    # 处理上传的批注文件
    reject_file_path = None
    if file and file.filename:
        # 验证文件类型
        allowed_types = [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持上传 Word 文档（.doc/.docx）"
            )
        
        # 保存文件到 reject_files 目录
        reject_dir = settings.data_dir / "reject_files"
        reject_dir.mkdir(parents=True, exist_ok=True)
        
        # 保留原始文件名，必要时添加时间戳避免冲突
        from pathlib import Path as FilePath
        original_name = file.filename or "批注.docx"
        stem = FilePath(original_name).stem
        suffix = FilePath(original_name).suffix or ".docx"
        saved_filename = original_name
        saved_path = reject_dir / saved_filename
        
        # 如果文件已存在，添加时间戳
        if saved_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            saved_filename = f"{stem}_{timestamp}{suffix}"
            saved_path = reject_dir / saved_filename
        
        # 保存文件
        content = await file.read()
        with open(saved_path, "wb") as f:
            f.write(content)
        
        reject_file_path = f"reject_files/{saved_filename}"
    
    # 执行驳回操作
    result = report_service.review_report(
        session=session,
        report_id=report_id,
        reviewer_id=current_user.id,
        review_status='rejected',
        comment=comment,
        reject_file_path=reject_file_path,
        reject_original_filename=file.filename if file and file.filename else None
    )
    return result


@router.get("/review/{review_id}/reject-file")
def download_reject_file(
    review_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    下载驳回时上传的批注文件
    
    参数：
    - review_id: 审核记录ID
    
    返回：
    - 批注文件
    """
    # 查询审核记录
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="审核记录不存在"
        )
    
    if not review.reject_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该驳回记录没有上传批注文件"
        )
    
    # 检查权限：只有报告作者和审核人员可以下载
    report = session.get(Report, review.report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    
    if report.user_id != current_user.id and current_user.role == Role.ACTIVIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权下载此文件"
        )
    
    file_path = settings.data_dir / review.reject_file_path
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 优先使用原始文件名，如果没有则使用磁盘文件名
    filename = review.reject_original_filename or file_path.name
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/{report_id}/reviews")
def get_report_reviews(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Review]:
    """
    查询报告的所有审核记录
    
    参数：
    - report_id: 报告ID
    
    返回：
    - 按时间顺序排列的审核记录列表
    """
    return report_service.get_report_reviews(session, report_id)


@router.get("/pending/list")
def list_pending_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> List[Dict]:
    """
    查询待当前审核人审核的报告列表
    
    根据当前用户的角色，返回需要该角色审核的所有待审核报告
    
    返回：
    - 待审核报告列表
    """
    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        month = None  # 季度优先，忽略月份
    elif month:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="月份必须在 1-12 之间",
            )

    reports = report_service.list_pending_reports_for_reviewer(
        session, 
        current_user,
        year=year,
        month=month,
        quarter=quarter
    )
    
    # 添加提交人姓名和培养人信息
    result = []
    for report in reports:
        # 获取培养人列表
        trainers = []
        if report.author:
            trainers = report_service.list_assigned_trainer_names(report.author)
        
        report_dict = {
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "year": report.year,
            "month": report.month,
            "file_path": report.file_path,
            "uploaded_time": report.uploaded_time.isoformat(),
            "current_step": report.current_step,
            "status": report.status,
            "updated_at": report.updated_at.isoformat(),
            "submitted_by": report.author.real_name if report.author else None,
            "trainers": trainers  # 添加培养人列表
        }
        result.append(report_dict)
    
    return result


@router.get("/all/list")
def list_all_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZS)),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None,
) -> List[Dict]:
    """
    查询所有报告列表（仅供总支书查看）
    
    参数：
    - year: 年份过滤（可选）
    - month: 月份过滤（可选）
    - quarter: 季度过滤（可选）
    - status_filter: 状态过滤（可选）
    
    返回：
    - 所有报告列表
    """
    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        month = None
    elif month:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="月份必须在 1-12 之间",
            )

    reports = report_service.list_all_reports(
        session=session,
        year=year,
        month=month,
        quarter=quarter,
        status_filter=status_filter
    )
    
    # 添加提交人姓名和支部
    result = []
    for report in reports:
        report_dict = {
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "year": report.year,
            "month": report.month,
            "file_path": report.file_path,
            "uploaded_time": report.uploaded_time.isoformat(),
            "current_step": report.current_step,
            "status": report.status,
            "updated_at": report.updated_at.isoformat(),
            "submitted_by": report.author.real_name if report.author else None,
            "zhibu": report.author.zhibu if report.author else None
        }
        result.append(report_dict)
    
    return result


@router.get("/zzs/stats")
def get_zzs_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZS)),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> Dict:
    now = datetime.now()
    target_year = year or now.year

    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        return report_service.get_zzs_report_stats(session, target_year, month=None, quarter=quarter)

    target_month = month or now.month
    if not (1 <= target_month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="月份必须在 1-12 之间",
        )

    return report_service.get_zzs_report_stats(session, target_year, month=target_month)


@router.get("/zhibu/stats")
def get_zhibu_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZWY, Role.ZBSJ)),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
) -> Dict:
    """
    获取支部统计数据（组织委员和支部书记专用）
    
    参数：
    - year: 年份（可选，默认当前年份）
    - month: 月份（可选，默认当前月份）
    - quarter: 季度（可选）
    
    返回：
    - 支部统计数据
    """
    if not current_user.zhibu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户未设置所属支部"
        )
    
    now = datetime.now()
    target_year = year or now.year

    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        return report_service.get_zhibu_report_stats(
            session, 
            current_user.zhibu, 
            target_year, 
            month=None,
            quarter=quarter
        )

    target_month = month or now.month

    if not (1 <= target_month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="月份必须在 1-12 之间",
        )

    return report_service.get_zhibu_report_stats(
        session, 
        current_user.zhibu, 
        target_year, 
        month=target_month
    )


@router.get("/zhibu/list")
def list_zhibu_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZWY, Role.ZBSJ)),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None,
) -> List[Dict]:
    """
    查询支部报告列表（组织委员和支部书记专用）
    
    参数：
    - year: 年份过滤（可选）
    - month: 月份过滤（可选）
    - quarter: 季度过滤（可选）
    - status_filter: 状态过滤（可选）
    
    返回：
    - 支部报告列表
    """
    if not current_user.zhibu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户未设置所属支部"
        )
    
    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        month = None
    elif month:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="月份必须在 1-12 之间",
            )

    reports = report_service.list_zhibu_reports(
        session=session,
        zhibu=current_user.zhibu,
        year=year,
        month=month,
        quarter=quarter,
        status_filter=status_filter
    )
    
    # 添加提交人姓名
    result = []
    for report in reports:
        report_dict = {
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "year": report.year,
            "month": report.month,
            "file_path": report.file_path,
            "uploaded_time": report.uploaded_time.isoformat(),
            "current_step": report.current_step,
            "status": report.status,
            "updated_at": report.updated_at.isoformat(),
            "submitted_by": report.author.real_name if report.author else None
        }
        result.append(report_dict)
    
    return result


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    删除思想汇报
    
    只有报告作者可以删除自己的报告
    删除操作会同时删除数据库记录、关联的审核记录和文件
    
    参数：
    - report_id: 报告ID
    
    返回：
    - 删除结果
    """
    result = report_service.delete_report(
        session=session,
        report_id=report_id,
        user_id=current_user.id
    )
    return result


# ==================== 管理员报告管理 ====================

@router.get("/admin/list")
def admin_list_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    status_filter: Optional[ReportStatus] = None,
) -> List[Dict]:
    """
    获取所有报告列表（管理员专用）
    """
    if quarter:
        if not (1 <= quarter <= 4):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="季度必须在 1-4 之间",
            )
        month = None
    elif month:
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="月份必须在 1-12 之间",
            )

    reports = report_service.list_all_reports(
        session=session,
        year=year,
        month=month,
        quarter=quarter,
        status_filter=status_filter
    )
    
    result = []
    for report in reports:
        result.append({
            "id": report.id,
            "user_id": report.user_id,
            "title": report.title,
            "year": report.year,
            "month": report.month,
            "file_path": report.file_path,
            "uploaded_time": report.uploaded_time.isoformat(),
            "current_step": report.current_step,
            "status": report.status,
            "updated_at": report.updated_at.isoformat(),
            "submitted_by": report.author.real_name if report.author else None,
            "zhibu": report.author.zhibu if report.author else None
        })
    
    return result


class AdminReportUpdate(BaseModel):
    """管理员更新报告请求"""
    year: Optional[int] = None
    month: Optional[int] = None
    current_step: Optional[str] = None
    status: Optional[str] = None


@router.put("/admin/{report_id}")
def admin_update_report(
    report_id: int,
    payload: AdminReportUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    更新报告信息（管理员专用）
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    
    if payload.year is not None:
        report.year = payload.year
    
    if payload.month is not None:
        if not (1 <= payload.month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="月份必须在 1-12 之间"
            )
        report.month = payload.month
    
    if payload.current_step is not None:
        try:
            report.current_step = CurrentStep(payload.current_step)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的审核步骤: {payload.current_step}"
            )
    
    if payload.status is not None:
        try:
            report.status = ReportStatus(payload.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态: {payload.status}"
            )
    
    report.updated_at = datetime.utcnow()
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return {
        "id": report.id,
        "year": report.year,
        "month": report.month,
        "current_step": report.current_step,
        "status": report.status,
        "message": "报告更新成功"
    }


@router.delete("/admin/{report_id}")
def admin_delete_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    删除报告（管理员专用）
    
    管理员可以删除任何报告
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在"
        )
    
    # 删除关联的审核记录
    reviews = session.exec(select(Review).where(Review.report_id == report_id)).all()
    for review in reviews:
        session.delete(review)
    
    # 删除文件
    from app.config import settings
    file_path = settings.data_dir / report.file_path
    if file_path.exists():
        file_path.unlink()
    
    # 删除预览文件
    preview_path = settings.data_dir / "previews" / f"report_{report.id}.pdf"
    if preview_path.exists():
        preview_path.unlink()
    
    # 删除报告记录
    session.delete(report)
    session.commit()
    
    return {"message": "报告删除成功"}
