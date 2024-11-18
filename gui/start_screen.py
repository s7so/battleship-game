# استيراد المكتبات الأساسية المطلوبة من PyQt6 للواجهة الرسومية
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QMessageBox, QMainWindow)  # لإنشاء النوافذ والأزرار والتخطيطات
from PyQt6.QtCore import Qt  # لخصائص وثوابت Qt الأساسية
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette  # للخطوط والأيقونات والألوان
from .instructions_screen import InstructionsScreen  # استيراد شاشة التعليمات
from .settings_screen import SettingsScreen  # استيراد شاشة الإعدادات

class StartScreen(QMainWindow):
    """
    شاشة البداية للعبة حرب السفن (Battleship)
    
    هذه الشاشة هي أول ما يراه المستخدم عند فتح اللعبة
    وتحتوي على:
    - زر لبدء لعبة جديدة
    - زر لعرض تعليمات اللعبة
    - زر لفتح الإعدادات
    - زر للخروج من اللعبة
    """
    def __init__(self, main_window):
        """
        دالة ال��داية التي تُنشئ شاشة البداية
        
        المدخلات:
            main_window: النافذة الرئيسية للعبة التي سيتم عرضها بعد الضغط على "لعبة جديدة"
        """
        super().__init__()  # استدعاء دالة البداية للفئة الأساسية
        self.main_window = main_window  # حفظ مرجع للنافذة الرئيسية
        self.instructions_window = None  # متغير لتخزين نافذة التعليمات (فارغ في البداية)
        self.settings_window = None  # متغير لتخزين نافذة الإعدادات (فارغ في البداية)
        self.init_ui()  # تهيئة واجهة المستخدم

    def init_ui(self):
        """
        تهيئة واجهة المستخدم وتصميمها
        تقوم بإنشاء كل العناصر المرئية وتنسيقها
        """
        # تعيين عنوان النافذة وحجمها الأدنى
        self.setWindowTitle("Battleship Game")
        self.setMinimumSize(800, 600)
        
        # تعيين التصميم العام للنافذة وعناصرها
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;  /* لون خلفية رمادي فاتح */
            }
            QLabel {
                color: #2c3e50;  /* لون النص أزرق داكن */
                padding: 20px;  /* مساحة داخلية حول النص */
            }
            QPushButton {
                background-color: #3498db;  /* لون خلفية الأزرار أزرق */
                color: white;  /* لون نص الأزرار أبيض */
                border: none;  /* بدون حدود */
                border-radius: 5px;  /* زوايا دائرية */
                padding: 10px;  /* مساحة داخلية */
                font-weight: bold;  /* خط عريض */
                min-width: 200px;  /* أقل عرض للزر */
                margin: 5px;  /* مساحة خارجية */
            }
            QPushButton:hover {
                background-color: #2980b9;  /* لون الزر عند تمرير الماوس */
            }
        """)
        
        # إنشاء العنصر المركزي الذي سيحتوي كل العناصر الأخرى
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # إنشاء تخطيط رأسي لترتيب العناصر من أعلى لأسفل
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(30)  # المسافة بين العناصر
        layout.setContentsMargins(50, 50, 50, 50)  # الهوامش من كل جانب

        # إنشاء وتنسيق عنوان اللعبة
        title = QLabel("BATTLESHIP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # توسيط العنوان
        title_font = QFont()
        title_font.setPointSize(36)  # حجم الخط
        title_font.setBold(True)  # جعل الخط عريض
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;  /* لون النص */
                background-color: rgba(255, 255, 255, 0.9);  /* خلفية شبه شفافة */
                border-radius: 10px;  /* زوايا دائرية */
            }
        """)
        layout.addWidget(title)

        # قائمة بالأزرار المطلوبة وخصائصها
        buttons_data = [
            ("New Game", self.start_new_game, "#2ecc71"),  # زر اللعبة الجديدة - أخضر
            ("Instructions", self.show_instructions, "#3498db"),  # زر التعليمات - أزرق
            ("Settings", self.show_settings, "#e67e22"),  # زر الإعدادات - برتقالي
            ("Exit", self.close_game, "#e74c3c")  # زر الخروج - أحمر
        ]

        # إنشاء الأزرار وتنسيقها
        for text, handler, color in buttons_data:
            btn = QPushButton(text)  # إنشاء زر جديد
            btn.setMinimumSize(300, 60)  # تعيين الحجم الأدنى
            btn.clicked.connect(handler)  # ربط الزر بالدالة المناسبة
            btn.setFont(QFont("Arial", 14))  # تعيين الخط وحجمه
            # تنسيق الزر باستخدام دالة مساعدة لتجنب التكرار
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};  /* لون خلفية الزر */
                    color: white;  /* لون النص أبيض */
                    border: none;  /* بدون حدود */
                    border-radius: 10px;  /* زوايا دائرية */
                    padding: 10px;  /* مساحة داخلية */
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};  /* لون الزر عند تمرير الماوس */
                }}
            """)
            # إضافة الزر للتخطيط مع توسيطه
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # إضافة مساحة فارغة في النهاية
        layout.addStretch()

    def start_new_game(self):
        """
        تبدأ لعبة جديدة عند الضغط على زر New Game
        - تخفي شاشة البداية
        - تظهر النافذة الرئيسية
        - تبدأ لعبة جديدة
        """
        self.hide()  # إخفاء شاشة البداية
        self.main_window.show()  # إظهار النافذة الرئيسية
        self.main_window.start_new_game()  # بدء لعبة جديدة

    def show_instructions(self):
        """
        تعرض شاشة التعليمات في نافذة منفصلة
        تنشئ نافذة جديدة إذا لم تكن موجودة
        """
        if not self.instructions_window:  # إذا لم تكن نافذة التعليمات موجودة
            self.instructions_window = InstructionsScreen()  # إنشاء نافذة جديدة
            # جعل النافذة مستقلة
            self.instructions_window.setWindowFlags(Qt.WindowType.Window)
            # تعيين عنوان وحجم النافذة
            self.instructions_window.setWindowTitle("Game Instructions")
            self.instructions_window.resize(800, 600)
        self.instructions_window.show()  # إظهار النافذة
        self.instructions_window.raise_()  # رفع النافذة للمقدمة

    def show_settings(self):
        """
        تعرض شاشة الإعدادات في نافذة منفصلة
        تتحقق أولاً من تسجيل دخول اللاعب
        """
        if not self.settings_window:  # إذا لم تكن نافذة الإعدادات موجودة
            # التحقق من تسجيل دخول اللاعب
            if not self.main_window.game_controller.current_player_id:
                QMessageBox.warning(self, "Error", "No player is currently logged in.")
                return
            # تجهيز الإعدادات الحالية
            current_settings = {
                'grid_size': self.main_window.game_controller.grid_size
            }
            # إنشاء نافذة الإعدادات
            self.settings_window = SettingsScreen(
                current_settings, 
                current_player_id=self.main_window.game_controller.current_player_id,
                db_manager=self.main_window.game_controller.db_manager
            )
            self.settings_window.setWindowFlags(Qt.WindowType.Window)
            self.settings_window.setWindowTitle("Game Settings")
            self.settings_window.resize(500, 400)
            # ربط إشارة تغيير الإعدادات بدالة تطبيق الإعدادات
            self.settings_window.settings_changed.connect(self.apply_settings)
        self.settings_window.show()  # إظهار النافذة
        self.settings_window.raise_()  # رفع النافذة للمقدمة

    def apply_settings(self, new_settings):
        """
        تطبيق الإعدادات الجديدة التي اختارها المستخدم
        وعرض رسالة تأكيد
        """
        self.main_window.game_controller.update_settings(new_settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")

    def close_game(self):
        """
        إغلاق اللعبة بعد تأكيد المستخدم
        تغلق جميع النوافذ المفتوحة
        """
        # عرض مربع حوار للتأكيد
        reply = QMessageBox.question(
            self, 'Exit Game',
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # إغلاق جميع النوافذ المفتوحة
            if self.instructions_window:
                self.instructions_window.close()
            if self.settings_window:
                self.settings_window.close()
            if self.main_window:
                self.main_window.close()
            self.close()

    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """
        دالة مساعدة لتعتيم لون معين بنسبة محددة
        """
        # تحويل اللون من صيغة hex إلى RGB
        color = color.lstrip('#')
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        
        # تعتيم كل قناة لون بضربها في معامل التعتيم
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # إرجاع اللون بصيغة hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def closeEvent(self, event):
        """
        معالجة حدث إغلاق النافذة
        تعرض مربع حوار للتأكيد قبل الإغلاق
        """
        try:
            # عرض مربع حوار للتأكيد
            reply = QMessageBox.question(
                self, 'Exit Game',
                'Are you sure you want to exit the game?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # إغلاق جميع النوافذ المفتوحة
                if self.instructions_window:
                    self.instructions_window.close()
                if self.settings_window:
                    self.settings_window.close()
                if self.main_window:
                    self.main_window.close()
                    
                event.accept()  # قبول حدث الإغلاق
            else:
                event.ignore()  # تجاهل حدث الإغلاق
        except Exception as e:
            # في حالة حدوث خطأ، طباعة رسالة الخطأ وإغلاق النافذة
            print(f"Error during window closure: {e}")
            event.accept()