# 程序员求职加速器Agent 项目文档

## 项目概述

程序员求职加速器Agent是一个基于AI技术的智能求职助手，旨在帮助程序员更高效地求职。系统通过分析用户的GitHub和LeetCode数据，生成个性化的技能报告、学习路径和岗位推荐。

## 核心功能

### 1. 技能分析
- **GitHub分析**: 分析用户的代码仓库，识别编程语言、框架、项目类型等技能
- **LeetCode分析**: 
  - 支持截图上传自动解析题目数据
  - 题目难度分布统计（简单/中等/困难）
  - 编程语言使用分析
  - 可视化图表展示技能分布
- **技能报告**: 生成详细的技能分析报告，包括强项、弱项和改进建议

### 2. 学习路径生成
- **个性化路径**: 基于用户技能差距和目标岗位生成专属学习路径
- **任务分解**: 将学习目标分解为具体的可执行任务
- **资源推荐**: 提供相关的学习资源和实践项目

### 3. AI督学
- **每日任务**: 推送个性化的每日学习任务
- **进度跟踪**: 实时跟踪学习进度和完成情况
- **智能提醒**: 根据学习习惯提供智能提醒

### 4. 岗位匹配
- **智能匹配**: 基于技能匹配算法推荐最适合的岗位
- **差距分析**: 分析用户技能与岗位要求的差距
- **求职建议**: 提供针对性的求职建议和简历优化建议

## 技术架构

### 后端技术栈
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **认证**: JWT
- **AI引擎**: ModelScope-CodeGeeX (本地部署)

### 前端技术栈
- **框架**: Next.js 14 (React)
- **样式**: TailwindCSS
- **图标**: Lucide React
- **图表**: Chart.js + react-chartjs-2
- **HTTP客户端**: Axios
- **OCR**: Tesseract.js

### 部署架构
- **前端**: Vercel (免费托管)
- **后端**: Vercel Serverless Functions
- **数据库**: Vercel Postgres (免费版)
- **AI模型**: 本地部署

## 项目结构

```
Technical_test/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # Next.js前端
│   ├── app/               # 页面组件
│   ├── components/        # 可复用组件
│   │   ├── LeetCodeAnalysis.tsx  # LeetCode分析主组件
│   │   ├── ImageUploader.tsx     # 截图上传组件
│   │   ├── OCRResultEditor.tsx   # OCR结果编辑器
│   │   └── SkillVisualization.tsx # 技能可视化
│   ├── lib/               # 工具函数
│   │   ├── ocrService.ts  # OCR解析服务
│   │   └── leetcodeParser.ts # LeetCode数据解析
│   ├── types/             # TypeScript类型
│   └── package.json       # Node.js依赖
├── agent/                 # AI Agent核心
├── database/              # 数据库迁移
├── docs/                  # 项目文档
└── scripts/               # 部署脚本
```

## 更新日志

### v1.1.0 (2025-07-12)
- 新增LeetCode分析功能
  - 实现截图上传和OCR解析
  - 添加题目难度分布可视化
  - 支持编程语言使用分析
  - 提供数据修正编辑功能
- 前端新增组件:
  - LeetCodeAnalysis: 主分析组件
  - ImageUploader: 截图上传组件
  - OCRResultEditor: 结果编辑组件
  - SkillVisualization: 可视化图表组件
- 后端新增服务:
  - leetcode_service: LeetCode数据分析服务
  - 新增/api/leetcode/analyze接口

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基础功能：用户认证、技能分析、学习路径、岗位匹配
- 集成AI Agent功能
- 完成前后端开发
- 提供部署脚本和文档

[其余原有内容保持不变...]
