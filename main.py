# أول حاجة بنعملها هي استيراد بعض الحاجات اللي هنحتاجها في البرنامج
import sys  # ده بيساعدنا نتعامل مع النظام اللي شغال عليه البرنامج
from PyQt6.QtWidgets import QApplication  # ده جزء من مكتبة PyQt6 اللي بنستخدمها عشان نعمل واجهة رسومية
from gui.main_window import MainWindow  # بنستورد النافذة الرئيسية من ملف اسمه main_window
from gui.start_screen import StartScreen  # بنستورد شاشة البداية من ملف اسمه start_screen
from gui.login_screen import LoginScreen  # بنستورد شاشة تسجيل الدخول من ملف اسمه login_screen
from game.game_controller import GameController  # بنستورد متحكم اللعبة من ملف اسمه game_controller
from database.db_manager import DatabaseManager  # بنستورد مدير قاعدة البيانات من ملف اسمه db_manager

# هنا بنعرف فئة اسمها BattleshipGame
class BattleshipGame:
    """
    الفئة دي هي المسؤولة عن تشغيل اللعبة وربط كل الأجزاء ببعضها
    """
    
    def __init__(self):
        """
        دي دالة البداية اللي بتشتغل أول ما نعمل كائن من الفئة دي
        """
        # بنعمل تطبيق PyQt اللي هو الأساس اللي هنشتغل عليه
        self.app = QApplication(sys.argv)
        
        # بنعمل مدير لقاعدة البيانات عشان نخزن البيانات ونجيبها
        self.db_manager = DatabaseManager()
        
        # بنعمل متحكم للعبة عشان يدير اللعبة
        self.game_controller = GameController(self.db_manager)
        
        # بنعمل النافذة الرئيسية اللي هتظهر فيها اللعبة
        self.main_window = MainWindow(self.game_controller)
        self.game_controller.set_main_window(self.main_window)
        
        # بنعمل شاشة البداية اللي هتظهر أول ما اللعبة تشتغل
        self.start_screen = StartScreen(self.main_window)
        
        # بنعمل شاشة تسجيل الدخول عشان اللاعب يدخل بياناته
        self.login_screen = LoginScreen(self.db_manager)
        self.login_screen.login_successful.connect(self.on_login_success)

    def run(self):
        """دي دالة بتشغل اللعبة"""
        # بنعرض شاشة تسجيل الدخول الأول
        self.login_screen.show()
        return self.app.exec()

    def on_login_success(self, player_data):
        """دي دالة بتتعامل مع نجاح تسجيل الدخول"""
        # بنخزن معلومات اللاعب في متحكم اللعبة
        self.game_controller.current_player_id = player_data['id']
        self.game_controller.current_player_name = player_data['name']
        
        # بنحدث الإحصائيات بتاعت اللاعب
        self.game_controller.stats.update({
            'games_played': player_data.get('games_played', 0),
            'games_won': player_data.get('games_won', 0),
            'total_shots': player_data.get('total_shots', 0),
            'hits': player_data.get('total_hits', 0)
        })
        
        # بنعرض شاشة البداية بعد تسجيل الدخول
        self.start_screen.show()


# هنا بنحدد نقطة البداية للبرنامج
if __name__ == "__main__":
    # بنعمل كائن من الفئة BattleshipGame
    game = BattleshipGame()
    
    # بنشغل اللعبة ونخرج بالكود المناسب
    sys.exit(game.run())
