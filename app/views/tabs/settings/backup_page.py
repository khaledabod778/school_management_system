"""
واجهة النسخ الاحتياطي والصيانة - مع تحميل غير متزامن.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Optional
import qtawesome as qta
import subprocess
import os
from datetime import datetime
from pathlib import Path

from app.database.connection import db_manager
from app.core.config import config_manager
from app.services.permission_service import PermissionService
from app.views.widgets.custom_widgets import GradientButton
from app.utils.async_loader import run_async
from app.views.widgets.loading_overlay import LoadingOverlay


class BackupPage(QWidget):
    """صفحة النسخ الاحتياطي - مع تحميل غير متزامن."""
    
    def __init__(self, user, academic_year, 
                 permission_service: Optional[PermissionService] = None, 
                 parent=None):
        super().__init__(parent)
        self.user = user
        self.academic_year = academic_year
        # ✅ تعريف permission_service (كان مفقوداً)
        self.permission_service = permission_service
        
        # ✅ dicts للسجل
        self.backup_files_data: List[Dict] = []
        
        # ✅ منع التوليد المزدوج
        self._is_creating = False
        self._is_restoring = False
        
        self.setup_ui()
        
        # ✅ إنشاء طبقة التحميل
        self.loading_overlay = LoadingOverlay(self)
        
        # ✅ تحميل أولي
        QTimer.singleShot(100, self.load_backup_history)
    
    def setup_ui(self):
        """إعداد واجهة الصفحة."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        title = QLabel("النسخ الاحتياطي والصيانة")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0F172A;")
        main_layout.addWidget(title)
        
        # أزرار النسخ الاحتياطي
        buttons_card = QFrame()
        buttons_card.setObjectName("filterCard")
        buttons_card.setStyleSheet("""
            QFrame#filterCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        buttons_layout = QHBoxLayout(buttons_card)
        
        self.create_btn = GradientButton("إنشاء نسخة احتياطية", "fa5s.download")
        self.create_btn.clicked.connect(self.create_backup)
        buttons_layout.addWidget(self.create_btn)
        
        self.restore_btn = GradientButton("استعادة نسخة", "fa5s.upload")
        self.restore_btn.setObjectName("warningButton")
        self.restore_btn.clicked.connect(self.restore_backup)
        buttons_layout.addWidget(self.restore_btn)
        
        refresh_btn = GradientButton("تحديث السجل", "fa5s.sync")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.load_backup_history)
        buttons_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(buttons_card)
        
        # سجل النسخ الاحتياطية
        history_card = QFrame()
        history_card.setObjectName("tableCard")
        history_card.setStyleSheet("""
            QFrame#tableCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        history_layout = QVBoxLayout(history_card)
        
        history_title = QLabel("سجل النسخ الاحتياطية")
        history_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #0F172A;"
        )
        history_layout.addWidget(history_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "اسم الملف", "الحجم", "التاريخ", "إجراء"
        ])
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        history_layout.addWidget(self.table)
        
        main_layout.addWidget(history_card)
        
        # إعدادات النسخ التلقائي
        auto_card = QFrame()
        auto_card.setObjectName("autoCard")
        auto_card.setStyleSheet("""
            QFrame#autoCard {
                background: white;
                border: 2px solid #1976D3;
                border-radius: 12px;
                padding: 10px 15px;
            }
        """)
        
        auto_layout = QHBoxLayout(auto_card)
        
        auto_layout.addWidget(QLabel("النسخ الاحتياطي التلقائي:"))
        
        self.auto_backup_checkbox = QCheckBox("تفعيل")
        # ✅ فحص آمن
        try:
            self.auto_backup_checkbox.setChecked(
                config_manager.app_config.backup_enabled
            )
        except Exception:
            self.auto_backup_checkbox.setChecked(False)
        
        self.auto_backup_checkbox.stateChanged.connect(
            self.save_auto_backup_settings
        )
        auto_layout.addWidget(self.auto_backup_checkbox)
        
        auto_layout.addWidget(QLabel("  "))
        auto_layout.addWidget(QLabel("التكرار:"))
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["يومي", "أسبوعي"])
        self.frequency_combo.currentIndexChanged.connect(
            self.save_auto_backup_settings
        )
        auto_layout.addWidget(self.frequency_combo)
        
        auto_layout.addStretch()
        
        main_layout.addWidget(auto_card)
    
    # ============================================================
    # ✅ التحميل غير المتزامن - السجل
    # ============================================================
    
    def load_backup_history(self):
        """تحميل سجل النسخ الاحتياطية في الخلفية."""
        self.loading_overlay.show_loading("جاري تحميل السجل...")
        
        def _fetch_data():
            """فحص مجلد النسخ (في الخلفية)."""
            backup_dir = Path("backups")
            
            if not backup_dir.exists():
                return []
            
            files = list(backup_dir.glob("*.sql"))
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # ✅ تحويل إلى dicts
            return [
                {
                    'name': f.name,
                    'path': str(f),
                    'size_kb': f.stat().st_size / 1024,
                    'mtime_str': datetime.fromtimestamp(
                        f.stat().st_mtime
                    ).strftime("%Y/%m/%d %H:%M"),
                    'mtime': f.stat().st_mtime,
                }
                for f in files
            ]
        
        def _on_result(data):
            try:
                self.backup_files_data = data
                self._display_history(data)
            except Exception as e:
                print(f"خطأ: {str(e)}")
            finally:
                self.loading_overlay.hide_loading()
        
        def _on_error(error_msg):
            self.loading_overlay.hide_loading()
            print(f"فشل تحميل السجل: {error_msg}")
        
        run_async(_fetch_data, on_result=_on_result, on_error=_on_error)
    
    def _display_history(self, files: List[Dict]):
        """عرض السجل في الجدول."""
        self.table.setRowCount(len(files))
        
        for row, file_info in enumerate(files):
            self.table.setItem(
                row, 0, QTableWidgetItem(file_info['name'])
            )
            self.table.setItem(
                row, 1, 
                QTableWidgetItem(f"{file_info['size_kb']:.1f} KB")
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(file_info['mtime_str'])
            )
            
            # ✅ أزرار العمليات (مفعّلة الآن)
            action_widget = QWidget()
            action_widget.setStyleSheet("background: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)
            
            # زر الاستعادة
            restore_btn = QPushButton("استعادة")
            restore_btn.setStyleSheet("""
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
            # ✅ تمرير مسار الملف
            restore_btn.clicked.connect(
                lambda checked, path=file_info['path']: 
                self._restore_specific_backup(path)
            )
            action_layout.addWidget(restore_btn)
            
            # زر التحميل (فتح المجلد)
            download_btn = QPushButton("فتح المجلد")
            download_btn.setStyleSheet("""
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
            download_btn.clicked.connect(
                lambda checked, path=file_info['path']: 
                self._open_file_location(path)
            )
            action_layout.addWidget(download_btn)
            
            self.table.setCellWidget(row, 3, action_widget)
            self.table.setRowHeight(row, 45)
    
    # ============================================================
    # ✅ إنشاء نسخة احتياطية (Async) - الأهم!
    # ============================================================
    
    def create_backup(self):
        """إنشاء نسخة احتياطية في الخلفية."""
        # ✅ فحص الصلاحيات
        if self.permission_service and not self.permission_service.can_add("الإعدادات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لإنشاء نسخة احتياطية"
            )
            return
        
        # ✅ منع الإنشاء المتزامن
        if self._is_creating:
            QMessageBox.information(
                self, "تنبيه",
                "يوجد عملية نسخ احتياطي قيد التنفيذ"
            )
            return
        
        # ✅ تأكيد
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل تريد إنشاء نسخة احتياطية جديدة لقاعدة البيانات؟\n\n"
            "⚠️ قد يستغرق هذا الإجراء بعض الوقت حسب حجم البيانات",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._is_creating = True
        self.create_btn.setEnabled(False)
        self.loading_overlay.show_loading("جاري إنشاء النسخة الاحتياطية...")
        
        def _create_backup():
            """إنشاء النسخة (في الخلفية)."""
            # إنشاء مجلد
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = backup_dir / f"backup_{timestamp}.sql"
            
            db_config = db_manager.config
            
            # ✅ تشغيل pg_dump
            cmd = [
                "pg_dump",
                "-h", db_config.local_host,
                "-p", str(db_config.local_port),
                "-U", db_config.local_user,
                "-d", db_config.local_db_name,
                "-f", str(filename)
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config.local_password
            
            try:
                result = subprocess.run(
                    cmd, env=env, check=True, 
                    capture_output=True, text=True, timeout=3600
                )
                
                # ✅ التحقق من وجود الملف
                if not filename.exists():
                    raise RuntimeError(
                        "فشل إنشاء الملف. تحقق من إعدادات pg_dump"
                    )
                
                size_kb = filename.stat().st_size / 1024
                
                return {
                    'filename': str(filename),
                    'name': filename.name,
                    'size_kb': size_kb,
                }
            except subprocess.TimeoutExpired:
                raise RuntimeError(
                    "انتهت مهلة العملية (أكثر من ساعة). "
                    "قد تكون قاعدة البيانات كبيرة جداً"
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                raise RuntimeError(f"فشل pg_dump: {error_msg}")
        
        def _on_result(data):
            """عند اكتمال الإنشاء."""
            self._is_creating = False
            self.create_btn.setEnabled(True)
            self.loading_overlay.hide_loading()
            
            QMessageBox.information(
                self, "نجاح",
                f"✅ تم إنشاء النسخة الاحتياطية بنجاح\n\n"
                f"📁 الملف: {data['name']}\n"
                f"📊 الحجم: {data['size_kb']:.1f} KB"
            )
            
            self.load_backup_history()
        
        def _on_error(error_msg):
            """عند حدوث خطأ."""
            self._is_creating = False
            self.create_btn.setEnabled(True)
            self.loading_overlay.hide_loading()
            
            # ✅ رسالة خطأ مفصلة
            if "pg_dump" in error_msg and "not found" in error_msg.lower():
                QMessageBox.warning(
                    self, "تنبيه",
                    "pg_dump غير موجود على النظام.\n\n"
                    "الرجاء تثبيت PostgreSQL وإضافته إلى PATH"
                )
            elif "FileNotFoundError" in error_msg:
                QMessageBox.warning(
                    self, "تنبيه",
                    "pg_dump غير موجود. تأكد من تثبيت PostgreSQL "
                    "وإضافته إلى PATH"
                )
            else:
                QMessageBox.critical(
                    self, "خطأ",
                    f"فشل إنشاء النسخة الاحتياطية:\n\n{error_msg}"
                )
        
        run_async(_create_backup, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ استعادة نسخة احتياطية (Async)
    # ============================================================
    
    def restore_backup(self):
        """استعادة نسخة احتياطية من ملف خارجي."""
        # ✅ فحص الصلاحيات
        if self.permission_service and not self.permission_service.can_delete("الإعدادات"):
            QMessageBox.warning(
                self, "تنبيه",
                "ليس لديك الصلاحية لاستعادة نسخة احتياطية"
            )
            return
        
        # ✅ فحص العملية الجارية
        if self._is_restoring:
            QMessageBox.information(
                self, "تنبيه",
                "يوجد عملية استعادة قيد التنفيذ"
            )
            return
        
        # ✅ اختيار الملف
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف النسخة الاحتياطية", "", "SQL Files (*.sql)"
        )
        
        if not file_path:
            return
        
        self._restore_specific_backup(file_path)
    
    def _restore_specific_backup(self, file_path: str):
        """استعادة نسخة محددة."""
        # ✅ تأكيد خطير
        reply = QMessageBox.warning(
            self, "⚠️ تأكيد خطير",
            f"⚠️ تحذير: سيتم استبدال جميع البيانات الحالية!\n\n"
            f"📁 الملف: {Path(file_path).name}\n\n"
            "هل أنت متأكد تماماً من الاستعادة؟\n"
            "لا يمكن التراجع عن هذه العملية!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # ✅ تأكيد ثانٍ
        confirm_text = QLineEdit()
        confirm_text.setPlaceholderText("اكتب كلمة 'تأكيد' للمتابعة")
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("تأكيد نهائي")
        msg.setText(
            "للمتابعة، اكتب كلمة 'تأكيد' في الحقل أدناه:"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.layout().addWidget(confirm_text, 1, 0, 1, msg.layout().columnCount())
        
        if msg.exec() != QMessageBox.StandardButton.Ok:
            return
        
        if confirm_text.text().strip() != "تأكيد":
            QMessageBox.warning(
                self, "إلغاء",
                "لم يتم إدخال كلمة التأكيد. تم إلغاء العملية"
            )
            return
        
        self._is_restoring = True
        self.restore_btn.setEnabled(False)
        self.loading_overlay.show_loading("جاري استعادة النسخة...")
        
        def _restore():
            """استعادة النسخة (في الخلفية)."""
            db_config = db_manager.config
            
            # ✅ استخدام psql للاستعادة
            cmd = [
                "psql",
                "-h", db_config.local_host,
                "-p", str(db_config.local_port),
                "-U", db_config.local_user,
                "-d", db_config.local_db_name,
                "-f", file_path
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config.local_password
            
            try:
                result = subprocess.run(
                    cmd, env=env, check=True,
                    capture_output=True, text=True, timeout=3600
                )
                return True
            except subprocess.TimeoutExpired:
                raise RuntimeError("انتهت مهلة العملية")
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                raise RuntimeError(f"فشل psql: {error_msg}")
        
        def _on_result(_):
            self._is_restoring = False
            self.restore_btn.setEnabled(True)
            self.loading_overlay.hide_loading()
            
            QMessageBox.information(
                self, "نجاح",
                "✅ تم استعادة النسخة بنجاح\n\n"
                "⚠️ يُنصح بإعادة تشغيل التطبيق لضمان تحميل البيانات الجديدة"
            )
        
        def _on_error(error_msg):
            self._is_restoring = False
            self.restore_btn.setEnabled(True)
            self.loading_overlay.hide_loading()
            
            if "psql" in error_msg and "not found" in error_msg.lower():
                QMessageBox.warning(
                    self, "تنبيه",
                    "psql غير موجود على النظام.\n\n"
                    "الرجاء تثبيت PostgreSQL وإضافته إلى PATH"
                )
            else:
                QMessageBox.critical(
                    self, "خطأ",
                    f"فشل استعادة النسخة:\n\n{error_msg}"
                )
        
        run_async(_restore, on_result=_on_result, on_error=_on_error)
    
    # ============================================================
    # ✅ فتح موقع الملف
    # ============================================================
    
    def _open_file_location(self, file_path: str):
        """فتح موقع الملف في مدير الملفات."""
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(
                    self, "تنبيه",
                    "الملف غير موجود"
                )
                return
            
            folder = path.parent.resolve()
            
            import sys
            if sys.platform == "win32":
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ",
                f"فشل فتح المجلد:\n{str(e)}"
            )
    
    # ============================================================
    # ✅ حفظ الإعدادات
    # ============================================================
    
    def save_auto_backup_settings(self):
        """حفظ إعدادات النسخ التلقائي."""
        try:
            enabled = self.auto_backup_checkbox.isChecked()
            frequency = self.frequency_combo.currentText()
            
            # ✅ حفظ في الإعدادات (إذا كانت متاحة)
            if hasattr(config_manager.app_config, 'backup_enabled'):
                config_manager.app_config.backup_enabled = enabled
            
            if hasattr(config_manager.app_config, 'backup_frequency'):
                config_manager.app_config.backup_frequency = frequency
            
            # ✅ محاولة الحفظ الدائم
            if hasattr(config_manager, 'save_settings'):
                config_manager.save_settings()
            
        except Exception as e:
            print(f"فشل حفظ الإعدادات: {str(e)}")
    
    # ============================================================
    # ✅ الأحداث
    # ============================================================
    
    def resizeEvent(self, event):
        """تحديث حجم طبقة التحميل."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh(self):
        """إعادة تحميل السجل."""
        self.load_backup_history()