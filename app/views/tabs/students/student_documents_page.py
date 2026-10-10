"""
واجهة أرشيف وثائق الطلاب - مع تحميل غير متزامن.
"""

import tempfile

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta
import shutil
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from app.database.session import session_scope
from app.database.models import Student, StudentDocument
from sqlalchemy import select, or_

from app.services.permission_service import PermissionService
from app.services.student_documents_factory import StudentDocumentsFactory
from app.views.widgets.custom_widgets import GradientButton, SearchBox
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class StudentDocumentsPage(QWidget):
    """صفحة وثائق الطلاب - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, permission_service: Optional[PermissionService] = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        self.permission_service = permission_service
        
        # ✅ تخزين ID السنة قبل فقدان الجلسة
        self.academic_year_id = academic_year.id if academic_year else None
        
        # ✅ تخزين بيانات الطالب المحدد (dicts)
        self.selected_student_id: Optional[int] = None
        self.selected_student_name: str = ""
        self.selected_student_number: str = ""
        
        # ✅ تخزين قائمة الطلاب والوثائق
        self.students_data: List[Dict] = []
        self.documents_data: List[Dict] = []
        
        # ✅ debounce للبحث
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)  # 300ms
        self._search_timer.timeout.connect(self.search_students)
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي للطلاب
        QTimer.singleShot(100, self.load_initial_students)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("أرشيف وثائق الطلاب")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # بحث عن طالب
        search_card = QFrame()
        search_card.setObjectName("filterCard")
        search_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        search_layout = QHBoxLayout(search_card)
        
        self.search_input = SearchBox("بحث عن طالب...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        main_layout.addWidget(search_card)
        
        # قائمة الطلاب
        self.students_list = QListWidget()
        self.students_list.setMaximumHeight(150)
        self.students_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:selected {
                background: #1976D3;
                color: white;
                border-radius: 4px;
            }
        """)
        self.students_list.itemClicked.connect(self.select_student)
        main_layout.addWidget(self.students_list)
        
        # منطقة الوثائق
        docs_card = QFrame()
        docs_card.setObjectName("filterCard")
        docs_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        self.docs_card = docs_card
        # self.docs_card.setVisible(False)  # ← مخفي حتى يتم اختيار طالب
        
        docs_layout = QVBoxLayout(docs_card)
        
        # معلومات الطالب
        self.student_info_label = QLabel()
        self.student_info_label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #0F172A; padding: 5px;"
        )
        docs_layout.addWidget(self.student_info_label)
        
        # جدول الوثائق
        self.docs_table = QTableWidget()
        self.docs_table.setColumnCount(4)  # ✅ 4 أعمدة (أضفنا عمود لعرض المستند)
        self.docs_table.setHorizontalHeaderLabels([
            "نوع الوثيقة", "تاريخ الرفع", "الملف", "إجراء"
        ])
        self.docs_table.setColumnWidth(0, 200)
        self.docs_table.setColumnWidth(1, 200)
        self.docs_table.setColumnWidth(2, 200)
        self.docs_table.setColumnWidth(3, 150)
        self.docs_table.horizontalHeader().setStretchLastSection(True)
        self.docs_table.setAlternatingRowColors(True)
        self.docs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.docs_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.docs_table.verticalHeader().setVisible(False)
        docs_layout.addWidget(self.docs_table)

        # أزرار العمليات
        toolbar = QHBoxLayout()  

        # زر رفع وثيقة
        upload_btn = GradientButton("رفع وثيقة جديدة", "fa5s.upload")
        upload_btn.clicked.connect(self.upload_document)
        toolbar.addWidget(upload_btn)

        # ✅ زر حذف وثيقة (مفعّل الآن)
        delete_btn = GradientButton("حذف وثيقة", "fa5s.trash")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_document)
        toolbar.addWidget(delete_btn)

        docs_layout.addLayout(toolbar)
        
        main_layout.addWidget(docs_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن - الطلاب
    # ============================================================
    
    def load_initial_students(self):
        """تحميل أولي للطلاب (آخر 20 طالب)."""
        self._load_students(search_text="")
    
    def _on_search_text_changed(self):
        """عند تغيير نص البحث - debounce."""
        self._search_timer.stop()
        self._search_timer.start()
    
    def search_students(self):
        """البحث عن الطلاب (يُستدعى بعد debounce)."""
        search_text = self.search_input.text().strip()
        self._load_students(search_text=search_text)
    
    def _load_students(self, search_text: str):
        """تحميل قائمة الطلاب."""
        self.loading_overlay.show_loading("جاري البحث...")
        academic_year_id = self.academic_year_id

        def _fetch():
            if StudentDocumentsFactory.is_remote():
                from app.services.student_factory import StudentFactory
                service = StudentFactory.get_service()
                return service.lookup(
                    academic_year_id=academic_year_id,
                    search=search_text or None,
                    limit=30,
                )
            else:
                from app.database.session import session_scope
                from app.database.models import Student
                from sqlalchemy import select, or_
                with session_scope() as session:
                    query = select(Student).where(
                        Student.academic_year_id == academic_year_id
                    )
                    if search_text:
                        query = query.where(or_(
                            Student.full_name.ilike(f"%{search_text}%"),
                            Student.student_number.ilike(f"%{search_text}%"),
                        ))
                    students = session.execute(
                        query.limit(30)
                    ).scalars().all()
                    return [
                        {
                            'id': s.id,
                            'full_name': s.full_name or '',
                            'student_number': s.student_number or '',
                        }
                        for s in students
                    ]

        def _ok(data):
            try:
                self.students_data = data
                self.students_list.clear()
                for s in data:
                    item = QListWidgetItem(
                        f"{s['full_name']} - {s['student_number']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, s['id'])
                    self.students_list.addItem(item)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)
        
    # ============================================================
    # ✅ اختيار طالب
    # ============================================================
    
    def select_student(self, item: QListWidgetItem):
        """اختيار طالب من القائمة."""
        student_id = item.data(Qt.ItemDataRole.UserRole)
        
        # ✅ البحث عن بيانات الطالب في القائمة المحفوظة
        student = next(
            (s for s in self.students_data if s['id'] == student_id),
            None
        )
        
        if not student:
            return
        
        # ✅ تخزين البيانات كـ dict (بدلاً من ORM object)
        self.selected_student_id = student['id']
        self.selected_student_name = student['full_name']
        self.selected_student_number = student['student_number']
        
        self.student_info_label.setText(
            f"📄 وثائق الطالب: {self.selected_student_name} "
            f"({self.selected_student_number})"
        )
        self.docs_card.setVisible(True)
        
        # ✅ تحميل الوثائق في الخلفية
        self.load_documents()
    
    # ============================================================
    # ✅ تحميل الوثائق
    # ============================================================
    
    def load_documents(self):
        """تحميل وثائق الطالب المحدد."""
        if not self.selected_student_id:
            return

        self.loading_overlay.show_loading("جاري تحميل الوثائق...")
        student_id = self.selected_student_id

        def _fetch():
            if StudentDocumentsFactory.is_remote():
                service = StudentDocumentsFactory.get_service()
                return service.list_documents(student_id)
            else:
                from app.database.session import session_scope
                from app.database.models import StudentDocument
                from sqlalchemy import select
                with session_scope() as session:
                    docs = session.execute(
                        select(StudentDocument)
                        .where(StudentDocument.student_id == student_id)
                        .order_by(StudentDocument.uploaded_at.desc())
                    ).scalars().all()
                    return [
                        {
                            'id': d.id,
                            'document_type': d.document_type or '',
                            'file_path': d.file_path or '',
                            'file_name': (
                                Path(d.file_path).name if d.file_path else ''
                            ),
                            'uploaded_at': (
                                d.uploaded_at.strftime("%Y/%m/%d %H:%M")
                                if d.uploaded_at else ''
                            ),
                        }
                        for d in docs
                    ]

        def _ok(data):
            try:
                self.documents_data = data
                self._display_documents(data)
            finally:
                self.loading_overlay.hide_loading()

        def _err(m):
            self.loading_overlay.hide_loading()
            QMessageBox.critical(self, "خطأ", f"فشل: {m}")

        run_async(_fetch, on_result=_ok, on_error=_err)

    def _display_documents(self, documents: List[Dict]):
        """عرض الوثائق في الجدول."""
        self.docs_table.setRowCount(len(documents))
        
        for row, doc in enumerate(documents):
            self.docs_table.setItem(
                row, 0, QTableWidgetItem(doc['document_type'])
            )
            self.docs_table.setItem(
                row, 1, QTableWidgetItem(doc['uploaded_at'])
            )
            self.docs_table.setItem(
                row, 2, QTableWidgetItem(doc['file_name'])
            )
            
            # ✅ زر العرض
            view_btn = QPushButton("عرض")
            view_btn.setObjectName("primaryButton")
            view_btn.setStyleSheet("""
                QPushButton#primaryButton {
                    background: #EEF2FF;
                    color: #0D47A1;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton#primaryButton:hover {
                    background: #E0E7FF;
                }
            """)
            # ✅ تمرير ID للعرض
            view_btn.clicked.connect(
                lambda checked, did=doc['id']: self.view_document(did)
            )
            self.docs_table.setCellWidget(row, 3, view_btn)
            self.docs_table.setRowHeight(row, 45)
    
    # ============================================================
    # ✅ عرض الوثيقة
    # ============================================================
    
    def view_document(self, document_id: int):
        """عرض الوثيقة."""
        doc = next(
            (d for d in self.documents_data if d['id'] == document_id),
            None,
        )
        if not doc:
            return

        def _do():
            if StudentDocumentsFactory.is_remote():
                # نزّل إلى temp ثم افتح
                service = StudentDocumentsFactory.get_service()
                tmp_dir = Path(tempfile.gettempdir()) / "school_erp_docs"
                tmp_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = tmp_dir / doc['file_name']
                service.download_document(document_id, str(tmp_path))
                _open_file(str(tmp_path))
            else:
                file_path = doc['file_path']
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"الملف غير موجود: {file_path}")
                _open_file(file_path)

        def _open_file(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])

        try:
            _do()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل فتح الملف: {e}")
            
    # ============================================================
    # ✅ رفع وثيقة
    # ============================================================
    
    def upload_document(self):
        """رفع وثيقة جديدة."""
        if (self.permission_service
                and not self.permission_service.can_add("وثائق الطلاب")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        if not self.selected_student_id:
            QMessageBox.warning(self, "تنبيه", "اختر طالباً أولاً")
            return

        doc_types = [
            "شهادة ميلاد", "بطاقة شخصية", "شهادة انتقالية",
            "صورة شخصية", "أخرى",
        ]
        doc_type, ok = QInputDialog.getItem(
            self, "نوع الوثيقة", "اختر النوع:",
            doc_types, 0, False,
        )
        if not ok:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر الملف", "",
            "Documents (*.pdf *.doc *.docx *.jpg *.jpeg *.png);;All Files (*.*)",
        )
        if not file_path:
            return

        def _do():
            if StudentDocumentsFactory.is_remote():
                service = StudentDocumentsFactory.get_service()
                service.upload_document(
                    self.selected_student_id, doc_type, file_path,
                )
            else:
                # الكود القديم (نسخ الملف + DB)
                upload_dir = Path("uploads/documents")
                upload_dir.mkdir(parents=True, exist_ok=True)
                original_name = Path(file_path).name
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = (
                    f"{self.selected_student_number}_{ts}_{original_name}"
                )
                dest = upload_dir / new_name
                shutil.copy2(file_path, dest)

                from app.database.session import session_scope
                from app.database.models import StudentDocument
                with session_scope() as session:
                    session.add(StudentDocument(
                        student_id=self.selected_student_id,
                        document_type=doc_type,
                        file_path=str(dest),
                    ))

        try:
            _do()
            QMessageBox.information(self, "نجاح", "تم رفع الوثيقة بنجاح")
            self.load_documents()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")

    # ============================================================
    # ✅ حذف وثيقة
    # ============================================================
    
    def delete_document(self):
        """حذف وثيقة."""
        if (self.permission_service
                and not self.permission_service.can_delete("وثائق الطلاب")):
            QMessageBox.warning(self, "تنبيه", "ليس لديك الصلاحية")
            return

        current_row = self.docs_table.currentRow()
        if current_row < 0 or current_row >= len(self.documents_data):
            QMessageBox.warning(self, "تنبيه", "اختر وثيقة للحذف")
            return

        doc = self.documents_data[current_row]
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"حذف الوثيقة:\n{doc['document_type']}\n{doc['file_name']}؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _do():
            if StudentDocumentsFactory.is_remote():
                service = StudentDocumentsFactory.get_service()
                service.delete_document(doc['id'])
            else:
                from app.database.session import session_scope
                from app.database.models import StudentDocument
                with session_scope() as session:
                    d = session.get(StudentDocument, doc['id'])
                    if d:
                        file_path = d.file_path
                        session.delete(d)
                        session.commit()
                        if file_path and os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except Exception:
                                pass

        try:
            _do()
            QMessageBox.information(self, "نجاح", "تم الحذف بنجاح")
            self.load_documents()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل: {e}")
            
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل البيانات."""
        self.selected_student_id = None
        self.selected_student_name = ""
        self.selected_student_number = ""
        self.documents_data = []
        self.docs_card.setVisible(False)
        self.load_initial_students()