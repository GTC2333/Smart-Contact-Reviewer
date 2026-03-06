# 测试指南

本文档说明如何编写和运行测试。

## 测试框架

- **pytest**: 测试框架
- **pytest-cov**: 覆盖率工具

## 安装测试依赖

```bash
pip install pytest pytest-cov
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_agents.py

# 运行特定测试
pytest tests/test_agents.py::test_contract_formatter

# 带覆盖率
pytest --cov=. --cov-report=html

# 详细输出
pytest -v
```

## 测试结构

```
tests/
├── __init__.py
├── test_agents.py
├── test_pipeline.py
├── test_services.py
└── fixtures/
    └── sample_contracts.py
```

## 编写测试

### 基础测试

```python
import pytest
from agents.contract_formatter import ContractFormatterAgent

def test_contract_formatter_basic():
    """测试合同格式化基础功能"""
    agent = ContractFormatterAgent()
    contract_text = "合同编号：C001\n甲方：A公司\n乙方：B公司"
    
    result = agent.process(contract_text)
    
    assert "clauses" in result
    assert "parties" in result
    assert isinstance(result["clauses"], list)
```

### 使用 Fixtures

```python
import pytest

@pytest.fixture
def sample_contract():
    return """
    合同编号：C2025-001
    甲方：示例公司A
    乙方：示例公司B
    第一条 合同标的
    本合同标的为软件开发服务。
    """

def test_pipeline_with_fixture(sample_contract):
    from main import run_pipeline
    
    result = run_pipeline({"contract_text": sample_contract})
    assert result["contract_id"] is not None
```

### Mock 外部依赖

```python
from unittest.mock import Mock, patch

@patch('core.llm.factory.get_llm_client')
def test_agent_with_mock(mock_llm):
    # 设置 mock
    mock_client = Mock()
    mock_client.chat_completion.return_value = {
        "content": '{"clauses": [], "parties": []}'
    }
    mock_llm.return_value = mock_client
    
    # 测试
    agent = ContractFormatterAgent()
    result = agent.process("合同文本")
    
    assert result is not None
```

### 参数化测试

```python
import pytest

@pytest.mark.parametrize("severity,expected", [
    ("High", "high"),
    ("Medium", "medium"),
    ("Low", "low"),
])
def test_severity_normalization(severity, expected):
    from agents.risk_annotator import RiskAnnotatorAgent
    
    # 测试逻辑
    assert severity.lower() == expected
```

## 测试类型

### 单元测试

测试单个函数或方法：

```python
def test_parse_json():
    from agents.base_agent import BaseAgent
    
    agent = BaseAgent.__new__(BaseAgent)
    result = agent._parse_json('{"key": "value"}')
    assert result == {"key": "value"}
```

### 集成测试

测试多个组件协作：

```python
def test_pipeline_integration():
    from services.pipeline_service import get_pipeline_service
    
    service = get_pipeline_service()
    result = service.audit_contract("合同文本")
    
    assert "contract_id" in result
    assert "annotations" in result
```

### 端到端测试

测试完整流程：

```python
def test_end_to_end():
    from main import run_pipeline
    
    contract_text = "完整的合同文本..."
    result = run_pipeline({"contract_text": contract_text})
    
    # 验证完整结果
    assert result["contract_id"]
    assert result["metadata"]["clause_count"] > 0
```

## 测试最佳实践

### 1. 测试命名

```python
def test_function_name_should_do_what():
    """测试应该做什么"""
    pass
```

### 2. 测试组织

```python
class TestContractFormatter:
    def test_basic_formatting(self):
        pass
    
    def test_empty_contract(self):
        pass
    
    def test_malformed_contract(self):
        pass
```

### 3. 断言清晰

```python
# 好的断言
assert result["clauses"] is not None
assert len(result["clauses"]) > 0

# 避免
assert result
```

### 4. 测试隔离

每个测试应该独立，不依赖其他测试。

### 5. 清理资源

```python
def test_with_cleanup():
    # 设置
    service = create_service()
    
    try:
        # 测试
        result = service.process()
        assert result
    finally:
        # 清理
        service.cleanup()
```

## 覆盖率

### 查看覆盖率

```bash
pytest --cov=. --cov-report=html
# 打开 htmlcov/index.html
```

### 覆盖率目标

- 核心模块: > 80%
- 工具模块: > 70%
- 整体: > 75%

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
```

## 常见问题

### 测试失败但代码正常

- 检查测试环境
- 验证 mock 设置
- 查看详细错误信息

### 测试太慢

- 使用 mock 替代真实 API 调用
- 并行运行测试
- 优化测试数据

### 覆盖率低

- 添加边界情况测试
- 测试错误路径
- 增加集成测试

## 下一步

- 查看[开发环境设置](setup.md)
- 阅读[贡献指南](contributing.md)
