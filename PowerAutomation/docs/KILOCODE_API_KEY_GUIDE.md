# KiloCode API密钥配置指南

## 🔑 API密钥配置

### 当前配置的API密钥
```
KILO_API_KEY=sk-ant-api03-[YOUR_API_KEY_HERE]
```

## 📋 配置方法

### 方法1: 直接在配置文件中设置
编辑 `PowerAutomation/config/code_generation/kilocode_integration_config.toml`:

```toml
[code_generation_mcp.kilocode]
enabled = true
kilocode_url = "http://localhost:8080"
kilocode_api_key = "sk-ant-api03-[YOUR_API_KEY_HERE]"
timeout = 30
```

### 方法2: 使用环境变量（推荐）
1. 复制环境变量示例文件:
```bash
cp PowerAutomation/config/code_generation/.env.example .env
```

2. 在代码中使用环境变量:
```python
import os
from components.code_generation_mcp import CodeGenerationMcp

config = {
    "kilocode": {
        "enabled": True,
        "kilocode_url": os.getenv("KILOCODE_URL", "http://localhost:8080"),
        "kilocode_api_key": os.getenv("KILO_API_KEY"),
        "timeout": int(os.getenv("KILOCODE_TIMEOUT", "30"))
    },
    "use_kilocode_fallback": os.getenv("USE_KILOCODE_FALLBACK", "true").lower() == "true",
    "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "0.7"))
}

mcp = CodeGenerationMcp(config)
```

### 方法3: 程序化配置
```python
from components.code_generation_mcp import CodeGenerationMcp

config = {
    "kilocode": {
        "enabled": True,
        "kilocode_url": "http://localhost:8080",
        "kilocode_api_key": "sk-ant-api03-[YOUR_API_KEY_HERE]",
        "timeout": 30
    },
    "use_kilocode_fallback": True,
    "quality_threshold": 0.7
}

mcp = CodeGenerationMcp(config)
```

## 🧪 测试API密钥

运行测试脚本验证API密钥配置:
```bash
cd PowerAutomation
python test_kilocode_integration.py
```

预期输出:
```
🚀 开始测试KiloCode集成...
✅ MCP初始化完成: CodeGenerationMcp v1.0.0
📊 KiloCode集成状态: 启用
🎯 质量阈值: 0.7
```

## 🔒 安全注意事项

### 1. 环境变量保护
- 不要将API密钥提交到版本控制系统
- 使用 `.env` 文件并添加到 `.gitignore`
- 在生产环境中使用环境变量管理

### 2. 权限控制
- 确保API密钥只有必要的权限
- 定期轮换API密钥
- 监控API密钥使用情况

### 3. 配置验证
```python
def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if not api_key:
        return False
    if not api_key.startswith("sk-ant-api03-"):
        return False
    if len(api_key) < 50:
        return False
    return True

# 使用示例
api_key = "sk-ant-api03-[YOUR_API_KEY_HERE]"
if validate_api_key(api_key):
    print("✅ API密钥格式有效")
else:
    print("❌ API密钥格式无效")
```

## 🚀 快速开始

### 1. 基本使用
```python
from components.code_generation_mcp import CodeGenerationMcp

# 使用配置的API密钥
mcp = CodeGenerationMcp({
    "kilocode": {
        "enabled": True,
        "kilocode_api_key": "sk-ant-api03-[YOUR_API_KEY_HERE]"
    }
})

# 生成代码
result = await mcp._generate_code({
    "code_type": "api",
    "language": "python",
    "requirements": "创建用户管理API"
})

print(f"生成方法: {result['code_info']['generation_method']}")
print(f"质量分数: {result['code_info']['quality_score']}")
```

### 2. 高级配置
```python
config = {
    "kilocode": {
        "enabled": True,
        "kilocode_url": "http://localhost:8080",
        "kilocode_api_key": "sk-ant-api03-[YOUR_API_KEY_HERE]",
        "timeout": 30
    },
    "use_kilocode_fallback": True,
    "quality_threshold": 0.8,  # 更高的质量要求
    "prefer_kilocode_for_types": ["api", "backend"],
    "prefer_template_for_types": ["frontend", "script"]
}

mcp = CodeGenerationMcp(config)
```

## 📊 监控和调试

### 启用详细日志
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_generation_mcp")

# 在配置中启用日志
config = {
    "kilocode": {
        "enabled": True,
        "kilocode_api_key": "sk-ant-api03-[YOUR_API_KEY_HERE]"
    },
    "logging": {
        "level": "INFO",
        "log_kilocode_calls": True,
        "log_quality_comparisons": True
    }
}
```

### 性能监控
```python
# 获取性能统计
stats = mcp.performance_stats
print(f"KiloCode使用次数: {stats['kilocode_usage']}")
print(f"模板使用次数: {stats['template_usage']}")
print(f"平均质量分数: {stats['code_quality_score']}")
```

## 🎯 故障排除

### 常见问题

1. **API密钥无效**
   - 检查密钥格式是否正确
   - 确认密钥未过期
   - 验证网络连接

2. **KiloCode服务不可用**
   - 检查 `kilocode_url` 配置
   - 确认服务是否运行
   - 检查防火墙设置

3. **质量分数异常**
   - 调整 `quality_threshold` 参数
   - 检查代码生成逻辑
   - 查看详细日志

### 调试命令
```bash
# 测试API连接
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Bearer sk-ant-api03-[YOUR_API_KEY_HERE]" \
  -H "Content-Type: application/json" \
  -d '{"requirements": "test", "language": "python"}'

# 运行完整测试
python test_kilocode_integration.py

# 检查配置
python -c "import toml; print(toml.load('config/code_generation/kilocode_integration_config.toml'))"
```

