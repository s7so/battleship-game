"""
شاشة تسجيل الدخول للعبة السفن الحربية
=====================================

هذا الملف يحتوي على كود شاشة تسجيل الدخول للعبة. سأشرح لك كيف يعمل بالتفصيل:

1. المكتبات المستخدمة
--------------------
- PyQt6: مكتبة لإنشاء واجهات المستخدم الرسومية
- نستورد منها:
  * QWidget: النافذة الأساسية
  * QVBoxLayout: لترتيب العناصر بشكل عمودي 
  * QPushButton: لإنشاء الأزرار
  * QLabel: لعرض النصوص
  * QLineEdit: لإدخال النص
  * QMessageBox: لعرض الرسائل المنبثقة

2. الفئة الرئيسية (LoginScreen)
-----------------------------
- تمتد من QWidget لإنشاء نافذة
- تحتوي على:
  * حقل لإدخال اسم اللاعب
  * زر لتسجيل الدخول
  * رسائل ترحيب وتنبيهات

3. الدوال الرئيسية
-----------------
- __init__: تهيئة النافذة وربطها بقاعدة البيانات
- init_ui: إنشاء وتنسيق عناصر الواجهة
- handle_login: معالجة عملية تسجيل الدخول
- _get_or_create_player: البحث عن لاعب أو إنشاء حساب جديد

4. كيف يعمل البرنامج
------------------
أ. عند فتح النافذة:
   - يظهر حقل لإدخال الاسم
   - زر لتسجيل الدخول

ب. عند إدخال الاسم:
   - يتحقق من صحة الاسم (3-20 حرف، أحرف وأرقام فقط)
   - يبحث عن اللاعب في قاعدة البيانات

ج. إذا كان اللاعب موجوداً:
   - يعرض إحصائياته (عدد الألعاب، نسبة الفوز، الدقة)
   - يرحب به مجدداً

د. إذا كان لاعباً جديداً:
   - ينشئ حساب جديد
   - يرحب به في اللعبة

5. ملاحظات مهمة
-------------
- تأكد من تثبيت مكتبة PyQt6
- تحتاج لوجود قاعدة بيانات متصلة
- يمكنك تعديل رسائل الترحيب والتنبيهات حسب الحاجة
"""

from PyQt6.QtWidgets import (
    QWidget,        # الفئة الأساسية للنوافذ
    QVBoxLayout,    # تخطيط عمودي للعناصر
    QPushButton,    # زر
    QLabel,         # نص ثابت
    QLineEdit,      # حقل إدخال النص
    QMessageBox     # نافذة الرسائل
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

class LoginScreen(QWidget):
    """
    شاشة تسجيل الدخول
    -----------------
    تتيح للاعب:
    - إدخال اسمه
    - تسجيل الدخول
    - عرض إحصائياته السابقة
    """
    # إشارة لإرسال معلومات اللاعب بعد تسجيل الدخول
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager, parent=None):
        """
        تهيئة شاشة تسجيل الدخول
        
        المعاملات:
            db_manager: مدير قاعدة البيانات
            parent: النافذة الأم (اختياري)
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """
        تهيئة عناصر واجهة المستخدم
        ---------------------------
        يقوم بإنشاء:
        1. عنوان الشاشة
        2. حقل إدخال الاسم مع تلميحات
        3. زر تسجيل الدخول مع تلميحات
        4. تنسيق الشاشة
        """
        # إعداد النافذة
        self.setWindowTitle("Battleship Login")
        self.setMinimumSize(400, 300)
        
        # إنشاء تخطيط عمودي
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # المسافة بين العناصر
        layout.setContentsMargins(40, 40, 40, 40)  # الهوامش
        
        # إضافة العنوان
        title = QLabel("Welcome to Battleship")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # حقل إدخال اسم اللاعب مع تلميحات لتحسين تجربة المستخدم
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Arial", 12))
        self.name_input.setToolTip("Please enter a unique name (3-20 characters, letters and numbers only)")
        # تفعيل الاستجابة لضغط Enter
        self.name_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.name_input)
        
        # أزرار تسجيل الدخول مع تلميحات
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setFont(QFont("Arial", 12))
        login_btn.setToolTip("Click to login with the entered name")
        layout.addWidget(login_btn)
        
        # تنسيق الشاشة
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
    def handle_login(self):
        """
        معالجة تسجيل دخول اللاعب
        ------------------------
        1. يتحقق من صحة الاسم المدخل
        2. يستخدم _get_or_create_player للتعامل مع اللاعب
        3. يكمل عملية تسجيل الدخول مع رسائل أوضح
        """
        player_name = self.name_input.text().strip()
        
        # التحقق من صحة الاسم مع رسائل أكثر وضوحًا
        if not player_name:
            QMessageBox.warning(self, "Invalid Input", "Name field cannot be empty. Please enter your name to continue.")
            self.name_input.setFocus()
            return
        
        if len(player_name) < 3:
            QMessageBox.warning(self, "Invalid Input", "Name must be at least 3 characters long. Please enter a longer name.")
            self.name_input.setFocus()
            return
        
        if len(player_name) > 20:
            QMessageBox.warning(self, "Invalid Input", "Name must be less than 20 characters. Please enter a shorter name.")
            self.name_input.setFocus()
            return
        
        # التحقق من الأحرف المسموح بها مع رسالة توضيحية
        if not player_name.replace(' ', '').isalnum():
            QMessageBox.warning(self, "Invalid Characters", "Name can only contain letters, numbers, and spaces. Please correct your name.")
            self.name_input.setFocus()
            return
        
        try:
            # استخدام _get_or_create_player للتعامل مع اللاعب
            player_id = self._get_or_create_player(player_name)
            
            # الحصول على بيانات اللاعب وإكمال تسجيل الدخول
            player = self.db_manager.get_player(player_id)
            if player:
                self.login_successful.emit(player)
                self.hide()
                QMessageBox.information(
                    self, 
                    "Login Successful", 
                    f"Welcome, {player['name']}! You have successfully logged in."
                )
            else:
                raise Exception("Could not retrieve player data. Please try again.")
                
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", f"An error occurred during login: {str(e)}\nPlease try again.")
            self.name_input.setFocus()
            
    def _get_or_create_player(self, name: str) -> int:
        """
        البحث عن اللاعب أو إنشاء لاعب جديد
        ----------------------------------
        المعاملات:
            name: اسم اللاعب
            
        يقوم بـ:
        1. البحث عن اللاعب في قاعدة البيانات
        2. إذا وجد: يعرض إحصائياته
        3. إذا لم يجد: ينشئ حساب جديد
        
        يعيد:
            معرف اللاعب (ID)
        """
        # البحث عن اللاعب بالاسم
        player = self.db_manager.find_player_by_name(name)
        
        if player:
            # إذا وجد اللاعب، نجلب إحصائياته ونعرض رسالة ترحيب
            stats = self.db_manager.get_player_statistics(player['id'])
            
            # حساب نسبة الفوز
            win_rate = (stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
            # حساب الدقة
            accuracy = (stats['total_hits'] / stats['total_shots'] * 100) if stats['total_shots'] > 0 else 0
            
            welcome_message = f"""
            🎉 Welcome back, {player['name']}! 🎉

            📊 **Your Statistics:**
            -----------------------
            - **Games Played:** {stats['games_played']}
            - **Games Won:** {stats['games_won']}
            - **Win Rate:** {win_rate:.1f}%
            - **Total Shots:** {stats['total_shots']}
            - **Total Hits:** {stats['total_hits']}
            - **Accuracy:** {accuracy:.1f}%
            - **Best Game:** {stats['best_game'] if stats['best_game'] else 'N/A'} moves
            
            Keep up the great work and aim for higher stats!
            """
            
            QMessageBox.information(
                self, 
                "Welcome Back", 
                welcome_message
            )
            return player['id']
        else:
            # إنشاء لاعب جديد مع رسالة ترحيبية أوضح
            player_id = self.db_manager.create_player(name)
            QMessageBox.information(
                self, 
                "Welcome to Battleship", 
                f"🎉 Welcome, {name}! 🎉\nYour account has been created successfully.\nGood luck in your first game!"
            )
            return player_id 