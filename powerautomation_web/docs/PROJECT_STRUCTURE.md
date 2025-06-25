# PowerAutomation Web 項目結構

## 📁 目錄結構

```
powerautomation_web/
├── frontend/                       # 🎨 前端應用
│   ├── src/                       # 源代碼
│   │   ├── components/            # React 組件
│   │   │   ├── auth/             # 認證相關組件
│   │   │   ├── dashboard/        # 儀表板組件
│   │   │   └── common/           # 通用組件
│   │   ├── pages/                # 頁面組件
│   │   ├── hooks/                # 自定義 Hooks
│   │   ├── utils/                # 工具函數
│   │   └── assets/               # 靜態資源
│   ├── public/                   # 公共文件
│   └── dist/                     # 構建輸出
├── backend/                        # 🔧 後端服務
│   ├── src/                      # 源代碼
│   │   ├── routes/               # 路由定義
│   │   ├── controllers/          # 控制器
│   │   ├── middleware/           # 中間件
│   │   ├── models/               # 數據模型
│   │   └── services/             # 業務服務
│   ├── tests/                    # 測試文件
│   └── logs/                     # 日誌文件
├── shared/                         # 🔄 共享代碼
├── docs/                           # 📖 文檔
└── config/                         # ⚙️ 配置文件
```

## 🎯 設計理念

### 前端架構
- **React + Vite**: 現代化前端開發
- **組件化設計**: 可重用的 UI 組件
- **響應式佈局**: 適配各種設備
- **三角色界面**: 管理員、開發者、用戶專屬界面

### 後端架構
- **RESTful API**: 標準化接口設計
- **中間件模式**: 靈活的請求處理
- **服務層分離**: 清晰的業務邏輯
- **三角色權限**: 基於 API Key 的認證

### 整合特色
- **統一認證**: 與 PowerAutomation_local 對接
- **智慧UI**: 根據用戶角色動態調整
- **實時通信**: WebSocket 支援
- **數據可視化**: 豐富的圖表展示

## 📋 功能規劃

### 認證系統 (auth/)
- 登錄界面
- 角色選擇
- API Key 驗證
- OAuth 整合

### 儀表板 (dashboard/)
- 管理員控制台
- 開發者工具
- 用戶界面
- 數據統計

### 通用組件 (common/)
- UI 組件庫
- 佈局組件
- 工具組件
- 主題系統

## 🔧 技術棧

### 前端技術
- React 18
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts
- Lucide React

### 後端技術
- Node.js
- Express.js
- JWT 認證
- WebSocket
- 數據庫整合

### 開發工具
- ESLint
- Prettier
- TypeScript (可選)
- Jest 測試

## 🚀 開發流程

1. **初始化項目**: 設置前後端環境
2. **整合登錄系統**: 從 powerauto.aiweb 移植
3. **實現三角色界面**: 差異化用戶體驗
4. **API 對接**: 與 PowerAutomation_local 整合
5. **測試部署**: 完整的測試和部署流程

