# 配置说明

详细说明系统配置选项。

## 配置文件位置

主要配置文件位于 `config/` 目录：

- `settings.yaml` - 系统配置
- `prompt_templates.yaml` - 提示词模板

## 配置结构

### 前端配置

```yaml
frontend:
  title: "智能合同审核系统"
  port: 8501
  theme:
    primaryColor: "#FF6B6B"
    backgroundColor: "#FFFFFF"
    secondaryBackgroundColor: "#F0F2F6"
    textColor: "#262730"
```

### 后端 API 配置

```yaml
backend_api:
  host: "127.0.0.1"
  port: 8000
  endpoint_audit: "/audit"
```

### Agents 配置

每个 Agent 的模型和参数配置：

```yaml
agents:
  contract_formatter:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 2000
  law_search:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 800
  risk_annotator:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 1000
  correction:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 1500
```

### LLM 配置

#### OpenAI

```yaml
llm:
  provider: "openai"
  openai:
    api_key: "sk-..."
    base_url: "https://api.openai.com/v1"  # 可选，用于代理
```

#### Azure OpenAI

```yaml
llm:
  provider: "azure"
  azure:
    api_key: "your-key"
    endpoint: "https://xxx.openai.azure.com/"
    api_version: "2024-02-01"
    deployment: "gpt-4o-mini"
```

#### Anthropic (Claude)

```yaml
llm:
  provider: "anthropic"
  anthropic:
    api_key: "your-key"
    base_url: null
```

#### Google Gemini

```yaml
llm:
  provider: "gemini"
  gemini:
    api_key: "your-key"
```

#### DeepSeek

```yaml
llm:
  provider: "deepseek"
  deepseek:
    api_key: "your-key"
    base_url: "https://api.deepseek.com/v1"
```

### RAG 配置

```yaml
rag:
  enabled: true
  embedding_model: "openai"  # openai | simple
  embedding_model_name: "text-embedding-3-small"
  vector_store_path: "outputs/vector_store.pkl"
  retrieval_top_k: 3
```

### 模型映射

用于映射配置中的模型名到实际模型名：

```yaml
model_mapping:
  gpt-4o-mini: "gpt-4o-mini"
  claude-3-haiku: "claude-3-haiku-20240307"
```

## 环境变量（可选）

可以通过环境变量覆盖配置：

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

## 配置优先级

1. 环境变量（最高优先级）
2. `config/settings.yaml`
3. 默认值（最低优先级）

## 配置验证

系统启动时会验证配置：

- API Key 是否设置
- 端口是否可用
- 文件路径是否存在

## 常见配置场景

### 场景 1: 使用本地代理

```yaml
llm:
  provider: "openai"
  openai:
    api_key: "sk-..."
    base_url: "http://localhost:8080/v1"  # 本地代理地址
```

### 场景 2: 禁用 RAG

```yaml
rag:
  enabled: false
```

### 场景 3: 使用不同的模型

```yaml
agents:
  risk_annotator:
    model: "gpt-4"  # 使用更强的模型进行风险评估
    temperature: 0.1
    max_tokens: 2000
```

## 配置热重载

某些配置支持热重载（无需重启）：

- 提示词模板
- 前端主题配置

其他配置需要重启服务才能生效。

## 安全建议

1. **不要提交 API Key 到版本控制**
   - 使用 `.gitignore` 排除配置文件
   - 或使用环境变量

2. **使用配置文件模板**
   - 创建 `settings.yaml.example`
   - 在 README 中说明如何配置

3. **限制 API 访问**
   - 生产环境使用防火墙
   - 配置 API 认证

## 故障排除

### 配置未生效

- 检查配置文件格式（YAML 语法）
- 确认文件路径正确
- 重启服务

### API Key 错误

- 验证 API Key 格式
- 检查 API Key 是否有效
- 确认网络连接

### 端口冲突

- 修改 `backend_api.port` 或 `frontend.port`
- 检查端口是否被占用
