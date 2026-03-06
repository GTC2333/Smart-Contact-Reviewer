---

# 🧠 智能合同审核系统（AI Contract Review System）

## 📘 项目简介

本项目利用 **AI + 法律知识图谱 + 多智能体系统**，实现对商业合同的**自动化审核、风险标注与修改建议生成**。
支持 **PDF / Word / TXT** 输入，输出结构化 JSON 报告，并提供 **Web 前端交互界面**（Streamlit）与 **RESTful API**（FastAPI）。

---

## 📚 文档

**完整的文档索引请查看**: [docs/README.md](docs/README.md)

快速链接：
- [快速开始](docs/getting-started/quick-start.md)
- [安装指南](docs/getting-started/installation.md)
- [配置说明](docs/getting-started/configuration.md)
- [RAG 功能](docs/features/rag.md)
- [API 文档](docs/api/overview.md)
- [架构文档](docs/architecture/overview.md)

---

## 🏗️ 系统架构总览

```
smart_contact_audit/
├── main.py                    # 主审核流程（Pipeline）
├── api/
│   └── server.py              # FastAPI 后端服务
├── frontend/
│   └── app.py                 # Streamlit 前端界面
├── agents/
│   ├── contract_formatter.py
│   ├── law_search_agent.py
│   ├── risk_annotator.py
│   ├── correction_agent.py
│   └── __init__.py
├── utils/
│   ├── api_tools.py
│   ├── text_preprocess.py     # 新增：统一文本提取（PDF/Word/TXT）
│   └── init.py
├── config/
│   ├── prompt_templates.yaml
│   └── settings.yaml          # 新增前端 & API 配置
├── outputs/
│   ├── latest_annotations.json # 最新审核结果
│   ├── example_annotations.json
│   └── logs/
│       └── system.log
├── uploads/                   # FastAPI 上传临时目录
├── start_all.sh               # 一键启动脚本（新增）
├── README.md
└── __init__.py
```

---

## ⚙️ 统一配置（`config/settings.yaml`）

```yaml
frontend:
  title: "智能合同审核系统"
  port: 8501
  theme:
    primaryColor: "#FF6B6B"
    ...

backend_api:
  host: "127.0.0.1"
  port: 8000
  endpoint_audit: "/audit"

agents:
  contract_formatter:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 2000
  law_search:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 800
  ...
```

## 🌐 前端界面（Streamlit）

**文件**：`frontend/app.py`

### 功能特性

- 支持 **拖拽上传** `.txt` / `.pdf` / `.docx`
- 实时调用 **本地 Pipeline** 或 **FastAPI 后端**
- 可视化展示：
  - 风险统计（高/中/低）
  - 逐条风险明细（可展开）
  - 法律依据引用与建议修改
- 一键下载 JSON 报告

### 启动方式

```bash
streamlit run frontend/app.py
```

## ⚙️ 模块说明与输入输出格式

### 1️⃣ `ContractFormatterAgent`
- **实现**：`agents/contract_formatter.py`（OpenAI `gpt-4o-mini` + JSON mode）
- **输入**：`contract_text`（原始全文）
- **输出**：`{"clauses": [{id,title,content}], "parties": [...]}`

### 2️⃣ `LawSearchAgent`
- **实现**：`agents/law_search_agent.py`
- **输入**：单条 `clause_content`
- **输出**：`{matched, law_name, article, issue}`

### 3️⃣ `RiskAnnotatorAgent`
- **实现**：`agents/risk_annotator.py`
- **输入**：`clause`, `law_info`, `parties`
- **输出**：风险对象（若无风险返回 `None`）

### 4️⃣ `CorrectionAgent`
- **实现**：`agents/correction_agent.py`
- **输入**：`risk_info`（含 `original_clause`）
- **输出**：`{clause_id, suggested_revision, note}`

### 依赖
```bash
pip install openai==1.47.0 jinja2 pyyaml
```

---

## 🧩 主流程：`main.py`

**主要逻辑**：

```python
from agents.contract_formatter import ContractFormatterAgent
from agents.law_search_agent import LawSearchAgent
from agents.risk_annotator import RiskAnnotatorAgent
from agents.correction_agent import CorrectionAgent

formatter = ContractFormatterAgent()
law_search = LawSearchAgent()
risk_annotator = RiskAnnotatorAgent()
correction_agent = CorrectionAgent()

def run_pipeline(contract_text):
    formatted = formatter.process(contract_text)
    results = []
    for clause in formatted["clauses"]:
        law_info = law_search.check_law(clause["content"])
        risk_info = risk_annotator.annotate(clause, law_info)
        correction = correction_agent.suggest(risk_info)
        results.append(correction)
    return results
```

**输入**：

* `.txt`、`.pdf`、或 `.docx` 合同文件

**输出**：

* 结构化 JSON (`outputs/example_annotations.json`)，包含全部风险点、建议、法条引用。

---

## 🧠 智能体提示词设计（位于 `config/prompt_templates.yaml`）

```yaml
formatter_prompt: |
  你是一名法律合同分析师，请将以下合同文本切分为条款，识别甲方、乙方及每条款标题：
  - 输出为JSON，字段包括 {id, title, content}。
  - 不要总结，不要省略任何文字。

law_search_prompt: |
  请比对以下合同条款内容，确认其中引用的法律是否正确：
  - 指出是否已被《民法典》替代；
  - 输出字段：{matched, law_name, article, issue}。

risk_annotation_prompt: |
  你是一名合同风险专家，请识别以下条款的潜在风险。
  - 请区分甲方和乙方的风险角度；
  - 输出字段：{party, issue_type, description, severity, recommendation}。

correction_prompt: |
  请基于风险标注，为合同生成修改建议。
  - 保留原意，保证措辞合法且明确；
  - 输出修改后的条款文本。
```

---

## 🧰 API与外部调用接口

| 功能       | API来源                                       | 用途            |
| -------- | ------------------------------------------- | ------------- |
| 法条检索     | `https://api.openlaw.cn/api/law/search`     | 匹配合同引用的法条     |
| 文本清洗与OCR | `tesseract` / `Azure Document Intelligence` | 从PDF中提取合同内容   |
| 模型调用     | OpenAI GPT-5 / Claude / 自建LLM               | 进行语义分析与生成修改建议 |

---

## 📤 输出示例

```json
{
  "contract_id": "C2025-001",
  "annotations": [
    {
      "id": "anno-001",
      "clause_id": "2",
      "party": "乙方",
      "issue_type": "Risk",
      "description": "付款期限过短，履约风险较高。",
      "recommendation": "修改为五个工作日。",
      "law_reference": "民法典 第五百九十条"
    }
  ]
}
```

---

## 安装依赖

```bash
pip install streamlit fastapi uvicorn python-multipart PyMuPDF python-docx
```

## 🧩 可扩展功能（下一阶段）

* 引入 RAG（检索增强生成）机制，将法条数据库嵌入向量索引。
* 接入 PDF/Word 批注生成器（可在合同原文上高亮标注）。
* 加入"风险评分系统"，评估整体合同风险等级。
* 引入版本对比：标注合同修订前后的变更差异。
