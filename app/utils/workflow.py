from typing import Optional

from app.models import Report, ReportStatus, ReviewAction, ReviewStep, Role, User

ROLE_BY_STEP = {
    ReviewStep.TRAINER: Role.TRAINER,
    ReviewStep.ORGANIZER: Role.ORGANIZER,
    ReviewStep.SECRETARY: Role.SECRETARY,
}

STATUS_BY_STEP = {
    ReviewStep.TRAINER: ReportStatus.PENDING_TRAINER,
    ReviewStep.ORGANIZER: ReportStatus.PENDING_ORGANIZER,
    ReviewStep.SECRETARY: ReportStatus.PENDING_SECRETARY,
}


def next_step(step: ReviewStep) -> Optional[ReviewStep]:
    if step == ReviewStep.TRAINER:
        return ReviewStep.ORGANIZER
    if step == ReviewStep.ORGANIZER:
        return ReviewStep.SECRETARY
    return None


def can_review(report: Report, reviewer: User) -> bool:
    expected_role = ROLE_BY_STEP.get(report.current_step)
    return reviewer.role == expected_role


def apply_action(report: Report, action: ReviewAction) -> Report:
    if action == ReviewAction.REJECTED:
        report.status = ReportStatus.RETURNED
        report.current_step = ReviewStep.TRAINER
        return report

    nxt = next_step(report.current_step)
    if nxt is None:
        report.status = ReportStatus.APPROVED
    else:
        report.current_step = nxt
        report.status = STATUS_BY_STEP[nxt]
    return report
