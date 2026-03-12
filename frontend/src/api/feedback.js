import request from '@/utils/request'

/**
 * 提交意见反馈
 * @param {Object} data - { feedback_type, title, content }
 */
export function submitFeedback(data) {
  return request({
    url: '/feedback',
    method: 'post',
    data
  })
}

/**
 * 获取我的反馈列表
 */
export function getMyFeedback() {
  return request({
    url: '/feedback/my/list',
    method: 'get'
  })
}

// ==================== 管理员接口 ====================

/**
 * 获取所有反馈列表（管理员专用）
 * @param {Object} params - { status_filter }
 */
export function getAdminFeedbackList(params) {
  return request({
    url: '/feedback/admin/list',
    method: 'get',
    params
  })
}

/**
 * 获取反馈统计（管理员专用）
 */
export function getAdminFeedbackStats() {
  return request({
    url: '/feedback/admin/stats',
    method: 'get'
  })
}

/**
 * 回复反馈（管理员专用）
 * @param {number} id - 反馈ID
 * @param {Object} data - { reply, status }
 */
export function replyFeedback(id, data) {
  return request({
    url: `/feedback/admin/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除反馈（管理员专用）
 * @param {number} id - 反馈ID
 */
export function deleteFeedback(id) {
  return request({
    url: `/feedback/admin/${id}`,
    method: 'delete'
  })
}







