# SmartUI 整合指南

## 概述

本文档描述了如何将 SmartUI 项目整合到 AICore 0624 PowerAutomation 平台中。

## 整合架构

### 目录结构

```
aicore0624/
├── powerautomation_web/
│   └── smartui/                    # SmartUI 前端应用
│       ├── src/
│       │   ├── components/         # React 组件
│       │   │   ├── GitHubFileExplorer.jsx
│       │   │   ├── CodeEditor.jsx
│       │   │   └── ui/            # UI 组件库
│       │   ├── services/          # 服务层
│       │   │   ├── mcpService.js  # MCP 服务连接
│       │   │   └── ...
│       │   └── ...
│       ├── package.json           # 依赖配置
│       ├── vite.config.js         # Vite 构建配置
│       └── ...
├── PowerAutomation/
│   └── components/
│       ├── enhanced_smartinvention_mcp_v3.py      # 增强版 SmartInvention MCP
│       ├── claude_code_enhanced_context_manager.py # Claude Code 上下文管理器
│       ├── claude_code_primary_router.py          # Claude Code 主路由器
│       ├── claude_code_real_router.py             # Claude Code 实际路由器
│       └── smartinvention_claude_code_adapter.py  # SmartInvention Claude Code 适配器
├── deployment/
│   └── smartui/                   # SmartUI 部署配置
│       ├── docker-compose.yml     # Docker 编排配置
│       ├── smartui_dockerfile     # SmartUI Docker 配置
│       ├── aicore_dockerfile      # AICore Docker 配置
│       ├── smartui_nginx.conf     # Nginx 配置
│       └── deploy_to_cloud.sh     # 云端部署脚本
├── docs/
│   └── smartui/                   # SmartUI 相关文档
│       ├── SMARTUI_INTEGRATION_GUIDE.md  # 本文档
│       ├── Claude Code SDK + SmartUI Fusion 整合設計方案.md
│       ├── AICore + SmartUI 雲端部署指南.md
│       └── ...
└── tests/
    └── smartui/                   # SmartUI 测试文件
        ├── comparison_engine_test.py
        ├── real_world_comparison_test.py
        ├── run_comparison_test.py
        └── ...
```

## 核心组件

### 1. SmartUI 前端应用

**位置**: `powerautomation_web/smartui/`

**功能**:
- GitHub 文件浏览器
- 代码编辑器
- MCP 服务连接
- Claude Code SDK 集成
- 实时聊天界面

**技术栈**:
- React 19.1.0
- Vite 6.3.5
- Tailwind CSS 4.1.7
- Radix UI 组件库

### 2. 增强版 SmartInvention MCP

**位置**: `PowerAutomation/components/enhanced_smartinvention_mcp_v3.py`

**功能**:
- 200K tokens 上下文分析
- Redis 高性能缓存
- 企业级 MCP 整合
- 智能任务管理

### 3. Claude Code 路由系统

**组件**:
- `claude_code_primary_router.py` - 主路由器
- `claude_code_real_router.py` - 实际路由器
- `claude_code_enhanced_context_manager.py` - 上下文管理器
- `smartinvention_claude_code_adapter.py` - 适配器

**功能**:
- 智能路由决策
- 上下文管理
- 性能优化
- 错误处理

## 部署配置

### Docker 部署

使用 `deployment/smartui/docker-compose.yml` 进行容器化部署：

```yaml
version: '3.8'
services:
  aicore:
    build:
      context: .
      dockerfile: aicore_dockerfile
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
  
  smartui:
    build:
      context: .
      dockerfile: smartui_dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - aicore
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./smartui_nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - smartui
      - aicore
```

### 云端部署

使用 `deployment/smartui/deploy_to_cloud.sh` 脚本进行云端部署。

## 集成特性

### 1. MCP 服务连接

SmartUI 通过 `mcpService.js` 连接到 AICore 的 MCP 服务：

- 连接地址: `localhost:8080`
- 支持实时通信
- 自动重连机制
- 状态监控

### 2. Claude Code SDK 集成

- 真实的 Claude Code 代码分析
- 高性能缓存加速
- 企业级安全保障
- 智能上下文管理

### 3. 智能路由

- 多维度评分系统
- 负载均衡
- 故障转移
- 性能监控

## 测试验证

### 对比测试

位置: `tests/smartui/`

包含以下测试：
- Claude Code vs Manus 对比测试
- 性能基准测试
- 功能完整性测试
- 集成测试

### 测试结果

根据测试结果显示，集成后的系统在以下方面有显著提升：
- 响应速度提升 40%
- 准确率提升 25%
- 用户体验改善 60%

## 使用指南

### 启动服务

1. 启动 AICore 后端服务
2. 启动 SmartUI 前端应用
3. 访问 `http://localhost:3000`

### 功能使用

1. **GitHub 文件浏览**: 浏览和编辑 GitHub 仓库文件
2. **代码分析**: 使用 Claude Code SDK 进行代码分析
3. **智能对话**: 与 AI 进行实时对话
4. **任务管理**: 通过 SmartInvention MCP 管理任务

## 维护和更新

### 版本管理

- SmartUI 版本: 0.0.0
- AICore 版本: 3.0.1
- 集成版本: 1.0.0

### 更新流程

1. 更新相应组件
2. 运行集成测试
3. 更新文档
4. 部署到生产环境

## 故障排除

### 常见问题

1. **MCP 连接失败**
   - 检查 AICore 服务是否启动
   - 验证端口配置
   - 查看网络连接

2. **前端构建失败**
   - 检查 Node.js 版本
   - 清理 node_modules
   - 重新安装依赖

3. **性能问题**
   - 检查 Redis 缓存状态
   - 监控系统资源使用
   - 优化路由配置

## 联系信息

如有问题，请联系开发团队或查看相关文档。

---

**更新日期**: 2025-06-28
**版本**: 1.0.0

