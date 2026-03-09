# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Smart Contract Audit System** (智能合同审核系统) that uses AI + multi-agent system to automatically review commercial contracts, identify risks, and generate correction suggestions. It supports PDF/Word/TXT input and outputs structured JSON reports.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start both backend API and frontend (recommended)
./start_all.sh

# Start backend API only
PYTHONPATH=. uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload

# Start frontend only
streamlit run frontend/app.py

# Run main pipeline directly
PYTHONPATH=. python main.py
```

## Architecture

### Layer Structure

```
Frontend (Streamlit) → API (FastAPI) → Service Layer → Pipeline → Agent Layer + RAG + Core
```

- **Frontend**: Streamlit web UI in `frontend/app.py`
- **API**: FastAPI REST API in `api/server.py`
- **Service Layer**: `services/pipeline_service.py`, `services/audit_service.py`
- **Pipeline**: `core/pipeline/contract_pipeline.py` - orchestrates the 4-step audit flow
- **Agent Layer**: `agents/` - 4 specialized agents for contract processing
- **RAG**: `core/rag/` - retrieval-augmented generation for legal references
- **Core**: `core/` - config, logging, LLM interfaces

### Pipeline Flow

The audit pipeline runs 4 sequential steps:
1. **ContractFormatterStep** - Splits contract into structured clauses
2. **LawSearchStep** - Searches legal references for each clause
3. **RiskAnnotationStep** - Identifies risks in clauses
4. **CorrectionStep** - Generates correction suggestions

### Agents

All agents extend `BaseAgent` (`agents/base_agent.py`):
- `ContractFormatterAgent` - Formats contract into clauses
- `LawSearchAgent` - Searches legal references (uses RAG)
- `RiskAnnotatorAgent` - Annotates risks
- `CorrectionAgent` - Generates revision suggestions

### Configuration

- **Settings**: `config/settings.yaml` - model config, LLM providers (openai/azure/anthropic/gemini/deepseek), RAG settings
- **Prompts**: `config/prompt_templates.yaml` - prompt templates for each agent

#### LLM Providers

Configure in `config/settings.yaml`:
- **openai**: OpenAI API (default)
- **azure**: Azure OpenAI
- **anthropic**: Anthropic Claude
- **gemini**: Google Gemini
- **deepseek**: DeepSeek (default, cost-effective)

API keys should be set via environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) or in a local config file.

### Data Models

- `models/contract.py` - FormattedContract
- `models/annotation.py` - AnnotationResult

### Directory Structure

```
├── main.py                    # Pipeline entry point
├── api/server.py              # FastAPI backend
├── frontend/app.py            # Streamlit UI
├── agents/                    # 4 specialized agents
│   ├── contract_formatter.py
│   ├── law_search_agent.py
│   ├── risk_annotator.py
│   └── correction_agent.py
├── core/
│   ├── pipeline/              # Pipeline orchestration
│   ├── llm/                   # LLM client factory
│   ├── rag/                   # RAG for legal references
│   └── config_manager.py
├── services/                  # Service layer
├── models/                    # Data models
├── config/                    # YAML configs
└── utils/                     # Utilities (file handling, text preprocessing)
```

### Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point for pipeline |
| `api/server.py` | FastAPI server |
| `frontend/app.py` | Streamlit UI |
| `core/pipeline/contract_pipeline.py` | Pipeline orchestration |
| `services/pipeline_service.py` | Service layer for pipeline |
| `core/llm/factory.py` | LLM client factory |
| `core/config_manager.py` | Configuration management |
| `utils/text_preprocess.py` | PDF/Word/TXT text extraction |
