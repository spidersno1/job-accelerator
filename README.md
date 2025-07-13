# 程序员求职加速器 - AI驱动的智能求职助手

> 🚀 **项目状态**：生产就绪，代码完整注释，易于维护  
> 📅 **最后更新**：2025年1月  
> 🎯 **完成度**：核心功能 100%，代码注释完整

## 🌟 项目概述

程序员求职加速器是一个基于AI技术的智能求职助手，帮助程序员分析技能、匹配职位、规划学习路径，提升求职成功率。

### ✨ 核心功能

#### 🎯 职位智能匹配 (商业级)
- **智能爬虫**：自动从拉勾网、智联招聘、BOSS直聘等平台爬取职位
- **合规爬取**：遵循robots.txt协议，只爬取公开合法信息
- **智能算法**：基于技能相似度的职位匹配
- **实时计算**：动态匹配度百分比评估
- **可视化展示**：直观的匹配结果和职位详情
- **个性化推荐**：根据用户技能推荐最适合的职位

#### 📊 技能深度分析 (商业级)
- **多样化输入**：支持文件上传、文本输入、图片分析
- **智能代码分析**：支持20+编程语言，复杂度分析，设计模式识别
- **多维度统计**：技能分类、熟练度、来源分析
- **可视化图表**：雷达图、柱状图、饼图等多种展示方式
- **智能识别**：自动识别最强技能和改进领域
- **学习建议**：个性化学习路径和资源推荐

#### 🛤️ 学习路径生成 (商业级)
- **智能路径规划**：结合技能分析和岗位匹配数据生成个性化学习路径
- **多种创建方式**：支持基于目标职位或技能目标创建
- **依赖关系排序**：智能分析技能依赖，合理安排学习顺序
- **进度跟踪管理**：完整的任务管理和进度跟踪系统
- **学习资源推荐**：提供高质量的学习资源和实践建议
- **里程碑设置**：设置学习里程碑，增强学习动机

#### 💡 LeetCode分析
- **截图识别**：支持LeetCode截图的OCR解析
- **手动输入**：灵活的数据输入方式
- **数据修正**：可编辑的解析结果
- **可视化展示**：直观的统计图表
- **技能映射**：将算法能力映射到实际技能

#### 🤖 AI助手
- **智能对话**：基于用户数据的个性化建议
- **学习督导**：智能提醒和进度跟踪
- **求职指导**：简历优化和面试准备建议

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI (Python 3.11+)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + OAuth2
- **文档**: 自动生成Swagger/OpenAPI文档
- **代码质量**: 完整的类型注解和文档字符串

### 前端技术栈
- **框架**: Next.js 14 (React 18)
- **语言**: TypeScript
- **样式**: TailwindCSS
- **图标**: Lucide React
- **图表**: Chart.js + react-chartjs-2
- **HTTP客户端**: Axios
- **OCR**: Tesseract.js

### 代码质量保证
- **完整注释**：所有文件都有详细的文档注释
- **类型安全**：TypeScript和Python类型注解
- **模块化设计**：清晰的代码结构和职责分离
- **错误处理**：完善的异常处理和用户反馈
- **安全性**：JWT认证、输入验证、SQL注入防护

## 📁 项目结构

```
Technical_test/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── core/           # 核心配置和安全
│   │   ├── models/         # 数据模型定义
│   │   ├── routers/        # API路由处理
│   │   ├── services/       # 业务逻辑服务
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # Next.js前端
│   ├── app/               # 页面组件
│   ├── components/        # 可复用组件
│   ├── lib/               # 工具函数
│   ├── types/             # TypeScript类型定义
│   └── package.json       # Node.js依赖
├── agent/                 # AI Agent核心逻辑
├── alembic/               # 数据库迁移
├── docs/                  # 项目文档
└── scripts/               # 部署脚本
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Technical_test
```

2. **后端设置**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **前端设置**
```bash
cd frontend
npm install
npm run dev
```

4. **启动服务**
```bash
# 在项目根目录
npm run dev  # 同时启动前后端
```

### 访问地址
- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📖 API文档

系统提供完整的API文档，包括：
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- 所有端点都有详细的请求/响应示例
- 完整的错误码说明

## 🔧 配置说明

### 环境变量
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=sqlite:///./job_accelerator.db

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub API
GITHUB_TOKEN=your-github-token

# 其他配置
DEBUG=true
ENVIRONMENT=development
```

### 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 🔒 安全特性

- JWT令牌认证
- 密码强度验证
- 登录尝试限制
- SQL注入防护
- XSS防护
- CORS配置
- 输入验证和清理

## 🎯 部署指南

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
# 构建前端
cd frontend && npm run build

# 启动后端
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# 或使用Docker
docker-compose up -d
```

## 📝 维护指南

### 代码规范
- 所有函数都有详细的文档字符串
- 使用类型注解提高代码可读性
- 遵循PEP 8 (Python) 和 ESLint (TypeScript)
- 模块化设计，单一职责原则

### 添加新功能
1. 在相应的 `services/` 目录添加业务逻辑
2. 在 `routers/` 目录添加API端点
3. 在 `models/` 目录添加数据模型
4. 更新前端组件和类型定义
5. 添加完整的文档注释

### 调试建议
- 使用 `/health` 端点检查服务状态
- 查看 `/docs` 了解API详情
- 检查浏览器控制台和网络请求
- 使用Python调试器和React DevTools

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 📞 联系我们

- 项目维护者：程序员求职加速器团队
- 技术支持：查看项目文档和代码注释
- 问题反馈：GitHub Issues

---

**注意**：本项目所有代码都有详细的中文注释，便于理解和维护。建议在修改代码时保持注释的完整性和准确性。
