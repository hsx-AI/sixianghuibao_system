import request from '@/utils/request'

/**
 * 获取我的报告列表
 * @param {Object} params - 查询参数
 */
export function getReportList(params) {
  return request({
    url: '/reports/my/list',
    method: 'get',
    params
  })
}

/**
 * 获取报告详情
 * @param {number} id - 报告ID
 */
export function getReportDetail(id) {
  return request({
    url: `/reports/${id}`,
    method: 'get'
  })
}

/**
 * 上传报告
 * @param {Object} data - 报告数据
 */
export function uploadReport(data) {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('period', data.period)
  formData.append('file', data.file)
  
  return request({
    url: '/reports',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取待审核报告列表（审核人员专用）
 * @param {Object} params - 查询参数
 */
export function getPendingReports(params) {
  return request({
    url: '/reports/pending/list',
    method: 'get',
    params
  })
}

/**
 * 获取所有报告列表（党总支专用）
 * @param {Object} params - 查询参数
 */
export function getAllReports(params) {
  return request({
    url: '/reports/all/list',
    method: 'get',
    params
  })
}

/**
 * 获取党总支统计数据（党总支专用）
 * @param {Object} params - 查询参数 { year, month }
 */
export function getZzsStats(params) {
  return request({
    url: '/reports/zzs/stats',
    method: 'get',
    params
  })
}

/**
 * 获取支部统计数据（组织委员和支部书记专用）
 * @param {Object} params - 查询参数 { year, month }
 */
export function getZhibuStats(params) {
  return request({
    url: '/reports/zhibu/stats',
    method: 'get',
    params
  })
}

/**
 * 获取支部报告列表（组织委员和支部书记专用）
 * @param {Object} params - 查询参数
 */
export function getZhibuReports(params) {
  return request({
    url: '/reports/zhibu/list',
    method: 'get',
    params
  })
}

/**
 * 审核报告
 * @param {number} id - 报告ID
 * @param {string} action - 审核动作：'approve' 或 'reject'
 * @param {string} comment - 审核意见
 */
export function reviewReport(id, action, comment) {
  return request({
    url: `/reports/${id}/review`,
    method: 'post',
    data: {
      status: action === 'approve' ? 'approved' : 'rejected',
      comment: comment || undefined
    }
  })
}

/**
 * 驳回报告（支持上传批注文件）
 * @param {number} id - 报告ID
 * @param {string} comment - 驳回意见
 * @param {File} file - 批注文件（可选）
 */
export function rejectReportWithFile(id, comment, file) {
  const formData = new FormData()
  formData.append('comment', comment)
  if (file) {
    formData.append('file', file)
  }
  
  return request({
    url: `/reports/${id}/reject-with-file`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 下载驳回批注文件（返回 blob 和原始文件名）
 * @param {number} reviewId - 审核记录ID
 * @returns {Promise<{blob: Blob, filename: string}>} 包含文件内容和原始文件名的对象
 */
export async function downloadRejectFile(reviewId) {
  const { useUserStore } = await import('@/stores/user')
  const userStore = useUserStore()
  
  // 直接使用 fetch 以获取完整响应头
  const response = await fetch(`/api/reports/review/${reviewId}/reject-file`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${userStore.token}`
    }
  })
  
  if (!response.ok) {
    throw new Error('下载失败')
  }
  
  // 从 Content-Disposition 头中提取文件名
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = `批注_${reviewId}.docx` // 默认文件名
  
  if (contentDisposition) {
    // 尝试解析 filename*= (RFC 5987 编码格式，支持中文)
    const filenameStarMatch = contentDisposition.match(/filename\*=(?:UTF-8''|utf-8'')([^;\s]+)/i)
    if (filenameStarMatch) {
      filename = decodeURIComponent(filenameStarMatch[1])
    } else {
      // 尝试解析 filename= (可能带引号)
      const filenameMatch = contentDisposition.match(/filename=["']?([^"';\s]+)["']?/i)
      if (filenameMatch) {
        // 尝试解码，如果是 URL 编码的中文
        try {
          filename = decodeURIComponent(filenameMatch[1])
        } catch {
          filename = filenameMatch[1]
        }
      }
    }
  }
  
  const blob = await response.blob()
  return { blob, filename }
}

/**
 * 下载报告（返回 blob 和原始文件名）
 * @param {number} id - 报告ID
 * @returns {Promise<{blob: Blob, filename: string}>} 包含文件内容和原始文件名的对象
 */
export async function downloadReport(id) {
  const { useUserStore } = await import('@/stores/user')
  const userStore = useUserStore()
  
  // 直接使用 fetch 以获取完整响应头
  const response = await fetch(`/api/reports/${id}/download`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${userStore.token}`
    }
  })
  
  if (!response.ok) {
    throw new Error('下载失败')
  }
  
  // 从 Content-Disposition 头中提取文件名
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = `思想汇报_${id}.docx` // 默认文件名
  
  if (contentDisposition) {
    // 尝试解析 filename*= (RFC 5987 编码格式，支持中文)
    const filenameStarMatch = contentDisposition.match(/filename\*=(?:UTF-8''|utf-8'')([^;\s]+)/i)
    if (filenameStarMatch) {
      filename = decodeURIComponent(filenameStarMatch[1])
    } else {
      // 尝试解析 filename= (可能带引号)
      const filenameMatch = contentDisposition.match(/filename=["']?([^"';\s]+)["']?/i)
      if (filenameMatch) {
        // 尝试解码，如果是 URL 编码的中文
        try {
          filename = decodeURIComponent(filenameMatch[1])
        } catch {
          filename = filenameMatch[1]
        }
      }
    }
  }
  
  const blob = await response.blob()
  return { blob, filename }
}

/**
 * 在线预览报告（PDF）
 * @param {number} id - 报告ID
 */
export function previewReport(id) {
  return request({
    url: `/reports/${id}/preview`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除报告
 * @param {number} id - 报告ID
 */
export function deleteReport(id) {
  return request({
    url: `/reports/${id}`,
    method: 'delete'
  })
}

// ==================== 管理员报告管理 ====================

/**
 * 获取所有报告列表（管理员专用）
 */
export function getAdminReportList(params) {
  return request({
    url: '/reports/admin/list',
    method: 'get',
    params
  })
}

/**
 * 更新报告（管理员专用）
 */
export function adminUpdateReport(id, data) {
  return request({
    url: `/reports/admin/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除报告（管理员专用）
 */
export function adminDeleteReport(id) {
  return request({
    url: `/reports/admin/${id}`,
    method: 'delete'
  })
}
