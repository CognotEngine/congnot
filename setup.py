from setuptools import setup, find_packages

setup(
    name="cognot_ai",
    version="0.1.0",
    description="AI 工作流引擎，专注于 AI 绘图和 AI 视频处理",
    author="Cognot AI Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "websockets>=11.0",
    ],
    entry_points={
        "console_scripts": [
            "cognot-server=api.gateway.main:run_server",
        ],
    },
)
