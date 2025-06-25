#!/usr/bin/env python3
"""
KiloCode Integration Client
KiloCode 整合客戶端

整合 KiloCode 作為高質量代碼生成的備選方案
提供代碼生成回退機制和質量保證
"""

import asyncio
import json
import logging
import time
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class KiloCodeModel(Enum):
    """KiloCode 模型類型"""
    GENERAL = "general"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"

class GenerationMode(Enum):
    """生成模式"""
    COMPLETION = "completion"
    CHAT = "chat"
    INSTRUCTION = "instruction"
    REFACTOR = "refactor"
    OPTIMIZE = "optimize"
    TEST_GENERATION = "test_generation"

@dataclass
class KiloCodeRequest:
    """KiloCode 請求"""
    prompt: str
    model: KiloCodeModel = KiloCodeModel.GENERAL
    mode: GenerationMode = GenerationMode.COMPLETION
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class KiloCodeResponse:
    """KiloCode 響應"""
    success: bool
    generated_code: Optional[str] = None
    quality_score: float = 0.0
    confidence_score: float = 0.0
    model_used: Optional[KiloCodeModel] = None
    tokens_used: int = 0
    generation_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class KiloCodeClient:
    """KiloCode 客戶端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.api_endpoint = self.config.get("api_endpoint", "https://api.kilocode.com/v1")
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1.0)
        
        # 會話管理
        self.session = None
        self.initialized = False
        
        # 性能統計
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens_used": 0,
            "model_usage": {model.value: 0 for model in KiloCodeModel}
        }
        
        # 緩存配置
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        self.request_cache = {}
        
    async def initialize(self):
        """初始化 KiloCode 客戶端"""
        if not self.enabled:
            logger.info("KiloCode integration is disabled")
            self.initialized = True
            return
        
        try:
            # 創建 HTTP 會話
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # 驗證 API 連接
            if await self._test_connection():
                self.initialized = True
                logger.info("KiloCode client initialized successfully")
            else:
                logger.warning("KiloCode API connection test failed, using fallback mode")
                self.initialized = True  # 仍然初始化，但會使用回退模式
                
        except Exception as e:
            logger.error(f"Failed to initialize KiloCode client: {e}")
            self.initialized = True  # 允許回退模式
    
    async def _test_connection(self) -> bool:
        """測試 API 連接"""
        if not self.api_key:
            logger.warning("No KiloCode API key provided")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.api_endpoint}/health",
                headers=headers
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"KiloCode connection test failed: {e}")
            return False
    
    async def generate_code(self, request_data: Any, context: Dict[str, Any]) -> KiloCodeResponse:
        """生成代碼"""
        if not self.initialized:
            return KiloCodeResponse(
                success=False,
                error="KiloCode client not initialized"
            )
        
        if not self.enabled:
            return await self._fallback_generation(request_data, context)
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 構建 KiloCode 請求
            kilocode_request = self._build_kilocode_request(request_data, context)
            
            # 檢查緩存
            cache_key = self._generate_cache_key(kilocode_request)
            if self.cache_enabled and cache_key in self.request_cache:
                cached_response = self.request_cache[cache_key]
                if datetime.now() - cached_response["timestamp"] < timedelta(seconds=self.cache_ttl):
                    logger.info("Using cached KiloCode response")
                    return cached_response["response"]
            
            # 發送請求到 KiloCode API
            response = await self._send_request(kilocode_request)
            
            # 緩存響應
            if self.cache_enabled and response.success:
                self.request_cache[cache_key] = {
                    "response": response,
                    "timestamp": datetime.now()
                }
            
            # 更新統計
            response.generation_time = time.time() - start_time
            if response.success:
                self.stats["successful_requests"] += 1
                self.stats["total_tokens_used"] += response.tokens_used
                if response.model_used:
                    self.stats["model_usage"][response.model_used.value] += 1
            else:
                self.stats["failed_requests"] += 1
            
            # 更新平均響應時間
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["total_requests"] - 1) + response.generation_time)
                / self.stats["total_requests"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in KiloCode generation: {e}")
            self.stats["failed_requests"] += 1
            
            # 嘗試回退生成
            return await self._fallback_generation(request_data, context)
    
    def _build_kilocode_request(self, request_data: Any, context: Dict[str, Any]) -> KiloCodeRequest:
        """構建 KiloCode 請求"""
        # 從請求數據中提取信息
        if hasattr(request_data, 'requirements'):
            prompt = request_data.requirements
            language = getattr(request_data, 'language', 'python')
        else:
            prompt = str(request_data)
            language = context.get('language', 'python')
        
        # 選擇合適的模型
        model_map = {
            'python': KiloCodeModel.PYTHON,
            'javascript': KiloCodeModel.JAVASCRIPT,
            'typescript': KiloCodeModel.TYPESCRIPT,
            'java': KiloCodeModel.JAVA,
            'cpp': KiloCodeModel.CPP,
            'csharp': KiloCodeModel.CSHARP,
            'go': KiloCodeModel.GO
        }
        model = model_map.get(language.lower(), KiloCodeModel.GENERAL)
        
        # 構建增強的提示
        enhanced_prompt = self._enhance_prompt(prompt, context)
        
        return KiloCodeRequest(
            prompt=enhanced_prompt,
            model=model,
            mode=GenerationMode.COMPLETION,
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.7),
            context=context
        )
    
    def _enhance_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """增強提示詞"""
        enhanced_parts = []
        
        # 添加上下文信息
        if context.get('project_path'):
            enhanced_parts.append(f"Project Context: Working on project at {context['project_path']}")
        
        if context.get('language'):
            enhanced_parts.append(f"Target Language: {context['language']}")
        
        if context.get('framework'):
            enhanced_parts.append(f"Framework: {context['framework']}")
        
        # 添加 RAG 上下文
        if context.get('rag_context'):
            enhanced_parts.append("Similar Code Examples:")
            rag_context = context['rag_context']
            if isinstance(rag_context, list) and len(rag_context) > 0:
                for i, example in enumerate(rag_context[:2]):  # 限制例子數量
                    if hasattr(example, 'chunk') and hasattr(example.chunk, 'content'):
                        enhanced_parts.append(f"Example {i+1}:")
                        enhanced_parts.append(example.chunk.content[:500])  # 限制長度
        
        # 添加 LSP 上下文
        if context.get('lsp_context'):
            lsp_context = context['lsp_context']
            if isinstance(lsp_context, dict):
                if lsp_context.get('architecture_patterns'):
                    enhanced_parts.append(f"Project Architecture: {', '.join(lsp_context['architecture_patterns'])}")
                if lsp_context.get('dependencies'):
                    key_deps = lsp_context['dependencies'][:5]  # 限制依賴數量
                    enhanced_parts.append(f"Key Dependencies: {', '.join(key_deps)}")
        
        # 添加原始需求
        enhanced_parts.append(f"Requirements: {prompt}")
        
        # 添加生成指導
        enhanced_parts.append("Generate high-quality, production-ready code that follows best practices and integrates well with the existing codebase.")
        
        return "\n\n".join(enhanced_parts)
    
    async def _send_request(self, request: KiloCodeRequest) -> KiloCodeResponse:
        """發送請求到 KiloCode API"""
        if not self.session or not self.api_key:
            return await self._fallback_generation(request, {})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": request.prompt,
            "model": request.model.value,
            "mode": request.mode.value,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stop": request.stop_sequences
        }
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.api_endpoint}/generate",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_api_response(data, request.model)
                    elif response.status == 429:  # Rate limit
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                            await asyncio.sleep(wait_time)
                            continue
                    else:
                        error_text = await response.text()
                        logger.error(f"KiloCode API error {response.status}: {error_text}")
                        
            except Exception as e:
                logger.error(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
        
        # 所有重試都失敗，使用回退
        return await self._fallback_generation(request, request.context)
    
    def _parse_api_response(self, data: Dict[str, Any], model: KiloCodeModel) -> KiloCodeResponse:
        """解析 API 響應"""
        try:
            generated_code = data.get("generated_text", "")
            quality_score = data.get("quality_score", 0.8)  # 假設 KiloCode 提供質量分數
            confidence_score = data.get("confidence", 0.9)
            tokens_used = data.get("tokens_used", 0)
            
            return KiloCodeResponse(
                success=True,
                generated_code=generated_code,
                quality_score=quality_score,
                confidence_score=confidence_score,
                model_used=model,
                tokens_used=tokens_used,
                metadata=data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error parsing KiloCode response: {e}")
            return KiloCodeResponse(
                success=False,
                error=f"Failed to parse API response: {e}"
            )
    
    async def _fallback_generation(self, request_data: Any, context: Dict[str, Any]) -> KiloCodeResponse:
        """回退代碼生成"""
        logger.info("Using KiloCode fallback generation")
        
        # 提取需求
        if hasattr(request_data, 'requirements'):
            requirements = request_data.requirements
            language = getattr(request_data, 'language', 'python')
        else:
            requirements = str(request_data)
            language = context.get('language', 'python')
        
        # 基於模板的回退生成
        fallback_code = self._generate_fallback_code(requirements, language, context)
        
        return KiloCodeResponse(
            success=True,
            generated_code=fallback_code,
            quality_score=0.6,  # 回退代碼質量較低
            confidence_score=0.7,
            model_used=KiloCodeModel.GENERAL,
            tokens_used=len(fallback_code.split()),
            metadata={"fallback": True}
        )
    
    def _generate_fallback_code(self, requirements: str, language: str, context: Dict[str, Any]) -> str:
        """生成回退代碼"""
        if language.lower() == 'python':
            return self._generate_python_fallback(requirements, context)
        elif language.lower() in ['javascript', 'js']:
            return self._generate_javascript_fallback(requirements, context)
        elif language.lower() in ['typescript', 'ts']:
            return self._generate_typescript_fallback(requirements, context)
        else:
            return self._generate_generic_fallback(requirements, language, context)
    
    def _generate_python_fallback(self, requirements: str, context: Dict[str, Any]) -> str:
        """生成 Python 回退代碼"""
        return f'''
"""
{requirements}

Generated by KiloCode fallback system.
This is a basic template that should be customized based on your specific needs.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeneratedSolution:
    """
    Generated solution for: {requirements}
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the solution"""
        try:
            # TODO: Add initialization logic based on requirements
            self.initialized = True
            logger.info("Solution initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {{e}}")
            return False
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the main logic based on requirements.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Result of the execution
        """
        if not self.initialized:
            raise RuntimeError("Solution not initialized")
        
        try:
            # TODO: Implement the main logic based on requirements:
            # {requirements}
            
            result = {{
                "success": True,
                "data": input_data,
                "message": "Processing completed",
                "requirements_addressed": "{requirements}"
            }}
            
            return result
            
        except Exception as e:
            logger.error(f"Execution failed: {{e}}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {{
            "initialized": self.initialized,
            "config": self.config
        }}

# Usage example
async def main():
    solution = GeneratedSolution()
    await solution.initialize()
    
    result = await solution.execute({{"input": "test_data"}})
    print(f"Result: {{result}}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
    
    def _generate_javascript_fallback(self, requirements: str, context: Dict[str, Any]) -> str:
        """生成 JavaScript 回退代碼"""
        return f'''
/**
 * {requirements}
 * 
 * Generated by KiloCode fallback system.
 * This is a basic template that should be customized based on your specific needs.
 */

class GeneratedSolution {{
    constructor(config = {{}}) {{
        this.config = config;
        this.initialized = false;
    }}

    async initialize() {{
        try {{
            // TODO: Add initialization logic based on requirements
            this.initialized = true;
            console.log('Solution initialized successfully');
            return true;
        }} catch (error) {{
            console.error('Failed to initialize:', error);
            return false;
        }}
    }}

    async execute(inputData) {{
        if (!this.initialized) {{
            throw new Error('Solution not initialized');
        }}

        try {{
            // TODO: Implement the main logic based on requirements:
            // {requirements}
            
            const result = {{
                success: true,
                data: inputData,
                message: 'Processing completed',
                requirementsAddressed: '{requirements}'
            }};

            return result;
        }} catch (error) {{
            console.error('Execution failed:', error);
            throw error;
        }}
    }}

    getStatus() {{
        return {{
            initialized: this.initialized,
            config: this.config
        }};
    }}
}}

// Usage example
async function main() {{
    const solution = new GeneratedSolution();
    await solution.initialize();
    
    const result = await solution.execute({{ input: 'test_data' }});
    console.log('Result:', result);
}}

module.exports = {{ GeneratedSolution }};
'''
    
    def _generate_typescript_fallback(self, requirements: str, context: Dict[str, Any]) -> str:
        """生成 TypeScript 回退代碼"""
        return f'''
/**
 * {requirements}
 * 
 * Generated by KiloCode fallback system.
 * This is a basic template that should be customized based on your specific needs.
 */

interface Config {{
    [key: string]: any;
}}

interface InputData {{
    [key: string]: any;
}}

interface Result {{
    success: boolean;
    data: InputData;
    message: string;
    requirementsAddressed: string;
}}

interface Status {{
    initialized: boolean;
    config: Config;
}}

class GeneratedSolution {{
    private config: Config;
    private initialized: boolean = false;

    constructor(config: Config = {{}}) {{
        this.config = config;
    }}

    async initialize(): Promise<boolean> {{
        try {{
            // TODO: Add initialization logic based on requirements
            this.initialized = true;
            console.log('Solution initialized successfully');
            return true;
        }} catch (error) {{
            console.error('Failed to initialize:', error);
            return false;
        }}
    }}

    async execute(inputData: InputData): Promise<Result> {{
        if (!this.initialized) {{
            throw new Error('Solution not initialized');
        }}

        try {{
            // TODO: Implement the main logic based on requirements:
            // {requirements}
            
            const result: Result = {{
                success: true,
                data: inputData,
                message: 'Processing completed',
                requirementsAddressed: '{requirements}'
            }};

            return result;
        }} catch (error) {{
            console.error('Execution failed:', error);
            throw error;
        }}
    }}

    getStatus(): Status {{
        return {{
            initialized: this.initialized,
            config: this.config
        }};
    }}
}}

// Usage example
async function main(): Promise<void> {{
    const solution = new GeneratedSolution();
    await solution.initialize();
    
    const result = await solution.execute({{ input: 'test_data' }});
    console.log('Result:', result);
}}

export {{ GeneratedSolution, Config, InputData, Result, Status }};
'''
    
    def _generate_generic_fallback(self, requirements: str, language: str, context: Dict[str, Any]) -> str:
        """生成通用回退代碼"""
        return f'''
/*
 * {requirements}
 * 
 * Generated by KiloCode fallback system for {language}.
 * This is a basic template that should be customized based on your specific needs.
 */

// TODO: Implement the functionality based on requirements:
// {requirements}

function processRequirement() {{
    // Implementation placeholder
    return {{
        success: true,
        message: "Requirement processed",
        language: "{language}",
        requirements: "{requirements}"
    }};
}}

// Main execution
function main() {{
    const result = processRequirement();
    console.log("Result:", result);
    return result;
}}

// Export or run based on your environment
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ processRequirement, main }};
}} else {{
    main();
}}
'''
    
    def _generate_cache_key(self, request: KiloCodeRequest) -> str:
        """生成緩存鍵"""
        key_data = {
            "prompt": request.prompt[:200],  # 限制長度
            "model": request.model.value,
            "mode": request.mode.value,
            "temperature": request.temperature
        }
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    async def get_model_info(self, model: KiloCodeModel) -> Dict[str, Any]:
        """獲取模型信息"""
        if not self.enabled or not self.session:
            return {"available": False, "reason": "KiloCode not available"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{self.api_endpoint}/models/{model.value}",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"available": False, "status": response.status}
                    
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"available": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """獲取客戶端狀態"""
        return {
            "initialized": self.initialized,
            "enabled": self.enabled,
            "api_connected": bool(self.session and self.api_key),
            "stats": self.stats,
            "cache_size": len(self.request_cache) if self.cache_enabled else 0
        }
    
    async def shutdown(self):
        """關閉客戶端"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("KiloCode client shut down")

# 工廠函數
async def create_kilocode_client(config: Dict[str, Any] = None) -> KiloCodeClient:
    """創建並初始化 KiloCode 客戶端"""
    client = KiloCodeClient(config)
    await client.initialize()
    return client

