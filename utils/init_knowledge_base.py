"""
Utility script to initialize knowledge base with legal documents.
"""
import json
from pathlib import Path
from services.knowledge_base import KnowledgeBaseService, initialize_default_knowledge_base
from core.config_manager import get_config_manager


def create_sample_knowledge_base():
    """Create a sample knowledge base with common legal documents."""
    service = KnowledgeBaseService()
    config = get_config_manager()
    
    # Sample legal documents (民法典相关条款)
    sample_laws = [
        {
            "law_name": "民法典",
            "article": "第四百六十四条",
            "content": "合同是民事主体之间设立、变更、终止民事法律关系的协议。婚姻、收养、监护等有关身份关系的协议，适用有关该身份关系的法律规定；没有规定的，可以根据其性质参照适用本编规定。"
        },
        {
            "law_name": "民法典",
            "article": "第四百六十五条",
            "content": "依法成立的合同，受法律保护。依法成立的合同，仅对当事人具有法律约束力，但是法律另有规定的除外。"
        },
        {
            "law_name": "民法典",
            "article": "第四百六十九条",
            "content": "当事人订立合同，可以采用书面形式、口头形式或者其他形式。书面形式是合同书、信件、电报、电传、传真等可以有形地表现所载内容的形式。以电子数据交换、电子邮件等方式能够有形地表现所载内容，并可以随时调取查用的数据电文，视为书面形式。"
        },
        {
            "law_name": "民法典",
            "article": "第五百零九条",
            "content": "当事人应当按照约定全面履行自己的义务。当事人应当遵循诚信原则，根据合同的性质、目的和交易习惯履行通知、协助、保密等义务。当事人在履行合同过程中，应当避免浪费资源、污染环境和破坏生态。"
        },
        {
            "law_name": "民法典",
            "article": "第五百一十条",
            "content": "合同生效后，当事人就质量、价款或者报酬、履行地点等内容没有约定或者约定不明确的，可以协议补充；不能达成补充协议的，按照合同相关条款或者交易习惯确定。"
        },
        {
            "law_name": "民法典",
            "article": "第五百七十七条",
            "content": "当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。"
        },
        {
            "law_name": "民法典",
            "article": "第五百八十三条",
            "content": "当事人一方不履行合同义务或者履行合同义务不符合约定，造成对方损失的，损失赔偿额应当相当于因违约所造成的损失，包括合同履行后可以获得的利益；但是，不得超过违约一方订立合同时预见到或者应当预见到的因违约可能造成的损失。"
        },
        {
            "law_name": "民法典",
            "article": "第五百九十条",
            "content": "当事人一方因不可抗力不能履行合同的，根据不可抗力的影响，部分或者全部免除责任，但是法律另有规定的除外。因不可抗力不能履行合同的，应当及时通知对方，以减轻可能给对方造成的损失，并应当在合理期限内提供证明。"
        },
        {
            "law_name": "民法典",
            "article": "第五百九十二条",
            "content": "当事人都违反合同的，应当各自承担相应的责任。当事人一方违约造成对方损失，对方对损失的发生有过错的，可以减少相应的损失赔偿额。"
        },
        {
            "law_name": "民法典",
            "article": "第六百二十六条",
            "content": "买受人应当按照约定的数额和支付方式支付价款。对价款的数额和支付方式没有约定或者约定不明确，依据本法第五百一十条的规定仍不能确定的，按照订立合同时履行地的市场价格履行；依法应当执行政府定价或者政府指导价的，依照规定履行。"
        }
    ]
    
    service.add_law_documents_batch(sample_laws)
    print(f"✓ 已添加 {len(sample_laws)} 条法律文档到知识库")
    
    # Save to JSON file for future reference
    data_dir = config.project_root / "data"
    data_dir.mkdir(exist_ok=True)
    kb_file = data_dir / "knowledge_base.json"
    
    with open(kb_file, "w", encoding="utf-8") as f:
        json.dump({"laws": sample_laws}, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 知识库数据已保存到: {kb_file}")
    print("✓ 知识库初始化完成！")


if __name__ == "__main__":
    print("正在初始化知识库...")
    create_sample_knowledge_base()
