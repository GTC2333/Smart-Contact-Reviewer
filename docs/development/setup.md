# 开发环境设置

本文档说明如何设置开发环境。

## 前置要求

- Python 3.8+
- Git
- 代码编辑器（推荐 VS Code 或 PyCharm）

## 设置步骤

### 1. 克隆仓库

```bash
git clone <repository-url>
cd smart_contract_audit
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装开发依赖

```bash
pip install -r requirements.txt
pip install -e .  # 以开发模式安装
```

### 4. 安装开发工具（可选）

```bash
pip install black flake8 mypy pytest pytest-cov
```

### 5. 配置 IDE

#### VS Code

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

#### PyCharm

1. 打开项目
2. File → Settings → Project → Python Interpreter
3. 选择虚拟环境中的 Python

## 项目结构

```
smart_contract_audit/
├── agents/          # Agents 实现
├── api/             # API 层
├── core/            # 核心模块
├── docs/            # 文档
├── frontend/        # 前端
├── models/          # 数据模型
├── services/        # 服务层
├── utils/           # 工具函数
└── tests/           # 测试（待创建）
```

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/new-feature
```

### 2. 编写代码

遵循代码规范：
- 使用类型提示
- 添加文档字符串
- 遵循 PEP 8

### 3. 运行测试

```bash
pytest tests/
```

### 4. 代码格式化

```bash
black .
flake8 .
```

### 5. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feature/new-feature
```

## 代码规范

### Python 风格

- 使用 Black 格式化代码
- 遵循 PEP 8
- 使用类型提示

### 命名约定

- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`

### 文档字符串

```python
def function(param: str) -> dict:
    """
    函数说明。
    
    Args:
        param: 参数说明
    
    Returns:
        返回值说明
    """
    pass
```

## 调试

### 使用调试器

VS Code:
1. 设置断点
2. 按 F5 启动调试

PyCharm:
1. 设置断点
2. 右键 → Debug

### 日志调试

```python
from core.logger import get_logger

logger = get_logger(__name__)
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告")
logger.error("错误")
```

## 测试

### 运行测试

```bash
# 所有测试
pytest

# 特定文件
pytest tests/test_agents.py

# 带覆盖率
pytest --cov=. --cov-report=html
```

### 编写测试

```python
import pytest
from agents.contract_formatter import ContractFormatterAgent

def test_contract_formatter():
    agent = ContractFormatterAgent()
    result = agent.process("合同文本...")
    assert "clauses" in result
    assert "parties" in result
```

## 常见问题

### 导入错误

确保在项目根目录运行，并激活虚拟环境。

### 模块未找到

检查 `PYTHONPATH` 或使用 `pip install -e .`

### 配置错误

确保 `config/settings.yaml` 存在且格式正确。

## 下一步

- 查看[贡献指南](contributing.md)
- 阅读[测试指南](testing.md)
