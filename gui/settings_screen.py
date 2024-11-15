from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QComboBox, QHBoxLayout, QMessageBox, QTabWidget,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.constants import GRID_SIZES

class SettingsScreen(QWidget):
    """شاشة الإعدادات والإحصائيات"""
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings: dict, db_manager=None, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        self.setWindowTitle("Game Settings & Statistics")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # إنشاء مجموعة تبويبات
        tabs = QTabWidget()
        
        # تبويب الإعدادات
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        # تبويب الإحصائيات
        stats_tab = self._create_stats_tab()
        tabs.addTab(stats_tab, "Statistics")
        
        # تبويب لوحة المتصدرين
        leaderboard_tab = self._create_leaderboard_tab()
        tabs.addTab(leaderboard_tab, "Leaderboard")
        
        # تبويب الإنجازات
        achievements_tab = self._create_achievements_tab()
        tabs.addTab(achievements_tab, "Achievements")
        
        layout.addWidget(tabs)
        
    def _create_settings_tab(self) -> QWidget:
        """إنشاء تبويب الإعدادات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات حجم الشبكة
        grid_size_layout = QHBoxLayout()
        grid_size_label = QLabel("Grid Size:")
        self.grid_size_combo = QComboBox()
        for size in GRID_SIZES:
            self.grid_size_combo.addItem(f"{size}x{size}")
        current_index = GRID_SIZES.index(self.current_settings['grid_size'])
        self.grid_size_combo.setCurrentIndex(current_index)
        
        grid_size_layout.addWidget(grid_size_label)
        grid_size_layout.addWidget(self.grid_size_combo)
        layout.addLayout(grid_size_layout)
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        return tab
        
    def _create_stats_tab(self) -> QWidget:
        """إنشاء تبويب الإحصائيات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager and hasattr(self.db_manager, 'current_player_id'):
            stats = self.db_manager.get_player_statistics(self.db_manager.current_player_id)
            
            if any(stats.values()):  # التحقق من وجود إحصائيات
                # عرض الإحصائيات في جدول
                stats_table = QTableWidget()
                stats_table.setColumnCount(2)
                stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
                
                stats_data = [
                    ("Games Played", stats.get('games_played', 0)),
                    ("Games Won", stats.get('games_won', 0)),
                    ("Win Rate", f"{stats.get('win_rate', 0):.1f}%"),
                    ("Total Shots", stats.get('total_shots', 0)),
                    ("Total Hits", stats.get('total_hits', 0)),
                    ("Accuracy", f"{stats.get('accuracy_rate', 0):.1f}%"),
                    ("Best Game", stats.get('best_game', 'N/A')),
                    ("Quick Wins", stats.get('quick_wins', 0))
                ]
                
                stats_table.setRowCount(len(stats_data))
                for i, (stat, value) in enumerate(stats_data):
                    stats_table.setItem(i, 0, QTableWidgetItem(stat))
                    stats_table.setItem(i, 1, QTableWidgetItem(str(value)))
                
                layout.addWidget(stats_table)
            else:
                # رسالة في حالة عدم وجود إحصائيات
                no_stats_label = QLabel("You haven't played any games yet!\nPlay some games to see your statistics here.")
                no_stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_stats_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        padding: 20px;
                    }
                """)
                layout.addWidget(no_stats_label)
        else:
            layout.addWidget(QLabel("Please log in to view statistics"))
        
        return tab
        
    def _create_leaderboard_tab(self) -> QWidget:
        """إنشاء تبويب لوحة المتصدرين"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager:
            # جلب البيانات
            leaderboard = self.db_manager.get_leaderboard(limit=10)
            
            if leaderboard:  # التحقق من وجود بيانات
                # إضافة فلتر الفترة الزمنية
                time_filter = QComboBox()
                time_filter.addItems(["All Time", "This Week", "This Month", "This Year"])
                layout.addWidget(time_filter)
                
                # جدول المتصدرين
                leaderboard_table = QTableWidget()
                leaderboard_table.setColumnCount(5)
                leaderboard_table.setHorizontalHeaderLabels([
                    "Rank", "Player", "Win Rate", "Games Won", "Accuracy"
                ])
                
                leaderboard_table.setRowCount(len(leaderboard))
                for i, player in enumerate(leaderboard):
                    leaderboard_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    leaderboard_table.setItem(i, 1, QTableWidgetItem(player['name']))
                    leaderboard_table.setItem(i, 2, QTableWidgetItem(f"{player['win_ratio']:.1f}%"))
                    leaderboard_table.setItem(i, 3, QTableWidgetItem(str(player['games_won'])))
                    leaderboard_table.setItem(i, 4, QTableWidgetItem(f"{player['accuracy']:.1f}%"))
                
                layout.addWidget(leaderboard_table)
            else:
                # رسالة في حالة عدم وجود بيانات
                no_data_label = QLabel("No players on the leaderboard yet!\nBe the first to make history!")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_data_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        padding: 20px;
                    }
                """)
                layout.addWidget(no_data_label)
        else:
            layout.addWidget(QLabel("Leaderboard unavailable"))
        
        return tab
        
    def _create_achievements_tab(self) -> QWidget:
        """إنشاء تبويب الإنجازات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager and hasattr(self.db_manager, 'current_player_id'):
            achievements = self.db_manager.get_player_achievements(self.db_manager.current_player_id)
            
            if achievements:  # التحقق من وجود إنجازات
                for achievement in achievements:
                    achievement_widget = QWidget()
                    achievement_layout = QHBoxLayout(achievement_widget)
                    
                    icon = QLabel(achievement['icon'])
                    title = QLabel(achievement['title'])
                    description = QLabel(achievement['description'])
                    
                    achievement_layout.addWidget(icon)
                    achievement_layout.addWidget(title)
                    achievement_layout.addWidget(description)
                    
                    layout.addWidget(achievement_widget)
            else:
                # رسالة في حالة عدم وجود إنجازات
                no_achievements_label = QLabel("""
                    No achievements unlocked yet!
                    
                    Keep playing to earn achievements:
                    • Win games
                    • Improve your accuracy
                    • Complete special challenges
                    
                    Your achievements will appear here.
                """)
                no_achievements_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_achievements_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        padding: 20px;
                    }
                """)
                layout.addWidget(no_achievements_label)
        else:
            layout.addWidget(QLabel("Please log in to view achievements"))
        
        return tab
        
    def save_settings(self):
        """حفظ الإعدادات مع التأكيد"""
        grid_size = int(self.grid_size_combo.currentText().split('x')[0])
        
        # التحقق من تغيير الحجم
        if grid_size != self.current_settings['grid_size']:
            reply = QMessageBox.question(
                self,
                'Confirm Changes',
                'Changing grid size will start a new game. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        new_settings = {
            'grid_size': grid_size
        }
        
        self.settings_changed.emit(new_settings)
        self.close()