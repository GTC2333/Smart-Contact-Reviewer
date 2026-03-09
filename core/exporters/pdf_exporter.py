"""
PDF exporter for contract audit reports.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from typing import Dict, Any
import tempfile


class PDFExporter:
    """Export audit results to PDF format."""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def export(self, audit_result: Dict[str, Any], output_path: str = None) -> str:
        """
        Export audit result to PDF.

        Args:
            audit_result: Audit result dictionary
            output_path: Output file path (optional, returns temp path if None)

        Returns:
            Path to exported PDF file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".pdf")

        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        story = []

        # Title
        title = Paragraph("合同审核报告", self.styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Contract info
        contract_id = audit_result.get("contract_id", "N/A")
        metadata = audit_result.get("metadata", {})
        processed_at = metadata.get("processed_at", "N/A")
        clause_count = metadata.get("clause_count", 0)
        party_count = metadata.get("party_count", 0)

        story.append(Paragraph(f"<b>合同ID:</b> {contract_id}", self.styles['Normal']))
        story.append(Paragraph(f"<b>审核时间:</b> {processed_at}", self.styles['Normal']))
        story.append(Paragraph(f"<b>条款数量:</b> {clause_count}", self.styles['Normal']))
        story.append(Paragraph(f"<b>当事方数量:</b> {party_count}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Risk statistics (severity is in Chinese: 高/中/低)
        annotations = audit_result.get("annotations", [])
        high = len([a for a in annotations if a.get("severity", "").strip() == "高"])
        medium = len([a for a in annotations if a.get("severity", "").strip() == "中"])
        low = len([a for a in annotations if a.get("severity", "").strip() == "低"])

        story.append(Paragraph("<b>风险统计</b>", self.styles['Heading2']))
        story.append(Spacer(1, 10))

        # Risk table
        risk_data = [
            ["风险等级", "数量"],
            ["高风险", str(high)],
            ["中风险", str(medium)],
            ["低风险", str(low)],
            ["总计", str(len(annotations))]
        ]
        risk_table = Table(risk_data, colWidths=[2*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 20))

        # Risk details
        if annotations:
            story.append(Paragraph("<b>风险详情</b>", self.styles['Heading2']))
            story.append(Spacer(1, 10))

            for i, anno in enumerate(annotations[:20], 1):  # Limit to 20
                severity = anno.get("severity", "Unknown").upper()
                issue_type = anno.get("issue_type", "Risk")
                description = anno.get("description", "N/A")
                recommendation = anno.get("recommendation", "")

                story.append(Paragraph(
                    f"<b>{i}. [{severity}] {issue_type}</b>",
                    self.styles['Heading3']
                ))
                story.append(Paragraph(f"<b>问题描述:</b> {description}", self.styles['Normal']))
                if recommendation:
                    story.append(Paragraph(f"<b>建议:</b> {recommendation}", self.styles['Normal']))
                story.append(Spacer(1, 10))

        # Corrections
        corrections = audit_result.get("corrections", [])
        if corrections:
            story.append(Paragraph("<b>修改建议</b>", self.styles['Heading2']))
            story.append(Spacer(1, 10))

            for i, corr in enumerate(corrections[:10], 1):
                revision = corr.get("suggested_revision", "N/A")
                note = corr.get("note", "")

                story.append(Paragraph(f"<b>{i}. 修改建议:</b> {revision}", self.styles['Normal']))
                if note:
                    story.append(Paragraph(f"<b>备注:</b> {note}", self.styles['Normal']))
                story.append(Spacer(1, 10))

        # Build PDF
        doc.build(story)
        return output_path
