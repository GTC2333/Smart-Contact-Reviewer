# Agents 说明

智能体（Agents）是系统的核心组件，负责执行各种合同审核任务。

## Agents 架构

系统采用多智能体架构，每个 Agent 负责特定任务：

```
BaseAgent (基类)
├── ContractFormatterAgent (合同格式化)
├── LawSearchAgent (法律检索)
├── RiskAnnotatorAgent (风险标注)
└── CorrectionAgent (修改建议)
```

## BaseAgent

所有 Agents 的基类，提供：

- LLM 调用接口
- Prompt 模板渲染
- JSON 解析
- 日志记录

### 依赖注入

BaseAgent 支持依赖注入，便于测试和扩展：

```python
from agents.base_agent import BaseAgent
from core.llm.factory import get_llm_client
from core.config_manager import get_config_manager

# 使用默认配置
agent = ContractFormatterAgent()

# 自定义注入
llm_client = get_llm_client()
config = get_config_manager()
agent = ContractFormatterAgent(
    llm_client=custom_llm_client,
    config_manager=custom_config
)
```

## ContractFormatterAgent

**功能**: 将原始合同文本结构化

**输入**: 原始合同文本（字符串）

**输出**: 结构化合同对象

```python
{
  "clauses": [
    {
      "id": "1",
      "title": "合同标的",
      "content": "本合同标的为..."
    }
  ],
  "parties": [
    {"role": "甲方", "name": "公司A"},
    {"role": "乙方", "name": "公司B"}
  ]
}
```

**使用示例**:

```python
from agents.contract_formatter import ContractFormatterAgent

agent = ContractFormatterAgent()
result = agent.process(contract_text)
```

## LawSearchAgent

**功能**: 检索和验证合同中的法律引用

**输入**: 条款内容（字符串）

**输出**: 法律信息对象

```python
{
  "matched": true,
  "law_name": "民法典",
  "article": "第五百一十条",
  "issue": "法条引用正确"
}
```

**RAG 增强**: 自动使用 RAG 检索相关法条

**使用示例**:

```python
from agents.law_search_agent import LawSearchAgent

agent = LawSearchAgent()
result = agent.check_law(clause_content)
```

## RiskAnnotatorAgent

**功能**: 识别合同条款中的风险点

**输入**: 
- 条款对象
- 法律信息
- 合同当事人列表

**输出**: 风险标注对象（如果发现风险）

```python
{
  "id": "anno-001",
  "clause_id": "2",
  "party": "乙方",
  "issue_type": "Risk",
  "description": "付款期限过短",
  "severity": "High",
  "recommendation": "建议延长至10个工作日",
  "law_reference": "民法典 第五百一十条"
}
```

**使用示例**:

```python
from agents.risk_annotator import RiskAnnotatorAgent

agent = RiskAnnotatorAgent()
risk = agent.annotate(clause, law_info, parties)
```

## CorrectionAgent

**功能**: 基于风险标注生成修改建议

**输入**: 风险信息对象

**输出**: 修改建议对象

```python
{
  "clause_id": "2",
  "suggested_revision": "修改后的完整条款文本",
  "note": "修改说明"
}
```

**使用示例**:

```python
from agents.correction_agent import CorrectionAgent

agent = CorrectionAgent()
correction = agent.suggest(risk_info)
```

## 扩展 Agents

### 创建自定义 Agent

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="custom")
    
    def process(self, input_data):
        # 实现自定义逻辑
        system_prompt = "你的系统提示"
        user_prompt = self._render_prompt(
            "custom_prompt",
            data=input_data
        )
        
        result = self._call_llm(
            system=system_prompt,
            user=user_prompt,
            response_format={"type": "json_object"}
        )
        
        return self._parse_json(result["raw"])
```

### 注册新 Agent

1. 在 `agents/__init__.py` 中导出
2. 在 `config/settings.yaml` 中添加配置
3. 在 Pipeline 中集成

## 配置 Agents

在 `config/settings.yaml` 中配置每个 Agent：

```yaml
agents:
  custom_agent:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 1000
```

## 最佳实践

1. **错误处理**: 所有 Agents 都应包含适当的错误处理
2. **日志记录**: 使用 `self.logger` 记录重要操作
3. **输入验证**: 验证输入数据的格式和内容
4. **输出标准化**: 使用统一的数据格式

## 故障排除

### Agent 初始化失败

- 检查配置中的 agent_name 是否正确
- 确认模型配置存在

### LLM 调用失败

- 检查 API Key 配置
- 验证网络连接
- 查看日志文件

### 输出格式错误

- 检查 prompt 模板
- 验证 JSON 解析逻辑
- 查看 LLM 响应内容
