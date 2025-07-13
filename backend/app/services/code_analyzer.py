"""
代码分析器服务模块

这个模块提供全面的代码分析功能，支持多种输入方式和编程语言：

核心功能：
1. 文件分析 - 分析上传的代码文件
2. 文本分析 - 分析粘贴的代码片段
3. 图片分析 - 分析代码截图（需要OCR）
4. 技能提取 - 从代码中识别技能和框架
5. 复杂度评估 - 评估代码复杂度和质量
6. 设计模式识别 - 识别常见设计模式

支持的编程语言：
- Python, JavaScript, TypeScript, Java, C++, C#
- Go, PHP, Ruby, Swift, Kotlin, Scala, Rust
- HTML, CSS, SQL, JSON, XML, YAML等

分析维度：
- 编程语言和框架识别
- 技能熟练度评估
- 代码质量指标
- 设计模式使用
- 学习建议生成

使用方式：
analyzer = CodeAnalyzer()
result = analyzer.analyze_file("example.py", file_content)
report = analyzer.generate_skill_report([result])

作者: 程序员求职加速器团队
创建时间: 2024年
最后更新: 2025年1月
"""

import re
import json
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile
import os
from datetime import datetime

class CodeAnalyzer:
    """
    代码分析器 - 分析不同类型的代码输入并提取技能
    
    这个类提供了全面的代码分析功能，能够：
    1. 分析各种编程语言的代码文件
    2. 识别使用的技术栈和框架
    3. 评估代码复杂度和质量
    4. 生成技能熟练度报告
    5. 提供个性化学习建议
    """
    
    def __init__(self):
        """初始化代码分析器，设置语言映射和技能关键词"""
        # 编程语言文件扩展名映射
        self.language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.rs': 'Rust',
            '.dart': 'Dart',
            '.vue': 'Vue.js',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }
        
        # 技能关键词映射 - 用于从代码中识别技能
        self.skill_keywords = {
            # 编程语言
            'Python': ['python', 'py', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'express', 'jquery'],
            'TypeScript': ['typescript', 'ts', 'interface', 'type', 'enum'],
            'Java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
            'C++': ['cpp', 'c++', 'iostream', 'vector', 'string'],
            'C#': ['csharp', 'c#', 'dotnet', '.net', 'asp.net'],
            'Go': ['golang', 'go', 'goroutine', 'channel'],
            'PHP': ['php', 'laravel', 'symfony', 'composer'],
            'Ruby': ['ruby', 'rails', 'gem', 'bundler'],
            'Swift': ['swift', 'ios', 'xcode', 'cocoapods'],
            'Kotlin': ['kotlin', 'android', 'coroutines'],
            'Rust': ['rust', 'cargo', 'tokio'],
            'Dart': ['dart', 'flutter', 'widget'],
            
            # 前端框架
            'React': ['react', 'jsx', 'component', 'usestate', 'useeffect'],
            'Vue.js': ['vue', 'vuex', 'nuxt', 'composition'],
            'Angular': ['angular', 'typescript', 'component', 'service'],
            
            # 后端框架
            'Django': ['django', 'models', 'views', 'urls', 'admin'],
            'Flask': ['flask', 'route', 'request', 'session'],
            'FastAPI': ['fastapi', 'pydantic', 'async', 'await'],
            'Express': ['express', 'middleware', 'router'],
            'Spring': ['spring', 'boot', 'mvc', 'security'],
            
            # 数据库
            'MySQL': ['mysql', 'select', 'insert', 'update', 'delete'],
            'PostgreSQL': ['postgresql', 'postgres', 'psql'],
            'MongoDB': ['mongodb', 'mongo', 'collection', 'document'],
            'Redis': ['redis', 'cache', 'session'],
            
            # 云服务
            'AWS': ['aws', 'ec2', 's3', 'lambda', 'rds'],
            'Azure': ['azure', 'blob', 'functions'],
            'GCP': ['gcp', 'cloud', 'bigquery'],
            
            # 工具和技术
            'Docker': ['docker', 'container', 'dockerfile'],
            'Kubernetes': ['kubernetes', 'k8s', 'pod', 'service'],
            'Git': ['git', 'commit', 'branch', 'merge'],
            'CI/CD': ['jenkins', 'github actions', 'gitlab ci'],
            'Testing': ['test', 'unittest', 'pytest', 'jest', 'mocha']
        }
    
    def analyze_file(self, file_path: str, file_content: bytes) -> Dict[str, Any]:
        """
        分析文件内容并提取技能信息
        
        Args:
            file_path: 文件路径
            file_content: 文件内容（字节形式）
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 获取文件扩展名
            file_ext = Path(file_path).suffix.lower()
            
            # 尝试解码文件内容
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = file_content.decode('gbk')
                except UnicodeDecodeError:
                    return {"error": "无法解码文件内容"}
            
            # 分析文件类型和语言
            language = self.language_extensions.get(file_ext, 'Unknown')
            
            # 分析代码内容
            analysis = self._analyze_code_content(content, language)
            analysis.update({
                'file_name': Path(file_path).name,
                'file_type': file_ext,
                'language': language,
                'file_size': len(file_content),
                'line_count': len(content.splitlines())
            })
            
            return analysis
            
        except Exception as e:
            return {"error": f"文件分析失败: {str(e)}"}
    
    def analyze_text(self, text_content: str) -> Dict[str, Any]:
        """
        分析文本内容并提取技能信息
        
        Args:
            text_content: 要分析的文本内容
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 检测可能的编程语言
            detected_languages = self._detect_languages(text_content)
            
            # 分析代码内容
            analysis = self._analyze_code_content(text_content, detected_languages[0] if detected_languages else 'Mixed')
            analysis.update({
                'input_type': 'text',
                'detected_languages': detected_languages,
                'character_count': len(text_content),
                'line_count': len(text_content.splitlines())
            })
            
            return analysis
            
        except Exception as e:
            return {"error": f"文本分析失败: {str(e)}"}
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        分析图片内容 (OCR) 并提取技能信息
        
        Args:
            image_data: 图片数据（字节形式）
            
        Returns:
            Dict: 包含分析结果的字典
            
        Note:
            当前版本返回基础信息，完整OCR功能需要集成Tesseract或其他OCR服务
        """
        try:
            # 这里可以集成OCR服务，暂时返回基础信息
            return {
                'input_type': 'image',
                'image_size': len(image_data),
                'analysis_note': '图片分析功能需要集成OCR服务',
                'skills': [],
                'frameworks': [],
                'complexity_score': 0
            }
            
        except Exception as e:
            return {"error": f"图片分析失败: {str(e)}"}
    
    def _analyze_code_content(self, content: str, language: str) -> Dict[str, Any]:
        """分析代码内容并提取技能"""
        content_lower = content.lower()
        
        # 提取技能
        detected_skills = []
        frameworks = []
        
        # 检查每个技能类别
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    skill_info = {
                        'name': keyword.title(),
                        'category': category,
                        'confidence': self._calculate_confidence(content_lower, keyword),
                        'occurrences': content_lower.count(keyword)
                    }
                    
                    if category in ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Rust']:
                        detected_skills.append(skill_info)
                    else:
                        frameworks.append(skill_info)
        
        # 计算复杂度分数
        complexity_score = self._calculate_complexity(content)
        
        # 检测设计模式
        design_patterns = self._detect_design_patterns(content)
        
        # 分析代码质量指标
        quality_metrics = self._analyze_code_quality(content)
        
        return {
            'primary_language': language,
            'skills': detected_skills,
            'frameworks': frameworks,
            'design_patterns': design_patterns,
            'complexity_score': complexity_score,
            'quality_metrics': quality_metrics,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _detect_languages(self, content: str) -> List[str]:
        """检测文本中的编程语言"""
        detected = []
        content_lower = content.lower()
        
        # 语言特征检测
        language_patterns = {
            'Python': [r'def\s+\w+\(', r'import\s+\w+', r'from\s+\w+\s+import', r'print\(', r'if\s+__name__\s*==\s*["\']__main__["\']'],
            'JavaScript': [r'function\s+\w+\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'console\.log\(', r'=>'],
            'TypeScript': [r'interface\s+\w+', r'type\s+\w+\s*=', r':\s*\w+\s*=', r'export\s+default'],
            'Java': [r'public\s+class\s+\w+', r'public\s+static\s+void\s+main', r'System\.out\.println'],
            'C++': [r'#include\s*<\w+>', r'int\s+main\s*\(', r'std::', r'cout\s*<<'],
            'C#': [r'using\s+System', r'public\s+class\s+\w+', r'Console\.WriteLine'],
            'Go': [r'package\s+\w+', r'func\s+\w+\(', r'fmt\.Print'],
            'PHP': [r'<\?php', r'\$\w+\s*=', r'echo\s+'],
            'Ruby': [r'def\s+\w+', r'puts\s+', r'end\s*$'],
            'SQL': [r'SELECT\s+', r'FROM\s+', r'WHERE\s+', r'INSERT\s+INTO']
        }
        
        for language, patterns in language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    if language not in detected:
                        detected.append(language)
                    break
        
        return detected
    
    def _calculate_confidence(self, content: str, keyword: str) -> float:
        """计算技能关键词的置信度"""
        occurrences = content.count(keyword)
        content_length = len(content.split())
        
        if content_length == 0:
            return 0.0
        
        # 基于出现频率和上下文计算置信度
        frequency_score = min(occurrences / content_length * 100, 1.0)
        context_score = 0.5  # 可以基于上下文进一步优化
        
        return min(frequency_score + context_score, 1.0)
    
    def _calculate_complexity(self, content: str) -> int:
        """计算代码复杂度分数"""
        complexity = 0
        
        # 基于代码特征计算复杂度
        complexity += len(re.findall(r'\bif\b', content, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bfor\b', content, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bwhile\b', content, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bclass\b', content, re.IGNORECASE)) * 3
        complexity += len(re.findall(r'\bfunction\b', content, re.IGNORECASE)) * 1
        complexity += len(re.findall(r'\bdef\b', content, re.IGNORECASE)) * 1
        complexity += len(re.findall(r'\btry\b', content, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bcatch\b', content, re.IGNORECASE)) * 2
        
        return min(complexity, 100)  # 限制在100以内
    
    def _detect_design_patterns(self, content: str) -> List[str]:
        """检测设计模式"""
        patterns = []
        content_lower = content.lower()
        
        pattern_keywords = {
            'Singleton': ['singleton', 'instance', 'getinstance'],
            'Factory': ['factory', 'create', 'builder'],
            'Observer': ['observer', 'notify', 'subscribe'],
            'Strategy': ['strategy', 'algorithm'],
            'Decorator': ['decorator', 'wrapper'],
            'MVC': ['model', 'view', 'controller'],
            'Repository': ['repository', 'dao'],
            'Dependency Injection': ['inject', 'dependency', 'ioc']
        }
        
        for pattern, keywords in pattern_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_code_quality(self, content: str) -> Dict[str, Any]:
        """分析代码质量指标"""
        lines = content.splitlines()
        total_lines = len(lines)
        
        # 计算注释率
        comment_lines = len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*', '<!--'))])
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        # 计算平均行长度
        avg_line_length = sum(len(line) for line in lines) / total_lines if total_lines > 0 else 0
        
        # 检测长函数
        long_functions = len(re.findall(r'def\s+\w+.*?(?=def|\Z)', content, re.DOTALL))
        
        return {
            'total_lines': total_lines,
            'comment_ratio': round(comment_ratio, 2),
            'avg_line_length': round(avg_line_length, 1),
            'long_functions': long_functions,
            'quality_score': round((comment_ratio * 0.3 + (1 - min(avg_line_length / 100, 1)) * 0.7) * 100, 1)
        }
    
    def generate_skill_report(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合技能报告"""
        all_skills = []
        all_frameworks = []
        languages = set()
        total_complexity = 0
        
        for result in analysis_results:
            if 'error' not in result:
                all_skills.extend(result.get('skills', []))
                all_frameworks.extend(result.get('frameworks', []))
                if 'primary_language' in result:
                    languages.add(result['primary_language'])
                total_complexity += result.get('complexity_score', 0)
        
        # 聚合技能数据
        skill_summary = self._aggregate_skills(all_skills)
        framework_summary = self._aggregate_skills(all_frameworks)
        
        # 生成学习建议
        learning_recommendations = self._generate_learning_recommendations(skill_summary, framework_summary)
        
        return {
            'summary': {
                'total_analyses': len(analysis_results),
                'languages_detected': list(languages),
                'total_skills': len(skill_summary),
                'total_frameworks': len(framework_summary),
                'avg_complexity': round(total_complexity / len(analysis_results), 1) if analysis_results else 0
            },
            'skills': skill_summary,
            'frameworks': framework_summary,
            'learning_recommendations': learning_recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def _aggregate_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """聚合技能数据"""
        skill_map = {}
        
        for skill in skills:
            name = skill['name']
            if name in skill_map:
                skill_map[name]['confidence'] = max(skill_map[name]['confidence'], skill['confidence'])
                skill_map[name]['occurrences'] += skill['occurrences']
            else:
                skill_map[name] = skill.copy()
        
        # 按置信度排序
        return sorted(skill_map.values(), key=lambda x: x['confidence'], reverse=True)
    
    def _generate_learning_recommendations(self, skills: List[Dict[str, Any]], frameworks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成学习建议"""
        recommendations = []
        
        # 基于技能水平生成建议
        skill_levels = {skill['name']: skill['confidence'] for skill in skills}
        
        # 推荐相关技能
        if 'Python' in skill_levels:
            if skill_levels['Python'] > 0.7:
                recommendations.append({
                    'type': 'advanced',
                    'skill': 'Python',
                    'suggestion': '考虑学习高级Python特性：装饰器、元类、异步编程',
                    'resources': ['Python官方文档', 'Fluent Python', 'Effective Python']
                })
            else:
                recommendations.append({
                    'type': 'basic',
                    'skill': 'Python',
                    'suggestion': '加强Python基础：数据结构、面向对象编程',
                    'resources': ['Python基础教程', 'LeetCode Python练习']
                })
        
        if 'JavaScript' in skill_levels:
            recommendations.append({
                'type': 'framework',
                'skill': 'JavaScript',
                'suggestion': '学习现代JavaScript框架：React、Vue.js或Angular',
                'resources': ['React官方教程', 'Vue.js指南', 'JavaScript MDN文档']
            })
        
        return recommendations[:5]  # 限制推荐数量 