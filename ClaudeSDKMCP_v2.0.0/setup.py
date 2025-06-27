#!/usr/bin/env python3
"""
ClaudeSDKMCP 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements 文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="claude-sdk-mcp",
    version="2.0.0",
    author="ClaudeSDKMCP Team",
    author_email="team@claudesdkmcp.com",
    description="基于0624架构的智能代码分析和专家咨询系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claudesdkmcp/claude-sdk-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-sdk-mcp=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="ai, code-analysis, claude, mcp, expert-system, code-review",
    project_urls={
        "Bug Reports": "https://github.com/claudesdkmcp/claude-sdk-mcp/issues",
        "Source": "https://github.com/claudesdkmcp/claude-sdk-mcp",
        "Documentation": "https://github.com/claudesdkmcp/claude-sdk-mcp/blob/main/README.md",
    },
)

