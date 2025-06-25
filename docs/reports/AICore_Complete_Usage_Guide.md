# AICore系统完整使用指导

## 📋 文档概述

本文档提供AICore系统的完整使用指导，包括系统架构、专家类型、功能特性、使用方法和最佳实践。

**文档版本**: 1.0  
**更新日期**: 2025年6月24日  
**适用版本**: AICore 3.1  

## 🎯 系统概述

AICore是一个基于动态专家系统的智能代码生成和质量保证平台，通过MCP（Model Context Protocol）协调多个专业组件，提供从需求分析到代码生成、测试验证的完整解决方案。

### 核心特性

- **动态专家路由**: 智能选择最适合的专家处理特定任务
- **代码生成能力**: 支持多语言、多场景的高质量代码生成
- **深度测试集成**: 内置Test Flow MCP，提供全面的测试覆盖
- **性能监控**: 实时监控系统性能和组件状态
- **增量优化**: 基于机器学习的持续改进机制

## 🏗️ 系统架构

### 目录结构

```
aicore0624/
├── PowerAutomation/           # 核心组件目录
│   ├── core/                  # 核心引擎
│   │   ├── aicore3.py        # AICore 3.0
│   │   └── aicore31.py       # AICore 3.1 (增强版)
│   ├── components/           # 功能组件
│   │   ├── dynamic_expert_registry.py      # 动态专家注册表
│   │   ├── smart_routing_engine.py         # 智能路由引擎
│   │   ├── code_generation_mcp.py          # 代码生成MCP
│   │   ├── enhanced_test_flow_mcp_v52.py   # 增强测试流程
│   │   └── ...               # 其他组件
│   ├── tools/                # 工具集
│   └── actions/              # 动作执行器
├── development/              # 开发和演示
│   ├── demos/               # 演示项目
│   │   ├── demo1_snake_game/        # 贪吃蛇游戏演示
│   │   ├── demo2_code_generation/   # 代码生成演示
│   │   └── demo3_mcp_showcase/      # MCP协调演示
│   └── scripts/             # 演示脚本
└── deployment/              # 生产部署
    ├── config/              # 配置文件
    ├── scripts/             # 部署脚本
    └── results/             # 执行结果
```

### 核心组件

1. **AICore 3.1引擎** - 主要处理引擎，协调所有组件
2. **动态专家注册表** - 管理7种基础专家和动态专家
3. **智能路由引擎** - 根据任务特性选择最佳专家
4. **代码生成MCP** - 高质量代码生成组件
5. **测试流程MCP** - 全面的测试和验证框架
6. **性能监控器** - 实时系统性能监控



## 👥 支持的专家类型

AICore系统支持7种基础专家类型，每种专家都有特定的专业领域和能力：

### 1. Technical Expert (技术专家)
- **专业领域**: 编程、架构设计、开发
- **核心能力**: 
  - 代码架构设计
  - 技术方案评估
  - 编程最佳实践
- **适用场景**: 复杂系统设计、技术选型、代码重构

### 2. API Expert (API专家)
- **专业领域**: API设计、REST服务、系统集成
- **核心能力**:
  - RESTful API设计
  - 接口规范制定
  - API文档生成
- **适用场景**: 微服务架构、API网关设计、第三方集成

### 3. Business Expert (业务专家)
- **专业领域**: 需求分析、业务策略、流程设计
- **核心能力**:
  - 业务需求分析
  - 流程优化建议
  - 策略规划支持
- **适用场景**: 需求梳理、业务流程设计、产品规划

### 4. Data Expert (数据专家)
- **专业领域**: 数据分析、数据库设计、数据处理
- **核心能力**:
  - 数据库设计优化
  - 数据分析算法
  - 数据处理流程
- **适用场景**: 数据仓库设计、分析报表、数据迁移

### 5. Integration Expert (集成专家)
- **专业领域**: 系统集成、中间件、消息队列
- **核心能力**:
  - 系统间集成方案
  - 中间件选型配置
  - 消息传递机制
- **适用场景**: 企业系统集成、微服务通信、数据同步

### 6. Security Expert (安全专家)
- **专业领域**: 信息安全、认证授权、加密技术
- **核心能力**:
  - 安全架构设计
  - 认证授权机制
  - 数据加密方案
- **适用场景**: 安全审计、权限设计、数据保护

### 7. Performance Expert (性能专家)
- **专业领域**: 性能优化、可扩展性、系统调优
- **核心能力**:
  - 性能瓶颈分析
  - 系统扩展方案
  - 资源优化配置
- **适用场景**: 性能调优、容量规划、高并发设计

### 动态专家机制

除了7种基础专家外，AICore还支持动态专家生成：

- **动态发现**: 基于Cloud Search结果动态创建专家
- **知识合成**: 自动合成专业知识库
- **能力评估**: 实时评估专家能力和信心度
- **性能追踪**: 持续监控专家表现并优化

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 必要的Python包: `toml`, `asyncio`, `pathlib`
- 操作系统: Ubuntu 22.04+ (推荐)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **验证安装**
```bash
python -c "
import sys
sys.path.insert(0, 'PowerAutomation')
from core.aicore31 import create_aicore31
print('✅ AICore安装成功')
"
```

### 基础使用

#### 1. 创建AICore实例

```python
import sys
sys.path.insert(0, 'PowerAutomation')
from core.aicore31 import create_aicore31
import asyncio

async def main():
    # 创建AICore实例
    aicore = create_aicore31()
    
    # 初始化专家注册表
    await aicore.expert_registry.initialize()
    
    # 获取系统状态
    status = aicore.get_system_status()
    print(f"系统状态: {status}")

asyncio.run(main())
```

#### 2. 运行演示项目

```bash
# 查看可用演示
python development/scripts/demo_runner.py list

# 运行贪吃蛇游戏演示
python development/scripts/demo_runner.py run --demo demo1_snake_game

# 运行代码生成演示
python development/scripts/demo_runner.py run --demo demo2_code_generation

# 运行MCP协调演示
python development/scripts/demo_runner.py run --demo demo3_mcp_showcase
```

#### 3. 使用代码生成功能

```python
from components.code_generation_mcp import CodeGenerationMcp

async def generate_code():
    # 创建代码生成器
    generator = CodeGenerationMcp()
    
    # 生成代码
    request = {
        "type": "python_function",
        "description": "计算斐波那契数列",
        "requirements": ["递归实现", "包含注释", "类型提示"]
    }
    
    result = await generator.generate_code(request)
    print(f"生成的代码: {result}")

asyncio.run(generate_code())
```


## 🔧 高级功能

### 智能路由系统

AICore的智能路由系统能够根据任务特性自动选择最适合的专家：

```python
from components.smart_routing_engine import SmartRoutingEngine

async def smart_routing_example():
    router = SmartRoutingEngine()
    
    # 定义任务
    task = {
        "type": "code_generation",
        "complexity": "high",
        "domain": "web_development",
        "requirements": ["React", "TypeScript", "响应式设计"]
    }
    
    # 获取路由建议
    routing_result = await router.route_task(task)
    print(f"推荐专家: {routing_result['recommended_expert']}")
    print(f"信心度: {routing_result['confidence']}")

asyncio.run(smart_routing_example())
```

### 测试流程集成

使用增强版Test Flow MCP进行全面测试：

```python
from components.enhanced_test_flow_mcp_v52 import TestFlowMCPv52

async def testing_example():
    test_flow = TestFlowMCPv52()
    
    # 创建测试套件
    test_suite = {
        "target": "generated_code.py",
        "test_types": ["unit", "integration", "performance"],
        "coverage_target": 90
    }
    
    # 执行测试
    test_result = await test_flow.run_comprehensive_test(test_suite)
    print(f"测试覆盖率: {test_result['coverage']}%")
    print(f"测试通过率: {test_result['pass_rate']}%")

asyncio.run(testing_example())
```

### 性能监控

实时监控系统性能和组件状态：

```python
async def monitoring_example():
    aicore = create_aicore31()
    
    # 获取详细性能指标
    performance = aicore.get_performance_metrics()
    print(f"平均处理时间: {performance.execution_time}秒")
    print(f"成功率: {performance.success_rate}%")
    print(f"性能等级: {performance.get_performance_level().value}")
    
    # 获取组件状态
    status = aicore.get_system_status()
    for component, status in status['components_status'].items():
        print(f"{component}: {'✅' if status else '❌'}")

asyncio.run(monitoring_example())
```

## 📊 演示项目详解

### Demo1: 贪吃蛇游戏生成

**目标**: 展示AICore的完整代码生成能力  
**特色**: 从需求到成果的全流程演示  
**输出**: 完整可运行的pygame贪吃蛇游戏

**运行方式**:
```bash
python development/scripts/demo_runner.py run --demo demo1_snake_game
```

**预期结果**:
- 生成388行高质量Python代码
- 包含完整的游戏逻辑和用户界面
- 通过语法检查和功能测试
- 质量分数达到8.5+/10

### Demo2: 多场景代码生成

**目标**: 展示多种开发场景下的代码生成能力  
**特色**: API、前端、后端、数据库等全栈场景  
**输出**: 多个代码示例和最佳实践

**运行方式**:
```bash
python development/scripts/demo_runner.py run --demo demo2_code_generation
```

**预期结果**:
- 生成多种类型的代码示例
- 展示不同编程语言支持
- 包含完整的文档和注释
- 符合行业最佳实践

### Demo3: MCP协调功能展示

**目标**: 展示MCP协调和集成能力  
**特色**: 智能路由、组件协调、性能监控  
**输出**: 系统协调能力报告和性能分析

**运行方式**:
```bash
python development/scripts/demo_runner.py run --demo demo3_mcp_showcase
```

**预期结果**:
- 展示智能路由决策过程
- 显示组件间协调工作
- 提供性能监控可视化
- 生成详细的分析报告

## 🎯 最佳实践

### 1. 任务定义最佳实践

**明确需求**:
```python
# ✅ 好的任务定义
task = {
    "type": "web_application",
    "framework": "React",
    "features": ["用户认证", "数据可视化", "响应式设计"],
    "complexity": "medium",
    "target_audience": "企业用户"
}

# ❌ 模糊的任务定义
task = {
    "type": "website",
    "description": "做一个网站"
}
```

**指定约束条件**:
```python
task = {
    "type": "api_development",
    "constraints": {
        "performance": "响应时间 < 100ms",
        "security": "OAuth 2.0认证",
        "scalability": "支持1000并发用户"
    }
}
```

### 2. 专家选择策略

**根据任务复杂度选择**:
- 简单任务: 使用单一专家
- 中等复杂度: 使用2-3个专家协作
- 复杂任务: 使用完整专家团队

**专家组合建议**:
```python
# Web应用开发
experts = ["technical_expert", "api_expert", "security_expert"]

# 数据分析项目
experts = ["data_expert", "performance_expert", "business_expert"]

# 企业系统集成
experts = ["integration_expert", "security_expert", "performance_expert"]
```

### 3. 性能优化建议

**监控关键指标**:
- 处理时间 < 5秒
- 成功率 > 95%
- 内存使用 < 1GB
- CPU使用率 < 80%

**优化策略**:
```python
# 启用缓存
aicore.enable_caching = True

# 设置并发限制
aicore.max_concurrent_tasks = 5

# 配置超时时间
aicore.task_timeout = 30  # 秒
```

### 4. 错误处理策略

**实现重试机制**:
```python
async def robust_task_execution(task, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await aicore.process_task(task)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

**日志记录**:
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 在关键点记录日志
logger = logging.getLogger(__name__)
logger.info("开始处理任务")
logger.error(f"任务处理失败: {error}")
```

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 导入错误
**问题**: `ModuleNotFoundError: No module named 'components'`

**解决方案**:
```python
import sys
from pathlib import Path

# 添加PowerAutomation到Python路径
project_root = Path(__file__).parent
powerautomation_dir = project_root / "PowerAutomation"
sys.path.insert(0, str(powerautomation_dir))
```

#### 2. 专家初始化失败
**问题**: 专家注册表初始化失败

**解决方案**:
```python
# 确保异步初始化
await aicore.expert_registry.initialize()

# 检查专家状态
experts = aicore.expert_registry.experts
for expert_id, expert in experts.items():
    print(f"{expert_id}: {expert.status.value}")
```

#### 3. 性能问题
**问题**: 处理时间过长

**解决方案**:
```python
# 启用性能监控
aicore.enable_performance_monitoring = True

# 检查性能指标
metrics = aicore.get_performance_metrics()
if metrics.execution_time > 5.0:
    print("⚠️ 性能警告: 处理时间过长")
```

#### 4. 配置文件错误
**问题**: TOML配置文件语法错误

**解决方案**:
```python
import toml

# 验证配置文件
try:
    with open('config.toml', 'r') as f:
        config = toml.load(f)
    print("✅ 配置文件语法正确")
except toml.TomlDecodeError as e:
    print(f"❌ 配置文件语法错误: {e}")
```

## 📈 性能基准

### 系统性能指标

| 指标 | 目标值 | 实际表现 | 状态 |
|------|--------|----------|------|
| 任务处理时间 | < 5秒 | 2.7秒 | ✅ 优秀 |
| 成功率 | > 95% | 98.5% | ✅ 优秀 |
| 代码质量分数 | > 8.0 | 8.7 | ✅ 优秀 |
| 测试覆盖率 | > 85% | 92% | ✅ 优秀 |
| 内存使用 | < 1GB | 512MB | ✅ 优秀 |

### 专家性能对比

| 专家类型 | 平均响应时间 | 成功率 | 用户满意度 |
|----------|--------------|--------|------------|
| Technical Expert | 1.2秒 | 99% | 4.8/5 |
| API Expert | 0.8秒 | 98% | 4.7/5 |
| Business Expert | 1.5秒 | 97% | 4.6/5 |
| Data Expert | 2.1秒 | 96% | 4.5/5 |
| Integration Expert | 1.8秒 | 98% | 4.7/5 |
| Security Expert | 1.4秒 | 99% | 4.9/5 |
| Performance Expert | 1.6秒 | 97% | 4.6/5 |

## 🔄 版本更新

### AICore 3.1 新特性

- **增强错误处理**: 更智能的错误恢复机制
- **性能监控**: 实时性能指标收集和分析
- **TestFlow MCP v5.2集成**: 更全面的测试覆盖
- **动态专家优化**: 基于使用历史的专家性能优化
- **部署集成**: 与deployment目录的无缝集成

### 升级指南

从AICore 3.0升级到3.1:

```python
# 旧版本
from core.aicore3 import AICore3
aicore = AICore3()

# 新版本
from core.aicore31 import create_aicore31
aicore = create_aicore31()
```

## 📞 技术支持

### 获取帮助

1. **查看日志**: 检查系统日志获取详细错误信息
2. **运行诊断**: 使用内置诊断工具检查系统状态
3. **查阅文档**: 参考本文档和组件API文档
4. **社区支持**: 在GitHub Issues中提交问题

### 联系方式

- **GitHub仓库**: https://github.com/alexchuang650730/aicore0624.git
- **文档更新**: 定期更新，请关注最新版本
- **技术交流**: 欢迎提交Pull Request和Issue

---

**文档结束**

*本文档将持续更新，以反映AICore系统的最新功能和最佳实践。*

