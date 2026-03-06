# 设计模式

本文档介绍系统中使用的主要设计模式。

## 1. 单例模式 (Singleton Pattern)

### 用途

确保某些服务只有一个实例。

### 实现位置

- `ConfigManager`: 配置管理器
- `LoggerFactory`: 日志工厂
- `get_llm_client()`: LLM 客户端
- `get_rag_retriever()`: RAG 检索器

### 示例

```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## 2. 工厂模式 (Factory Pattern)

### 用途

创建对象而不指定具体的类。

### 实现位置

- `core/llm/factory.py`: LLM 客户端工厂
- `core/rag/factory.py`: RAG 组件工厂
- `core/rag/embedding.py`: 嵌入模型工厂

### 示例

```python
def create_llm_client() -> LLMClient:
    provider = config.get("llm.provider")
    if provider == "openai":
        return OpenAICompatibleClient(...)
    elif provider == "azure":
        return AzureCompatibleClient(...)
    # ...
```

## 3. 策略模式 (Strategy Pattern)

### 用途

定义一系列算法，使它们可以互换。

### 实现位置

- LLM 提供商选择（OpenAI, Azure, Anthropic 等）
- 嵌入模型选择（OpenAI, Simple）
- 向量存储选择（内存, 持久化）

### 示例

```python
class LLMClient(ABC):
    @abstractmethod
    def chat_completion(self, ...):
        pass

class OpenAICompatibleClient(LLMClient):
    def chat_completion(self, ...):
        # OpenAI 实现

class AnthropicCompatibleClient(LLMClient):
    def chat_completion(self, ...):
        # Anthropic 实现
```

## 4. 模板方法模式 (Template Method Pattern)

### 用途

定义算法骨架，子类实现具体步骤。

### 实现位置

- `BaseAgent`: 定义 Agent 执行流程
- `PipelineStep`: 定义步骤执行流程

### 示例

```python
class BaseAgent:
    def _call_llm(self, system, user):
        # 模板方法
        messages = self._prepare_messages(system, user)
        result = self.llm_client.chat_completion(...)
        return self._process_result(result)
    
    def _prepare_messages(self, system, user):
        # 可被子类覆盖
        return [...]
```

## 5. 依赖注入 (Dependency Injection)

### 用途

将依赖关系从类内部移到外部。

### 实现位置

- `BaseAgent`: 注入 LLM 客户端和配置
- `PipelineService`: 注入 Agents
- `AuditService`: 注入文件处理器和 Pipeline

### 示例

```python
class BaseAgent:
    def __init__(self, llm_client=None, config_manager=None):
        self.llm_client = llm_client or get_llm_client()
        self.config_manager = config_manager or get_config_manager()
```

## 6. 责任链模式 (Chain of Responsibility)

### 用途

将请求沿着处理者链传递。

### 实现位置

- `ContractAuditPipeline`: Pipeline 步骤链

### 示例

```python
class ContractAuditPipeline:
    def __init__(self, ...):
        self.steps = [
            ContractFormatterStep(...),
            LawSearchStep(...),
            RiskAnnotationStep(...),
            CorrectionStep(...)
        ]
    
    def run(self, input_data):
        context = input_data
        for step in self.steps:
            context = step.execute(context)
        return context
```

## 7. 适配器模式 (Adapter Pattern)

### 用途

使不兼容的接口能够协同工作。

### 实现位置

- LLM 客户端适配器（统一不同提供商的接口）
- `AnthropicCompatibleClient`: 适配 Anthropic API
- `GeminiCompatibleClient`: 适配 Gemini API

### 示例

```python
class AnthropicCompatibleClient(LLMClient):
    def __init__(self, client):
        self.client = client  # Anthropic 原生客户端
    
    def chat_completion(self, ...):
        # 适配为统一接口
        resp = self.client.messages.create(...)
        return {"content": resp.content[0].text}
```

## 8. 观察者模式 (Observer Pattern)

### 用途

定义对象间一对多的依赖关系。

### 实现位置

- 日志系统（多个处理器观察日志事件）

### 示例

```python
class LoggerFactory:
    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.addHandler(FileHandler(...))  # 观察者1
        logger.addHandler(ConsoleHandler(...))  # 观察者2
        return logger
```

## 9. 建造者模式 (Builder Pattern)

### 用途

逐步构建复杂对象。

### 实现位置

- Pipeline 构建（未来扩展）

### 潜在应用

```python
class PipelineBuilder:
    def add_step(self, step):
        self.steps.append(step)
        return self
    
    def build(self):
        return ContractAuditPipeline(self.steps)
```

## 10. 门面模式 (Facade Pattern)

### 用途

为复杂子系统提供简化接口。

### 实现位置

- `PipelineService`: 简化 Pipeline 使用
- `AuditService`: 简化审核流程

### 示例

```python
class PipelineService:
    def audit_contract(self, contract_text):
        # 隐藏复杂的 Pipeline 构建和执行细节
        return self.pipeline.run({"contract_text": contract_text})
```

## 模式组合使用

### 示例：Agent 创建流程

```python
# 工厂模式创建 LLM 客户端
llm_client = create_llm_client()  # Factory

# 单例模式获取配置
config = get_config_manager()  # Singleton

# 依赖注入创建 Agent
agent = ContractFormatterAgent(
    llm_client=llm_client,  # Dependency Injection
    config_manager=config
)

# 策略模式选择不同的 LLM 提供商
# 模板方法模式定义 Agent 执行流程
```

## 设计模式的优势

1. **可维护性**: 清晰的代码结构
2. **可扩展性**: 易于添加新功能
3. **可测试性**: 依赖注入便于测试
4. **可复用性**: 通用组件可复用

## 最佳实践

1. **适度使用**: 不要过度设计
2. **保持简单**: 优先选择简单方案
3. **文档说明**: 记录设计决策
4. **持续重构**: 根据需求调整
