#!/bin/bash

# Enhanced AICore 3.0 Fusion - GitHub推送脚本
# 使用说明：在本地环境中运行此脚本完成推送

echo "🚀 Enhanced AICore 3.0 Fusion - GitHub推送脚本"
echo "================================================"

# 检查git状态
echo "📋 检查git状态..."
git status

echo ""
echo "💡 推送选项："
echo "1. 使用HTTPS (需要Personal Access Token)"
echo "2. 使用SSH (需要SSH密钥配置)"
echo ""

read -p "请选择推送方式 (1/2): " choice

case $choice in
    1)
        echo "🔐 使用HTTPS推送..."
        echo "请准备您的GitHub Personal Access Token"
        echo "获取方式：GitHub Settings > Developer settings > Personal access tokens"
        echo ""
        git push origin main
        ;;
    2)
        echo "🔑 使用SSH推送..."
        echo "设置SSH远程URL..."
        git remote set-url origin git@github.com:alexchuang650730/aicore0624.git
        echo "推送到GitHub..."
        git push origin main
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 推送成功！"
    echo "📍 项目地址: https://github.com/alexchuang650730/aicore0624"
    echo ""
    echo "✅ Enhanced AICore 3.0 Fusion 已成功部署到GitHub！"
else
    echo ""
    echo "❌ 推送失败，请检查网络连接和认证信息"
fi

