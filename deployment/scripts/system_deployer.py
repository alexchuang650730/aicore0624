#!/usr/bin/env python3
"""
系统部署器脚本
用于部署和配置AICore系统
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
import argparse

class SystemDeployer:
    """系统部署器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.deployment_dir = self.script_dir.parent
        self.project_root = self.deployment_dir.parent
        self.powerautomation_dir = self.project_root / "PowerAutomation"
        
    def deploy_development(self):
        """部署开发环境"""
        print("🚀 部署AICore开发环境...")
        
        steps = [
            ("检查环境", self._check_environment),
            ("创建配置", self._create_dev_config),
            ("设置权限", self._setup_permissions),
            ("验证部署", self._verify_deployment)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                success = step_func()
                if success:
                    print(f"   ✅ {step_name}完成")
                else:
                    print(f"   ❌ {step_name}失败")
                    return False
            except Exception as e:
                print(f"   ❌ {step_name}时发生错误: {str(e)}")
                return False
        
        print("\n🎉 开发环境部署完成！")
        return True
    
    def deploy_production(self):
        """部署生产环境"""
        print("🚀 部署AICore生产环境...")
        
        steps = [
            ("检查环境", self._check_environment),
            ("创建生产配置", self._create_prod_config),
            ("优化性能", self._optimize_performance),
            ("设置权限", self._setup_permissions),
            ("配置监控", self._setup_monitoring),
            ("验证部署", self._verify_deployment)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                success = step_func()
                if success:
                    print(f"   ✅ {step_name}完成")
                else:
                    print(f"   ❌ {step_name}失败")
                    return False
            except Exception as e:
                print(f"   ❌ {step_name}时发生错误: {str(e)}")
                return False
        
        print("\n🎉 生产环境部署完成！")
        return True
    
    def _check_environment(self):
        """检查环境"""
        # 运行环境检查器
        env_checker = self.script_dir / "environment_checker.py"
        if env_checker.exists():
            result = subprocess.run([sys.executable, str(env_checker)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        return True
    
    def _create_dev_config(self):
        """创建开发配置"""
        config_dir = self.deployment_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        dev_config = {
            "environment": "development",
            "debug": True,
            "log_level": "DEBUG",
            "performance_monitoring": True,
            "auto_reload": True,
            "demo_mode": True,
            "aicore": {
                "max_concurrent_tasks": 5,
                "task_timeout": 300,
                "enable_caching": True,
                "cache_ttl": 3600
            },
            "mcp": {
                "coordination_timeout": 30,
                "max_retries": 3,
                "enable_fallback": True
            },
            "testing": {
                "enable_test_flow": True,
                "test_coverage_threshold": 80,
                "auto_test_on_change": True
            }
        }
        
        config_file = config_dir / "development.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(dev_config, f, indent=2, ensure_ascii=False)
        
        print(f"   📄 开发配置已创建: {config_file}")
        return True
    
    def _create_prod_config(self):
        """创建生产配置"""
        config_dir = self.deployment_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        prod_config = {
            "environment": "production",
            "debug": False,
            "log_level": "INFO",
            "performance_monitoring": True,
            "auto_reload": False,
            "demo_mode": False,
            "aicore": {
                "max_concurrent_tasks": 20,
                "task_timeout": 600,
                "enable_caching": True,
                "cache_ttl": 7200
            },
            "mcp": {
                "coordination_timeout": 60,
                "max_retries": 5,
                "enable_fallback": True
            },
            "testing": {
                "enable_test_flow": True,
                "test_coverage_threshold": 90,
                "auto_test_on_change": False
            },
            "security": {
                "enable_rate_limiting": True,
                "max_requests_per_minute": 100,
                "enable_authentication": True
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_interval": 60,
                "enable_alerting": True
            }
        }
        
        config_file = config_dir / "production.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(prod_config, f, indent=2, ensure_ascii=False)
        
        print(f"   📄 生产配置已创建: {config_file}")
        return True
    
    def _optimize_performance(self):
        """优化性能"""
        print("   🔧 应用性能优化...")
        
        # 创建性能优化配置
        perf_config = {
            "python_optimization": {
                "enable_bytecode_cache": True,
                "optimize_imports": True,
                "enable_gc_optimization": True
            },
            "memory_optimization": {
                "max_memory_usage": "2GB",
                "enable_memory_profiling": False,
                "gc_threshold": [700, 10, 10]
            },
            "concurrency": {
                "max_workers": 4,
                "enable_async_processing": True,
                "task_queue_size": 1000
            }
        }
        
        config_dir = self.deployment_dir / "config"
        perf_file = config_dir / "performance.json"
        with open(perf_file, 'w', encoding='utf-8') as f:
            json.dump(perf_config, f, indent=2, ensure_ascii=False)
        
        print(f"   📄 性能配置已创建: {perf_file}")
        return True
    
    def _setup_permissions(self):
        """设置权限"""
        print("   🔐 设置文件权限...")
        
        # 设置脚本执行权限
        script_files = [
            self.script_dir / "demo_runner.py",
            self.script_dir / "environment_checker.py",
            self.script_dir / "system_deployer.py"
        ]
        
        for script_file in script_files:
            if script_file.exists():
                os.chmod(script_file, 0o755)
                print(f"   ✅ {script_file.name} 权限已设置")
        
        # 设置演示脚本权限
        demos_dir = self.deployment_dir / "demos"
        if demos_dir.exists():
            for demo_script in demos_dir.glob("*/*_demo.py"):
                os.chmod(demo_script, 0o755)
                print(f"   ✅ {demo_script.name} 权限已设置")
        
        return True
    
    def _setup_monitoring(self):
        """配置监控"""
        print("   📊 配置系统监控...")
        
        monitoring_config = {
            "metrics": {
                "enabled": True,
                "collection_interval": 60,
                "retention_days": 30
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5
            },
            "alerts": {
                "enabled": True,
                "thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "error_rate": 5,
                    "response_time": 1000
                }
            }
        }
        
        config_dir = self.deployment_dir / "config"
        monitoring_file = config_dir / "monitoring.json"
        with open(monitoring_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_config, f, indent=2, ensure_ascii=False)
        
        print(f"   📄 监控配置已创建: {monitoring_file}")
        return True
    
    def _verify_deployment(self):
        """验证部署"""
        print("   🔍 验证部署完整性...")
        
        # 检查关键文件和目录
        required_items = [
            self.deployment_dir / "demos",
            self.deployment_dir / "scripts",
            self.deployment_dir / "config",
            self.deployment_dir / "templates",
            self.powerautomation_dir / "core" / "aicore3.py",
            self.powerautomation_dir / "components" / "code_generation_mcp.py"
        ]
        
        all_exist = True
        for item in required_items:
            if item.exists():
                print(f"   ✅ {item.name} 存在")
            else:
                print(f"   ❌ {item.name} 不存在")
                all_exist = False
        
        return all_exist
    
    def create_templates(self):
        """创建部署模板"""
        print("📄 创建部署模板...")
        
        templates_dir = self.deployment_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Docker模板
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONPATH=/app
ENV AICORE_ENV=production

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "deployment/scripts/demo_runner.py", "run-all"]
"""
        
        dockerfile = templates_dir / "Dockerfile"
        with open(dockerfile, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # Docker Compose模板
        docker_compose_content = """version: '3.8'

services:
  aicore:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AICORE_ENV=production
    volumes:
      - ./deployment/config:/app/deployment/config
      - ./deployment/results:/app/deployment/results
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./deployment/templates/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - aicore
    restart: unless-stopped
"""
        
        docker_compose = templates_dir / "docker-compose.yml"
        with open(docker_compose, 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        
        # Nginx配置模板
        nginx_content = """events {
    worker_connections 1024;
}

http {
    upstream aicore {
        server aicore:8000;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://aicore;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
"""
        
        nginx_conf = templates_dir / "nginx.conf"
        with open(nginx_conf, 'w', encoding='utf-8') as f:
            f.write(nginx_content)
        
        print("   ✅ Docker模板已创建")
        print("   ✅ Docker Compose模板已创建")
        print("   ✅ Nginx配置模板已创建")
        
        return True
    
    def uninstall(self):
        """卸载系统"""
        print("🗑️ 卸载AICore系统...")
        
        # 确认操作
        response = input("确定要卸载AICore系统吗？这将删除所有配置和结果文件。(y/N): ")
        if response.lower() != 'y':
            print("取消卸载操作")
            return False
        
        # 删除配置文件
        config_dir = self.deployment_dir / "config"
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print("   ✅ 配置文件已删除")
        
        # 删除结果文件
        results_dir = self.deployment_dir / "results"
        if results_dir.exists():
            shutil.rmtree(results_dir)
            print("   ✅ 结果文件已删除")
        
        # 删除模板文件
        templates_dir = self.deployment_dir / "templates"
        if templates_dir.exists():
            shutil.rmtree(templates_dir)
            print("   ✅ 模板文件已删除")
        
        print("🎉 AICore系统已卸载")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AICore系统部署器")
    parser.add_argument('action', choices=['dev', 'prod', 'templates', 'uninstall'], 
                       help='部署操作')
    
    args = parser.parse_args()
    
    deployer = SystemDeployer()
    
    if args.action == 'dev':
        success = deployer.deploy_development()
    elif args.action == 'prod':
        success = deployer.deploy_production()
    elif args.action == 'templates':
        success = deployer.create_templates()
    elif args.action == 'uninstall':
        success = deployer.uninstall()
    
    if success:
        print("\n🎉 操作完成！")
        sys.exit(0)
    else:
        print("\n❌ 操作失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()

