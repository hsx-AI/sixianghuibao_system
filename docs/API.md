# API 接口文档

本文档详细说明思想汇报管理系统的所有 REST API 接口。

## 📋 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 🔐 认证接口

### 1. 用户登录

**端点**: `POST /api/auth/token`

**Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:
```
username=your_username&password=your_password
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. 获取当前用户信息

**端点**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "id": 1,
  "username": "activist1",
  "role": "activist",
  "real_name": "张三",
  "created_at": "2024-12-01T00:00:00"
}
```

---

## 📝 报告接口

### 1. 提交思想汇报

**端点**: `POST /api/reports`

**权限**: 需要 activist 角色

**Content-Type**: `multipart/form-data`

**请求参数**:
- `year`: 年份（整数）
- `month`: 月份（1-12）
- `file`: 文件（PDF/Word）

**响应示例**:
```json
{
  "id": 1,
  "user_id": 1,
  "year": 2024,
  "month": 12,
  "file_path": "data/reports/2024/12/report_1.pdf",
  "uploaded_time": "2024-12-01T08:00:00",
  "current_step": "trainer",
  "status": "pending",
  "updated_at": "2024-12-01T08:00:00"
}
```

### 2. 查询我的报告列表

**端点**: `GET /api/reports/my/list`

**权限**: 需要认证

**查询参数**:
- `year`: 年份过滤（可选）
- `month`: 月份过滤（可选）
- `status_filter`: 状态过滤（可选：pending/rejected/approved）

**示例**: `GET /api/reports/my/list?year=2024&month=12`

**响应示例**:
```json
[
  {
    "id": 1,
    "user_id": 10,
    "year": 2024,
    "month": 12,
    "file_path": "reports/2024/12/report_1.pdf",
    "uploaded_time": "2024-12-01T08:00:00",
    "current_step": "secretary",
    "status": "pending",
    "updated_at": "2024-12-02T08:00:00"
  }
]
```

### 3. 下载报告文件

**端点**: `GET /api/reports/{report_id}/download`

**权限**: 需要认证

**响应**: 文件流（PDF/Word）

---

## ✅ 审核接口

### 1. 审核思想汇报

**端点**: `POST /api/reports/{report_id}/review`

**权限**: 需要相应角色的审核权限

**请求体**:
```json
{
  "status": "approved",  // 或 "rejected"
  "comment": "审核意见（可选）"
}
```

**响应示例**:

#### 通过审核（流转到下一步）
```json
{
  "success": true,
  "message": "报告已通过当前审核，流转至 organizer 步骤",
  "data": {
    "report_id": 1,
    "current_step": "organizer",
    "status": "pending",
    "updated_at": "2024-12-02T10:30:00",
    "review": {
      "id": 1,
      "reviewer_id": 2,
      "reviewer_name": "张三",
      "reviewer_role": "trainer",
      "status": "approved",
      "comment": "内容详实，思想积极",
      "review_time": "2024-12-02T10:30:00"
    }
  }
}
```

#### 退回审核（返回上一步）
```json
{
  "success": true,
  "message": "报告被退回，返回至 trainer 步骤",
  "data": {
    "report_id": 1,
    "current_step": "trainer",
    "status": "rejected",
    "updated_at": "2024-12-02T10:30:00",
    "review": {
      "id": 2,
      "reviewer_id": 3,
      "reviewer_name": "李四",
      "reviewer_role": "organizer",
      "status": "rejected",
      "comment": "内容需要补充完善",
      "review_time": "2024-12-02T10:30:00"
    }
  }
}
```

#### 最终审核通过
```json
{
  "success": true,
  "message": "报告已通过全部审核流程",
  "data": {
    "report_id": 1,
    "current_step": "final",
    "status": "approved",
    "updated_at": "2024-12-02T10:30:00",
    "review": {
      "id": 4,
      "reviewer_id": 5,
      "reviewer_name": "王五",
      "reviewer_role": "secretary",
      "status": "approved",
      "comment": "全部审核通过",
      "review_time": "2024-12-02T10:30:00"
    }
  }
}
```

### 2. 查询待审核报告列表

**端点**: `GET /api/reports/pending/list`

**权限**: 需要审核人员角色

**说明**: 根据当前用户角色，自动返回需要该角色审核的所有待审核报告

**响应示例**:
```json
[
  {
    "id": 1,
    "user_id": 10,
    "year": 2024,
    "month": 12,
    "file_path": "reports/2024/12/report_1.pdf",
    "uploaded_time": "2024-12-01T08:00:00",
    "current_step": "trainer",
    "status": "pending",
    "updated_at": "2024-12-01T08:00:00"
  }
]
```

### 3. 查询报告的审核记录

**端点**: `GET /api/reports/{report_id}/reviews`

**权限**: 需要认证

**说明**: 查询指定报告的所有审核历史记录，按时间顺序排列

**响应示例**:
```json
[
  {
    "id": 1,
    "report_id": 1,
    "reviewer_id": 2,
    "role": "trainer",
    "status": "approved",
    "comment": "内容详实，思想积极",
    "review_time": "2024-12-01T10:00:00"
  },
  {
    "id": 2,
    "report_id": 1,
    "reviewer_id": 3,
    "role": "organizer",
    "status": "approved",
    "comment": "符合要求",
    "review_time": "2024-12-01T14:00:00"
  }
]
```

---

## 🔄 审核流程说明

审核流程遵循以下顺序：

```
积极分子提交 → 培养人审核 → 组织委员审核 → 支部书记审核 → 最终完成
```

### 流程详解

1. **培养人 (TRAINER)** - 第一级审核
2. **组织委员 (ORGANIZER)** - 第二级审核
3. **支部书记 (SECRETARY)** - 第三级审核
4. **最终完成 (FINAL)** - 审核完成状态

### 审核规则

- **通过 (approved)**：报告流转到下一个审核步骤
  - 培养人通过 → 流转到组织委员
  - 组织委员通过 → 流转到支部书记
  - 支部书记通过 → 流转到最终完成
  - 最终完成 → 报告状态标记为 APPROVED

- **退回 (rejected)**：报告退回到上一个审核步骤
  - 组织委员退回 → 返回到培养人
  - 支部书记退回 → 返回到组织委员
  - 最终审核退回 → 返回到支部书记
  - 培养人退回 → 仍为培养人（第一步）

---

## 💻 使用示例

### Python 示例

```python
import requests

# 配置
BASE_URL = "http://localhost:8000/api"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 登录获取 Token
login_data = {
    "username": "trainer1",
    "password": "123456"
}
response = requests.post(
    f"{BASE_URL}/auth/token",
    data=login_data
)
token = response.json()["access_token"]

# 2. 查询待审核报告
response = requests.get(
    f"{BASE_URL}/reports/pending/list",
    headers={"Authorization": f"Bearer {token}"}
)
pending_reports = response.json()
print(f"待审核报告数量: {len(pending_reports)}")

# 3. 审核报告（通过）
report_id = pending_reports[0]["id"]
review_data = {
    "status": "approved",
    "comment": "内容详实，思想积极，同意通过"
}

response = requests.post(
    f"{BASE_URL}/reports/{report_id}/review",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=review_data
)

result = response.json()
if result["success"]:
    print(f"审核成功: {result['message']}")
    print(f"当前步骤: {result['data']['current_step']}")

# 4. 查询审核记录
response = requests.get(
    f"{BASE_URL}/reports/{report_id}/reviews",
    headers={"Authorization": f"Bearer {token}"}
)
reviews = response.json()
print(f"审核记录数量: {len(reviews)}")
for review in reviews:
    print(f"- {review['role']}: {review['status']} - {review['comment']}")
```

### JavaScript/Axios 示例

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api';

// 创建客户端实例
const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 1. 登录获取 Token
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await client.post('/auth/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  
  const token = response.data.access_token;
  
  // 设置 Token 到后续请求
  client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  
  return token;
}

// 2. 查询待审核报告
async function getPendingReports() {
  const response = await client.get('/reports/pending/list');
  return response.data;
}

// 3. 审核报告（通过）
async function approveReport(reportId, comment) {
  const response = await client.post(`/reports/${reportId}/review`, {
    status: 'approved',
    comment: comment
  });
  
  return response.data;
}

// 4. 审核报告（退回）
async function rejectReport(reportId, comment) {
  const response = await client.post(`/reports/${reportId}/review`, {
    status: 'rejected',
    comment: comment
  });
  
  return response.data;
}

// 5. 查询审核记录
async function getReviewHistory(reportId) {
  const response = await client.get(`/reports/${reportId}/reviews`);
  return response.data;
}

// 使用示例
(async () => {
  try {
    // 登录
    await login('trainer1', '123456');
    
    // 获取待审核报告
    const pending = await getPendingReports();
    console.log(`待审核报告数量: ${pending.length}`);
    
    if (pending.length > 0) {
      const reportId = pending[0].id;
      
      // 审核通过
      const result = await approveReport(reportId, '内容详实，思想积极，同意通过');
      console.log(`审核成功: ${result.message}`);
      
      // 查询审核历史
      const reviews = await getReviewHistory(reportId);
      reviews.forEach(review => {
        console.log(`- ${review.role}: ${review.status} - ${review.comment}`);
      });
    }
  } catch (error) {
    console.error('操作失败:', error.response?.data || error.message);
  }
})();
```

### cURL 示例

```bash
# 1. 登录获取 Token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=trainer1&password=123456"

# 保存返回的 access_token
TOKEN="your_access_token_here"

# 2. 查询待审核报告
curl -X GET "http://localhost:8000/api/reports/pending/list" \
  -H "Authorization: Bearer $TOKEN"

# 3. 审核报告（通过）
curl -X POST "http://localhost:8000/api/reports/1/review" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "comment": "内容详实，思想积极，同意通过"
  }'

# 4. 审核报告（退回）
curl -X POST "http://localhost:8000/api/reports/1/review" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "comment": "内容需要补充完善，请重新提交"
  }'

# 5. 查询审核记录
curl -X GET "http://localhost:8000/api/reports/1/reviews" \
  -H "Authorization: Bearer $TOKEN"

# 6. 下载报告
curl -X GET "http://localhost:8000/api/reports/1/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o report.pdf
```

---

## ⚠️ 错误处理

### 常见错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 失效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "detail": "错误详细信息"
}
```

### 错误示例

#### 参数错误
```json
{
  "detail": "审核状态必须是 'approved' 或 'rejected'"
}
```

#### 权限错误
```json
{
  "detail": "当前步骤需要 trainer 角色审核，您的角色是 activist"
}
```

#### 资源不存在
```json
{
  "detail": "报告 ID 999 不存在"
}
```

#### Token 失效
```json
{
  "detail": "Could not validate credentials"
}
```

---

## 📊 数据字典

### Report 状态

| 字段 | 说明 |
|------|------|
| current_step | 当前审核步骤：activist/trainer/organizer/secretary/final |
| status | 报告状态：pending（待审核）/rejected（已驳回）/approved（已通过） |

### Review 状态

| 字段 | 说明 |
|------|------|
| status | 审核状态：pending（待审核）/approved（通过）/rejected（驳回） |

### User 角色

| 角色 | 说明 |
|------|------|
| activist | 积极分子，可提交报告 |
| trainer | 培养人，第一级审核 |
| organizer | 组织委员，第二级审核 |
| secretary | 支部书记，第三级审核 |
| final | 总支书记，最终审核 |

---

## 📝 注意事项

1. **Token 有效期**: JWT Token 默认有效期为 30 天，过期后需要重新登录
2. **权限检查**: 每个审核步骤只能由对应角色的用户审核
3. **状态流转**: 审核状态会自动更新，无需手动修改
4. **审核记录**: 每次审核都会在 Review 表中创建一条记录
5. **退回机制**: 退回后报告会返回到上一个审核步骤
6. **并发安全**: 使用数据库事务确保审核操作的原子性
7. **文件上传**: 支持 PDF 和 Word 格式，建议大小不超过 10MB

---

**最后更新**: 2024-12-02  
**API 版本**: v1.0.0





























