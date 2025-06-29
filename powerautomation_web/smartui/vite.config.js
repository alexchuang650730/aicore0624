import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// 生成时间戳用于缓存破坏
const timestamp = Date.now()

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    // 确保环境变量在构建时正确替换
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || 'https://8080-i7wsi1yp91r4t34rn26rh-79fe3299.manusvm.computer/api'),
    'import.meta.env.VITE_BACKEND_URL': JSON.stringify(process.env.VITE_BACKEND_URL || 'https://8080-i7wsi1yp91r4t34rn26rh-79fe3299.manusvm.computer'),
    // 添加构建时间戳
    'import.meta.env.VITE_BUILD_TIMESTAMP': JSON.stringify(timestamp),
  },
  build: {
    // 强制缓存破坏策略
    rollupOptions: {
      output: {
        // 为所有文件添加时间戳
        entryFileNames: `assets/[name]-[hash]-${timestamp}.js`,
        chunkFileNames: `assets/[name]-[hash]-${timestamp}.js`,
        assetFileNames: `assets/[name]-[hash]-${timestamp}.[ext]`,
        // 确保每次构建都生成新的文件名
        manualChunks: undefined,
      },
    },
    // 清除输出目录
    emptyOutDir: true,
    // 生成源映射用于调试
    sourcemap: false,
  },
  // 开发服务器配置
  server: {
    // 禁用缓存
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  },
})

