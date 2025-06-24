# Demo2: 多场景代码生成演示

## 📋 演示概述

这个演示展示了AICore系统在多种开发场景下的代码生成能力，包括API开发、前端组件、后端服务和数据库设计等全栈开发场景。

## 🎯 演示目标

- 展示AICore的多场景代码生成能力
- 演示不同技术栈的支持程度
- 展示从前端到后端的完整开发栈覆盖
- 提供实用的代码模板和最佳实践

## 🚀 演示场景

### 场景1: API接口生成 🌐
- **技术栈**: Python + FastAPI
- **功能**: RESTful API接口
- **特性**: 数据验证、错误处理、API文档、认证授权
- **输出**: 完整的用户管理API

### 场景2: 前端组件生成 🎨
- **技术栈**: TypeScript + React + TailwindCSS
- **功能**: 可复用的UI组件
- **特性**: 响应式设计、无障碍支持、TypeScript类型
- **输出**: UserCard和UserForm组件

### 场景3: 后端服务生成 ⚙️
- **技术栈**: Python + Flask + PostgreSQL
- **功能**: 微服务架构
- **特性**: 数据库连接、错误处理、日志记录、配置管理
- **输出**: 用户服务和认证服务

### 场景4: 数据库模式生成 🗄️
- **技术栈**: PostgreSQL + SQL
- **功能**: 数据库设计
- **特性**: 索引优化、外键约束、触发器、视图
- **输出**: 完整的用户管理数据库模式

## 🛠️ 技术栈覆盖

### 编程语言
- ✅ **Python** - 后端开发、API服务
- ✅ **TypeScript** - 前端开发、类型安全
- ✅ **JavaScript** - 前端交互、动态功能
- ✅ **SQL** - 数据库设计、查询优化

### 框架和库
- ✅ **FastAPI** - 现代Python Web框架
- ✅ **React** - 流行的前端框架
- ✅ **Flask** - 轻量级Python Web框架
- ✅ **TailwindCSS** - 实用优先的CSS框架
- ✅ **PostgreSQL** - 强大的关系型数据库

### 开发特性
- ✅ **RESTful API设计**
- ✅ **响应式前端组件**
- ✅ **微服务架构**
- ✅ **数据库优化**
- ✅ **类型安全**
- ✅ **错误处理**
- ✅ **文档生成**

## 🚀 快速开始

### 运行完整演示
```bash
# 进入演示目录
cd deployment/demos/demo2_code_generation/

# 运行演示
python code_generation_demo.py
```

### 运行特定场景
```bash
# 修改demo_config.toml，只启用需要的场景
[scenarios]
api_generation = true
frontend_components = false
backend_services = false
database_schemas = false
```

## 📊 演示流程

1. **初始化阶段**
   - 启动AICore系统
   - 加载演示配置
   - 准备输出目录

2. **场景1: API生成**
   - 分析API需求
   - 生成FastAPI代码
   - 包含CRUD操作和认证

3. **场景2: 前端组件**
   - 分析组件需求
   - 生成React+TypeScript代码
   - 包含样式和类型定义

4. **场景3: 后端服务**
   - 分析服务架构
   - 生成Flask微服务代码
   - 包含数据库集成

5. **场景4: 数据库设计**
   - 分析数据模型
   - 生成PostgreSQL模式
   - 包含优化和约束

6. **报告生成**
   - 汇总所有结果
   - 生成详细报告
   - 提供使用建议

## 📈 预期结果

### 生成文件
- `user_api.py` - FastAPI用户管理接口
- `user_components.tsx` - React用户组件
- `user_service.py` - Flask用户服务
- `database_schema.sql` - PostgreSQL数据库模式
- `demo_summary_report.md` - 演示总结报告

### 质量指标
- **代码质量分数**: ≥ 7.5/10
- **生成时间**: < 45秒/场景
- **功能完整性**: > 90%
- **最佳实践遵循**: 优秀

### 技术覆盖
- **全栈开发**: 前端 + 后端 + 数据库
- **现代技术栈**: 最新框架和最佳实践
- **生产就绪**: 可直接用于项目开发

## ⚙️ 自定义配置

### 启用/禁用场景
```toml
[scenarios]
api_generation = true      # API接口生成
frontend_components = true # 前端组件生成
backend_services = true    # 后端服务生成
database_schemas = true    # 数据库模式生成
```

### 选择技术栈
```toml
[languages]
python = true
typescript = true
javascript = true

[frameworks]
fastapi = true    # Python API框架
react = true      # 前端框架
flask = true      # Python微服务框架
postgresql = true # 数据库
```

### 质量要求
```toml
[quality_requirements]
min_quality_score = 8.0        # 提高质量要求
max_generation_time = 30       # 缩短生成时间
documentation_level = "detailed" # 详细文档
```

## 🎯 演示价值

### 技术展示价值
- **多语言支持** - 展示跨语言代码生成能力
- **全栈覆盖** - 从前端到后端的完整解决方案
- **现代技术栈** - 使用最新的框架和最佳实践
- **生产就绪** - 生成的代码可直接用于项目

### 商业价值
- **开发效率** - 显著提升开发速度
- **代码质量** - 确保一致的高质量代码
- **技术标准化** - 统一的代码风格和架构
- **学习成本降低** - 提供最佳实践模板

### 教育价值
- **架构设计** - 展示现代应用架构
- **最佳实践** - 提供行业标准代码示例
- **技术选型** - 展示不同技术的适用场景
- **代码规范** - 统一的编码标准

## 📚 生成代码示例

### API接口示例
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="User Management API")

class User(BaseModel):
    username: str
    email: str

@app.get("/users")
async def get_users():
    # 获取用户列表
    pass

@app.post("/users")
async def create_user(user: User):
    # 创建新用户
    pass
```

### React组件示例
```typescript
interface UserCardProps {
  user: User;
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* 用户卡片内容 */}
    </div>
  );
};
```

### 数据库模式示例
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

## 🔧 故障排除

### 常见问题
1. **生成失败** - 检查网络连接和API配置
2. **质量分数低** - 调整质量要求参数
3. **生成时间长** - 简化需求或提高超时时间
4. **文件保存失败** - 检查输出目录权限

### 解决方案
- 查看详细错误日志
- 检查配置文件格式
- 验证依赖组件状态
- 参考演示报告中的错误信息

## 🎊 成功标准

- ✅ 所有启用的场景都能成功生成代码
- ✅ 生成的代码质量达到预期标准
- ✅ 技术栈覆盖符合配置要求
- ✅ 演示报告自动生成且内容完整
- ✅ 生成的代码可以直接使用或作为模板

---

**🚀 体验AICore的强大多场景代码生成能力！**

