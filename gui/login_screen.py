from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

class LoginScreen(QWidget):
    """شاشة تسجيل الدخول للاعب"""
    # إشارة لإرسال معلومات اللاعب بعد تسجيل الدخول
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        self.setWindowTitle("Battleship Login")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # عنوان الشاشة
        title = QLabel("Welcome to Battleship")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # حقل إدخال اسم اللاعب
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Arial", 12))
        # تفعيل الاستجابة لضغط Enter
        self.name_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.name_input)
        
        # أزرار تسجيل الدخول
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setFont(QFont("Arial", 12))
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
        """معالجة تسجيل دخول اللاعب"""
        player_name = self.name_input.text().strip()
        
        # التحقق من صحة الاسم
        if not player_name:
            QMessageBox.warning(self, "Error", "Please enter your name")
            return
        
        if len(player_name) < 3:
            QMessageBox.warning(self, "Error", "Name must be at least 3 characters long")
            return
        
        if len(player_name) > 20:
            QMessageBox.warning(self, "Error", "Name must be less than 20 characters")
            return
        
        # التحقق من الأحرف المسموح بها
        if not player_name.replace(' ', '').isalnum():
            QMessageBox.warning(self, "Error", "Name can only contain letters, numbers and spaces")
            return
        
        try:
            # البحث عن اللاعب في قاعدة البيانات
            existing_player = self.db_manager.find_player_by_name(player_name)
            
            if existing_player:
                # لاعب موجود - عرض إحصائياته وترحيب العودة
                stats = self.db_manager.get_player_statistics(existing_player['id'])
                # حساب نسبة الفوز
                win_rate = (stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
                # حساب الدقة
                accuracy = (stats['total_hits'] / stats['total_shots'] * 100) if stats['total_shots'] > 0 else 0
                
                welcome_message = f"""
                Welcome back {existing_player['name']}!

                Your Statistics:
                ---------------
                Games Played: {stats['games_played']}
                Games Won: {stats['games_won']}
                Win Rate: {win_rate:.1f}%
                
                Total Shots: {stats['total_shots']}
                Total Hits: {stats['total_hits']}
                Accuracy: {accuracy:.1f}%
                
                Best Game: {stats['best_game'] if stats['best_game'] else 'N/A'} moves
                """
                
                QMessageBox.information(
                    self, 
                    "Welcome Back", 
                    welcome_message
                )
                self.login_successful.emit(existing_player)
                self.hide()
            else:
                # لاعب جديد - إنشاء حساب جديد
                try:
                    player_id = self.db_manager.create_player(player_name)
                    if player_id:
                        print(f"New player created with ID: {player_id}")  # للتأكد من الإنشاء
                        new_player = self.db_manager.get_player(player_id)
                        if new_player:
                            print(f"Player data retrieved: {new_player}")  # للتأكد من البيانات
                            self.login_successful.emit(new_player)
                            self.hide()
                        else:
                            raise Exception("Could not retrieve new player data")
                    else:
                        raise Exception("Failed to create new player")
                except Exception as e:
                    print(f"Error creating new player: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to create new player: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")
            
    def _get_or_create_player(self, name: str) -> int:
        """البحث عن اللاعب أو إنشاء لاعب جديد"""
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
            Welcome back {player['name']}!

            Your Statistics:
            ---------------
            Games Played: {stats['games_played']}
            Games Won: {stats['games_won']}
            Win Rate: {win_rate:.1f}%
            
            Total Shots: {stats['total_shots']}
            Total Hits: {stats['total_hits']}
            Accuracy: {accuracy:.1f}%
            
            Best Game: {stats['best_game'] if stats['best_game'] else 'N/A'} moves
            """
            
            QMessageBox.information(
                self, 
                "Welcome Back", 
                welcome_message
            )
            return player['id']
        else:
            # إنشاء لاعب جديد
            player_id = self.db_manager.create_player(name)
            QMessageBox.information(
                self, 
                "Welcome", 
                f"Welcome {name}! Good luck in your first game!"
            )
            return player_id 