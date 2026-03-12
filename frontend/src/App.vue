<template>
  <router-view />
</template>

<script setup>
</script>

<style>
:root {
  --brand-primary: #2563eb;
  --brand-secondary: #0ea5e9;
  --brand-surface: #ffffff;
  --brand-border: #e5e7eb;
  --brand-text: #0f172a;
  --brand-muted: #6b7280;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: 'Segoe UI', 'Noto Sans SC', 'PingFang SC', -apple-system, BlinkMacSystemFont,
    'Helvetica Neue', Arial, sans-serif;
  color: var(--brand-text);
  background: radial-gradient(1200px at 15% 20%, #e3edff 0, transparent 45%),
    radial-gradient(1000px at 80% 0%, #d2f4ff 0, transparent 40%),
    linear-gradient(135deg, #f7f9ff 0%, #eef3ff 45%, #e8f4f1 100%);
  line-height: 1.6;
}

a {
  color: var(--brand-primary);
  text-decoration: none;
}

a:hover {
  color: #1d4ed8;
}

/* 精细的滚动条样式，保持轻盈感 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 999px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #c3d5ff, #9ad8ff);
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.7);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #91b5ff, #6cc8ff);
}
</style>




















