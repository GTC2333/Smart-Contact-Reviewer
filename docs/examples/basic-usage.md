# 基础使用示例

本文档提供系统的基础使用示例。

## 示例 1: 使用 Python 代码审核合同

```python
from main import run_pipeline

# 准备合同文本
contract_text = """
合同编号：C2025-001

甲方：北京科技有限公司
乙方：上海软件开发有限公司

第一条 合同标的
本合同标的为软件开发服务，包括系统设计、编码实现、测试验收等。

第二条 付款方式
乙方应在合同签订后3个工作日内支付全部款项，金额为人民币10万元。

第三条 交付时间
甲方应在收到款项后30个工作日内完成开发并交付。
"""

# 运行审核
result = run_pipeline({"contract_text": contract_text})

# 查看结果
print(f"合同ID: {result['contract_id']}")
print(f"条款数量: {result['metadata']['clause_count']}")
print(f"发现风险: {len(result['annotations'])} 个\n")

# 遍历风险标注
for annotation in result['annotations']:
    print(f"条款 {annotation['clause_id']}:")
    print(f"  受影响方: {annotation['party']}")
    print(f"  问题描述: {annotation['description']}")
    print(f"  严重程度: {annotation['severity']}")
    print(f"  修改建议: {annotation['recommendation']}")
    if annotation.get('suggested_revision'):
        print(f"  建议修改: {annotation['suggested_revision']}")
    print()
```

## 示例 2: 使用服务层

```python
from services.pipeline_service import get_pipeline_service

# 获取服务实例
service = get_pipeline_service()

# 审核合同
result = service.audit_contract(contract_text)

# 处理结果
if result['annotations']:
    print("发现以下风险：")
    for anno in result['annotations']:
        print(f"- {anno['description']} (严重程度: {anno['severity']})")
else:
    print("未发现风险")
```

## 示例 3: 使用 API

### Python 客户端

```python
import requests

def audit_contract_api(file_path):
    """通过 API 审核合同"""
    url = "http://127.0.0.1:8000/audit"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

# 使用
result = audit_contract_api("contract.pdf")
print(result)
```

### cURL

```bash
# 审核 PDF 文件
curl -X POST "http://127.0.0.1:8000/audit" \
  -F "file=@contract.pdf" \
  -o result.json

# 查看结果
cat result.json | jq '.contract_id'
cat result.json | jq '.annotations[].description'
```

## 示例 4: 处理审核结果

```python
from main import run_pipeline
import json

def analyze_audit_result(result):
    """分析审核结果"""
    analysis = {
        "total_risks": len(result['annotations']),
        "high_risks": 0,
        "medium_risks": 0,
        "low_risks": 0,
        "by_party": {}
    }
    
    for anno in result['annotations']:
        severity = anno['severity'].lower()
        if severity == 'high':
            analysis['high_risks'] += 1
        elif severity == 'medium':
            analysis['medium_risks'] += 1
        else:
            analysis['low_risks'] += 1
        
        party = anno['party']
        if party not in analysis['by_party']:
            analysis['by_party'][party] = 0
        analysis['by_party'][party] += 1
    
    return analysis

# 使用
result = run_pipeline({"contract_text": contract_text})
analysis = analyze_audit_result(result)

print(f"总风险数: {analysis['total_risks']}")
print(f"高风险: {analysis['high_risks']}")
print(f"中风险: {analysis['medium_risks']}")
print(f"低风险: {analysis['low_risks']}")
print(f"按当事人分类: {analysis['by_party']}")
```

## 示例 5: 保存审核结果

```python
from main import run_pipeline
import json
from datetime import datetime

def save_audit_result(result, output_dir="outputs"):
    """保存审核结果到文件"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{output_dir}/audit_{result['contract_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {filename}")
    return filename

# 使用
result = run_pipeline({"contract_text": contract_text})
save_audit_result(result)
```

## 示例 6: 批量处理

```python
from main import run_pipeline
from pathlib import Path

def batch_audit(contract_files):
    """批量审核合同"""
    results = []
    
    for file_path in contract_files:
        # 读取文件内容
        if file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                contract_text = f.read()
        else:
            from utils.text_preprocess import extract_text_from_file
            contract_text = extract_text_from_file(str(file_path))
        
        # 审核
        result = run_pipeline({"contract_text": contract_text})
        results.append({
            "file": str(file_path),
            "result": result
        })
    
    return results

# 使用
contract_files = [
    Path("contracts/contract1.txt"),
    Path("contracts/contract2.pdf"),
    Path("contracts/contract3.docx")
]

results = batch_audit(contract_files)
for r in results:
    print(f"{r['file']}: {len(r['result']['annotations'])} 个风险")
```

## 示例 7: 自定义 Agents

```python
from agents import (
    ContractFormatterAgent,
    LawSearchAgent,
    RiskAnnotatorAgent,
    CorrectionAgent
)
from core.pipeline.contract_pipeline import ContractAuditPipeline

# 创建自定义 Agents
formatter = ContractFormatterAgent()
law_search = LawSearchAgent()
risk_annotator = RiskAnnotatorAgent()
correction = CorrectionAgent()

# 创建 Pipeline
pipeline = ContractAuditPipeline(
    formatter_agent=formatter,
    law_search_agent=law_search,
    risk_annotator_agent=risk_annotator,
    correction_agent=correction
)

# 运行
result = pipeline.run({"contract_text": contract_text})
```

## 下一步

- 查看[高级用法](advanced-usage.md)
- 阅读[功能文档](../features/rag.md)
- 了解[API 使用](../api/endpoints.md)
