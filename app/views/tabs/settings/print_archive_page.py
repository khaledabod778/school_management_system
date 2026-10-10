"""
واجهة أرشيف المطبوعات - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Optional, Dict
import qtawesome as qta

from app.database.session import session_scope
from app.database.models import PrintArchive
from app.services.permission_service import PermissionService
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.services.print_archive_factory import PrintArchiveFactory
from app.views.widgets.custom_widgets import QDateEditEN
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class PrintArchivePage(QWidget):
    """صفحة أرشيف المطبوعات - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        
        # ✅ dicts بدلاً من ORM
        self.all_prints: List[Dict] = []
        self.current_filtered_prints: List[Dict] = []
        
        # ✅ منع التحميل المزدوج
        self._is_loading = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        title = QLabel("أرشيف المطبوعات")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # بطاقة الفلاتر
        filter_card = QFrame()
        filter_card.setObjectName("filterCard")
        filter_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        filter_layout = QHBoxLayout(filter_card)
        
        filter_layout.addWidget(QLabel("نوع المستند:"))
        self.doc_type_filter = QComboBox()
        self.doc_type_filter.addItem("جميع الأنواع", None)
        # ✅ Bug fix: استخدام addItem مع data بدلاً من addItems
        doc_types = ["سند قبض", "سند صرف", "شهادة", "تقرير", "كشف"]
        for doc_type in doc_types:
            self.doc_type_filter.addItem(doc_type, doc_type)
        self.doc_type_filter.currentIndexChanged.connect(self.filter_prints)
        filter_layout.addWidget(self.doc_type_filter)
        
        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEditEN(QDate.currentDate().addDays(-30))
        self.date_from.dateChanged.connect(self.filter_prints)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEditEN()
        self.date_to.dateChanged.connect(self.filter_prints)
        filter_layout.addWidget(self.date_to)
        
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_card)
        
        # بطاقة الجدول
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_card.setStyleSheet("""
            QFrame#tableCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(table_card)
        
        self.count_label = QLabel("عدد المطبوعات: 0")
        self.count_label.setObjectName("count_label")
        card_layout.addWidget(self.count_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "رقم المستند", "نوع المستند", "المستفيد", "تاريخ الطباعة", 
            "المستخدم", "إجراء"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.preview_print)
        card_layout.addWidget(self.table)
        
        main_layout.addWidget(table_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن
    # ============================================================
    
    def load_data(self):
        """تحميل الأرشيف - Local أو Remote."""
        if self._is_loading:
            return

        self._is_loading = True
        self.loading_overlay.show_loading("جاري تحميل الأرشيف...")

        def _fetch_data():
            # ✅ Remote
            if PrintArchiveFactory.is_remote():
                return PrintArchiveFactory.get_service() \
                    .list_prints(limit=1000)

            # Local (الكود القديم)
            with session_scope() as session:
                prints = session.execute(
                    select(PrintArchive)
                    .options(joinedload(PrintArchive.printer))
                    .order_by(PrintArchive.printed_at.desc())
                    .limit(1000)
                ).unique().scalars().all()

                prints_data = []
                for p in prints:
                    prints_data.append({
                        'id': p.id,
                        'document_number': p.document_number or '',
                        'document_type': p.document_type or '',
                        'related_record_id': p.related_record_id,
                        'printed_at': p.printed_at,
                        'printed_at_str': (
                            p.printed_at.strftime("%Y/%m/%d %H:%M")
                            if p.printed_at else ''
                        ),
                        'printed_date': (
                            p.printed_at.date() if p.printed_at else None
                        ),
                        'printer_name': (
                            p.printer.username if p.printer else ''
                        ),
                    })

                return prints_data

        def _on_result(data):
            try:
                self.all_prints = data
                self.current_filtered_prints = list(self.all_prints)
                self.display_prints(self.all_prints)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self._is_loading = False
                self.loading_overlay.hide_loading()

        def _on_error(error_msg):
            self._is_loading = False
            self.loading_overlay.hide_loading()
            QMessageBox.critical(
                self, "خطأ", f"فشل التحميل:\n{error_msg}"
            )
            self.all_prints = []
            self.current_filtered_prints = []
            self.display_prints([])

        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
        
    # ============================================================
    # ✅ عرض البيانات
    # ============================================================
    
    def display_prints(self, prints: List[Dict]):
        """عرض المطبوعات."""
        self.table.setRowCount(len(prints))
        
        for row, print_data in enumerate(prints):
            self.table.setItem(
                row, 0, QTableWidgetItem(print_data['document_number'])
            )
            self.table.setItem(
                row, 1, QTableWidgetItem(print_data['document_type'])
            )
            self.table.setItem(
                row, 2, 
                QTableWidgetItem(str(print_data['related_record_id'] or ""))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(print_data['printed_at_str'])
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(print_data['printer_name'])
            )
            
            # ✅ أزرار العمليات (مفعّلة)
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)
            
            # زر المعاينة
            preview_btn = QPushButton("معاينة")
            preview_btn.setStyleSheet("""
                QPushButton {
                    background: #EEF2FF;
                    color: #0D47A1;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #E0E7FF;
                }
            """)
            # ✅ تمرير ID
            preview_btn.clicked.connect(
                lambda checked, pid=print_data['id']: 
                self.preview_print_by_id(pid)
            )
            action_layout.addWidget(preview_btn)
            
            # زر إعادة الطباعة
            reprint_btn = QPushButton("إعادة طباعة")
            reprint_btn.setStyleSheet("""
                QPushButton {
                    background: #FEF3C7;
                    color: #D97706;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #FDE68A;
                }
            """)
            reprint_btn.clicked.connect(
                lambda checked, pid=print_data['id']: 
                self.reprint_by_id(pid)
            )
            action_layout.addWidget(reprint_btn)
            
            self.table.setCellWidget(row, 5, action_widget)
            self.table.setRowHeight(row, 45)
        
        self.count_label.setText(f"عدد المطبوعات: {len(prints)}")
    
    # ============================================================
    # ✅ الفلترة
    # ============================================================
    
    def filter_prints(self):
        """تصفية المطبوعات."""
        # ✅ Bug fix: استخدام currentData() الصحيح
        doc_type = self.doc_type_filter.currentData()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        
        filtered = []
        for print_data in self.all_prints:
            # فلتر النوع
            if doc_type and print_data['document_type'] != doc_type:
                continue
            
            # فلتر التاريخ
            print_date = print_data['printed_date']
            if print_date:
                # ✅ دعم str (من JSON) و date (من Local)
                if isinstance(print_date, str):
                    try:
                        from datetime import date as _date
                        print_date = _date.fromisoformat(print_date)
                    except Exception:
                        print_date = None
                if print_date and (
                    print_date < date_from or print_date > date_to
                ):
                    continue
            
            filtered.append(print_data)
        
        self.current_filtered_prints = filtered
        self.display_prints(filtered)
    
    # ============================================================
    # ✅ الحصول على السجل المحدد
    # ============================================================
    
    def _get_selected_print_id(self) -> Optional[int]:
        """الحصول على ID السجل المحدد."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        if current_row >= len(self.current_filtered_prints):
            return None
        
        return self.current_filtered_prints[current_row]['id']
    
    def _get_print_by_id(self, print_id: int) -> Optional[Dict]:
        """الحصول على سجل بواسطة ID."""
        return next(
            (p for p in self.all_prints if p['id'] == print_id),
            None
        )
    
    # ============================================================
    # ✅ المعاينة
    # ============================================================
    
    def preview_print(self):
        """معاينة السجل المحدد."""
        print_id = self._get_selected_print_id()
        if not print_id:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار سجل")
            return
        
        self.preview_print_by_id(print_id)
    
    def preview_print_by_id(self, print_id: int):
        """معاينة السجل بواسطة ID."""
        print_data = self._get_print_by_id(print_id)
        if not print_data:
            QMessageBox.warning(self, "تنبيه", "السجل غير موجود")
            return
        
        dialog = PrintPreviewDialog(print_data, parent=self)
        dialog.exec()
    
    # ============================================================
    # ✅ إعادة الطباعة
    # ============================================================
    
    def reprint_by_id(self, print_id: int):
        """إعادة طباعة السجل."""
        if self.permission_service and not self.permission_service.can_print("الإعدادات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لإعادة الطباعة"
            )
            return
        
        print_data = self._get_print_by_id(print_id)
        if not print_data:
            QMessageBox.warning(self, "تنبيه", "السجل غير موجود")
            return
        
        reply = QMessageBox.question(
            self, "تأكيد إعادة الطباعة",
            f"هل تريد إعادة طباعة المستند:\n\n"
            f"📄 النوع: {print_data['document_type']}\n"
            f"🔢 الرقم: {print_data['document_number']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self, "طباعة",
                "سيتم تنفيذ الطباعة في مرحلة التقارير"
            )
    
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
        self.load_data()


# ============================================================
# ✅ نافذة معاينة السجل (مع dicts)
# ============================================================

class PrintPreviewDialog(QDialog):
    """نافذة معاينة المطبوع."""
    
    def __init__(self, print_data: Dict, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("معاينة المستند")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog {
                background: #F8FAFC;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        
        # العنوان
        title = QLabel(f"معاينة: {print_data['document_type']}")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #0F172A;
            padding: 10px;
            background: white;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # التفاصيل
        details_widget = QWidget()
        details_widget.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        details_layout = QGridLayout(details_widget)
        details_layout.setSpacing(10)
        
        details = [
            ("رقم المستند:", print_data['document_number']),
            ("نوع المستند:", print_data['document_type']),
            ("رقم السجل المرتبط:", str(print_data['related_record_id'] or "-")),
            ("تاريخ الطباعة:", print_data['printed_at_str']),
            ("تمت الطباعة بواسطة:", print_data['printer_name']),
        ]
        
        for row, (label, value) in enumerate(details):
            label_widget = QLabel(label)
            label_widget.setStyleSheet(
                "color: #64748B; font-weight: 600; font-size: 13px;"
            )
            details_layout.addWidget(label_widget, row, 0)
            
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet(
                "color: #0F172A; font-weight: 500; font-size: 13px;"
            )
            value_widget.setWordWrap(True)
            details_layout.addWidget(value_widget, row, 1)
        
        main_layout.addWidget(details_widget)
        
        # ملاحظة
        note = QLabel(
            "ℹ️ معاينة المستند الفعلية ستكون متاحة في مرحلة التقارير"
        )
        note.setStyleSheet("""
            color: #64748B;
            font-size: 12px;
            padding: 10px;
            background: #FEF3C7;
            border-radius: 8px;
        """)
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(note)
        
        main_layout.addStretch()
        
        # زر الإغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1976D3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1565C0;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)