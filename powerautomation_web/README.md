# PowerAutomation Web 系統

智能編程助手 - 三角色權限系統

## 🚀 快速開始

### 環境要求
- Node.js >= 18.0.0
- npm 或 pnpm

### 安裝和運行

#### 1. 啟動後端服務器
```bash
cd backend
npm install
npm start
```
後端將運行在 http://localhost:3001

#### 2. 啟動前端服務器
```bash
cd frontend  
pnpm install
pnpm run dev --host
```
前端將運行在 http://localhost:5175

### 測試賬號

#### API Key 登錄 (高級模式)
- **管理員**: `admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U`
- **開發者**: `dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg`  
- **用戶**: `user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k`

#### OAuth 登錄 (用戶模式)
- GitHub 登錄 (模擬)
- Google 登錄 (模擬)

## 🔐 權限系統

### 三種角色
- **管理員 (Admin)**: 完整系統管理權限
- **開發者 (Developer)**: 開發工具和 API 訪問權限
- **用戶 (User)**: 基礎聊天和文件操作權限

### 功能對比

| 功能 | 管理員 | 開發者 | 用戶 |
|------|--------|--------|------|
| 系統統計 | ✅ | ❌ | ❌ |
| 用戶管理 | ✅ | ❌ | ❌ |
| MCP 訪問 | ✅ | ✅ | ❌ |
| 調試工具 | ✅ | ✅ | ❌ |
| 基礎聊天 | ✅ | ✅ | ✅ |

## 🏗️ 技術棧

### 前端
- React 18 + Vite
- shadcn/ui + Tailwind CSS
- Lucide React Icons

### 後端  
- Node.js + Express.js
- Socket.IO (實時通信)
- JWT 認證
- CORS + Helmet 安全

## 📁 項目結構

```
powerautomation_web/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # UI 組件
│   │   ├── App.jsx         # 主應用組件
│   │   └── main.jsx        # 入口文件
│   ├── package.json
│   └── vite.config.js
├── backend/                 # Node.js 後端
│   ├── src/
│   │   ├── routes/         # API 路由
│   │   ├── middleware/     # 中間件
│   │   └── server.js       # 服務器入口
│   └── package.json
├── config/                 # 配置文件
└── docs/                   # 文檔
```

## 🔧 開發指南

### API 端點

#### 認證
- `POST /api/auth/api-key` - API Key 登錄
- `POST /api/auth/oauth/github` - GitHub OAuth
- `POST /api/auth/email` - 郵箱登錄

#### 管理員
- `GET /api/admin/stats` - 系統統計
- `GET /api/admin/users` - 用戶管理

#### 系統
- `GET /api/system/monitoring` - 系統監控
- `POST /api/mcp/process` - MCP 處理

### 環境變量
```bash
NODE_ENV=development
JWT_SECRET=powerautomation_secret_key_2024
PORT=3001
```

## 🧪 測試

### 運行測試
```bash
# 後端測試
cd backend
npm test

# 前端測試  
cd frontend
pnpm test
```

### 手動測試
1. 訪問 http://localhost:5175
2. 選擇登錄方式 (用戶模式/高級模式)
3. 使用測試 API Key 登錄
4. 驗證角色權限和功能

## 📊 監控和日誌

### 健康檢查
```bash
curl http://localhost:3001/health
```

### 日誌查看
後端日誌會實時顯示在控制台，包括：
- API 請求記錄
- 用戶登錄事件  
- 錯誤信息

## 🚀 部署

### 生產構建
```bash
# 前端構建
cd frontend
pnpm run build

# 後端生產模式
cd backend  
NODE_ENV=production npm start
```

### Docker 部署 (可選)
```dockerfile
# 示例 Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

## 📝 更新日誌

### v1.0.0 (2025-06-25)
- ✅ 完整的三角色權限系統
- ✅ React + Node.js 技術棧
- ✅ JWT + API Key 認證
- ✅ 現代化 UI 設計
- ✅ 完整的測試覆蓋

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打開 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情

## 📞 聯繫我們

- 項目主頁: [GitHub Repository]
- 問題報告: [GitHub Issues]
- 郵箱: powerautomation@example.com

---

**PowerAutomation Team** © 2025

