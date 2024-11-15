import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.start_screen import StartScreen
from gui.login_screen import LoginScreen
from game.game_controller import GameController
from database.db_manager import DatabaseManager


class BattleshipGame:
    """
    الفئة الرئيسية للعبة Battleship
    مسؤولة عن تهيئة وربط جميع مكونات اللعبة
    """
    
    def __init__(self):
        """
        تهيئة مكونات اللعبة الأساسية:
        - تطبيق PyQt
        - مدير قاعدة البيانات
        - متحكم اللعبة
        - النافذة الرئيسية
        - شاشة البداية
        """
        # إنشاء تطبيق PyQt
        self.app = QApplication(sys.argv)
        
        # إنشاء مدير قاعدة البيانات
        self.db_manager = DatabaseManager()
        
        # إنشاء متحكم اللعبة
        self.game_controller = GameController(self.db_manager)
        
        # إنشاء النافذة الرئيسية
        self.main_window = MainWindow(self.game_controller)
        self.game_controller.set_main_window(self.main_window)
        
        # إنشاء شاشة البداية
        self.start_screen = StartScreen(self.main_window)
        
        # إنشاء شاشة تسجيل الدخول
        self.login_screen = LoginScreen(self.db_manager)
        self.login_screen.login_successful.connect(self.on_login_success)

    def run(self):
        """تشغيل اللعبة"""
        # عرض شاشة تسجيل الدخول أولاً
        self.login_screen.show()
        return self.app.exec()

    def on_login_success(self, player_data):
        """معالجة نجاح تسجيل الدخول"""
        # تخزين معلومات اللاعب في وحدة التحكم
        self.game_controller.current_player_id = player_data['id']
        self.game_controller.current_player_name = player_data['name']
        
        # تحديث الإحصائيات
        self.game_controller.stats.update({
            'games_played': player_data.get('games_played', 0),
            'games_won': player_data.get('games_won', 0),
            'total_shots': player_data.get('total_shots', 0),
            'hits': player_data.get('total_hits', 0)
        })
        
        # عرض شاشة البداية
        self.start_screen.show()


# نقطة دخول البرنامج
if __name__ == "__main__":
    # إنشاء كائن اللعبة
    game = BattleshipGame()
    
    # تشغيل اللعبة والخروج بالكود المناسب
    sys.exit(game.run())
