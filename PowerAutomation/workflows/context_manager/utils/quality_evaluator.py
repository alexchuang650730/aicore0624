#!/usr/bin/env python3
"""
Code Quality Evaluator
代碼質量評估器

評估生成代碼的質量，包括語法正確性、風格一致性、最佳實踐遵循等
支持多種編程語言和質量指標
"""

import ast
import re
import logging
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class QualityMetric(Enum):
    """質量指標"""
    SYNTAX_CORRECTNESS = "syntax_correctness"
    STYLE_CONSISTENCY = "style_consistency"
    BEST_PRACTICES = "best_practices"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    ERROR_HANDLING = "error_handling"
    TESTABILITY = "testability"

class CodeLanguage(Enum):
    """支持的編程語言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"

@dataclass
class QualityIssue:
    """質量問題"""
    issue_id: str
    metric: QualityMetric
    severity: str  # "error", "warning", "info"
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "metric": self.metric.value,
            "severity": self.severity,
            "message": self.message,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "suggestion": self.suggestion
        }

@dataclass
class QualityReport:
    """質量報告"""
    overall_score: float
    metric_scores: Dict[QualityMetric, float]
    issues: List[QualityIssue]
    suggestions: List[str]
    language: CodeLanguage
    code_length: int
    complexity_score: float
    maintainability_index: float
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "metric_scores": {k.value: v for k, v in self.metric_scores.items()},
            "issues": [issue.to_dict() for issue in self.issues],
            "suggestions": self.suggestions,
            "language": self.language.value,
            "code_length": self.code_length,
            "complexity_score": self.complexity_score,
            "maintainability_index": self.maintainability_index,
            "generated_at": self.generated_at.isoformat()
        }

class PythonQualityAnalyzer:
    """Python 代碼質量分析器"""
    
    def __init__(self):
        self.style_rules = {
            "max_line_length": 88,
            "max_function_length": 50,
            "max_class_length": 200,
            "max_complexity": 10
        }
    
    async def analyze(self, code: str, context: Dict[str, Any] = None) -> QualityReport:
        """分析 Python 代碼質量"""
        issues = []
        metric_scores = {}
        suggestions = []
        
        # 語法正確性檢查
        syntax_score, syntax_issues = await self._check_syntax(code)
        metric_scores[QualityMetric.SYNTAX_CORRECTNESS] = syntax_score
        issues.extend(syntax_issues)
        
        # 風格一致性檢查
        style_score, style_issues = await self._check_style(code)
        metric_scores[QualityMetric.STYLE_CONSISTENCY] = style_score
        issues.extend(style_issues)
        
        # 最佳實踐檢查
        practices_score, practices_issues = await self._check_best_practices(code)
        metric_scores[QualityMetric.BEST_PRACTICES] = practices_score
        issues.extend(practices_issues)
        
        # 可讀性檢查
        readability_score, readability_issues = await self._check_readability(code)
        metric_scores[QualityMetric.READABILITY] = readability_score
        issues.extend(readability_issues)
        
        # 文檔檢查
        doc_score, doc_issues = await self._check_documentation(code)
        metric_scores[QualityMetric.DOCUMENTATION] = doc_score
        issues.extend(doc_issues)
        
        # 錯誤處理檢查
        error_score, error_issues = await self._check_error_handling(code)
        metric_scores[QualityMetric.ERROR_HANDLING] = error_score
        issues.extend(error_issues)
        
        # 安全性檢查
        security_score, security_issues = await self._check_security(code)
        metric_scores[QualityMetric.SECURITY] = security_score
        issues.extend(security_issues)
        
        # 計算複雜度
        complexity_score = await self._calculate_complexity(code)
        
        # 計算可維護性指數
        maintainability_index = await self._calculate_maintainability_index(code, complexity_score)
        
        # 計算總體分數
        overall_score = sum(metric_scores.values()) / len(metric_scores)
        
        # 生成建議
        suggestions = await self._generate_suggestions(issues, metric_scores)
        
        return QualityReport(
            overall_score=overall_score,
            metric_scores=metric_scores,
            issues=issues,
            suggestions=suggestions,
            language=CodeLanguage.PYTHON,
            code_length=len(code),
            complexity_score=complexity_score,
            maintainability_index=maintainability_index
        )
    
    async def _check_syntax(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查語法正確性"""
        issues = []
        
        try:
            ast.parse(code)
            return 1.0, issues
        except SyntaxError as e:
            issue = QualityIssue(
                issue_id="syntax_error",
                metric=QualityMetric.SYNTAX_CORRECTNESS,
                severity="error",
                message=f"Syntax error: {e.msg}",
                line_number=e.lineno,
                column_number=e.offset,
                suggestion="Fix the syntax error before proceeding"
            )
            issues.append(issue)
            return 0.0, issues
        except Exception as e:
            issue = QualityIssue(
                issue_id="parse_error",
                metric=QualityMetric.SYNTAX_CORRECTNESS,
                severity="error",
                message=f"Parse error: {str(e)}",
                suggestion="Check code structure and syntax"
            )
            issues.append(issue)
            return 0.0, issues
    
    async def _check_style(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查風格一致性"""
        issues = []
        score = 1.0
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 行長度檢查
            if len(line) > self.style_rules["max_line_length"]:
                issue = QualityIssue(
                    issue_id=f"line_too_long_{i}",
                    metric=QualityMetric.STYLE_CONSISTENCY,
                    severity="warning",
                    message=f"Line {i} is too long ({len(line)} > {self.style_rules['max_line_length']})",
                    line_number=i,
                    suggestion=f"Break line into multiple lines or refactor"
                )
                issues.append(issue)
                score -= 0.05
            
            # 縮進檢查
            if line.strip() and not line.startswith(' ' * (len(line) - len(line.lstrip())) // 4 * 4):
                if '\t' in line:
                    issue = QualityIssue(
                        issue_id=f"tab_indentation_{i}",
                        metric=QualityMetric.STYLE_CONSISTENCY,
                        severity="warning",
                        message=f"Line {i} uses tabs instead of spaces",
                        line_number=i,
                        suggestion="Use 4 spaces for indentation"
                    )
                    issues.append(issue)
                    score -= 0.02
        
        # 命名約定檢查
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        issue = QualityIssue(
                            issue_id=f"function_naming_{node.name}",
                            metric=QualityMetric.STYLE_CONSISTENCY,
                            severity="info",
                            message=f"Function '{node.name}' doesn't follow snake_case convention",
                            line_number=node.lineno,
                            suggestion="Use snake_case for function names"
                        )
                        issues.append(issue)
                        score -= 0.03
                
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        issue = QualityIssue(
                            issue_id=f"class_naming_{node.name}",
                            metric=QualityMetric.STYLE_CONSISTENCY,
                            severity="info",
                            message=f"Class '{node.name}' doesn't follow PascalCase convention",
                            line_number=node.lineno,
                            suggestion="Use PascalCase for class names"
                        )
                        issues.append(issue)
                        score -= 0.03
        except:
            pass
        
        return max(0.0, score), issues
    
    async def _check_best_practices(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查最佳實踐"""
        issues = []
        score = 1.0
        
        # 檢查導入語句
        if 'import *' in code:
            issue = QualityIssue(
                issue_id="wildcard_import",
                metric=QualityMetric.BEST_PRACTICES,
                severity="warning",
                message="Avoid wildcard imports (import *)",
                suggestion="Import specific modules or use 'import module as alias'"
            )
            issues.append(issue)
            score -= 0.1
        
        # 檢查全局變量
        try:
            tree = ast.parse(code)
            global_vars = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Global):
                    global_vars.extend(node.names)
            
            if global_vars:
                issue = QualityIssue(
                    issue_id="global_variables",
                    metric=QualityMetric.BEST_PRACTICES,
                    severity="info",
                    message=f"Global variables found: {', '.join(global_vars)}",
                    suggestion="Consider using class attributes or function parameters"
                )
                issues.append(issue)
                score -= 0.05
        except:
            pass
        
        # 檢查空的 except 塊
        if re.search(r'except\s*:\s*pass', code):
            issue = QualityIssue(
                issue_id="bare_except",
                metric=QualityMetric.BEST_PRACTICES,
                severity="warning",
                message="Bare except clause found",
                suggestion="Specify exception types or use 'except Exception:'"
            )
            issues.append(issue)
            score -= 0.1
        
        return max(0.0, score), issues
    
    async def _check_readability(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查可讀性"""
        issues = []
        score = 1.0
        lines = code.split('\n')
        
        # 檢查函數長度
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                    if func_lines > self.style_rules["max_function_length"]:
                        issue = QualityIssue(
                            issue_id=f"long_function_{node.name}",
                            metric=QualityMetric.READABILITY,
                            severity="info",
                            message=f"Function '{node.name}' is too long ({func_lines} lines)",
                            line_number=node.lineno,
                            suggestion="Consider breaking into smaller functions"
                        )
                        issues.append(issue)
                        score -= 0.05
        except:
            pass
        
        # 檢查註釋密度
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines > 0:
            comment_ratio = comment_lines / total_lines
            if comment_ratio < 0.1:  # 少於10%的註釋
                issue = QualityIssue(
                    issue_id="low_comment_density",
                    metric=QualityMetric.READABILITY,
                    severity="info",
                    message=f"Low comment density ({comment_ratio:.1%})",
                    suggestion="Add more comments to explain complex logic"
                )
                issues.append(issue)
                score -= 0.1
        
        return max(0.0, score), issues
    
    async def _check_documentation(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查文檔"""
        issues = []
        score = 1.0
        
        try:
            tree = ast.parse(code)
            functions_without_docstring = []
            classes_without_docstring = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        functions_without_docstring.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        classes_without_docstring.append(node.name)
            
            if functions_without_docstring:
                issue = QualityIssue(
                    issue_id="missing_function_docstrings",
                    metric=QualityMetric.DOCUMENTATION,
                    severity="info",
                    message=f"Functions without docstrings: {', '.join(functions_without_docstring)}",
                    suggestion="Add docstrings to describe function purpose and parameters"
                )
                issues.append(issue)
                score -= 0.1 * len(functions_without_docstring)
            
            if classes_without_docstring:
                issue = QualityIssue(
                    issue_id="missing_class_docstrings",
                    metric=QualityMetric.DOCUMENTATION,
                    severity="info",
                    message=f"Classes without docstrings: {', '.join(classes_without_docstring)}",
                    suggestion="Add docstrings to describe class purpose and usage"
                )
                issues.append(issue)
                score -= 0.15 * len(classes_without_docstring)
        except:
            pass
        
        return max(0.0, score), issues
    
    async def _check_error_handling(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查錯誤處理"""
        issues = []
        score = 1.0
        
        # 檢查是否有錯誤處理
        has_try_except = 'try:' in code and 'except' in code
        
        if not has_try_except and len(code.split('\n')) > 10:  # 對於較長的代碼
            issue = QualityIssue(
                issue_id="no_error_handling",
                metric=QualityMetric.ERROR_HANDLING,
                severity="info",
                message="No error handling found in code",
                suggestion="Consider adding try-except blocks for potential errors"
            )
            issues.append(issue)
            score -= 0.2
        
        return max(0.0, score), issues
    
    async def _check_security(self, code: str) -> Tuple[float, List[QualityIssue]]:
        """檢查安全性"""
        issues = []
        score = 1.0
        
        # 檢查潛在的安全問題
        security_patterns = [
            (r'eval\s*\(', "Use of eval() function", "Avoid eval(), use safer alternatives"),
            (r'exec\s*\(', "Use of exec() function", "Avoid exec(), use safer alternatives"),
            (r'input\s*\(', "Use of input() function", "Validate and sanitize user input"),
            (r'os\.system\s*\(', "Use of os.system()", "Use subprocess module instead"),
            (r'shell\s*=\s*True', "Shell injection risk", "Avoid shell=True in subprocess calls")
        ]
        
        for pattern, message, suggestion in security_patterns:
            if re.search(pattern, code):
                issue = QualityIssue(
                    issue_id=f"security_{pattern[:10]}",
                    metric=QualityMetric.SECURITY,
                    severity="warning",
                    message=message,
                    suggestion=suggestion
                )
                issues.append(issue)
                score -= 0.15
        
        return max(0.0, score), issues
    
    async def _calculate_complexity(self, code: str) -> float:
        """計算代碼複雜度"""
        try:
            tree = ast.parse(code)
            complexity = 1  # 基礎複雜度
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
            
            return min(complexity / 10.0, 1.0)  # 歸一化到 0-1
        except:
            return 0.5  # 默認中等複雜度
    
    async def _calculate_maintainability_index(self, code: str, complexity: float) -> float:
        """計算可維護性指數"""
        lines_of_code = len([line for line in code.split('\n') if line.strip()])
        
        # 簡化的可維護性指數計算
        # 基於代碼行數、複雜度和註釋密度
        comment_lines = len([line for line in code.split('\n') if line.strip().startswith('#')])
        comment_ratio = comment_lines / max(lines_of_code, 1)
        
        # 可維護性指數 (0-1)
        maintainability = (
            (1.0 - min(lines_of_code / 200, 1.0)) * 0.4 +  # 代碼長度因子
            (1.0 - complexity) * 0.4 +                      # 複雜度因子
            comment_ratio * 0.2                             # 註釋因子
        )
        
        return max(0.0, min(1.0, maintainability))
    
    async def _generate_suggestions(self, issues: List[QualityIssue], 
                                  metric_scores: Dict[QualityMetric, float]) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        # 基於分數較低的指標生成建議
        low_score_metrics = [metric for metric, score in metric_scores.items() if score < 0.7]
        
        for metric in low_score_metrics:
            if metric == QualityMetric.SYNTAX_CORRECTNESS:
                suggestions.append("Fix syntax errors before proceeding with other improvements")
            elif metric == QualityMetric.STYLE_CONSISTENCY:
                suggestions.append("Use a code formatter like Black to improve style consistency")
            elif metric == QualityMetric.BEST_PRACTICES:
                suggestions.append("Review Python best practices and refactor accordingly")
            elif metric == QualityMetric.DOCUMENTATION:
                suggestions.append("Add comprehensive docstrings to functions and classes")
            elif metric == QualityMetric.ERROR_HANDLING:
                suggestions.append("Implement proper error handling with try-except blocks")
            elif metric == QualityMetric.SECURITY:
                suggestions.append("Review code for security vulnerabilities and fix them")
        
        # 基於問題嚴重程度生成建議
        error_count = len([issue for issue in issues if issue.severity == "error"])
        warning_count = len([issue for issue in issues if issue.severity == "warning"])
        
        if error_count > 0:
            suggestions.append(f"Address {error_count} critical error(s) immediately")
        if warning_count > 3:
            suggestions.append(f"Consider addressing {warning_count} warning(s) for better code quality")
        
        return suggestions

class JavaScriptQualityAnalyzer:
    """JavaScript 代碼質量分析器"""
    
    async def analyze(self, code: str, context: Dict[str, Any] = None) -> QualityReport:
        """分析 JavaScript 代碼質量"""
        # 簡化的 JavaScript 分析
        issues = []
        metric_scores = {
            QualityMetric.SYNTAX_CORRECTNESS: 0.8,
            QualityMetric.STYLE_CONSISTENCY: 0.7,
            QualityMetric.BEST_PRACTICES: 0.6,
            QualityMetric.READABILITY: 0.7,
            QualityMetric.DOCUMENTATION: 0.5
        }
        
        # 基本語法檢查
        if code.count('{') != code.count('}'):
            issue = QualityIssue(
                issue_id="brace_mismatch",
                metric=QualityMetric.SYNTAX_CORRECTNESS,
                severity="error",
                message="Mismatched braces",
                suggestion="Check brace pairing"
            )
            issues.append(issue)
            metric_scores[QualityMetric.SYNTAX_CORRECTNESS] = 0.0
        
        overall_score = sum(metric_scores.values()) / len(metric_scores)
        
        return QualityReport(
            overall_score=overall_score,
            metric_scores=metric_scores,
            issues=issues,
            suggestions=["Use ESLint for better JavaScript code analysis"],
            language=CodeLanguage.JAVASCRIPT,
            code_length=len(code),
            complexity_score=0.5,
            maintainability_index=0.6
        )

class QualityEvaluator:
    """代碼質量評估器主類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.analyzers = {
            CodeLanguage.PYTHON: PythonQualityAnalyzer(),
            CodeLanguage.JAVASCRIPT: JavaScriptQualityAnalyzer(),
            # 可以添加更多語言分析器
        }
        
        self.initialized = False
        
        # 性能統計
        self.stats = {
            "total_evaluations": 0,
            "average_score": 0.0,
            "language_usage": {lang.value: 0 for lang in CodeLanguage}
        }
    
    async def initialize(self):
        """初始化評估器"""
        self.initialized = True
        logger.info("Quality Evaluator initialized successfully")
    
    async def evaluate_code(self, code: str, language: str, context: Dict[str, Any] = None) -> float:
        """評估代碼質量並返回分數"""
        if not self.initialized:
            raise RuntimeError("Quality Evaluator not initialized")
        
        try:
            # 獲取詳細報告
            report = await self.evaluate_code_detailed(code, language, context)
            return report.overall_score
        except Exception as e:
            logger.error(f"Error evaluating code quality: {e}")
            return 0.5  # 默認中等分數
    
    async def evaluate_code_detailed(self, code: str, language: str, 
                                   context: Dict[str, Any] = None) -> QualityReport:
        """詳細評估代碼質量"""
        if not self.initialized:
            raise RuntimeError("Quality Evaluator not initialized")
        
        self.stats["total_evaluations"] += 1
        
        try:
            # 確定語言
            code_language = self._detect_language(language)
            self.stats["language_usage"][code_language.value] += 1
            
            # 獲取對應的分析器
            analyzer = self.analyzers.get(code_language)
            if not analyzer:
                # 使用通用分析器
                return await self._generic_analysis(code, code_language, context)
            
            # 執行分析
            report = await analyzer.analyze(code, context)
            
            # 更新統計
            self.stats["average_score"] = (
                (self.stats["average_score"] * (self.stats["total_evaluations"] - 1) + report.overall_score)
                / self.stats["total_evaluations"]
            )
            
            logger.info(f"Code quality evaluation completed: {report.overall_score:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"Error in detailed code evaluation: {e}")
            # 返回默認報告
            return QualityReport(
                overall_score=0.5,
                metric_scores={QualityMetric.SYNTAX_CORRECTNESS: 0.5},
                issues=[],
                suggestions=["Unable to analyze code quality"],
                language=CodeLanguage.PYTHON,
                code_length=len(code),
                complexity_score=0.5,
                maintainability_index=0.5
            )
    
    def _detect_language(self, language_hint: str) -> CodeLanguage:
        """檢測編程語言"""
        language_hint = language_hint.lower()
        
        language_map = {
            'python': CodeLanguage.PYTHON,
            'py': CodeLanguage.PYTHON,
            'javascript': CodeLanguage.JAVASCRIPT,
            'js': CodeLanguage.JAVASCRIPT,
            'typescript': CodeLanguage.TYPESCRIPT,
            'ts': CodeLanguage.TYPESCRIPT,
            'java': CodeLanguage.JAVA,
            'cpp': CodeLanguage.CPP,
            'c++': CodeLanguage.CPP,
            'csharp': CodeLanguage.CSHARP,
            'c#': CodeLanguage.CSHARP,
            'go': CodeLanguage.GO,
            'rust': CodeLanguage.RUST,
            'rs': CodeLanguage.RUST
        }
        
        return language_map.get(language_hint, CodeLanguage.PYTHON)
    
    async def _generic_analysis(self, code: str, language: CodeLanguage, 
                              context: Dict[str, Any] = None) -> QualityReport:
        """通用代碼分析"""
        issues = []
        
        # 基本檢查
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # 計算基本指標
        code_length = len(code)
        line_count = len(non_empty_lines)
        avg_line_length = sum(len(line) for line in non_empty_lines) / max(line_count, 1)
        
        # 基本質量分數
        metric_scores = {
            QualityMetric.SYNTAX_CORRECTNESS: 0.8,  # 假設語法基本正確
            QualityMetric.STYLE_CONSISTENCY: 0.7,
            QualityMetric.READABILITY: 0.6 if avg_line_length < 100 else 0.4,
            QualityMetric.DOCUMENTATION: 0.5
        }
        
        # 檢查是否有註釋
        comment_patterns = {
            CodeLanguage.PYTHON: r'#',
            CodeLanguage.JAVASCRIPT: r'//',
            CodeLanguage.JAVA: r'//',
            CodeLanguage.CPP: r'//',
            CodeLanguage.CSHARP: r'//',
            CodeLanguage.GO: r'//',
            CodeLanguage.RUST: r'//'
        }
        
        comment_pattern = comment_patterns.get(language, r'#')
        has_comments = any(re.search(comment_pattern, line) for line in lines)
        
        if not has_comments and line_count > 10:
            issue = QualityIssue(
                issue_id="no_comments",
                metric=QualityMetric.DOCUMENTATION,
                severity="info",
                message="No comments found in code",
                suggestion="Add comments to explain complex logic"
            )
            issues.append(issue)
            metric_scores[QualityMetric.DOCUMENTATION] = 0.3
        
        overall_score = sum(metric_scores.values()) / len(metric_scores)
        
        return QualityReport(
            overall_score=overall_score,
            metric_scores=metric_scores,
            issues=issues,
            suggestions=["Consider using language-specific linting tools for better analysis"],
            language=language,
            code_length=code_length,
            complexity_score=min(line_count / 50, 1.0),
            maintainability_index=0.6
        )
    
    async def compare_code_quality(self, code1: str, code2: str, language: str) -> Dict[str, Any]:
        """比較兩段代碼的質量"""
        report1 = await self.evaluate_code_detailed(code1, language)
        report2 = await self.evaluate_code_detailed(code2, language)
        
        comparison = {
            "code1_score": report1.overall_score,
            "code2_score": report2.overall_score,
            "better_code": "code1" if report1.overall_score > report2.overall_score else "code2",
            "score_difference": abs(report1.overall_score - report2.overall_score),
            "metric_comparison": {},
            "recommendations": []
        }
        
        # 比較各項指標
        for metric in report1.metric_scores:
            if metric in report2.metric_scores:
                comparison["metric_comparison"][metric.value] = {
                    "code1": report1.metric_scores[metric],
                    "code2": report2.metric_scores[metric],
                    "difference": report1.metric_scores[metric] - report2.metric_scores[metric]
                }
        
        # 生成建議
        if report1.overall_score > report2.overall_score:
            comparison["recommendations"].append("Code1 has better overall quality")
        elif report2.overall_score > report1.overall_score:
            comparison["recommendations"].append("Code2 has better overall quality")
        else:
            comparison["recommendations"].append("Both codes have similar quality")
        
        return comparison
    
    def get_status(self) -> Dict[str, Any]:
        """獲取評估器狀態"""
        return {
            "initialized": self.initialized,
            "supported_languages": [lang.value for lang in self.analyzers.keys()],
            "stats": self.stats
        }

# 工廠函數
async def create_quality_evaluator(config: Dict[str, Any] = None) -> QualityEvaluator:
    """創建並初始化質量評估器"""
    evaluator = QualityEvaluator(config)
    await evaluator.initialize()
    return evaluator

