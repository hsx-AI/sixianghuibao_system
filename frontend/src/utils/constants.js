// 角色定义
export const ROLES = {
  ADMIN: 'admin',            // 管理员
  ACTIVIST: 'activist',      // 积极分子
  PYR: 'pyr',                // 培养人
  ZZWY: 'zzwy',              // 组织委员
  ZBSJ: 'zbsj',              // 支部书记
  ZZS: 'zzs'                 // 党总支
}

// 角色中文名称
export const ROLE_NAMES = {
  [ROLES.ADMIN]: '管理员',
  [ROLES.ACTIVIST]: '积极分子',
  [ROLES.PYR]: '培养人',
  [ROLES.ZZWY]: '组织委员',
  [ROLES.ZBSJ]: '支部书记',
  [ROLES.ZZS]: '党总支'
}

// 报告状态
export const REPORT_STATUS = {
  PENDING: 'pending',      // 待审核
  APPROVED: 'approved',    // 已通过
  REJECTED: 'rejected'     // 已驳回
}

// 报告状态中文
export const REPORT_STATUS_NAMES = {
  [REPORT_STATUS.PENDING]: '待审核',
  [REPORT_STATUS.APPROVED]: '已通过',
  [REPORT_STATUS.REJECTED]: '已驳回'
}

// 报告状态标签类型
export const REPORT_STATUS_TYPES = {
  [REPORT_STATUS.PENDING]: 'warning',
  [REPORT_STATUS.APPROVED]: 'success',
  [REPORT_STATUS.REJECTED]: 'danger'
}

// 审核步骤
export const CURRENT_STEP = {
  ACTIVIST: 'activist',
  PYR: 'pyr',
  ZZWY: 'zzwy',
  ZBSJ: 'zbsj',
  ZZS: 'zzs'
}

// 审核步骤中文
export const CURRENT_STEP_NAMES = {
  [CURRENT_STEP.ACTIVIST]: '积极分子提交',
  [CURRENT_STEP.PYR]: '培养人审核',
  [CURRENT_STEP.ZZWY]: '组织委员审核',
  [CURRENT_STEP.ZBSJ]: '支部书记审核',
  [CURRENT_STEP.ZZS]: '党总支查看'
}

// 审核动作
export const REVIEW_ACTION = {
  APPROVE: 'approve',      // 通过
  REJECT: 'reject'         // 驳回
}

// 审核动作中文
export const REVIEW_ACTION_NAMES = {
  [REVIEW_ACTION.APPROVE]: '通过',
  [REVIEW_ACTION.REJECT]: '驳回'
}

















