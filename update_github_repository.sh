#!/bin/bash

# AICore Human-in-the-Loop Integration System
# GitHub 倉庫更新腳本
# 版本: 3.0.0
# 日期: 2025-06-24

set -e  # 遇到錯誤立即退出

echo "🚀 AICore Human-in-the-Loop Integration System GitHub 更新腳本"
echo "================================================================"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查是否在正確的目錄
if [ ! -f "PROJECT_SUMMARY.md" ]; then
    echo -e "${RED}❌ 錯誤: 請在 aicore0624 項目根目錄執行此腳本${NC}"
    exit 1
fi

echo -e "${BLUE}📋 檢查Git狀態...${NC}"
git status

echo ""
echo -e "${YELLOW}⚠️  即將更新以下檔案到GitHub倉庫:${NC}"
echo ""

# 核心系統檔案
echo -e "${GREEN}🔥 核心系統檔案:${NC}"
echo "  - aicore_master_system.py"
echo "  - aicore_dynamic_router.py"
echo "  - expert_invocation_system.py"
echo "  - deep_testing_framework.py"
echo "  - incremental_optimization_system.py"
echo ""

# 部署腳本
echo -e "${GREEN}🚀 部署腳本:${NC}"
echo "  - deploy_aicore_system.sh"
echo "  - mac_local_deployment_optimized.sh"
echo "  - mac_integration_deployment.sh"
echo "  - ssh_remote_deployment.sh"
echo "  - deploy_vsix.sh"
echo "  - deploy_vsix_mac.sh"
echo ""

# 文檔檔案
echo -e "${GREEN}📚 文檔檔案:${NC}"
echo "  - AICore_Complete_Guide.md"
echo "  - human_loop_mcp_analysis.md"
echo "  - GitHub_Update_File_List.md"
echo "  - Mac_Execution_Guide.md"
echo "  - Mac_Local_Deployment_Guide.md"
echo "  - SSH_Remote_Deployment_Guide.md"
echo ""

# 配置檔案
echo -e "${GREEN}⚙️  配置檔案:${NC}"
echo "  - real_mcp_connection_config.py"
echo "  - enhanced_vscode_installer_mcp_registration_config_20250624_002244.json"
echo "  - requirements.txt"
echo ""

# 確認提示
echo -e "${YELLOW}❓ 是否繼續更新? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 更新已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🔄 開始Git更新流程...${NC}"

# 第一批：核心系統檔案
echo -e "${GREEN}📦 第一批: 添加核心系統檔案...${NC}"
git add aicore_master_system.py || echo "檔案不存在，跳過"
git add aicore_dynamic_router.py || echo "檔案不存在，跳過"
git add expert_invocation_system.py || echo "檔案不存在，跳過"

if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  沒有核心系統檔案需要提交${NC}"
else
    git commit -m "feat: Add AICore Human-in-the-Loop Integration System core components

- Add aicore_master_system.py: Main controller and system integration
- Add aicore_dynamic_router.py: Dynamic routing system with intelligent decision making
- Add expert_invocation_system.py: Expert invocation mechanism with 7 expert types"
    echo -e "${GREEN}✅ 核心系統檔案提交完成${NC}"
fi

# 第二批：測試和優化系統
echo -e "${GREEN}📦 第二批: 添加測試和優化系統...${NC}"
git add deep_testing_framework.py || echo "檔案不存在，跳過"
git add incremental_optimization_system.py || echo "檔案不存在，跳過"

if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  沒有測試和優化檔案需要提交${NC}"
else
    git commit -m "feat: Add deep testing framework and incremental optimization system

- Add deep_testing_framework.py: Comprehensive testing with 5 test types
- Add incremental_optimization_system.py: Continuous learning and performance optimization"
    echo -e "${GREEN}✅ 測試和優化系統提交完成${NC}"
fi

# 第三批：部署腳本
echo -e "${GREEN}📦 第三批: 添加部署腳本...${NC}"
git add deploy_aicore_system.sh || echo "檔案不存在，跳過"
git add mac_local_deployment_optimized.sh || echo "檔案不存在，跳過"
git add mac_integration_deployment.sh || echo "檔案不存在，跳過"
git add ssh_remote_deployment.sh || echo "檔案不存在，跳過"
git add deploy_vsix.sh || echo "檔案不存在，跳過"
git add deploy_vsix_mac.sh || echo "檔案不存在，跳過"

if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  沒有部署腳本需要提交${NC}"
else
    git commit -m "feat: Add comprehensive deployment scripts for AICore system

- Add deploy_aicore_system.sh: One-click deployment script for AICore system
- Add mac_local_deployment_optimized.sh: Optimized Mac local deployment
- Add mac_integration_deployment.sh: Mac integration deployment
- Add ssh_remote_deployment.sh: SSH remote deployment capability
- Add deploy_vsix.sh: VSIX deployment script
- Add deploy_vsix_mac.sh: Mac-specific VSIX deployment"
    echo -e "${GREEN}✅ 部署腳本提交完成${NC}"
fi

# 第四批：文檔和指南
echo -e "${GREEN}📦 第四批: 添加文檔和指南...${NC}"
git add AICore_Complete_Guide.md || echo "檔案不存在，跳過"
git add human_loop_mcp_analysis.md || echo "檔案不存在，跳過"
git add GitHub_Update_File_List.md || echo "檔案不存在，跳過"
git add Mac_Execution_Guide.md || echo "檔案不存在，跳過"
git add Mac_Local_Deployment_Guide.md || echo "檔案不存在，跳過"
git add SSH_Remote_Deployment_Guide.md || echo "檔案不存在，跳過"

if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  沒有文檔檔案需要提交${NC}"
else
    git commit -m "docs: Add complete guide and documentation for AICore system

- Add AICore_Complete_Guide.md: Comprehensive usage guide and documentation
- Add human_loop_mcp_analysis.md: Human Loop MCP analysis and integration
- Add GitHub_Update_File_List.md: File update checklist for GitHub
- Add Mac_Execution_Guide.md: Mac execution guide
- Add Mac_Local_Deployment_Guide.md: Mac local deployment guide
- Add SSH_Remote_Deployment_Guide.md: SSH remote deployment guide"
    echo -e "${GREEN}✅ 文檔檔案提交完成${NC}"
fi

# 第五批：配置和其他檔案
echo -e "${GREEN}📦 第五批: 添加配置和其他檔案...${NC}"
git add real_mcp_connection_config.py || echo "檔案不存在，跳過"
git add enhanced_vscode_installer_mcp_registration_config_20250624_002244.json || echo "檔案不存在，跳過"
git add requirements.txt || echo "檔案不存在，跳過"

# 添加其他分析和報告檔案
git add aicore0623_to_0624_summary.md || echo "檔案不存在，跳過"
git add enhanced_test_flow_mcp_v5_optimization_summary.md || echo "檔案不存在，跳過"
git add enhanced_test_flow_mcp_v5_testing_guide.md || echo "檔案不存在，跳過"
git add vsix_deployment_code_architecture.md || echo "檔案不存在，跳過"
git add vsix_deployment_strategy_analysis.md || echo "檔案不存在，跳過"
git add vsix_deployment_workflow_documentation.md || echo "檔案不存在，跳過"
git add mac_vsix_deployment_architecture.md || echo "檔案不存在，跳過"

if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  沒有配置和其他檔案需要提交${NC}"
else
    git commit -m "feat: Add configuration files and analysis documentation

- Add real_mcp_connection_config.py: Real MCP connection configuration
- Add MCP registration configuration and requirements
- Add analysis and architecture documentation
- Add deployment strategy and workflow documentation"
    echo -e "${GREEN}✅ 配置和其他檔案提交完成${NC}"
fi

# 創建版本標籤
echo ""
echo -e "${BLUE}🏷️  創建版本標籤...${NC}"
echo -e "${YELLOW}❓ 是否創建版本標籤 v3.0.0? (y/N)${NC}"
read -r tag_response
if [[ "$tag_response" =~ ^[Yy]$ ]]; then
    git tag -a v3.0.0 -m "AICore Human-in-the-Loop Integration System v3.0.0

Features:
- Complete AICore Human-in-the-Loop Integration System
- Dynamic routing system with intelligent decision making
- Expert invocation mechanism with 7 expert types
- Deep testing framework with 5 test types
- Incremental optimization system with continuous learning
- Seamless Human Loop MCP integration
- Comprehensive deployment scripts and guides
- Mac and SSH remote deployment support"
    echo -e "${GREEN}✅ 版本標籤 v3.0.0 創建完成${NC}"
fi

# 推送到遠程倉庫
echo ""
echo -e "${BLUE}📤 推送到GitHub...${NC}"
echo -e "${YELLOW}❓ 是否推送到GitHub遠程倉庫? (y/N)${NC}"
read -r push_response
if [[ "$push_response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🔄 推送提交...${NC}"
    git push origin main
    
    if git tag -l | grep -q "v3.0.0"; then
        echo -e "${BLUE}🔄 推送標籤...${NC}"
        git push origin v3.0.0
    fi
    
    echo -e "${GREEN}✅ 推送完成${NC}"
else
    echo -e "${YELLOW}⚠️  推送已跳過，請手動執行: git push origin main${NC}"
fi

# 顯示最終狀態
echo ""
echo -e "${BLUE}📊 最終Git狀態:${NC}"
git status

echo ""
echo -e "${GREEN}🎉 AICore Human-in-the-Loop Integration System 更新完成!${NC}"
echo ""
echo -e "${BLUE}📋 更新摘要:${NC}"
echo "  ✅ 核心系統組件已更新"
echo "  ✅ 測試和優化系統已更新"
echo "  ✅ 部署腳本已更新"
echo "  ✅ 完整文檔已更新"
echo "  ✅ 配置檔案已更新"

if git tag -l | grep -q "v3.0.0"; then
    echo "  ✅ 版本標籤 v3.0.0 已創建"
fi

echo ""
echo -e "${BLUE}🔗 GitHub倉庫: https://github.com/alexchuang650730/aicore0624${NC}"
echo -e "${BLUE}📖 完整指南: AICore_Complete_Guide.md${NC}"
echo ""
echo -e "${GREEN}感謝使用 AICore Human-in-the-Loop Integration System! 🚀${NC}"

