"""
خدمة التقارير والطباعة - توليد PDF والطباعة المباشرة.
"""

import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, Frame, PageTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QDateTime

from app.database.session import session_scope
from app.database.models import (
    Student, Receipt, ExpenseVoucher, PayrollRecord,
    Employee, Grade, Section, Subject, AcademicYear,
    StudentFee, FeeInstallment, DailyAttendance,
    MonthlyEvaluation, TermExamScore
)
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


class ReportService:
    """خدمة توليد التقارير والطباعة."""
    
    # مسارات الخطوط
    ARABIC_FONT_PATH = Path("app/resources/fonts/Cairo-Regular.ttf")
    ARABIC_BOLD_FONT_PATH = Path("app/resources/fonts/Cairo-Bold.ttf")
    
    def __init__(self):
        self._register_fonts()
        self.styles = self._create_styles()
    
    def _register_fonts(self):
        """تسجيل الخطوط العربية."""
        try:
            if self.ARABIC_FONT_PATH.exists():
                pdfmetrics.registerFont(TTFont('Cairo', str(self.ARABIC_FONT_PATH)))
            if self.ARABIC_BOLD_FONT_PATH.exists():
                pdfmetrics.registerFont(TTFont('Cairo-Bold', str(self.ARABIC_BOLD_FONT_PATH)))
        except Exception as e:
            logger.warning(f"فشل تسجيل الخطوط: {str(e)}")
    
    def _create_styles(self) -> Dict:
        """إنشاء أنماط النص."""
        styles = getSampleStyleSheet()
        
        # تخصيص الأنماط للغة العربية
        arabic_styles = {
            'title': ParagraphStyle(
                'ArabicTitle',
                parent=styles['Title'],
                fontName='Cairo-Bold',
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=20,
            ),
            'subtitle': ParagraphStyle(
                'ArabicSubtitle',
                parent=styles['Heading2'],
                fontName='Cairo-Bold',
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=15,
            ),
            'heading': ParagraphStyle(
                'ArabicHeading',
                parent=styles['Heading3'],
                fontName='Cairo-Bold',
                fontSize=12,
                alignment=TA_RIGHT,
                spaceAfter=10,
                textColor=colors.HexColor('#1976D3'),
            ),
            'body': ParagraphStyle(
                'ArabicBody',
                parent=styles['Normal'],
                fontName='Cairo',
                fontSize=10,
                alignment=TA_RIGHT,
                leading=16,
            ),
            'body_center': ParagraphStyle(
                'ArabicBodyCenter',
                parent=styles['Normal'],
                fontName='Cairo',
                fontSize=10,
                alignment=TA_CENTER,
            ),
            'small': ParagraphStyle(
                'ArabicSmall',
                parent=styles['Normal'],
                fontName='Cairo',
                fontSize=8,
                alignment=TA_RIGHT,
                textColor=colors.HexColor('#64748B'),
            ),
            'bold': ParagraphStyle(
                'ArabicBold',
                parent=styles['Normal'],
                fontName='Cairo-Bold',
                fontSize=10,
                alignment=TA_RIGHT,
            ),
        }
        
        return arabic_styles
    
    def _create_document(self, filename: str, title: str) -> SimpleDocTemplate:
        """إنشاء مستند PDF."""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=title,
            author="School Management System",
        )
        return doc
    
    def _add_header_footer(self, doc: SimpleDocTemplate, school_name: str = ""):
        """إضافة رأس وتذييل للمستند."""
        def header_footer(canvas, doc):
            canvas.saveState()
            
            # الرأس
            canvas.setFont('Cairo-Bold', 10)
            canvas.setFillColor(colors.HexColor('#1976D3'))
            canvas.drawCentredString(A4[0] / 2, A4[1] - 1.5*cm, school_name or "نظام إدارة المدرسة")
            
            # خط تحت الرأس
            canvas.setStrokeColor(colors.HexColor('#1976D3'))
            canvas.setLineWidth(1)
            canvas.line(2*cm, A4[1] - 1.8*cm, A4[0] - 2*cm, A4[1] - 1.8*cm)
            
            # التذييل
            canvas.setFont('Cairo', 8)
            canvas.setFillColor(colors.HexColor('#64748B'))
            canvas.drawCentredString(A4[0] / 2, 1*cm, f"صفحة {doc.page}")
            
            canvas.restoreState()
        
        return header_footer
    
    # ============ تقارير الطلاب ============
    
    def generate_student_list_report(self, students: List[Student], 
                                      filename: str = "students_report.pdf"):
        """توليد تقرير قائمة الطلاب."""
        doc = self._create_document(filename, "كشف أسماء الطلاب")
        
        elements = []
        
        # العنوان
        elements.append(Paragraph("كشف أسماء الطلاب", self.styles['title']))
        elements.append(Paragraph(f"تاريخ الطباعة: {date.today().strftime('%Y/%m/%d')}", self.styles['small']))
        elements.append(Spacer(1, 20))
        
        # جدول الطلاب
        table_data = [["#", "رقم الطالب", "الاسم الكامل", "الصف", "الشعبة", "الجنس"]]
        
        for i, student in enumerate(students, 1):
            table_data.append([
                str(i),
                student.student_number,
                student.full_name,
                student.grade.grade_name if student.grade else "",
                student.section.section_name if student.section else "",
                student.gender or "",
            ])
        
        table = Table(table_data, colWidths=[1*cm, 3*cm, 6*cm, 3*cm, 2*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Cairo-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Cairo'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    def generate_student_certificate(self, student: Student, term: int,
                                      filename: str = "certificate.pdf"):
        """توليد شهادة طالب."""
        doc = self._create_document(filename, f"شهادة {student.full_name}")
        
        elements = []
        
        # إطار الشهادة
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("شهادة دراسية", self.styles['title']))
        elements.append(Spacer(1, 30))
        
        # بيانات الطالب
        student_info = f"""
        <para align="right">
        <b>اسم الطالب:</b> {student.full_name}<br/>
        <b>رقم الطالب:</b> {student.student_number}<br/>
        <b>الصف:</b> {student.grade.grade_name if student.grade else ""}<br/>
        <b>الشعبة:</b> {student.section.section_name if student.section else ""}<br/>
        <b>الفصل الدراسي:</b> {term}<br/>
        </para>
        """
        elements.append(Paragraph(student_info, self.styles['body']))
        elements.append(Spacer(1, 30))
        
        # جدول الدرجات
        with session_scope() as session:
            # الحصول على درجات الطالب
            evaluations = session.execute(
                select(MonthlyEvaluation, Subject)
                .join(Subject, MonthlyEvaluation.subject_id == Subject.id)
                .where(
                    MonthlyEvaluation.student_id == student.id,
                    MonthlyEvaluation.term == term
                )
            ).all()
            
            exam_scores = session.execute(
                select(TermExamScore, Subject)
                .join(Subject, TermExamScore.subject_id == Subject.id)
                .where(
                    TermExamScore.student_id == student.id,
                    TermExamScore.term == term
                )
            ).all()
            
            if evaluations or exam_scores:
                table_data = [["المادة", "الأعمال", "الاختبار", "المجموع", "التقدير"]]
                
                # دمج البيانات
                scores = {}
                for eval, subject in evaluations:
                    scores[subject.id] = {'monthly': eval.total_month_score, 'subject': subject}
                
                for exam, subject in exam_scores:
                    if subject.id in scores:
                        scores[subject.id]['exam'] = exam.exam_score
                    else:
                        scores[subject.id] = {'exam': exam.exam_score, 'subject': subject}
                
                for subject_id, data in scores.items():
                    monthly = data.get('monthly', Decimal('0'))
                    exam = data.get('exam', Decimal('0'))
                    total = monthly + exam
                    
                    # التقدير
                    if total >= 90:
                        grade = "ممتاز"
                    elif total >= 80:
                        grade = "جيد جداً"
                    elif total >= 70:
                        grade = "جيد"
                    elif total >= 50:
                        grade = "مقبول"
                    else:
                        grade = "راسب"
                    
                    table_data.append([
                        data['subject'].subject_name,
                        str(monthly),
                        str(exam),
                        str(total),
                        grade,
                    ])
                
                table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#42A5F5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Cairo-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Cairo'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ]))
                
                elements.append(table)
        
        elements.append(Spacer(1, 30))
        
        # التوقيع
        signature = """
        <para align="left">
        توقيع المدير: ____________________<br/>
        التاريخ: {date}
        </para>
        """.format(date=date.today().strftime('%Y/%m/%d'))
        elements.append(Paragraph(signature, self.styles['body']))
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    # ============ التقارير المالية ============
    
    def generate_receipt_report(self, receipt: Receipt, 
                                 filename: str = "receipt.pdf"):
        """توليد سند قبض."""
        doc = self._create_document(filename, f"سند قبض {receipt.receipt_number}")
        
        elements = []
        
        # العنوان
        elements.append(Paragraph("سند قبض", self.styles['title']))
        elements.append(Spacer(1, 20))
        
        # بيانات السند
        receipt_info = f"""
        <para align="right">
        <b>رقم السند:</b> {receipt.receipt_number}<br/>
        <b>التاريخ:</b> {receipt.payment_date.strftime('%Y/%m/%d')}<br/>
        <b>اسم الطالب:</b> {receipt.student.full_name if receipt.student else ""}<br/>
        <b>المبلغ:</b> {receipt.amount_paid:,.2f} ريال<br/>
        <b>طريقة الدفع:</b> {receipt.payment_method}<br/>
        <b>بيان:</b> {receipt.notes or ""}<br/>
        </para>
        """
        elements.append(Paragraph(receipt_info, self.styles['body']))
        elements.append(Spacer(1, 30))
        
        # المبلغ بالأحرف
        amount_text = self._number_to_arabic_text(receipt.amount_paid)
        elements.append(Paragraph(f"المبلغ بالأحرف: {amount_text}", self.styles['bold']))
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("توقيع المستلم: ____________________", self.styles['body']))
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    def generate_expense_voucher_report(self, voucher: ExpenseVoucher,
                                         filename: str = "voucher.pdf"):
        """توليد سند صرف."""
        doc = self._create_document(filename, f"سند صرف {voucher.voucher_number}")
        
        elements = []
        
        elements.append(Paragraph("سند صرف", self.styles['title']))
        elements.append(Spacer(1, 20))
        
        voucher_info = f"""
        <para align="right">
        <b>رقم السند:</b> {voucher.voucher_number}<br/>
        <b>التاريخ:</b> {voucher.payment_date.strftime('%Y/%m/%d')}<br/>
        <b>المستفيد:</b> {voucher.beneficiary_name}<br/>
        <b>الفئة:</b> {voucher.expense_category}<br/>
        <b>المبلغ:</b> {voucher.amount:,.2f} ريال<br/>
        <b>طريقة الدفع:</b> {voucher.payment_method}<br/>
        <b>البيان:</b> {voucher.notes or ""}<br/>
        </para>
        """
        elements.append(Paragraph(voucher_info, self.styles['body']))
        elements.append(Spacer(1, 30))
        
        amount_text = self._number_to_arabic_text(voucher.amount)
        elements.append(Paragraph(f"المبلغ بالأحرف: {amount_text}", self.styles['bold']))
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    def generate_payroll_report(self, payroll_records: List[Tuple[PayrollRecord, Employee]],
                                 month: int, year: int,
                                 filename: str = "payroll.pdf"):
        """توليد كشف الرواتب."""
        doc = self._create_document(filename, f"كشف رواتب {month}/{year}")
        
        elements = []
        
        elements.append(Paragraph(f"كشف الرواتب الشهري - {month}/{year}", self.styles['title']))
        elements.append(Spacer(1, 20))
        
        # جدول الرواتب
        table_data = [
            ["الموظف", "الأساسي", "البدلات", "الخصومات", "السلف", "الصافي", "الحالة"]
        ]
        
        total_net = 0
        for payroll, employee in payroll_records:
            table_data.append([
                employee.full_name,
                f"{payroll.basic_salary:,.2f}",
                f"{payroll.total_allowances:,.2f}",
                f"{payroll.total_deductions:,.2f}",
                f"{payroll.loan_deduction:,.2f}",
                f"{payroll.net_salary:,.2f}",
                payroll.payment_status,
            ])
            total_net += float(payroll.net_salary)
        
        # صف الإجمالي
        table_data.append(["الإجمالي", "", "", "", "", f"{total_net:,.2f}", ""])
        
        table = Table(table_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2.5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Cairo-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Cairo'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0FDF4')),
            ('FONTNAME', (0, -1), (-1, -1), 'Cairo-Bold'),
        ]))
        
        elements.append(table)
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    def generate_financial_report(self, start_date: date, end_date: date,
                                    receipts: List[Receipt],
                                    vouchers: List[ExpenseVoucher],
                                    filename: str = "financial_report.pdf"):
        """توليد تقرير مالي شامل."""
        doc = self._create_document(filename, "التقرير المالي")
        
        elements = []
        
        elements.append(Paragraph("التقرير المالي الشامل", self.styles['title']))
        elements.append(Paragraph(
            f"الفترة من {start_date.strftime('%Y/%m/%d')} إلى {end_date.strftime('%Y/%m/%d')}",
            self.styles['subtitle']
        ))
        elements.append(Spacer(1, 20))
        
        # ملخص
        total_receipts = sum(r.amount_paid for r in receipts if r.status == 'نشط')
        total_expenses = sum(v.amount for v in vouchers if v.status == 'نشط')
        net = total_receipts - total_expenses
        
        summary_data = [
            ["البند", "المبلغ"],
            ["إجمالي المقبوضات", f"{total_receipts:,.2f} ريال"],
            ["إجمالي المصروفات", f"{total_expenses:,.2f} ريال"],
            ["الصافي", f"{net:,.2f} ريال"],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Cairo-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0FDF4')),
        ]))
        
        elements.append(summary_table)
        elements.append(PageBreak())
        
        # تفاصيل السندات
        elements.append(Paragraph("سندات القبض", self.styles['heading']))
        receipts_data = [["رقم السند", "الطالب", "المبلغ", "التاريخ"]]
        for r in receipts:
            if r.status == 'نشط':
                receipts_data.append([
                    r.receipt_number,
                    r.student.full_name if r.student else "",
                    f"{r.amount_paid:,.2f}",
                    r.payment_date.strftime('%Y/%m/%d'),
                ])
        
        receipts_table = Table(receipts_data, colWidths=[4*cm, 5*cm, 3*cm, 3*cm])
        receipts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Cairo'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        
        elements.append(receipts_table)
        elements.append(PageBreak())
        
        # تفاصيل سندات الصرف
        elements.append(Paragraph("سندات الصرف", self.styles['heading']))
        vouchers_data = [["رقم السند", "المستفيد", "الفئة", "المبلغ", "التاريخ"]]
        for v in vouchers:
            if v.status == 'نشط':
                vouchers_data.append([
                    v.voucher_number,
                    v.beneficiary_name,
                    v.expense_category,
                    f"{v.amount:,.2f}",
                    v.payment_date.strftime('%Y/%m/%d'),
                ])
        
        vouchers_table = Table(vouchers_data, colWidths=[3.5*cm, 4*cm, 3.5*cm, 3*cm, 3*cm])
        vouchers_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Cairo'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        
        elements.append(vouchers_table)
        
        doc.build(elements, onFirstPage=self._add_header_footer(doc))
        return filename
    
    def _number_to_arabic_text(self, number: Decimal) -> str:
        """تحويل رقم إلى نص عربي."""
        # تنفيذ مبسط - يمكن تحسينه
        units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
        teens = ["عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
        tens = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        
        amount = int(number)
        if amount == 0:
            return "صفر ريال"
        
        result = ""
        # يمكن إضافة تحويل كامل هنا
        result = f"{amount} ريال"
        
        return result