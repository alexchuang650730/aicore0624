#!/usr/bin/env python3
"""
Web管理界面組件 - 從aicore0620 mcp_coordinator_server.py提取
提供MCP協調器的Web管理界面功能
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# MCP協調器Web界面HTML模板
COORDINATOR_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP協調器</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .status {
            font-size: 16px;
            color: #28a745;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 14px;
            color: #666;
        }
        .mcp-list {
            margin-top: 20px;
        }
        .mcp-item {
            display: flex;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .mcp-item:last-child {
            border-bottom: none;
        }
        .mcp-bullet {
            margin-right: 10px;
            font-size: 16px;
        }
        .mcp-name {
            font-weight: bold;
            color: #333;
        }
        .mcp-status {
            margin-left: 10px;
            color: #28a745;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
        .metrics-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .metrics-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        .metric-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .metric-label {
            font-weight: 500;
        }
        .metric-value {
            color: #007bff;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">MCP協調器</div>
            <div class="status">{{ status }}</div>
            <div class="subtitle">統一工作流協調 | 智能介入管理</div>
        </div>
        
        <div class="mcp-list" id="mcpList">
            <!-- MCP服務列表將通過JavaScript動態加載 -->
        </div>
        
        <button class="refresh-btn" onclick="loadMCPServices()">刷新狀態</button>
        
        <div class="metrics-section">
            <div class="metrics-title">系統指標</div>
            <div class="metric-item">
                <span class="metric-label">總請求數:</span>
                <span class="metric-value" id="totalRequests">{{ total_requests }}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">活躍連接:</span>
                <span class="metric-value" id="activeConnections">{{ active_connections }}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">平均響應時間:</span>
                <span class="metric-value" id="avgResponseTime">{{ avg_response_time }}ms</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">系統運行時間:</span>
                <span class="metric-value" id="uptime">{{ uptime }}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">最後更新:</span>
                <span class="metric-value" id="lastUpdate">{{ last_update }}</span>
            </div>
        </div>
    </div>

    <script>
        // 加載MCP服務狀態
        function loadMCPServices() {
            fetch('/api/mcp-status')
                .then(response => response.json())
                .then(data => {
                    updateMCPList(data.services);
                    updateMetrics(data.metrics);
                })
                .catch(error => {
                    console.error('Error loading MCP services:', error);
                });
        }
        
        // 更新MCP服務列表
        function updateMCPList(services) {
            const mcpList = document.getElementById('mcpList');
            mcpList.innerHTML = '';
            
            services.forEach(service => {
                const item = document.createElement('div');
                item.className = 'mcp-item';
                item.innerHTML = `
                    <span class="mcp-bullet">●</span>
                    <span class="mcp-name">${service.name}</span>
                    <span class="mcp-status">${service.status}</span>
                    <span style="margin-left: auto; color: #666;">端口: ${service.port}</span>
                `;
                mcpList.appendChild(item);
            });
        }
        
        // 更新系統指標
        function updateMetrics(metrics) {
            document.getElementById('totalRequests').textContent = metrics.total_requests || 0;
            document.getElementById('activeConnections').textContent = metrics.active_connections || 0;
            document.getElementById('avgResponseTime').textContent = (metrics.avg_response_time || 0).toFixed(2) + 'ms';
            document.getElementById('uptime').textContent = metrics.uptime || '未知';
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        }
        
        // 頁面加載時自動刷新
        document.addEventListener('DOMContentLoaded', function() {
            loadMCPServices();
            // 每30秒自動刷新一次
            setInterval(loadMCPServices, 30000);
        });
    </script>
</body>
</html>
"""

class WebManagementInterface:
    """Web管理界面組件"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.start_time = datetime.now()
        self.total_requests = 0
        self.active_connections = 0
        self.response_times = []
        
        # 註冊路由
        self._register_routes()
    
    def _register_routes(self):
        """註冊Web界面路由"""
        
        @self.app.route('/')
        def index():
            """主頁面"""
            return render_template_string(
                COORDINATOR_HTML_TEMPLATE,
                status="運行中",
                total_requests=self.total_requests,
                active_connections=self.active_connections,
                avg_response_time=self._get_avg_response_time(),
                uptime=self._get_uptime(),
                last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        @self.app.route('/api/mcp-status')
        def mcp_status():
            """MCP服務狀態API"""
            return jsonify({
                "services": self._get_mcp_services(),
                "metrics": self._get_system_metrics()
            })
        
        @self.app.route('/api/metrics')
        def metrics():
            """系統指標API"""
            return jsonify(self._get_system_metrics())
    
    def _get_mcp_services(self):
        """獲取MCP服務列表"""
        # 這裡應該從實際的MCP註冊表中獲取服務信息
        # 暫時返回示例數據
        return [
            {
                "name": "Cloud Search MCP",
                "status": "運行中",
                "port": 8001,
                "description": "雲端搜索服務"
            },
            {
                "name": "Enhanced Test Flow MCP",
                "status": "運行中", 
                "port": 8002,
                "description": "增強測試流程"
            },
            {
                "name": "Smartinvention MCP",
                "status": "運行中",
                "port": 8003,
                "description": "智能發明服務"
            },
            {
                "name": "Tool Registry Manager",
                "status": "運行中",
                "port": 8004,
                "description": "工具註冊管理"
            }
        ]
    
    def _get_system_metrics(self):
        """獲取系統指標"""
        return {
            "total_requests": self.total_requests,
            "active_connections": self.active_connections,
            "avg_response_time": self._get_avg_response_time(),
            "uptime": self._get_uptime(),
            "last_update": datetime.now().isoformat()
        }
    
    def _get_avg_response_time(self):
        """獲取平均響應時間"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def _get_uptime(self):
        """獲取系統運行時間"""
        uptime_delta = datetime.now() - self.start_time
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天 {hours}小時 {minutes}分鐘"
        elif hours > 0:
            return f"{hours}小時 {minutes}分鐘"
        else:
            return f"{minutes}分鐘"
    
    def record_request(self, response_time: float = None):
        """記錄請求"""
        self.total_requests += 1
        if response_time is not None:
            self.response_times.append(response_time)
            # 只保留最近100個響應時間記錄
            if len(self.response_times) > 100:
                self.response_times = self.response_times[-100:]
    
    def update_active_connections(self, count: int):
        """更新活躍連接數"""
        self.active_connections = count

def create_web_management_interface(app: Flask) -> WebManagementInterface:
    """創建Web管理界面組件"""
    return WebManagementInterface(app)

