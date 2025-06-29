#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键部署功能测试脚本
测试 fully_integrated_system_with_deployment.py 的一键部署功能

使用方法:
python3 one_click_deployment_test.py
"""

import asyncio
import aiohttp
import json
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OneClickDeploymentTester:
    """一键部署测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.api_key = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_api_key(self) -> str:
        """获取 API Key"""
        try:
            # 获取系统状态，从中提取 API Key 信息
            async with self.session.get(f"{self.base_url}/api/system/health") as response:
                if response.status == 200:
                    logger.info("✅ 系统健康检查通过")
                else:
                    logger.error(f"❌ 系统健康检查失败: {response.status}")
                    return None
            
            # 这里应该从配置或环境变量获取 API Key
            # 为了测试，我们使用一个示例 API Key
            # 在实际使用中，需要从系统管理员获取有效的 API Key
            test_api_key = "admin_test_key_for_deployment"
            
            logger.info(f"🔑 使用测试 API Key: {test_api_key[:12]}...")
            return test_api_key
            
        except Exception as e:
            logger.error(f"❌ 获取 API Key 失败: {e}")
            return None
    
    async def test_system_status(self) -> bool:
        """测试系统状态"""
        try:
            headers = {'X-API-Key': self.api_key} if self.api_key else {}
            
            async with self.session.get(
                f"{self.base_url}/api/system/status",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ 系统状态检查成功")
                    logger.info(f"   系统名称: {data.get('system_name')}")
                    logger.info(f"   版本: {data.get('version')}")
                    logger.info(f"   部署功能: {'✅ 启用' if data.get('deployment_enabled') else '❌ 禁用'}")
                    return data.get('deployment_enabled', False)
                else:
                    logger.error(f"❌ 系统状态检查失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 系统状态检查异常: {e}")
            return False
    
    async def test_deployment_environments(self) -> bool:
        """测试部署环境配置"""
        try:
            headers = {'X-API-Key': self.api_key}
            
            async with self.session.get(
                f"{self.base_url}/api/deployment/environments",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    environments = data.get('environments', [])
                    logger.info(f"✅ 发现 {len(environments)} 个配置的环境")
                    
                    for env in environments:
                        logger.info(f"   - {env.get('environment_id')}: {env.get('description', 'N/A')}")
                    
                    return len(environments) > 0
                else:
                    logger.error(f"❌ 获取部署环境失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 获取部署环境异常: {e}")
            return False
    
    async def test_deployment_connection(self) -> bool:
        """测试部署连接"""
        try:
            headers = {'X-API-Key': self.api_key}
            
            async with self.session.post(
                f"{self.base_url}/api/deployment/test-connection",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ 部署连接测试成功")
                    logger.info(f"   消息: {data.get('message')}")
                    
                    components = data.get('components', {})
                    for comp, status in components.items():
                        logger.info(f"   - {comp}: {'✅ 可用' if status else '❌ 不可用'}")
                    
                    return data.get('success', False)
                else:
                    logger.error(f"❌ 部署连接测试失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 部署连接测试异常: {e}")
            return False
    
    async def trigger_one_click_deployment(self) -> str:
        """触发一键部署"""
        try:
            headers = {'X-API-Key': self.api_key, 'Content-Type': 'application/json'}
            payload = {
                'target_environments': ['mac_local_001']  # 测试特定环境
            }
            
            logger.info("🚀 触发一键部署...")
            
            async with self.session.post(
                f"{self.base_url}/api/deployment/one-click",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        deployment_id = data.get('deployment_id')
                        logger.info(f"✅ 一键部署触发成功")
                        logger.info(f"   部署ID: {deployment_id}")
                        logger.info(f"   状态: {data.get('status')}")
                        return deployment_id
                    else:
                        logger.error(f"❌ 一键部署触发失败: {data.get('error')}")
                        return None
                else:
                    logger.error(f"❌ 一键部署触发失败: {response.status}")
                    error_text = await response.text()
                    logger.error(f"   错误详情: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 一键部署触发异常: {e}")
            return None
    
    async def monitor_deployment_progress(self, deployment_id: str, max_wait_time: int = 300) -> bool:
        """监控部署进度"""
        try:
            headers = {'X-API-Key': self.api_key}
            start_time = time.time()
            
            logger.info(f"📊 开始监控部署进度: {deployment_id}")
            
            while time.time() - start_time < max_wait_time:
                async with self.session.get(
                    f"{self.base_url}/api/deployment/status",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('deployment_id') == deployment_id:
                            status = data.get('status')
                            progress = data.get('progress', 0)
                            
                            logger.info(f"📈 部署进度: {progress}% - {status}")
                            
                            # 显示最新日志
                            logs = data.get('logs', [])
                            if logs:
                                latest_log = logs[-1]
                                logger.info(f"   最新日志: {latest_log}")
                            
                            # 检查是否完成
                            if status == 'completed':
                                logger.info("🎉 部署成功完成！")
                                return True
                            elif status == 'failed':
                                error_msg = data.get('error_message', 'Unknown error')
                                logger.error(f"❌ 部署失败: {error_msg}")
                                return False
                        else:
                            logger.warning(f"⚠️ 部署ID不匹配: 期望 {deployment_id}, 实际 {data.get('deployment_id')}")
                    else:
                        logger.error(f"❌ 获取部署状态失败: {response.status}")
                
                # 等待5秒后再次检查
                await asyncio.sleep(5)
            
            logger.error(f"⏰ 部署监控超时 ({max_wait_time}秒)")
            return False
            
        except Exception as e:
            logger.error(f"❌ 部署进度监控异常: {e}")
            return False
    
    async def get_deployment_history(self) -> bool:
        """获取部署历史"""
        try:
            headers = {'X-API-Key': self.api_key}
            
            async with self.session.get(
                f"{self.base_url}/api/deployment/history",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    history = data.get('history', [])
                    
                    logger.info(f"📚 部署历史记录: {len(history)} 条")
                    
                    for record in history[-3:]:  # 显示最近3条记录
                        deployment_id = record.get('deployment_id')
                        status = record.get('status')
                        duration = record.get('duration')
                        
                        logger.info(f"   - {deployment_id}: {status}")
                        if duration:
                            logger.info(f"     执行时间: {duration:.2f}秒")
                    
                    return True
                else:
                    logger.error(f"❌ 获取部署历史失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 获取部署历史异常: {e}")
            return False
    
    async def run_full_test(self) -> bool:
        """运行完整测试"""
        logger.info("🧪 开始一键部署功能完整测试")
        logger.info("=" * 50)
        
        # 1. 获取 API Key
        self.api_key = await self.get_api_key()
        if not self.api_key:
            logger.error("❌ 无法获取 API Key，测试终止")
            return False
        
        # 2. 测试系统状态
        if not await self.test_system_status():
            logger.error("❌ 系统状态检查失败，测试终止")
            return False
        
        # 3. 测试部署环境配置
        if not await self.test_deployment_environments():
            logger.error("❌ 部署环境配置检查失败，测试终止")
            return False
        
        # 4. 测试部署连接
        if not await self.test_deployment_connection():
            logger.error("❌ 部署连接测试失败，测试终止")
            return False
        
        # 5. 触发一键部署
        deployment_id = await self.trigger_one_click_deployment()
        if not deployment_id:
            logger.error("❌ 一键部署触发失败，测试终止")
            return False
        
        # 6. 监控部署进度
        deployment_success = await self.monitor_deployment_progress(deployment_id)
        
        # 7. 获取部署历史
        await self.get_deployment_history()
        
        # 测试总结
        logger.info("=" * 50)
        if deployment_success:
            logger.info("🎉 一键部署功能测试成功！")
        else:
            logger.error("❌ 一键部署功能测试失败！")
        
        return deployment_success

async def main():
    """主函数"""
    async with OneClickDeploymentTester() as tester:
        success = await tester.run_full_test()
        return success

if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 测试被用户中断")
        exit(1)
    except Exception as e:
        logger.error(f"❌ 测试异常: {e}")
        exit(1)

