"""
واجهة استيراد وتصدير البيانات - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict, Any
import qtawesome as qta
import pandas as pd
from datetime import datetime
from pathlib import Path

from app.database.session import session_scope
from app.database.models import Student, Parent, Employee, Subject, Grade
from app.services.permission_service import PermissionService
from sqlalchemy import select

from app.views.widgets.custom_widgets import GradientButton
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class ImportExportPage(QWidget):
    """صفحة استيراد وتصدير البيانات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        
        # ✅ تخزين بيانات السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ البيانات المؤقتة
        self.selected_file_path: Optional[str] = None
        self.preview_data: Optional[pd.DataFrame] = None
        
        # ✅ منع العمليات المتزامنة
        self._is_importing = False
        self._is_exporting = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        title = QLabel("استيراد وتصدير البيانات")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("استيراد وتصدير البيانات من وإلى Excel")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        main_layout.addWidget(subtitle)
        
        # اختيار نوع البيانات
        type_card = QFrame()
        type_card.setObjectName("typeCard")
        type_card.setStyleSheet("""
            QFrame#typeCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        type_layout = QHBoxLayout(type_card)
        
        type_layout.addWidget(QLabel("نوع البيانات:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "الطلاب", "أولياء الأمور", "الموظفون", 
            "المواد الدراسية", "الصفوف"
        ])
        self.data_type_combo.setMinimumWidth(200)
        type_layout.addWidget(self.data_type_combo)
        
        type_layout.addStretch()
        
        main_layout.addWidget(type_card)
        
        # ============================================================
        # قسم الاستيراد
        # ============================================================
        import_card = QFrame()
        import_card.setObjectName("importCard")
        import_card.setStyleSheet("""
            QFrame#importCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        import_layout = QVBoxLayout(import_card)
        
        import_title = QLabel("استيراد البيانات")
        import_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #0F172A;"
        )
        import_layout.addWidget(import_title)
        
        # زر اختيار ملف
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel("لم يتم اختيار ملف")
        self.file_path_label.setStyleSheet("color: #64748B;")
        file_layout.addWidget(self.file_path_label)
        
        file_layout.addStretch()
        
        choose_btn = QPushButton("اختيار ملف Excel")
        choose_btn.setIcon(qta.icon('fa5s.folder-open'))
        choose_btn.setStyleSheet("""
            QPushButton {
                background: #EEF2FF;
                color: #0D47A1;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #E0E7FF;
            }
        """)
        choose_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(choose_btn)
        
        import_layout.addLayout(file_layout)
        
        # ✅ معاينة الملف
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("""
            color: #475569;
            font-size: 12px;
            padding: 8px;
            background: #F8FAFC;
            border-radius: 6px;
        """)
        self.preview_label.setVisible(False)
        self.preview_label.setWordWrap(True)
        import_layout.addWidget(self.preview_label)
        
        # ✅ شريط تقدم الاستيراد
        self.import_progress = QProgressBar()
        self.import_progress.setVisible(False)
        self.import_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D3, stop:1 #42A5F5);
                border-radius: 6px;
            }
        """)
        import_layout.addWidget(self.import_progress)
        
        # زر بدء الاستيراد
        self.import_btn = GradientButton("بدء الاستيراد", "fa5s.file-import")
        self.import_btn.setObjectName("primaryButton")
        self.import_btn.clicked.connect(self.import_data)
        self.import_btn.setEnabled(False)  # ✅ معطّل حتى اختيار ملف
        import_layout.addWidget(self.import_btn)
        
        main_layout.addWidget(import_card)
        
        # ============================================================
        # قسم التصدير
        # ============================================================
        export_card = QFrame()
        export_card.setObjectName("exportCard")
        export_card.setStyleSheet("""
            QFrame#exportCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        export_layout = QVBoxLayout(export_card)
        
        export_title = QLabel("تصدير البيانات")
        export_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #0F172A;"
        )
        export_layout.addWidget(export_title)
        
        # صيغة التصدير
        format_layout = QHBoxLayout()
        
        format_layout.addWidget(QLabel("صيغة التصدير:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems([
            "Excel (.xlsx)", "CSV (.csv)"
        ])
        format_layout.addWidget(self.export_format_combo)
        
        format_layout.addStretch()
        
        export_layout.addLayout(format_layout)
        
        # ✅ شريط تقدم التصدير
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        self.export_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10B981, stop:1 #34D399);
                border-radius: 6px;
            }
        """)
        export_layout.addWidget(self.export_progress)
        
        # زر التصدير
        self.export_btn = QPushButton("تصدير البيانات")
        self.export_btn.setIcon(qta.icon('fa5s.file-export', color='white'))
        self.export_btn.setObjectName("successButton")
        self.export_btn.clicked.connect(self.export_data)
        export_layout.addWidget(self.export_btn)
        
        main_layout.addWidget(export_card)
        
        main_layout.addStretch()
    
    # ============================================================
    # ✅ اختيار الملف + معاينة (Async)
    # ============================================================
    
    def choose_file(self):
        """اختيار ملف Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف Excel", "", 
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        self.selected_file_path = file_path
        self.file_path_label.setText(Path(file_path).name)
        self.import_btn.setEnabled(True)
        
        # ✅ معاينة الملف في الخلفية
        self._preview_file(file_path)
    
    def _preview_file(self, file_path: str):
        """معاينة محتوى الملف في الخلفية."""
        self.loading_overlay.show_loading("جاري قراءة الملف...")
        
        def _read_file():
            """قراءة الملف (في الخلفية)."""
            # ✅ قراءة أول 5 صفوف فقط للمعاينة
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=5)
                full_df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, nrows=5)
                full_df = pd.read_excel(file_path)
            
            return {
                'preview': df,
                'full': full_df,
                'rows': len(full_df),
                'columns': list(full_df.columns),
            }
        
        def _on_result(data):
            try:
                self.preview_data = data['full']
                
                # ✅ عرض المعاينة
                preview_text = (
                    f"📊 <b>عدد السجلات:</b> {data['rows']}\n"
                    f"📋 <b>الأعمدة:</b> {', '.join(data['columns'][:8])}"
                )
                if len(data['columns']) > 8:
                    preview_text += f" ... (+{len(data['columns']) - 8})"
                
                self.preview_label.setText(preview_text)
                self.preview_label.setVisible(True)
                
            except Exception as e:
                print(f"خطأ في المعاينة: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ",
                f"فشل قراءة الملف:\n{error_msg}"
            )
            self.selected_file_path = None
            self.import_btn.setEnabled(False)
        
        run_async(_read_file, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ الاستيراد (Async)
    # ============================================================
    
    def import_data(self):
        """استيراد البيانات من الملف."""
        # ✅ فحص الصلاحيات
        if self.permission_service and not self.permission_service.can_add("الطلاب"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لاستيراد البيانات"
            )
            return
        
        if not self.selected_file_path:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار ملف أولاً")
            return
        
        if not self.preview_data is not None:
            QMessageBox.warning(self, "تنبيه", "يرجى الانتظار حتى اكتمال القراءة")
            return
        
        if self._is_importing:
            QMessageBox.information(
                self, "تنبيه",
                "يوجد عملية استيراد قيد التنفيذ"
            )
            return
        
        data_type = self.data_type_combo.currentText()
        row_count = len(self.preview_data)
        
        # ✅ تأكيد
        reply = QMessageBox.question(
            self, "تأكيد الاستيراد",
            f"سيتم استيراد {row_count} سجل من النوع: {data_type}\n\n"
            "هل تريد المتابعة؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._is_importing = True
        self.import_btn.setEnabled(False)
        self.import_progress.setVisible(True)
        self.import_progress.setRange(0, 0)  # ✅ indeterminate
        self.loading_overlay.show_loading(f"جاري استيراد {row_count} سجل...")
        
        # ✅ نسخ البيانات قبل الـ Async
        data_to_import = self.preview_data.copy()
        academic_year_id = self.academic_year_id
        
        def _import():
            """استيراد البيانات (في الخلفية)."""
            success_count = 0
            error_count = 0
            errors = []
            
            with session_scope() as session:
                for index, row in data_to_import.iterrows():
                    try:
                        if data_type == "الطلاب":
                            _import_student(session, row, academic_year_id)
                        elif data_type == "أولياء الأمور":
                            _import_parent(session, row)
                        elif data_type == "الموظفون":
                            _import_employee(session, row)
                        elif data_type == "المواد الدراسية":
                            _import_subject(session, row)
                        elif data_type == "الصفوف":
                            _import_grade(session, row)
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        errors.append(f"صف {index + 1}: {str(e)}")
                
                # ✅ commit
                session.commit()
            
            return {
                'success': success_count,
                'error': error_count,
                'errors': errors[:10],  # أول 10 أخطاء
            }
        
        def _on_result(data):
            self._is_importing = False
            self.import_btn.setEnabled(True)
            self.import_progress.setVisible(False)
            self.loading_overlay.hide_loading()
            
            # ✅ عرض النتيجة
            message = (
                f"✅ <b>تم الاستيراد بنجاح</b>\n\n"
                f"📊 السجلات الناجحة: {data['success']}\n"
                f"❌ السجلات الفاشلة: {data['error']}"
            )
            
            if data['errors']:
                message += "\n\n<b>الأخطاء:</b>\n"
                for err in data['errors']:
                    message += f"• {err}\n"
            
            msg = QMessageBox(self)
            msg.setIcon(
                QMessageBox.Icon.Information 
                if data['error'] == 0 else QMessageBox.Icon.Warning
            )
            msg.setWindowTitle("نتيجة الاستيراد")
            msg.setText(message)
            msg.exec()
        
        def _on_error(error_msg):
            self._is_importing = False
            self.import_btn.setEnabled(True)
            self.import_progress.setVisible(False)
            self.loading_overlay.hide_loading()
            
            QMessageBox.critical(
                self, "خطأ",
                f"فشل الاستيراد:\n{error_msg}"
            )
        
        run_async(_import, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ التصدير (Async)
    # ============================================================
    
    def export_data(self):
        """تصدير البيانات."""
        # ✅ فحص الصلاحيات
        if self.permission_service and not self.permission_service.can_print("التقارير"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لتصدير البيانات"
            )
            return
        
        if self._is_exporting:
            QMessageBox.information(
                self, "تنبيه",
                "يوجد عملية تصدير قيد التنفيذ"
            )
            return
        
        data_type = self.data_type_combo.currentText()
        
        # ✅ تحديد الصيغة
        format_text = self.export_format_combo.currentText()
        if "CSV" in format_text:
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        else:
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        
        # ✅ اختيار مكان الحفظ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{data_type}_{timestamp}{default_ext}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف", default_name, file_filter
        )
        
        if not file_path:
            return
        
        self._is_exporting = True
        self.export_btn.setEnabled(False)
        self.export_progress.setVisible(True)
        self.export_progress.setRange(0, 0)
        self.loading_overlay.show_loading("جاري تصدير البيانات...")
        
        academic_year_id = self.academic_year_id
        is_csv = file_path.endswith('.csv')
        
        def _export():
            """تصدير البيانات (في الخلفية)."""
            with session_scope() as session:
                data = _fetch_data_for_export(
                    session, data_type, academic_year_id
                )
                
                if not data:
                    raise ValueError("لا توجد بيانات للتصدير")
                
                df = pd.DataFrame(data)
                
                if is_csv:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:
                    df.to_excel(file_path, index=False)
                
                return {
                    'file_path': file_path,
                    'row_count': len(df),
                }
        
        def _on_result(result):
            self._is_exporting = False
            self.export_btn.setEnabled(True)
            self.export_progress.setVisible(False)
            self.loading_overlay.hide_loading()
            
            QMessageBox.information(
                self, "نجاح",
                f"✅ تم تصدير {result['row_count']} سجل بنجاح\n\n"
                f"📁 {result['file_path']}"
            )
        
        def _on_error(error_msg):
            self._is_exporting = False
            self.export_btn.setEnabled(True)
            self.export_progress.setVisible(False)
            self.loading_overlay.hide_loading()
            
            QMessageBox.critical(
                self, "خطأ",
                f"فشل التصدير:\n{error_msg}"
            )
        
        run_async(_export, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تعيين الحالة."""
        self.selected_file_path = None
        self.preview_data = None
        self.file_path_label.setText("لم يتم اختيار ملف")
        self.preview_label.setVisible(False)
        self.import_btn.setEnabled(False)


# ============================================================
# ✅ دوال مساعدة للاستيراد (خارج الكلاس)
# ============================================================

def _import_student(session, row, academic_year_id):
    """استيراد طالب واحد."""
    student_number = str(row.get('رقم الطالب', '')).strip()
    full_name = str(row.get('الاسم', '')).strip()
    
    if not student_number or not full_name:
        raise ValueError("رقم الطالب والاسم مطلوبان")
    
    # ✅ فحص التكرار
    existing = session.execute(
        select(Student).where(
            Student.student_number == student_number,
            Student.academic_year_id == academic_year_id
        )
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(f"رقم الطالب {student_number} موجود مسبقاً")
    
    student = Student(
        student_number=student_number,
        full_name=full_name,
        mother_name=str(row.get('اسم الأم', '')).strip() or None,
        gender=str(row.get('الجنس', 'ذكر')).strip(),
        status=str(row.get('الحالة', 'مستمر')).strip(),
        enrollment_type=str(row.get('نوع القيد', 'مستجد')).strip(),
        academic_year_id=academic_year_id,
    )
    session.add(student)


def _import_parent(session, row):
    """استيراد ولي أمر."""
    full_name = str(row.get('الاسم', '')).strip()
    phone = str(row.get('الهاتف', '')).strip()
    
    if not full_name or not phone:
        raise ValueError("الاسم والهاتف مطلوبان")
    
    existing = session.execute(
        select(Parent).where(Parent.primary_phone == phone)
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(f"رقم الهاتف {phone} مسجل مسبقاً")
    
    parent = Parent(
        full_name=full_name,
        primary_phone=phone,
        secondary_phone=str(row.get('الهاتف الثانوي', '')).strip() or None,
        job=str(row.get('الوظيفة', '')).strip() or None,
        category=str(row.get('الفئة', 'عادي')).strip(),
    )
    session.add(parent)


def _import_employee(session, row):
    """استيراد موظف."""
    full_name = str(row.get('الاسم', '')).strip()
    job_title = str(row.get('المسمى', '')).strip()
    
    if not full_name or not job_title:
        raise ValueError("الاسم والمسمى مطلوبان")
    
    from decimal import Decimal
    
    employee = Employee(
        full_name=full_name,
        job_title=job_title,
        primary_phone=str(row.get('الهاتف', '')).strip() or None,
        basic_salary=Decimal(str(row.get('الراتب', 0))),
        status=str(row.get('الحالة', 'نشط')).strip(),
    )
    session.add(employee)


def _import_subject(session, row):
    """استيراد مادة."""
    subject_name = str(row.get('اسم المادة', '')).strip()
    
    if not subject_name:
        raise ValueError("اسم المادة مطلوب")
    
    from decimal import Decimal
    
    existing = session.execute(
        select(Subject).where(Subject.subject_name == subject_name)
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(f"المادة {subject_name} موجودة مسبقاً")
    
    subject = Subject(
        subject_name=subject_name,
        min_pass_score=Decimal(str(row.get('درجة النجاح', 50))),
        max_score=Decimal(str(row.get('الدرجة الكبرى', 100))),
    )
    session.add(subject)


def _import_grade(session, row):
    """استيراد صف."""
    grade_name = str(row.get('اسم الصف', '')).strip()
    stage_name = str(row.get('المرحلة', '')).strip()
    
    if not grade_name or not stage_name:
        raise ValueError("اسم الصف والمرحلة مطلوبان")
    
    existing = session.execute(
        select(Grade).where(Grade.grade_name == grade_name)
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(f"الصف {grade_name} موجود مسبقاً")
    
    grade = Grade(
        grade_name=grade_name,
        stage_name=stage_name,
        max_capacity=int(row.get('السعة', 30)),
    )
    session.add(grade)


# ============================================================
# ✅ دوال مساعدة للتصدير (خارج الكلاس)
# ============================================================

def _fetch_data_for_export(session, data_type: str, academic_year_id: int):
    """جلب البيانات للتصدير."""
    
    if data_type == "الطلاب":
        students = session.execute(
            select(Student).where(
                Student.academic_year_id == academic_year_id
            ).order_by(Student.full_name)
        ).scalars().all()
        
        return [
            {
                'رقم الطالب': s.student_number or '',
                'الاسم': s.full_name or '',
                'اسم الأم': s.mother_name or '',
                'الجنس': s.gender or '',
                'الحالة': s.status or '',
                'نوع القيد': s.enrollment_type or '',
            }
            for s in students
        ]
    
    elif data_type == "أولياء الأمور":
        parents = session.execute(
            select(Parent).order_by(Parent.full_name)
        ).scalars().all()
        
        return [
            {
                'الاسم': p.full_name or '',
                'الهاتف': p.primary_phone or '',
                'الهاتف الثانوي': p.secondary_phone or '',
                'الوظيفة': p.job or '',
                'الفئة': p.category or '',
            }
            for p in parents
        ]
    
    elif data_type == "الموظفون":
        employees = session.execute(
            select(Employee).order_by(Employee.full_name)
        ).scalars().all()
        
        return [
            {
                'الاسم': e.full_name or '',
                'المسمى': e.job_title or '',
                'الهاتف': e.primary_phone or '',
                'الراتب': float(e.basic_salary or 0),
                'الحالة': e.status or '',
            }
            for e in employees
        ]
    
    elif data_type == "المواد الدراسية":
        subjects = session.execute(
            select(Subject).order_by(Subject.subject_name)
        ).scalars().all()
        
        return [
            {
                'اسم المادة': s.subject_name or '',
                'درجة النجاح': float(s.min_pass_score or 0),
                'الدرجة الكبرى': float(s.max_score or 0),
            }
            for s in subjects
        ]
    
    elif data_type == "الصفوف":
        grades = session.execute(
            select(Grade).order_by(Grade.grade_name)
        ).scalars().all()
        
        return [
            {
                'اسم الصف': g.grade_name or '',
                'المرحلة': g.stage_name or '',
                'السعة': g.max_capacity or 0,
            }
            for g in grades
        ]
    
    return []