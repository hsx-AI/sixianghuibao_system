# OA系统集成接口文档

本文档描述了如何将思想汇报系统与公司OA系统集成，以实现待办事项提醒功能。

## 1. 接口概述

本系统提供了一个专用的RESTful API接口，用于查询指定用户的待办事项统计。OA系统可以定期或按需调用此接口，获取用户的待审批报告数量和被退回报告数量。

- **基础URL**: `/api/integration/oa/todos`
- **请求方式**: `GET`
- **认证方式**: 目前开放接口，后续可根据需求添加 API Key 或 IP 白名单限制。

## 2. 接口详情

### 查询用户待办统计

查询指定用户名的待办任务数量，包括作为审核人的待审批任务和作为提交人的被退回任务。

**请求 URL**
```
GET /api/integration/oa/todos?username={username}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `username` | string | 是 | OA系统中的用户名（需与本系统用户名一致） |

**响应示例**

```json
{
  "username": "zhangsan",
  "pending_reviews": 5,
  "returned_reports": 2,
  "total": 7
}
```

**响应字段说明**

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `username` | string | 查询的用户名 |
| `pending_reviews` | integer | **待审批数量**。针对审核人员（培养人/组织委员/支部书记/总支书），表示有多少份报告等待其审核。 |
| `returned_reports` | integer | **被退回数量**。针对提交人员（积极分子），表示有多少份报告被退回需要修改。 |
| `total` | integer | 待办总数 (`pending_reviews` + `returned_reports`)。OA系统可直接使用此数值作为红点提醒。 |

**错误响应**

- `404 Not Found`: 用户不存在
- `422 Validation Error`: 参数格式错误

## 3. 集成建议

1.  **用户同步**: 确保OA系统中的用户名与思想汇报系统中的用户名保持一致。
2.  **调用频率**: 建议OA系统在用户登录时调用一次，或每隔一定时间（如5-10分钟）轮询一次。
3.  **提醒逻辑**:
    - 当 `total > 0` 时，在OA待办中心显示提醒。
    - 具体的待办详情链接，可跳转至思想汇报系统的登录页或对应列表页：
        - 审核人员跳转至: `/#/review` (系统会自动根据角色跳转到对应审核页)
        - 提交人员跳转至: `/#/my-reports` (查看历史提交及状态)

## 4. 示例代码 (Python)

```python
import requests

def check_todos(username):
    url = "http://thought-report-system/api/integration/oa/todos"
    params = {"username": username}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"用户 {username} 待办总数: {data['total']}")
            return data
        else:
            print(f"查询失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None
```
