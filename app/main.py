"""
الملف الرئيسي لتشغيل التطبيق - مع نظام الصلاحيات ودعم السحابة.
"""

import hashlib
import sys
import os
import logging
import socket
import uuid
from pathlib import Path
from typing import Optional, Dict
from app.services.audit_service import AuditService, setup_audit_listeners
from app.services.permission_service import PermissionService
from app.services.sync.background_sync import BackgroundSyncService
from app.services.sync.change_tracker import ChangeTracker
from app.views.tabs.dashboards.accountant_dashboard import AccountantDashboardPage
from app.views.tabs.finance.employee_statement_page import EmployeeStatementPage
from app.views.tabs.finance.student_fee_statement_page import StudentFeeStatementPage

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import qtawesome as qta

from app.core.config import config_manager
from app.database.session import (
    init_database, create_tables, close_database, 
    session_scope, check_cloud_connection
)
from app.database.connection import db_manager
from app.database.models import AcademicYear, User, Role, Permission, RolePermission

from app.views.login_view import LoginWindow
from app.views.main_window import MainWindow

# استيراد جميع الصفحات
from app.views.tabs.dashboards.dashboard import DashboardPage
from app.views.tabs.students.student_list import StudentListPage
from app.views.tabs.attendance.attendance_page import AttendancePage
from app.views.tabs.grades.grades_page import GradesPage
from app.views.tabs.homeworks.homework_page import HomeworkPage
from app.views.tabs.behavior.behavior_page import BehaviorPage
from app.views.tabs.finance.fees_page import FeesPage
from app.views.tabs.finance.receipts_page import ReceiptsPage
from app.views.tabs.finance.expenses_page import ExpensesPage
from app.views.tabs.finance.payroll_page import PayrollPage
from app.views.tabs.finance.allowances_page import AllowancesPage
from app.views.tabs.finance.loans_page import LoansPage
from app.views.tabs.employees.employees_page import EmployeesPage
from app.views.tabs.users.users_page import UsersPage
from app.views.tabs.permissions.permissions_page import PermissionsPage
from app.views.tabs.academic.school_Info_page import SchoolInfoPage
from app.views.tabs.settings.audit_log_page import AuditLogPage
from app.views.tabs.settings.notifications_page import NotificationsPage
from app.views.tabs.settings.profile_page import ProfilePage
from app.views.tabs.reports.reports_page import ReportsPage
from app.views.tabs.academic.academic_years_page import AcademicYearsPage
from app.views.tabs.academic.grades_sections_page import GradesSectionsPage
from app.views.tabs.academic.subjects_page import SubjectsPage
from app.views.tabs.academic.fee_structure_page import FeeStructurePage
from app.views.tabs.academic.teacher_assignment_page import TeacherAssignmentPage
from app.views.tabs.academic.year_closing_page import YearClosingPage
from app.views.tabs.students.parents_page import ParentsPage
from app.views.tabs.students.student_documents_page import StudentDocumentsPage
from app.views.tabs.students.student_distribution_page import StudentDistributionPage
from app.views.tabs.certificates.certificates_page import CertificatesPage
from app.views.tabs.certificates.top_students_page import TopStudentsPage
from app.views.tabs.schedules.schedules_page import SchedulesPage
from app.views.tabs.settings.backup_page import BackupPage
from app.views.tabs.settings.import_export_page import ImportExportPage
from app.views.tabs.settings.print_archive_page import PrintArchivePage
from app.views.tabs.settings.bulk_notifications_page import BulkNotificationsPage

from sqlalchemy import select


def setup_logging():
    """إعداد التسجيل."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class ApplicationController:
    """وحدة التحكم الرئيسية."""
    
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.login_window: Optional[LoginWindow] = None
        self.main_window: Optional[MainWindow] = None
        self.current_user: Optional[User] = None
        self.current_academic_year: Optional[AcademicYear] = None
        self.pages: Dict[str, QWidget] = {}
        self.user_permissions: Dict[str, Dict] = {}
        self.user_role_name: str = ""
        self.permission_service: Optional[PermissionService] = None
        self.database_mode: str = "local"  # local / cloud / hybrid
        self.is_using_cloud: bool = False
        self.sync_service: Optional[BackgroundSyncService] = None

        
        # سجل الصفحات مع الصلاحيات المطلوبة
        self.page_registry: Dict[str, Dict] = {
            # ====== الرئيسية ======
            'dashboard': {
                'title': 'لوحة التحكم',
                'class': DashboardPage,
                'icon': 'fa5s.tachometer-alt',
                'section': 'الرئيسية',
                'module': 'لوحة التحكم'
            },
            'accountant_dashboard': {
                'title': 'لوحة المحاسب',
                'class': AccountantDashboardPage,
                'icon': 'fa5s.calculator',
                'section': 'الرئيسية',
                'module': 'المؤشرات المالية',
            },
            
            # ====== التهيئة الأكاديمية ======
            'school_info': {
                'title': 'بيانات المدرسة',
                'class': SchoolInfoPage,
                'icon': 'fa5s.building',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            'academic_years': {
                'title': 'السنوات الدراسية',
                'class': AcademicYearsPage,
                'icon': 'fa5s.calendar-alt',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            'grades_sections': {
                'title': 'الصفوف والشعب',
                'class': GradesSectionsPage,
                'icon': 'fa5s.school',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            'fee_structure': {
                'title': 'لائحة الرسوم',
                'class': FeeStructurePage,
                'icon': 'fa5s.money-bill-wave',
                'section': 'التهيئة الأكاديمية',
                'module': 'الرسوم'
            },
            'subjects': {
                'title': 'دليل المواد',
                'class': SubjectsPage,
                'icon': 'fa5s.book',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            'teacher_assignment': {
                'title': 'توزيع المواد',
                'class': TeacherAssignmentPage,
                'icon': 'fa5s.chalkboard-teacher',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            'year_closing': {
                'title': 'الإقفال السنوي',
                'class': YearClosingPage,
                'icon': 'fa5s.lock',
                'section': 'التهيئة الأكاديمية',
                'module': 'الإعدادات'
            },
            
            # ====== الطلاب وأولياء الأمور ======
            'students': {
                'title': 'إدارة الطلاب',
                'class': StudentListPage,
                'icon': 'fa5s.user-graduate',
                'section': 'الطلاب وأولياء الأمور',
                'module': 'إدارة الطلاب'
            },
            'parents': {
                'title': 'أولياء الأمور',
                'class': ParentsPage,
                'icon': 'fa5s.users',
                'section': 'الطلاب وأولياء الأمور',
                'module': 'أولياء الأمور'
            },
            'student_documents': {
                'title': 'وثائق الطلاب',
                'class': StudentDocumentsPage,
                'icon': 'fa5s.folder',
                'section': 'الطلاب وأولياء الأمور',
                'module': 'وثائق الطلاب'
            },
            'student_distribution': {
                'title': 'توزيع الطلاب',
                'class': StudentDistributionPage,
                'icon': 'fa5s.sitemap',
                'section': 'الطلاب وأولياء الأمور',
                'module': 'توزيع الطلاب'
            },
            
            # ====== المالية للطلاب ======
            'fees': {
                'title': 'رسوم الطلاب',
                'class': FeesPage,
                'icon': 'fa5s.money-bill',
                'section': 'المالية للطلاب',
                'module': 'رسوم الطلاب'
            },
            'receipts': {
                'title': 'سندات القبض',
                'class': ReceiptsPage,
                'icon': 'fa5s.receipt',
                'section': 'المالية للطلاب',
                'module': 'سندات القبض'
            },
            'student_fee_statement': {
                'title': 'كشف حساب طالب',
                'class': StudentFeeStatementPage,
                'icon': 'fa5s.file-invoice-dollar',
                'section': 'المالية للطلاب',
                'module': 'كشف حساب طالب'
            },
            
            # ====== الكادر ======
            'employees': {
                'title': 'الموظفين والمعلمين',
                'class': EmployeesPage,
                'icon': 'fa5s.user-tie',
                'section': 'الكادر التعليمي',
                'module': 'الموظفين والمعلمين'
            },
            
            # ====== المالية العامة ======
            'expenses': {
                'title': 'سندات الصرف',
                'class': ExpensesPage,
                'icon': 'fa5s.file-invoice',
                'section': 'المالية العامة',
                'module': 'سندات الصرف'
            },
            'allowances': {
                'title': 'البدلات والخصومات',
                'class': AllowancesPage,
                'icon': 'fa5s.coins',
                'section': 'المالية العامة',
                'module': 'البدلات والخصومات'
            },
            'loans': {
                'title': 'السلف المالية',
                'class': LoansPage,
                'icon': 'fa5s.hand-holding-usd',
                'section': 'المالية العامة',
                'module': 'السلف المالية'
            },
            'payroll': {
                'title': 'كشف الرواتب',
                'class': PayrollPage,
                'icon': 'fa5s.money-check-alt',
                'section': 'المالية العامة',
                'module': 'كشف الرواتب'
            },
            'employee_statement': {
                'title': 'كشف حساب موظف',
                'class': EmployeeStatementPage,
                'icon': 'fa5s.file-invoice-dollar',
                'section': 'المالية العامة',
                'module': 'كشف حساب موظف'
            },
            
            # ====== الاختبارات ======
            'grades': {
                'title': 'رصد الدرجات',
                'class': GradesPage,
                'icon': 'fa5s.graduation-cap',
                'section': 'الاختبارات والنتائج',
                'module': 'رصد الدرجات'
            },
            'monthly_certificates': {
                'title': 'الشهادات الشهرية',
                'class': lambda user, year: CertificatesPage(user, year, "monthly", self.permission_service),
                'icon': 'fa5s.file-alt',
                'section': 'الاختبارات والنتائج',
                'module': 'الشهادات والأوائل'
            },
            'term_certificates': {
                'title': 'الشهادات الفصلية',
                'class': lambda user, year: CertificatesPage(user, year, "term", self.permission_service),
                'icon': 'fa5s.file-alt',
                'section': 'الاختبارات والنتائج',
                'module': 'الشهادات والأوائل'
            },
            'final_certificates': {
                'title': 'الشهادات النهائية',
                'class': lambda user, year: CertificatesPage(user, year, "final", self.permission_service),
                'icon': 'fa5s.file-alt',
                'section': 'الاختبارات والنتائج',
                'module': 'الشهادات والأوائل'
            },
            'top_students': {
                'title': 'كشوفات الأوائل',
                'class': TopStudentsPage,
                'icon': 'fa5s.trophy',
                'section': 'الاختبارات والنتائج',
                'module': 'الشهادات والأوائل'
            },
            
            # ====== المتابعة اليومية ======
            'attendance': {
                'title': 'الحضور والغياب',
                'class': AttendancePage,
                'icon': 'fa5s.clipboard-check',
                'section': 'المتابعة اليومية',
                'module': 'الحضور والغياب'
            },
            'homeworks': {
                'title': 'الواجبات المنزلية',
                'class': HomeworkPage,
                'icon': 'fa5s.tasks',
                'section': 'المتابعة اليومية',
                'module': 'الواجبات المنزلية'
            },
            'behavior': {
                'title': 'المتابعة السلوكية',
                'class': BehaviorPage,
                'icon': 'fa5s.comments',
                'section': 'المتابعة اليومية',
                'module': 'المتابعة السلوكية'
            },
            
            # ====== الجداول ======
            'weekly_schedule': {
                'title': 'الجدول الأسبوعي',
                'class': lambda user, year: SchedulesPage(user, year, "weekly", self.permission_service),
                'icon': 'fa5s.calendar-week',
                'section': 'الجداول الدراسية',
                'module': 'الجداول الدراسية'
            },
            'monthly_exams_schedule': {
                'title': 'امتحانات شهرية',
                'class': lambda user, year: SchedulesPage(user, year, "monthly_exam", self.permission_service),
                'icon': 'fa5s.calendar-check',
                'section': 'الجداول الدراسية',
                'module': 'الجداول الدراسية'
            },
            'final_exams_schedule': {
                'title': 'امتحانات نهائية',
                'class': lambda user, year: SchedulesPage(user, year, "final_exam", self.permission_service),
                'icon': 'fa5s.calendar-alt',
                'section': 'الجداول الدراسية',
                'module': 'الجداول الدراسية'
            },

            # ====== التقارير ======
            'reports': {
                'title': 'التقارير والإحصائيات',
                'class': ReportsPage,
                'icon': 'fa5s.chart-bar',
                'section': 'التقارير',
                'module': 'التقارير'
            },            
            
            # ====== الإدارة والإعدادات ======
            'users': {
                'title': 'المستخدمين',
                'class': UsersPage,
                'icon': 'fa5s.user-cog',
                'section': 'الإدارة والإعدادات',
                'module': 'المستخدمين'
            },
            'permissions': {
                'title': 'الصلاحيات',
                'class': PermissionsPage,
                'icon': 'fa5s.shield-alt',
                'section': 'الإدارة والإعدادات',
                'module': 'الصلاحيات'
            },
            'backup': {
                'title': 'النسخ الاحتياطي',
                'class': BackupPage,
                'icon': 'fa5s.database',
                'section': 'الإدارة والإعدادات',
                'module': 'الإعدادات'
            },
            'profile': {
                'title': 'الملف الشخصي',
                'class': ProfilePage,
                'icon': 'fa5s.user',
                'section': 'الإدارة والإعدادات',
                'module': 'الملف الشخصي'
            },
            'audit_log': {
                'title': 'سجل العمليات',
                'class': AuditLogPage,
                'icon': 'fa5s.history',
                'section': 'الإدارة والإعدادات',
                'module': 'الإعدادات'
            },
            'notifications': {
                'title': 'الإشعارات',
                'class': NotificationsPage,
                'icon': 'fa5s.bell',
                'section': 'الإدارة والإعدادات',
                'module': 'الإشعارات'
            },
            'import_export': {
                'title': 'استيراد وتصدير',
                'class': ImportExportPage,
                'icon': 'fa5s.exchange-alt',
                'section': 'الإدارة والإعدادات',
                'module': 'الإعدادات'
            },
            'print_archive': {
                'title': 'أرشيف المطبوعات',
                'class': PrintArchivePage,
                'icon': 'fa5s.print',
                'section': 'الإدارة والإعدادات',
                'module': 'الإعدادات'
            },
            'bulk_notifications': {
                'title': 'إشعارات جماعية',
                'class': BulkNotificationsPage,
                'icon': 'fa5s.paper-plane',
                'section': 'الإدارة والإعدادات',
                'module': 'الإشعارات'
            },
        }
    
    def run(self):
        """تشغيل التطبيق."""
        try:
            # 1. إعداد متتبع التغييرات
            ChangeTracker.setup_listeners()

            setup_audit_listeners()
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(config_manager.app_config.app_name)
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            
            font = QFont("Cairo", 12)
            self.app.setFont(font)
            
            icon = qta.icon('fa5s.school', color='#1976D3')
            self.app.setWindowIcon(icon)
            
            self._load_stylesheet()
            
            # ✅ 1. عرض شاشة البداية فوراً
            from app.views.splash_screen import SplashScreen
            self.splash = SplashScreen()
            self.splash.show()
            self.app.processEvents()
            
            # ✅ 2. إنشاء عامل التهيئة في الخلفية
            from app.services.init_worker import DatabaseInitWorker
            self.init_worker = DatabaseInitWorker()
            
            # ✅ 3. ربط الإشارات
            self.init_worker.status_changed.connect(self._on_init_status_changed)
            self.init_worker.finished.connect(self._on_init_finished)
            self.init_worker.failed.connect(self._on_init_failed)
            
            # ✅ 4. بدء التهيئة في الخلفية
            self.init_worker.start()
            
            self.app.aboutToQuit.connect(self._cleanup)
            
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"خطأ: {str(e)}")
            if self.app:
                QMessageBox.critical(None, "خطأ", str(e))
            return 1


    def _on_init_status_changed(self, message: str, progress: int):
        """✅ تحديث شاشة البداية عند تغيير الحالة."""
        if hasattr(self, 'splash') and self.splash:
            self.splash.set_status(message, progress)


    def _on_init_finished(self):
        """✅ عند اكتمال التهيئة بنجاح."""
        logger.info("تمت تهيئة قاعدة البيانات بنجاح")

        # ✅ v3: الآن DB جاهزة — احفظ/اقرأ هوية النسخة
        try:
            hostname = socket.gethostname()
            safe_hostname = hashlib.md5(
                hostname.encode('utf-8')
            ).hexdigest()[:8]

            from app.database.session import session_scope
            from app.database.models.sync import SyncMetadata

            with session_scope() as s:
                instance_id = SyncMetadata.get(s, "sync_instance_id")
                if not instance_id:
                    instance_id = (
                        f"local-{safe_hostname}-"
                        f"{str(uuid.uuid4())[:8]}"
                    )
                    SyncMetadata.set(s, "sync_instance_id", instance_id)
                    logger.info(f"🆕 هوية جديدة: {instance_id}")
                else:
                    logger.info(f"♻️ هوية موجودة: {instance_id}")

            # ✅ حدّث ChangeTracker بالهوية الثابتة
            from app.services.sync.change_tracker import ChangeTracker
            ChangeTracker.set_instance(instance_id, source='local')

        except Exception as e:
            logger.error(f"فشل ضبط هوية المزامنة: {e}", exc_info=True)
            # استخدم افتراضي مؤقت
            from app.services.sync.change_tracker import ChangeTracker
            ChangeTracker.set_instance("local-temp", source='local')

        # ✅ إغلاق شاشة البداية
        if hasattr(self, 'splash') and self.splash:
            self.splash.set_status("جاهز!", 100)
            QApplication.processEvents()
        
        # ✅ إنشاء وعرض نافذة تسجيل الدخول
        self.login_window = LoginWindow()
        self.login_window.login_successful = self._on_login_success
        
        if hasattr(self, 'splash') and self.splash:
            self.splash.finish(self.login_window)
            self.splash = None
        
        self.login_window.show()


    def _on_init_failed(self, error_message: str):
        """✅ عند فشل التهيئة."""
        logger.error(f"فشل تهيئة قاعدة البيانات: {error_message}")
        
        # ✅ إغلاق شاشة البداية
        if hasattr(self, 'splash') and self.splash:
            self.splash.close()
            self.splash = None
        
        # ✅ عرض رسالة الخطأ
        QMessageBox.critical(
            None,
            "خطأ في تهيئة قاعدة البيانات",
            f"فشل تشغيل التطبيق:\n\n{error_message}\n\n"
            "يرجى التحقق من:\n"
            "• إعدادات قاعدة البيانات في config.json\n"
            "• الاتصال بالخادم السحابي (إن كان مُفعّلاً)\n"
            "• تشغيل خدمة PostgreSQL"
        )
        
        # ✅ إغلاق التطبيق
        if self.app:
            self.app.quit()          
            

    def _initialize_database(self) -> bool:
        """
        تهيئة قاعدة البيانات حسب الوضع المختار.
        
        الأوضاع:
        - local: العمل على القاعدة المحلية فقط
        - cloud: العمل على القاعدة السحابية مباشرة
        - hybrid: محاولة السحابة أولاً، ثم العودة للمحلية عند الفشل
        """
        try:
            self.database_mode = config_manager.app_config.database_mode
            cloud_config = config_manager.database_config
            
            logger.info(f"وضع قاعدة البيانات: {self.database_mode}")
            
            if self.database_mode == "cloud":
                # ===== الوضع السحابي =====
                if not cloud_config.cloud_host:
                    logger.error("لم يتم تكوين الخادم السحابي في config.json")
                    QMessageBox.critical(
                        None,
                        "خطأ في الإعدادات",
                        "وضع قاعدة البيانات 'cloud' مُفعّل لكن لم يتم تكوين الخادم السحابي.\n\n"
                        "يرجى تحديث config.json بمعلومات الخادم السحابي أو تغيير الوضع إلى 'local'."
                    )
                    return False
                
                logger.info("محاولة الاتصال بالخادم السحابي...")
                try:
                    init_database(use_local=False)
                    self.is_using_cloud = True
                    logger.info("تم الاتصال بالخادم السحابي بنجاح")
                except Exception as e:
                    logger.error(f"فشل الاتصال بالخادم السحابي: {str(e)}")
                    QMessageBox.critical(
                        None,
                        "خطأ الاتصال بالسحابة",
                        f"فشل الاتصال بالخادم السحابي:\n{str(e)}\n\n"
                        "يرجى التحقق من الإعدادات واتصال الإنترنت."
                    )
                    return False
                
            elif self.database_mode == "hybrid":
                # ===== الوضع المختلط =====
                logger.info("الوضع المختلط: محاولة الاتصال بالسحابة أولاً...")
                
                cloud_available = False
                if cloud_config.cloud_host:
                    cloud_available = check_cloud_connection()
                
                if cloud_available:
                    logger.info("تم الاتصال بالخادم السحابي - العمل على السحابة")
                    init_database(use_local=False)
                    self.is_using_cloud = True
                else:
                    logger.warning("تعذر الاتصال بالسحابة - العودة إلى القاعدة المحلية")
                    init_database(use_local=True)
                    self.is_using_cloud = False
                
            else:  # local
                # ===== الوضع المحلي =====
                logger.info("الوضع المحلي: الاتصال بقاعدة البيانات المحلية")
                init_database(use_local=True)
                self.is_using_cloud = False
            
            # ===== فحص الاتصال =====
            if not db_manager.check_connection():
                logger.error("فشل فحص الاتصال")
                QMessageBox.critical(
                    None,
                    "خطأ في الاتصال",
                    "فشل الاتصال بقاعدة البيانات.\n\n"
                    "يرجى التحقق من إعدادات قاعدة البيانات."
                )
                return False
            
            # ===== إنشاء الجداول =====
            try:
                create_tables()
                logger.info("تم إنشاء/التحقق من الجداول")
            except Exception as e:
                logger.warning(f"تحذير في إنشاء الجداول: {str(e)}")
            
            # ===== عرض حالة الاتصال =====
            mode_text = "السحابة" if self.is_using_cloud else "المحلي"
            logger.info(f"تم تهيئة قاعدة البيانات بنجاح - الوضع: {mode_text}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")
            QMessageBox.critical(
                None,
                "خطأ",
                f"فشل تهيئة قاعدة البيانات:\n{str(e)}"
            )
            return False
    
    def _load_stylesheet(self):
        """تحميل النمط."""
        try:
            style_file = PROJECT_ROOT / "app" / "resources" / "styles" / "main_style.qss"
            if style_file.exists():
                with open(style_file, 'r', encoding='utf-8') as f:
                    self.app.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"فشل تحميل النمط: {str(e)}")
    
    def _load_user_permissions(self, user):
        """تحميل صلاحيات المستخدم (API أو Local)."""
        self.user_permissions = {}
        self.user_role_name = ""

        # ✅ إذا كانت الصلاحيات محمّلة من API
        if hasattr(user, 'permissions') and user.permissions:
            try:
                self.user_permissions = user.permissions
                self.user_role_name = getattr(user, 'role_name', '') or ''
                logger.info(
                    f"✅ صلاحيات من API للدور: {self.user_role_name} "
                    f"({len(self.user_permissions)} وحدة)"
                )
                return
            except Exception as e:
                logger.error(f"فشل تحميل صلاحيات API: {e}")

        # ✅ Local mode
        try:
            with session_scope() as session:
                role = session.get(Role, user.role_id) if user.role_id else None
                if role:
                    self.user_role_name = role.role_name

                    role_permissions = session.execute(
                        select(RolePermission, Permission)
                        .join(Permission, RolePermission.permission_id == Permission.id)
                        .where(RolePermission.role_id == role.id)
                    ).all()

                    for rp, perm in role_permissions:
                        self.user_permissions[perm.module_name] = {
                            'can_view': rp.can_view,
                            'can_add': rp.can_add,
                            'can_edit': rp.can_edit,
                            'can_delete': rp.can_delete,
                            'can_print': rp.can_print,
                            'can_cancel': rp.can_cancel,
                        }

                    logger.info(f"تم تحميل صلاحيات الدور: {role.role_name}")
        except Exception as e:
            logger.error(f"فشل تحميل الصلاحيات: {str(e)}")
            

    def _has_permission(self, module: str) -> bool:
        """التحقق من صلاحية المستخدم للوحدة."""
        if self.user_role_name == "مدير النظام":
            return True
        
        always_allowed = ['الملف الشخصي']
        if module in always_allowed:
            return True
        
        if module in self.user_permissions:
            return self.user_permissions[module].get('can_view', False)
        
        return False
    
    def _on_login_success(self, user: User, academic_year: AcademicYear):
        """عند نجاح تسجيل الدخول."""
        logger.info(f"تم تسجيل دخول: {user.username}")
        
        self.current_user = user
        self.current_academic_year = academic_year
        
        AuditService.set_current_user(user.id)
        
        # ✅ Audit فقط في وضع Local
        from app.core.config import config_manager
        if config_manager.app_config.api_mode == 'local':
            try:
                with session_scope() as session:
                    AuditService.log_login(
                        session, user.id,
                        device_name=os.getenv('COMPUTERNAME', 'Unknown')
                    )
            except Exception as e:
                logger.warning(f"فشل تسجيل الدخول: {str(e)}")

        self.permission_service = PermissionService(user)
        self._load_user_permissions(user)
        
        self.main_window = MainWindow(user, academic_year)
        # ✅ بدء خدمة المزامنة
        self._start_sync_service()

        # ربط الإشارات
        self.main_window.add_student_requested.connect(
            lambda: self._call_page_method('students', 'add_student')
        )
        self.main_window.add_parent_requested.connect(
            lambda: self._call_page_method('parents', 'add_parent')
        )
        self.main_window.add_employee_requested.connect(
            lambda: self._call_page_method('employees', 'add_employee')
        )
        self.main_window.add_receipt_requested.connect(
            lambda: self._call_page_method('receipts', 'add_receipt')
        )
        self.main_window.add_voucher_requested.connect(
            lambda: self._call_page_method('expenses', 'add_voucher')
        )
        self.main_window.add_allowance_requested.connect(
            lambda: self._call_page_method('allowances', 'add_allowance')
        )
        self.main_window.add_loan_requested.connect(
            lambda: self._call_page_method('loans', 'add_loan')
        )
        self.main_window.add_homework_requested.connect(
            lambda: self._call_page_method('homeworks', 'add_homework')
        )
        self.main_window.add_behavior_requested.connect(
            lambda: self._call_page_method('behavior', 'add_behavior')
        )
        self.main_window.logout_requested.connect(self._on_logout)

        self._update_sidebar_user_info()
        self._setup_sidebar()
        self._navigate_to('dashboard')
        
        # عرض مؤشر الاتصال في شريط الحالة
        self._update_connection_indicator()
        
        self.main_window.show()
        
        if self.login_window:
            self.login_window.close()
    
    def _update_connection_indicator(self):
        """تحديث مؤشر الاتصال في شريط الحالة."""
        if not self.main_window:
            return
        
        try:
            if hasattr(self.main_window, 'connection_indicator'):
                if self.is_using_cloud:
                    self.main_window.connection_indicator.setText("☁️ متصل بالسحابة")
                    self.main_window.connection_indicator.setStyleSheet(
                        "color: #10B981; font-weight: 600; font-size: 11px;"
                    )
                else:
                    self.main_window.connection_indicator.setText("💻 الوضع المحلي")
                    self.main_window.connection_indicator.setStyleSheet(
                        "color: #64748B; font-weight: 600; font-size: 11px;"
                    )
        except Exception as e:
            logger.debug(f"لا يمكن تحديث مؤشر الاتصال: {str(e)}")

    def _call_page_method(self, page_key: str, method_name: str, *args, **kwargs):
        """استدعاء دالة في صفحة معينة مع الانتقال إليها تلقائياً."""
        if not self.main_window:
            return
        
        self._navigate_to(page_key)
        
        page = self.pages.get(page_key)
        if not page:
            logger.warning(f"الصفحة غير موجودة: {page_key}")
            return
        
        if not hasattr(page, method_name):
            logger.warning(f"الدالة {method_name} غير موجودة في {page_key}")
            return
        
        try:
            method = getattr(page, method_name)
            method(*args, **kwargs)
        except Exception as e:
            logger.error(f"فشل استدعاء {method_name} في {page_key}: {str(e)}")
            QMessageBox.critical(
                self.main_window,
                "خطأ",
                f"فشل تنفيذ العملية:\n{str(e)}"
            )
    
    def _update_sidebar_user_info(self):
        """تحديث معلومات المستخدم في الشريط الجانبي."""
        if not self.main_window:
            return
        
        try:
            user_name = self.current_user.username
            try:
                if hasattr(self.current_user, 'employee') and self.current_user.employee:
                    if self.current_user.employee.full_name:
                        user_name = self.current_user.employee.full_name
            except Exception:
                pass

            # ✅ في وضع API، استخدم display_name مباشرة
            if user_name == self.current_user.username and hasattr(self.current_user, 'display_name'):
                user_name = self.current_user.display_name or user_name
            
            role_name = self.user_role_name or "مستخدم"
            
            sidebar = self.main_window.sidebar
            if hasattr(sidebar, 'user_widget'):
                labels = sidebar.user_widget.findChildren(QLabel)
                if len(labels) >= 2:
                    labels[0].setText(user_name)
                    labels[1].setText(role_name)
        except Exception as e:
            logger.error(f"فشل تحديث معلومات المستخدم: {str(e)}")
    
    def _setup_sidebar(self):
        """إعداد الشريط الجانبي مع فلترة الصلاحيات."""
        if not self.main_window:
            return
        
        sidebar = self.main_window.sidebar
        sidebar.buttons.clear()
        sidebar.sections.clear()
        
        while sidebar.scroll_layout.count() > 0:
            item = sidebar.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        section_icons = {
            "الرئيسية": "fa5s.home",
            "التهيئة الأكاديمية": "fa5s.cogs",
            "الطلاب وأولياء الأمور": "fa5s.user-graduate",
            "المالية للطلاب": "fa5s.money-bill",
            "الكادر التعليمي": "fa5s.chalkboard-teacher",
            "المالية العامة": "fa5s.wallet",
            "الاختبارات والنتائج": "fa5s.graduation-cap",
            "المتابعة اليومية": "fa5s.clipboard-check",
            "الجداول الدراسية": "fa5s.calendar-alt",
            "التقارير": "fa5s.chart-bar",
            "الإدارة والإعدادات": "fa5s.cog",
        }
        
        sections_order = [
            "الرئيسية",
            "التهيئة الأكاديمية",
            "الطلاب وأولياء الأمور",
            "المالية للطلاب",
            "الكادر التعليمي",
            "المالية العامة",
            "الاختبارات والنتائج",
            "المتابعة اليومية",
            "الجداول الدراسية",
            "التقارير",
            "الإدارة والإعدادات",
        ]
        
        for section_name in sections_order:
            section_pages = []
            for page_key, page_info in self.page_registry.items():
                if page_info['section'] == section_name:
                    if self._has_permission(page_info['module']):
                        section_pages.append((page_key, page_info))
            
            if not section_pages:
                continue
            
            section = sidebar.add_section(
                section_name,
                icon=section_icons.get(section_name, "fa5s.folder"),
                expanded=False
            )
            
            for page_key, page_info in section_pages:
                try:
                    btn = section.add_button(
                        page_info['title'],
                        page_info['icon']
                    )
                    sidebar.buttons[page_key] = btn
                    btn.clicked.connect(
                        lambda checked, key=page_key: self._navigate_to(key)
                    )
                except Exception as e:
                    logger.error(f"فشل إنشاء زر {page_key}: {str(e)}")
        
        sidebar.scroll_layout.addStretch()
        logger.info(f"تم إعداد الشريط الجانبي - الأزرار المعروضة: {len(sidebar.buttons)}")

    def _navigate_to(self, page_key: str):
        """الانتقال إلى صفحة."""
        if not self.main_window:
            return
        
        page_info = self.page_registry.get(page_key)
        if page_info:
            if not self._has_permission(page_info['module']):
                QMessageBox.warning(
                    self.main_window,
                    "صلاحيات غير كافية",
                    f"ليس لديك صلاحية للوصول إلى: {page_info['title']}"
                )
                return
        
        self.main_window.sidebar.set_active_button(page_key)
        
        if page_key not in self.pages:
            self._create_page(page_key)
        
        if page_key in self.pages:
            page = self.pages[page_key]
            
            if self.main_window.current_page:
                self.main_window.content_layout.removeWidget(self.main_window.current_page)
                self.main_window.current_page.hide()
            
            self.main_window.current_page = page
            self.main_window.content_layout.addWidget(page)
            page.show()
            
            logger.info(f"تم الانتقال إلى: {page_key}")
    
    def _create_page(self, page_key: str):
        """إنشاء صفحة."""
        page_info = self.page_registry.get(page_key)
        
        if not page_info:
            return
        
        try:
            page_class = page_info['class']

            if self.permission_service:
                try:
                    page = page_class(
                        self.current_user, 
                        self.current_academic_year,
                        permission_service=self.permission_service
                    )
                except TypeError:
                    page = page_class(self.current_user, self.current_academic_year)
            else:
                page = page_class(self.current_user, self.current_academic_year)
            
            self.pages[page_key] = page
            logger.info(f"تم إنشاء صفحة: {page_key}")

        except Exception as e:
            logger.error(f"فشل إنشاء صفحة {page_key}: {str(e)}")
            
            fallback = QWidget()
            fallback_layout = QVBoxLayout(fallback)
            label = QLabel(f"صفحة {page_info['title']}\n\nخطأ: {str(e)}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 14px; color: #EF4444;")
            fallback_layout.addWidget(label)
            self.pages[page_key] = fallback

    def _start_sync_service(self):
        """بدء خدمة المزامنة في الخلفية."""
        try:
            if not config_manager.app_config.sync_enabled:
                logger.info("خدمة المزامنة معطلة في الإعدادات")
                return
            
            self.sync_service = BackgroundSyncService(
                sync_interval=config_manager.app_config.sync_interval,
                health_check_interval=config_manager.app_config.sync_health_check_interval,
                enabled=True
            )
            self.sync_service.start()
            logger.info("✅ تم بدء خدمة المزامنة")
        except Exception as e:
            logger.error(f"فشل بدء المزامنة: {str(e)}")

    def _on_logout(self):
        """معالج تسجيل الخروج."""
        # ✅ إيقاف المزامنة
        if self.sync_service:
            self.sync_service.stop()
            self.sync_service = None

        logger.info(f"تسجيل خروج المستخدم: {self.current_user.username if self.current_user else 'Unknown'}")
        
        if self.current_user:
            try:
                with session_scope() as session:
                    AuditService.log_logout(
                        session, self.current_user.id,
                        device_name=os.getenv('COMPUTERNAME', 'Unknown')
                    )
            except Exception as e:
                logger.warning(f"فشل تسجيل الخروج: {str(e)}")
            
            AuditService.set_current_user(None)
        
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        self.pages.clear()
        self.current_user = None
        self.current_academic_year = None
        self.permission_service = None
        
        self.login_window = LoginWindow()
        self.login_window.login_successful = self._on_login_success
        self.login_window.show()            
    
    def _cleanup(self):
        """تنظيف عند الخروج."""
        # ✅ إيقاف المزامنة
        if self.sync_service:
            self.sync_service.stop()

        logger.info("إغلاق التطبيق...")
        
        if self.current_user:
            try:
                with session_scope() as session:
                    AuditService.log_logout(
                        session, self.current_user.id,
                        device_name=os.getenv('COMPUTERNAME', 'Unknown')
                    )
            except Exception as e:
                logger.warning(f"فشل تسجيل الخروج: {str(e)}")
            
            AuditService.set_current_user(None)
        
        close_database()


def main():
    """الدالة الرئيسية."""
    controller = ApplicationController()
    return controller.run()


if __name__ == "__main__":
    sys.exit(main())