# PowerAutomation API 配置說明

## 快速開始

### 1. 複製配置模板
```bash
cp config/api_config.template.json config/api_config.json
```

### 2. 編輯配置文件
在 `config/api_config.json` 中填入您的實際 API 密鑰：

```json
{
  "api_keys": {
    "claude_api_key": "您的 Claude API 密鑰",
    "openai_api_key": "您的 OpenAI API 密鑰（可選）",
    "manus_api_key": "您的 Manus API 密鑰（可選）"
  },
  "authentication": {
    "manus_username": "您的 Manus 用戶名",
    "manus_password": "您的 Manus 密碼"
  }
}
```

### 3. 安全注意事項

⚠️ **重要**: 
- 切勿將包含真實 API 密鑰的 `api_config.json` 提交到 Git
- 該文件已添加到 `.gitignore` 中
- 建議使用環境變量來管理敏感信息

### 4. 環境變量配置（推薦）

```bash
export CLAUDE_API_KEY="您的 Claude API 密鑰"
export MANUS_USERNAME="您的 Manus 用戶名"
export MANUS_PASSWORD="您的 Manus 密碼"
```

### 5. 驗證配置

運行以下命令驗證配置是否正確：

```bash
python3 -c "
import json
with open('config/api_config.json', 'r') as f:
    config = json.load(f)
    print('✅ 配置文件格式正確')
    if config['api_keys']['claude_api_key'] != 'YOUR_CLAUDE_API_KEY_HERE':
        print('✅ Claude API 密鑰已配置')
    else:
        print('⚠️ 請配置 Claude API 密鑰')
"
```

## 獲取 API 密鑰

### Claude API
1. 訪問 [Anthropic Console](https://console.anthropic.com/)
2. 創建帳戶並獲取 API 密鑰

### Manus 平台
1. 訪問 [Manus 平台](https://manus.chat/)
2. 註冊帳戶並獲取認證信息

## 故障排除

### 常見問題

1. **配置文件不存在**
   ```bash
   cp config/api_config.template.json config/api_config.json
   ```

2. **API 密鑰無效**
   - 檢查密鑰是否正確複製
   - 確認密鑰是否已激活
   - 檢查 API 配額是否充足

3. **網絡連接問題**
   - 檢查網絡連接
   - 確認防火牆設置
   - 驗證 API 端點可訪問性

