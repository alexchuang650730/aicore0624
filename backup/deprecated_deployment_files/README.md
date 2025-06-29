# 过时部署文件备份目录

## 📋 目录说明

此目录包含了从 AICore0624 项目主目录中移动过来的过时和冗余部署文件。这些文件被保留以供历史参考和可能的回滚需求。

## 📁 目录结构

### scripts/
包含过时的部署和测试脚本：
- `install.sh` - 旧的安装脚本（功能已被 `init_aicore.sh` 替代）
- `test_auto_deployment.sh` - 旧的自动部署测试脚本
- `deploy_and_test_ec2.sh` - 旧的 EC2 部署测试脚本
- `test_ec2_deployment.sh` - 旧的 EC2 部署测试脚本
- `mock_deployment_api.py` - 旧的模拟部署 API（已被新的 `mock_local_environment.py` 替代）
- `deploy.sh` - PowerAutomation-v2 的旧版本部署脚本

### configs/
包含过时的配置和报告文件：
- `enhanced_vscode_installer_mcp_registration_*.json` - VSCode 安装器 MCP 注册配置文件（多个时间戳版本）
- `vscode_extension_test_flow_report_*.json` - VSCode 扩展测试流程报告
- `vsix_test_result_*.json` - VSIX 测试结果文件
- `vsix_deployment_report_*.json` - VSIX 部署报告

### test_data/
包含过时的测试数据包：
- `TC001_Complete_Fixed_Test_Package.tar.gz` - 完整的修复测试包
- `TC001_Login_Test_Recording.tar.gz` - 登录测试录制数据
- `TC001_Screenshots_and_Video.tar.gz` - 截图和视频测试数据

## 🔄 替代方案

### 当前活跃的部署架构
这些过时文件已被以下现代化组件替代：

1. **统一部署入口**: `init_aicore.sh`
2. **分布式部署协调**: `PowerAutomation/components/deployment_mcp/`
3. **完整测试套件**: `test_deployment_coordinator.py`
4. **模拟环境**: `mock_local_environment.py`

### 新的部署流程
```
EC2 主平台部署
       ↓
远程部署协调器
       ↓
本地环境初始化 (init_aicore.sh)
       ↓
组件启动和验证
```

## ⚠️ 使用注意事项

1. **不建议使用**: 这些文件已过时，不建议在新的部署中使用
2. **仅供参考**: 保留这些文件仅用于历史参考和理解演进过程
3. **定期清理**: 建议定期评估是否需要继续保留这些文件

## 📅 备份时间

- **备份日期**: 2025-06-29
- **原因**: 项目结构优化和部署流程现代化
- **替代版本**: 新的分布式部署协调机制

## 🗑️ 清理计划

建议在以下情况下考虑清理这些备份文件：
- 新部署机制稳定运行 6 个月以上
- 确认不需要回滚到旧版本
- 存储空间需要优化时

---

*此备份目录由 AICore0624 项目清理工具自动创建*

