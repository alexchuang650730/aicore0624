#!/usr/bin/env python3
"""
Production Deployment Configuration
生产环境部署配置管理器
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class DeploymentEnvironment(Enum):
    """部署环境类型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class ServiceType(Enum):
    """服务类型"""
    WEB_SERVICE = "web_service"
    API_SERVICE = "api_service"
    BACKGROUND_SERVICE = "background_service"
    DATABASE_SERVICE = "database_service"

@dataclass
class DeploymentConfig:
    """部署配置数据结构"""
    environment: DeploymentEnvironment
    service_name: str
    service_type: ServiceType
    version: str
    port: int
    host: str = "0.0.0.0"
    workers: int = 4
    timeout: int = 30
    max_memory: str = "512M"
    health_check_path: str = "/health"
    environment_variables: Dict[str, str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.environment_variables is None:
            self.environment_variables = {}
        if self.dependencies is None:
            self.dependencies = []

class ProductionDeploymentManager:
    """生产环境部署管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logging()
        self.deployment_configs = {}
        
        # 加载现有配置
        self._load_configurations()
        
        self.logger.info("Production Deployment Manager initialized")
    
    def _setup_logging(self):
        """设置日志"""
        logger = logging.getLogger("ProductionDeploymentManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_configurations(self):
        """加载配置文件"""
        try:
            config_files = list(self.config_dir.glob("*.json"))
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    config_name = config_file.stem
                    self.deployment_configs[config_name] = config_data
                    self.logger.info(f"Loaded configuration: {config_name}")
        except Exception as e:
            self.logger.error(f"Error loading configurations: {str(e)}")
    
    def create_deployment_config(self, config: DeploymentConfig) -> str:
        """创建部署配置"""
        config_name = f"{config.service_name}_{config.environment.value}"
        config_data = asdict(config)
        
        # 转换枚举为字符串
        config_data['environment'] = config.environment.value
        config_data['service_type'] = config.service_type.value
        
        self.deployment_configs[config_name] = config_data
        
        # 保存到文件
        config_file = self.config_dir / f"{config_name}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Created deployment configuration: {config_name}")
        return config_name
    
    def get_deployment_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """获取部署配置"""
        return self.deployment_configs.get(config_name)
    
    def list_configurations(self) -> List[str]:
        """列出所有配置"""
        return list(self.deployment_configs.keys())
    
    def generate_docker_compose(self, config_name: str) -> str:
        """生成Docker Compose配置"""
        config = self.get_deployment_config(config_name)
        if not config:
            raise ValueError(f"Configuration not found: {config_name}")
        
        docker_compose = f"""version: '3.8'

services:
  {config['service_name']}:
    build: .
    ports:
      - "{config['port']}:{config['port']}"
    environment:"""
        
        # 添加环境变量
        for key, value in config.get('environment_variables', {}).items():
            docker_compose += f"\n      - {key}={value}"
        
        docker_compose += f"""
    deploy:
      resources:
        limits:
          memory: {config['max_memory']}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{config['port']}{config['health_check_path']}"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
"""
        
        return docker_compose
    
    def generate_nginx_config(self, config_name: str) -> str:
        """生成Nginx配置"""
        config = self.get_deployment_config(config_name)
        if not config:
            raise ValueError(f"Configuration not found: {config_name}")
        
        nginx_config = f"""upstream {config['service_name']} {{
    server {config['host']}:{config['port']};
}}

server {{
    listen 80;
    server_name {config['service_name']}.example.com;
    
    location / {{
        proxy_pass http://{config['service_name']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout {config['timeout']}s;
        proxy_send_timeout {config['timeout']}s;
        proxy_read_timeout {config['timeout']}s;
    }}
    
    location {config['health_check_path']} {{
        proxy_pass http://{config['service_name']}{config['health_check_path']};
        access_log off;
    }}
}}
"""
        
        return nginx_config
    
    def generate_systemd_service(self, config_name: str) -> str:
        """生成Systemd服务配置"""
        config = self.get_deployment_config(config_name)
        if not config:
            raise ValueError(f"Configuration not found: {config_name}")
        
        systemd_config = f"""[Unit]
Description={config['service_name']} Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/{config['service_name']}
ExecStart=/opt/{config['service_name']}/venv/bin/python app.py
Restart=always
RestartSec=10

# Environment variables
"""
        
        for key, value in config.get('environment_variables', {}).items():
            systemd_config += f"Environment={key}={value}\n"
        
        systemd_config += f"""
# Resource limits
MemoryLimit={config['max_memory']}

[Install]
WantedBy=multi-user.target
"""
        
        return systemd_config
    
    def validate_configuration(self, config_name: str) -> Dict[str, Any]:
        """验证配置"""
        config = self.get_deployment_config(config_name)
        if not config:
            return {
                'valid': False,
                'errors': [f"Configuration not found: {config_name}"]
            }
        
        errors = []
        warnings = []
        
        # 检查必需字段
        required_fields = ['service_name', 'service_type', 'version', 'port']
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"Missing required field: {field}")
        
        # 检查端口范围
        port = config.get('port', 0)
        if not (1024 <= port <= 65535):
            errors.append(f"Port {port} is not in valid range (1024-65535)")
        
        # 检查内存限制格式
        memory = config.get('max_memory', '')
        if memory and not memory.endswith(('M', 'G')):
            warnings.append(f"Memory limit format may be invalid: {memory}")
        
        # 检查健康检查路径
        health_path = config.get('health_check_path', '')
        if health_path and not health_path.startswith('/'):
            warnings.append(f"Health check path should start with '/': {health_path}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# 预定义配置模板
def create_aicore_production_config() -> DeploymentConfig:
    """创建AICore生产环境配置"""
    return DeploymentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        service_name="aicore",
        service_type=ServiceType.API_SERVICE,
        version="3.1.0",
        port=8000,
        host="0.0.0.0",
        workers=8,
        timeout=60,
        max_memory="1G",
        health_check_path="/health",
        environment_variables={
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "WORKERS": "8"
        },
        dependencies=[
            "python:3.11",
            "fastapi",
            "uvicorn",
            "asyncio"
        ]
    )

def create_aicore_staging_config() -> DeploymentConfig:
    """创建AICore测试环境配置"""
    return DeploymentConfig(
        environment=DeploymentEnvironment.STAGING,
        service_name="aicore",
        service_type=ServiceType.API_SERVICE,
        version="3.1.0",
        port=8001,
        host="0.0.0.0",
        workers=4,
        timeout=30,
        max_memory="512M",
        health_check_path="/health",
        environment_variables={
            "ENVIRONMENT": "staging",
            "LOG_LEVEL": "DEBUG",
            "WORKERS": "4"
        },
        dependencies=[
            "python:3.11",
            "fastapi",
            "uvicorn",
            "asyncio"
        ]
    )

# 主函数
def main():
    """主函数"""
    print("Production Deployment Configuration Manager")
    print("=" * 50)
    
    # 创建部署管理器
    manager = ProductionDeploymentManager()
    
    # 创建示例配置
    prod_config = create_aicore_production_config()
    staging_config = create_aicore_staging_config()
    
    # 保存配置
    prod_config_name = manager.create_deployment_config(prod_config)
    staging_config_name = manager.create_deployment_config(staging_config)
    
    print(f"Created configurations:")
    print(f"  - {prod_config_name}")
    print(f"  - {staging_config_name}")
    
    # 验证配置
    print(f"\nValidating configurations:")
    for config_name in [prod_config_name, staging_config_name]:
        validation = manager.validate_configuration(config_name)
        status = "✅ Valid" if validation['valid'] else "❌ Invalid"
        print(f"  {config_name}: {status}")
        
        if validation['errors']:
            for error in validation['errors']:
                print(f"    Error: {error}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"    Warning: {warning}")
    
    # 生成部署文件示例
    print(f"\nGenerating deployment files for {prod_config_name}:")
    
    try:
        docker_compose = manager.generate_docker_compose(prod_config_name)
        print("  ✅ Docker Compose configuration generated")
        
        nginx_config = manager.generate_nginx_config(prod_config_name)
        print("  ✅ Nginx configuration generated")
        
        systemd_service = manager.generate_systemd_service(prod_config_name)
        print("  ✅ Systemd service configuration generated")
        
    except Exception as e:
        print(f"  ❌ Error generating deployment files: {str(e)}")

if __name__ == "__main__":
    main()

