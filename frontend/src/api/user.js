import request from '@/utils/request'

/**
 * 获取组织架构数据（党总支专用）
 */
export function getOrganizationStructure() {
  return request({
    url: '/users/organization',
    method: 'get'
  })
}

/**
 * 获取支部组织架构数据（组织委员和支部书记专用）
 */
export function getZhibuOrganization() {
  return request({
    url: '/users/organization/zhibu',
    method: 'get'
  })
}

// ==================== 管理员用户管理 ====================

/**
 * 获取所有用户列表（管理员专用）
 */
export function getUserList() {
  return request({
    url: '/users/list',
    method: 'get'
  })
}

/**
 * 创建用户（管理员专用）
 */
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

/**
 * 更新用户（管理员专用）
 */
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户（管理员专用）
 */
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

