# 安装指南

本文档将指导您完成智能合同审核系统的安装和环境配置。

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- 至少 2GB 可用磁盘空间

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd smart_contract_audit
```

### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

#### 4.1 配置 LLM API Key

编辑 `config/settings.yaml`，设置您的 API key：

```yaml
llm:
  provider: "openai"
  openai:
    api_key: "your-api-key-here"
```

支持的 LLM 提供商：
- OpenAI
- Azure OpenAI
- Anthropic (Claude)
- Google Gemini
- DeepSeek

#### 4.2 配置 RAG（可选）

如果需要使用 RAG 功能：

```yaml
rag:
  enabled: true
  embedding_model: "openai"
  embedding_model_name: "text-embedding-3-small"
```

### 5. 初始化知识库（可选）

如果使用 RAG 功能，初始化知识库：

```bash
python utils/init_knowledge_base.py
```

## 验证安装

运行测试命令：

```bash
python main.py
```

如果看到 "Audit completed!" 消息，说明安装成功。

## 常见问题

### 问题 1: 依赖安装失败

**解决方案**: 确保使用 Python 3.8+，并尝试升级 pip：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 问题 2: API Key 未配置

**解决方案**: 检查 `config/settings.yaml` 中的 API key 配置。

### 问题 3: 模块导入错误

**解决方案**: 确保在项目根目录下运行，并激活了虚拟环境。

## 下一步

安装完成后，请查看：
- [快速开始指南](quick-start.md)
- [配置说明](configuration.md)
