# 前端快速启动指南

## 1. 安装依赖

```bash
cd frontend
npm install
```

或使用 pnpm (推荐)：

```bash
cd frontend
pnpm install
```

## 2. 配置后端 API 地址

后端默认运行在 `http://localhost:8000`，前端配置了代理，所有 `/api` 请求会自动转发到后端。

如需修改，编辑 `vite.config.js`：

```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 修改为你的后端地址
      changeOrigin: true
    }
  }
}
```

## 3. 启动开发服务器

```bash
npm run dev
```

浏览器访问：http://localhost:5173

## 4. 登录测试

使用以下测试账号登录：

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 编制人 | activist1 | 123456 | 可以提交思想汇报 |
| 培养人 | trainer1 | 123456 | 审核第一级 |
| 组织委员 | organizer1 | 123456 | 审核第二级 |
| 支部书记 | secretary1 | 123456 | 审核第三级 |
| 总支书记 | final1 | 123456 | 查看所有汇报 |

## 5. 功能说明

### 编制人（积极分子）
- 提交思想汇报（上传 Word 文档）
- 查看自己的提交记录
- 下载已提交的文档

### 培养人/组织委员/支部书记
- 查看待审核的汇报列表
- 查看汇报详情
- 下载汇报文档
- 通过或驳回汇报

### 总支书记
- 查看所有汇报总览
- 查看统计数据
- 可按状态筛选汇报
- 对最终审核步骤的汇报进行审核

## 6. 生产构建

```bash
npm run build
```

构建产物在 `dist` 目录，可以部署到任何静态服务器。

## 7. 部署示例

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    # SPA 路由配置
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 8. 常见问题

### Q: 登录后显示 401 错误
**A**: 检查后端是否正常运行，确认后端地址配置正确。

### Q: 文件上传失败
**A**: 检查文件格式（只支持 .doc/.docx），文件大小（不超过 10MB）。

### Q: 路由跳转后页面空白
**A**: 检查对应的 Vue 组件是否存在，路由配置是否正确。

### Q: Element Plus 组件样式错误
**A**: 确保安装了所有依赖，尝试删除 `node_modules` 重新安装。

## 9. 开发建议

1. **使用 Vue DevTools** - 浏览器安装 Vue DevTools 扩展，方便调试
2. **使用 Pinia DevTools** - 查看和调试状态管理
3. **代码格式化** - 建议安装 ESLint 和 Prettier
4. **类型检查** - 如需 TypeScript 支持，可以迁移到 TS

## 10. 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口定义
│   │   ├── auth.js       # 认证相关 API
│   │   └── report.js     # 报告相关 API
│   ├── assets/           # 静态资源
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # Pinia 状态管理
│   │   └── user.js       # 用户状态
│   ├── utils/            # 工具函数
│   │   ├── constants.js  # 常量定义
│   │   └── request.js    # axios 封装
│   ├── views/            # 页面组件
│   │   ├── Login.vue     # 登录页
│   │   ├── Dashboard.vue # 首页
│   │   ├── activist/     # 编制人页面
│   │   ├── trainer/      # 培养人页面
│   │   ├── organizer/    # 组织委员页面
│   │   ├── secretary/    # 支部书记页面
│   │   └── final/        # 总支书记页面
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── index.html            # HTML 入口
├── vite.config.js        # Vite 配置
└── package.json          # 项目配置
```

## 技术支持

如遇到问题，请检查：
1. Node.js 版本 >= 16
2. 后端服务是否正常运行
3. 浏览器控制台是否有错误信息
4. 网络请求是否正常（查看 Network 标签）





























