"""
VSIX Auto Deployer - PowerAutomation Local MCP 自動部署組件
自動檢測並部署本地 VSIX 檔案的核心實現

Author: Manus AI
Version: 1.0.0
Date: 2025-06-24
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import aiofiles
import aiohttp
from dataclasses import dataclass, asdict


@dataclass
class VSIXFileInfo:
    """VSIX 檔案信息"""
    file_path: str
    file_name: str
    file_size: int
    modified_time: float
    version: Optional[str] = None
    is_valid: bool = False
    checksum: Optional[str] = None


@dataclass
class DeploymentResult:
    """部署結果"""
    file_path: str
    success: bool
    message: str
    deployment_time: float
    error_details: Optional[str] = None


class VSIXFileScanner:
    """VSIX 檔案掃描器"""
    
    def __init__(self, scan_directories: List[str], logger: logging.Logger):
        """
        初始化檔案掃描器
        
        Args:
            scan_directories: 要掃描的目錄列表
            logger: 日誌器
        """
        self.scan_directories = scan_directories
        self.logger = logger
        self.supported_extensions = ['.vsix']
    
    async def scan_for_vsix_files(self) -> List[VSIXFileInfo]:
        """
        掃描 VSIX 檔案
        
        Returns:
            VSIX 檔案信息列表
        """
        vsix_files = []
        
        for directory in self.scan_directories:
            if not os.path.exists(directory):
                self.logger.warning(f"掃描目錄不存在: {directory}")
                continue
            
            try:
                files = await self._scan_directory(directory)
                vsix_files.extend(files)
                self.logger.info(f"在目錄 {directory} 中發現 {len(files)} 個 VSIX 檔案")
            except Exception as e:
                self.logger.error(f"掃描目錄 {directory} 時發生錯誤: {e}")
        
        return vsix_files
    
    async def _scan_directory(self, directory: str) -> List[VSIXFileInfo]:
        """
        掃描單個目錄
        
        Args:
            directory: 目錄路徑
            
        Returns:
            VSIX 檔案信息列表
        """
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in self.supported_extensions):
                        file_path = os.path.join(root, filename)
                        file_info = await self._get_file_info(file_path)
                        if file_info:
                            files.append(file_info)
        except Exception as e:
            self.logger.error(f"掃描目錄內容時發生錯誤: {e}")
        
        return files
    
    async def _get_file_info(self, file_path: str) -> Optional[VSIXFileInfo]:
        """
        獲取檔案信息
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            VSIX 檔案信息或 None
        """
        try:
            stat = os.stat(file_path)
            
            file_info = VSIXFileInfo(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                file_size=stat.st_size,
                modified_time=stat.st_mtime,
                is_valid=await self._validate_vsix_file(file_path)
            )
            
            # 嘗試提取版本信息
            file_info.version = self._extract_version_from_filename(file_info.file_name)
            
            return file_info
            
        except Exception as e:
            self.logger.error(f"獲取檔案信息失敗 {file_path}: {e}")
            return None
    
    async def _validate_vsix_file(self, file_path: str) -> bool:
        """
        驗證 VSIX 檔案有效性
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            是否為有效的 VSIX 檔案
        """
        try:
            # 檢查檔案大小
            if os.path.getsize(file_path) < 1024:  # 小於 1KB 可能不是有效檔案
                return False
            
            # 檢查檔案是否可讀
            async with aiofiles.open(file_path, 'rb') as f:
                header = await f.read(4)
                # VSIX 檔案是 ZIP 格式，檢查 ZIP 檔案頭
                if header[:2] != b'PK':
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"驗證 VSIX 檔案失敗 {file_path}: {e}")
            return False
    
    def _extract_version_from_filename(self, filename: str) -> Optional[str]:
        """
        從檔案名提取版本號
        
        Args:
            filename: 檔案名
            
        Returns:
            版本號或 None
        """
        import re
        
        # 匹配常見的版本號格式，如 1.0.0, 2.1.3, 3.0.0-beta
        version_pattern = r'(\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?)'
        match = re.search(version_pattern, filename)
        
        if match:
            return match.group(1)
        
        return None


class DeploymentStrategy:
    """部署策略"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化部署策略
        
        Args:
            config: 配置字典
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
    
    def should_deploy(self, file_info: VSIXFileInfo) -> bool:
        """
        判斷是否應該部署檔案
        
        Args:
            file_info: VSIX 檔案信息
            
        Returns:
            是否應該部署
        """
        # 檢查檔案有效性
        if not file_info.is_valid:
            self.logger.warning(f"跳過無效檔案: {file_info.file_name}")
            return False
        
        # 檢查檔案大小限制
        max_size = self.config.get('max_file_size', 100 * 1024 * 1024)  # 默認 100MB
        if file_info.file_size > max_size:
            self.logger.warning(f"檔案過大，跳過部署: {file_info.file_name} ({file_info.file_size} bytes)")
            return False
        
        # 檢查檔案修改時間
        max_age_hours = self.config.get('max_file_age_hours', 24)  # 默認 24 小時
        if max_age_hours > 0:
            age_hours = (time.time() - file_info.modified_time) / 3600
            if age_hours > max_age_hours:
                self.logger.info(f"檔案過舊，跳過部署: {file_info.file_name} (age: {age_hours:.1f} hours)")
                return False
        
        return True
    
    def sort_files_for_deployment(self, files: List[VSIXFileInfo]) -> List[VSIXFileInfo]:
        """
        為部署排序檔案
        
        Args:
            files: VSIX 檔案列表
            
        Returns:
            排序後的檔案列表
        """
        # 按修改時間降序排序（最新的先部署）
        return sorted(files, key=lambda f: f.modified_time, reverse=True)


class VSIXAutoDeployer:
    """VSIX 自動部署器"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化自動部署器
        
        Args:
            config: 配置字典
            logger: 日誌器
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化組件
        scan_dirs = config.get('scan_directories', ['/home/ec2-user/aicore0624/PowerAutomation_local/vscode-extension'])
        self.file_scanner = VSIXFileScanner(scan_dirs, self.logger)
        self.deployment_strategy = DeploymentStrategy(config.get('deployment', {}), self.logger)
        
        # 部署狀態
        self.deployment_history: List[DeploymentResult] = []
        self.is_deploying = False
    
    async def auto_deploy_on_startup(self) -> Dict[str, Any]:
        """
        服務啟動時執行自動部署
        
        Returns:
            部署結果摘要
        """
        if self.is_deploying:
            self.logger.warning("自動部署已在進行中，跳過此次請求")
            return {"status": "skipped", "reason": "deployment_in_progress"}
        
        self.is_deploying = True
        start_time = time.time()
        
        try:
            self.logger.info("開始執行 VSIX 自動部署...")
            
            # 掃描 VSIX 檔案
            vsix_files = await self.file_scanner.scan_for_vsix_files()
            self.logger.info(f"發現 {len(vsix_files)} 個 VSIX 檔案")
            
            if not vsix_files:
                result = {
                    "status": "completed",
                    "total_files": 0,
                    "deployed_files": 0,
                    "skipped_files": 0,
                    "failed_files": 0,
                    "execution_time": time.time() - start_time
                }
                self.logger.info("未發現可部署的 VSIX 檔案")
                return result
            
            # 過濾和排序檔案
            deployable_files = [f for f in vsix_files if self.deployment_strategy.should_deploy(f)]
            sorted_files = self.deployment_strategy.sort_files_for_deployment(deployable_files)
            
            self.logger.info(f"準備部署 {len(sorted_files)} 個檔案")
            
            # 執行部署
            deployment_results = []
            for file_info in sorted_files:
                result = await self._deploy_single_file(file_info)
                deployment_results.append(result)
                self.deployment_history.append(result)
            
            # 統計結果
            successful_deployments = sum(1 for r in deployment_results if r.success)
            failed_deployments = len(deployment_results) - successful_deployments
            skipped_files = len(vsix_files) - len(deployable_files)
            
            summary = {
                "status": "completed",
                "total_files": len(vsix_files),
                "deployed_files": successful_deployments,
                "skipped_files": skipped_files,
                "failed_files": failed_deployments,
                "execution_time": time.time() - start_time,
                "deployment_results": [asdict(r) for r in deployment_results]
            }
            
            self.logger.info(f"自動部署完成: {successful_deployments} 成功, {failed_deployments} 失敗, {skipped_files} 跳過")
            return summary
            
        except Exception as e:
            self.logger.error(f"自動部署過程中發生錯誤: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        finally:
            self.is_deploying = False
    
    async def _deploy_single_file(self, file_info: VSIXFileInfo) -> DeploymentResult:
        """
        部署單個 VSIX 檔案
        
        Args:
            file_info: VSIX 檔案信息
            
        Returns:
            部署結果
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"開始部署: {file_info.file_name}")
            
            # 準備部署請求
            deployment_request = {
                "vsix_path": file_info.file_path,
                "target_environment": self.config.get('default_environment', 'development')
            }
            
            # 調用內部部署 API
            success, message, error_details = await self._call_deployment_api(deployment_request)
            
            result = DeploymentResult(
                file_path=file_info.file_path,
                success=success,
                message=message,
                deployment_time=time.time() - start_time,
                error_details=error_details
            )
            
            if success:
                self.logger.info(f"部署成功: {file_info.file_name}")
            else:
                self.logger.error(f"部署失敗: {file_info.file_name} - {message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"部署檔案時發生異常 {file_info.file_name}: {e}")
            return DeploymentResult(
                file_path=file_info.file_path,
                success=False,
                message=f"部署異常: {str(e)}",
                deployment_time=time.time() - start_time,
                error_details=str(e)
            )
    
    async def _call_deployment_api(self, request: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        調用內部部署 API
        
        Args:
            request: 部署請求
            
        Returns:
            (成功標誌, 消息, 錯誤詳情)
        """
        try:
            # 獲取 API 配置
            api_config = self.config.get('api', {})
            base_url = api_config.get('base_url', 'http://localhost:8394')
            timeout = api_config.get('timeout', 30)
            
            # 發送 HTTP 請求
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    f"{base_url}/api/mcp/deploy_vsix",
                    json=request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return True, result.get('message', '部署成功'), None
                    else:
                        error_text = await response.text()
                        return False, f"API 調用失敗 (HTTP {response.status})", error_text
                        
        except asyncio.TimeoutError:
            return False, "API 調用超時", "請求超時"
        except aiohttp.ClientError as e:
            return False, f"網路錯誤: {str(e)}", str(e)
        except Exception as e:
            return False, f"未知錯誤: {str(e)}", str(e)
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """
        獲取部署狀態
        
        Returns:
            部署狀態信息
        """
        return {
            "is_deploying": self.is_deploying,
            "total_deployments": len(self.deployment_history),
            "successful_deployments": sum(1 for r in self.deployment_history if r.success),
            "failed_deployments": sum(1 for r in self.deployment_history if not r.success),
            "last_deployment": asdict(self.deployment_history[-1]) if self.deployment_history else None
        }
    
    def get_deployment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取部署歷史
        
        Args:
            limit: 返回記錄數限制
            
        Returns:
            部署歷史記錄
        """
        recent_history = self.deployment_history[-limit:] if limit > 0 else self.deployment_history
        return [asdict(r) for r in recent_history]


def create_default_config() -> Dict[str, Any]:
    """
    創建默認配置
    
    Returns:
        默認配置字典
    """
    return {
        "scan_directories": [
            "/home/ubuntu/aicore0624/PowerAutomation_local/vscode-extension",
            "/home/ec2-user/aicore0624/PowerAutomation_local/vscode-extension"
        ],
        "deployment": {
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "max_file_age_hours": 24,  # 24 小時
        },
        "default_environment": "development",
        "api": {
            "base_url": "http://localhost:8394",
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


# 測試函數
async def test_auto_deployer():
    """測試自動部署器"""
    config = create_default_config()
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format=config['logging']['format']
    )
    logger = logging.getLogger(__name__)
    
    # 創建自動部署器
    deployer = VSIXAutoDeployer(config, logger)
    
    # 執行自動部署
    result = await deployer.auto_deploy_on_startup()
    
    print("部署結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 顯示部署狀態
    status = deployer.get_deployment_status()
    print("\n部署狀態:")
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_auto_deployer())

