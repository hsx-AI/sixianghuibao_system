import { previewReport } from '@/api/report'
import { ElMessage } from 'element-plus'

/**
 * 处理报告预览
 * @param {number} id 报告ID
 * @param {Ref} loadingRef loading状态的ref对象（可选）
 */
export const handlePreviewReport = async (id, loadingRef = null) => {
  const win = window.open('', '_blank')
  if (!win) {
    ElMessage.warning('浏览器阻止了新窗口，请允许弹窗后重试')
    return
  }
  
  // 写入 Loading 页面
  win.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>正在加载预览...</title>
        <meta charset="utf-8">
        <style>
          body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #303133;
          }
          .loader {
            border: 4px solid #e4e7ed;
            border-top: 4px solid #409eff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
          }
          .message {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 8px;
          }
          .sub-message {
            font-size: 14px;
            color: #909399;
          }
          .container {
            text-align: center;
            padding: 32px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="loader"></div>
          <div class="message">正在生成预览...</div>
          <div class="sub-message">首次转换可能需要较长时间，请耐心等待</div>
        </div>
      </body>
    </html>
  `)

  if (loadingRef) loadingRef.value = true
  
  try {
    const blob = await previewReport(id)
    const url = window.URL.createObjectURL(blob)
    
    // 重定向到 Blob URL
    win.location.href = url
    
    // 10分钟后清理 URL
    window.setTimeout(() => URL.revokeObjectURL(url), 10 * 60 * 1000)
    
  } catch (error) {
    console.error('预览失败:', error)
    // 在新窗口显示错误信息
    win.document.body.innerHTML = `
      <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5;">
        <div style="text-align: center; padding: 32px; background: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
          <div style="color: #f56c6c; font-size: 48px; margin-bottom: 16px;">✕</div>
          <h3 style="margin: 0 0 8px; color: #303133;">预览加载失败</h3>
          <p style="margin: 0 0 24px; color: #909399;">${error.message || '服务器处理请求时发生错误'}</p>
          <button onclick="window.close()" style="padding: 8px 20px; cursor: pointer; background: #fff; border: 1px solid #dcdfe6; border-radius: 4px; color: #606266; font-size: 14px; transition: all 0.3s;">关闭窗口</button>
        </div>
      </div>
    `
  } finally {
    if (loadingRef) loadingRef.value = false
  }
}
