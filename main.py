"""
Main entry point for contract audit pipeline.
Simplified to use service layer.
"""
from typing import Dict
from services.pipeline_service import get_pipeline_service


def run_pipeline(input_data: dict) -> dict:
    """
    Run contract audit pipeline.
    
    Args:
        input_data: Dictionary with 'contract_text' key
    
    Returns:
        Audit result dictionary
    """
    service = get_pipeline_service()
    return service.audit_contract(input_data["contract_text"])


if __name__ == "__main__":
    # Example usage
    example_text = """
    合同编号：C2025-001
    
    甲方：示例公司A
    乙方：示例公司B
    
    第一条 合同标的
    本合同标的为软件开发服务。
    
    第二条 付款方式
    乙方应在合同签订后3个工作日内支付全部款项。
    """
    
    result = run_pipeline({"contract_text": example_text})
    print("Audit completed!")
    print(f"Contract ID: {result.get('contract_id')}")
    print(f"Found {len(result.get('annotations', []))} risks")
