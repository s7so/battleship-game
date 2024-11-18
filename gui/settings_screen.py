# استيراد المكتبات اللازمة من PyQt6 للواجهة الرسومية
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QComboBox, QHBoxLayout, QMessageBox, QTabWidget,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.constants import GRID_SIZES

class SettingsScreen(QWidget):
    """
    شاشة الإعدادات والإحصائيات
    
    هذه الشاشة تعرض:
    - إعدادات اللعبة مثل حجم الشبكة
    - إحصائيات اللاعب مثل عدد المباريات والانتصارات
    - قائمة المتصدرين
    - الإنجازات التي حققها اللاعب
    """
    
    # إشارة تنبه باقي البرنامج عند تغيير الإعدادات
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings: dict, current_player_id: int, db_manager=None, parent=None):
        """
        تهيئة شاشة الإعدادات
        
        المعاملات:
        - current_settings: الإعدادات الحالية للعبة
        - current_player_id: رقم تعريف اللاعب الحالي
        - db_manager: مدير قاعدة البيانات للوصول للبيانات
        - parent: النافذة الأم التي تحتوي هذه الشاشة
        """
        super().__init__(parent)
        self.current_settings = current_settings
        self.current_player_id = current_player_id
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """
        إنشاء واجهة المستخدم الرئيسية
        تحتوي على تبويبات للإعدادات والإحصائيات وقائمة المتصدرين والإنجازات
        """
        # تعيين عنوان النافذة وحجمها الأدنى
        self.setWindowTitle("Game Settings & Statistics")
        self.setMinimumSize(800, 600)
        
        # إنشاء تخطيط رأسي للنافذة
        layout = QVBoxLayout(self)
        
        # إنشاء مجموعة تبويبات
        tabs = QTabWidget()
        
        # إضافة التبويبات المختلفة
        settings_tab = self._create_settings_tab()  # تبويب الإعدادات
        tabs.addTab(settings_tab, "Settings")
        
        stats_tab = self._create_stats_tab()  # تبويب الإحصائيات
        tabs.addTab(stats_tab, "Statistics")
        
        leaderboard_tab = self._create_leaderboard_tab()  # تبويب المتصدرين
        tabs.addTab(leaderboard_tab, "Leaderboard")
        
        achievements_tab = self._create_achievements_tab()  # تبويب الإنجازات
        tabs.addTab(achievements_tab, "Achievements")
        
        # إضافة التبويبات للنافذة
        layout.addWidget(tabs)
        
    def _create_settings_tab(self) -> QWidget:
        """
        إنشاء تبويب الإعدادات
        يحتوي على:
        - اختيار حجم شبكة اللعب
        - أزرار الحفظ والإلغاء
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إنشاء قسم اختيار حجم الشبكة
        grid_size_layout = QHBoxLayout()
        grid_size_label = QLabel("Grid Size:")  # نص توضيحي
        
        # قائمة منسدلة لاختيار الحجم
        self.grid_size_combo = QComboBox()
        for size in GRID_SIZES:
            self.grid_size_combo.addItem(f"{size}x{size}")
            
        # تحديد الحجم الحالي في القائمة
        current_index = GRID_SIZES.index(self.current_settings['grid_size'])
        self.grid_size_combo.setCurrentIndex(current_index)
        self.grid_size_combo.setToolTip("Select the size of the game grid.")
        
        # إضافة عناصر حجم الشبكة للتخطيط
        grid_size_layout.addWidget(grid_size_label)
        grid_size_layout.addWidget(self.grid_size_combo)
        layout.addLayout(grid_size_layout)
        
        # إنشاء أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setToolTip("Save the current settings and apply changes.")
        
        # زر الإلغاء
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setToolTip("Cancel any changes and close the settings window.")
        
        # إضافة الأزرار للتخطيط
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        return tab
        
    def _create_stats_tab(self) -> QWidget:
        """
        إنشاء تبويب الإحصائيات
        يعرض إحصائيات اللاعب مثل:
        - عدد المباريات
        - عدد الانتصارات
        - نسبة الفوز
        - عدد التصويبات والإصابات
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # التحقق من وجود مدير قاعدة بيانات ولاعب حالي
        if self.db_manager and self.current_player_id:
            # جلب إحصائيات اللاعب
            stats = self.db_manager.get_player_statistics(self.current_player_id)
            
            if any(stats.values()):  # إذا كان هناك إحصائيات
                # إنشاء جدول لعرض الإحصائيات
                stats_table = QTableWidget()
                stats_table.setColumnCount(2)
                stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
                stats_table.horizontalHeader().setStretchLastSection(True)
                
                # تجهيز بيانات الإحصائيات
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
                
                # إضافة البيانات للجدول
                stats_table.setRowCount(len(stats_data))
                for i, (stat, value) in enumerate(stats_data):
                    stats_table.setItem(i, 0, QTableWidgetItem(stat))
                    stats_table.setItem(i, 1, QTableWidgetItem(str(value)))
                
                layout.addWidget(stats_table)
            else:
                # عرض رسالة إذا لم تكن هناك إحصائيات
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
            # ع��ض رسالة إذا لم يكن المستخدم مسجل دخوله
            layout.addWidget(QLabel("Please log in to view statistics"))
        
        return tab
            
    def _create_leaderboard_tab(self) -> QWidget:
        """
        إنشاء تبويب قائمة المتصدرين
        يعرض أفضل اللاعبين حسب:
        - نسبة الفوز
        - عدد الانتصارات
        - الدقة في التصويب
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager:
            # إنشاء فلتر الفترة الزمنية
            time_filter_layout = QHBoxLayout()
            time_filter_label = QLabel("Filter by Time Period:")
            self.time_filter_combo = QComboBox()
            self.time_filter_combo.addItems(["All Time", "This Week", "This Month", "This Year"])
            self.time_filter_combo.currentIndexChanged.connect(self.update_leaderboard)
            time_filter_layout.addWidget(time_filter_label)
            time_filter_layout.addWidget(self.time_filter_combo)
            layout.addLayout(time_filter_layout)
            
            # إنشاء جدول المتصدرين
            self.leaderboard_table = QTableWidget()
            self.leaderboard_table.setColumnCount(5)
            self.leaderboard_table.setHorizontalHeaderLabels([
                "Rank", "Player", "Win Rate", "Games Won", "Accuracy"
            ])
            self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
            
            layout.addWidget(self.leaderboard_table)
            
            # تحميل بيانات المتصدرين
            self.load_leaderboard("All Time")
        else:
            # عرض رسالة إذا لم يكن هناك مدير قاعدة بيانات
            layout.addWidget(QLabel("Leaderboard unavailable"))
        
        return tab
            
    def _create_achievements_tab(self) -> QWidget:
        """
        إنشاء تبويب الإنجازات
        يعرض الإنجازات التي حققها اللاعب
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # التحقق من وجود مدير قاعدة بيانات ولاعب حالي
        if self.db_manager and self.current_player_id:
            # جلب إنجازات اللاعب
            achievements = self.db_manager.get_player_achievements(self.current_player_id)
            
            if achievements:  # إذا كان هناك إنجازات
                # عرض كل إنجاز
                for achievement in achievements:
                    achievement_widget = QWidget()
                    achievement_layout = QHBoxLayout(achievement_widget)
                    
                    icon = QLabel(achievement['icon'])
                    title = QLabel(achievement['title'])
                    description = QLabel(achievement['description'])
                    
                    # تنسيق الأيقونة والعنوان والوصف
                    icon.setFont(QFont("Arial", 16))
                    title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                    description.setFont(QFont("Arial", 12))
                    
                    achievement_layout.addWidget(icon)
                    achievement_layout.addWidget(title)
                    achievement_layout.addWidget(description)
                    
                    layout.addWidget(achievement_widget)
            else:
                # عرض رسالة إذا لم تكن هناك إنجازات
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
            # عرض رسالة إذا لم يكن المستخدم مسجل دخوله
            layout.addWidget(QLabel("Please log in to view achievements"))
        
        return tab
            
    def save_settings(self):
        """
        حفظ الإعدادات الجديدة
        - يتحقق من تغيير حجم الشبكة
        - يطلب تأكيد التغيير
        - يحفظ الإعدادات في قاعدة البيانات
        """
        # الحصول على حجم الشبكة المختار
        grid_size = int(self.grid_size_combo.currentText().split('x')[0])
        
        # التحقق من تغيير الحجم
        if grid_size != self.current_settings['grid_size']:
            # طلب تأكيد التغيير
            reply = QMessageBox.question(
                self,
                'Confirm Changes',
                'Changing grid size will start a new game. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # تجهيز الإعدادات الجديدة
        new_settings = {
            'grid_size': grid_size
        }
        
        # حفظ الإعدادات في قاعدة البيانات
        if self.db_manager:
            self.db_manager.save_game_settings(self.current_player_id, new_settings)
        
        # إرسال إشارة بتغيير الإعدادات
        self.settings_changed.emit(new_settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        self.close()
        
    def load_leaderboard(self, time_period: str):
        """
        تحميل قائمة المتصدرين
        
        المعاملات:
        - time_period: الفترة الزمنية المطلوبة (كل الوقت، هذا الأسبوع، هذا الشهر، هذه السنة)
        """
        # تحويل الفترة الزمنية إلى الصيغة المناسبة
        period_mapping = {
            "All Time": "all",
            "This Week": "week",
            "This Month": "month",
            "This Year": "year"
        }
        mapped_period = period_mapping.get(time_period, "all")
        
        # جلب بيانات المتصدرين
        leaderboard = self.db_manager.get_leaderboard(limit=10, time_period=mapped_period)
        
        if leaderboard:  # إذا كان هناك بيانات
            # عرض البيانات في الجدول
            self.leaderboard_table.setRowCount(len(leaderboard))
            for i, player in enumerate(leaderboard):
                self.leaderboard_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.leaderboard_table.setItem(i, 1, QTableWidgetItem(player['name']))
                self.leaderboard_table.setItem(i, 2, QTableWidgetItem(f"{player['win_ratio']:.1f}%"))
                self.leaderboard_table.setItem(i, 3, QTableWidgetItem(str(player['games_won'])))
                self.leaderboard_table.setItem(i, 4, QTableWidgetItem(f"{player['accuracy']:.1f}%"))
        else:
            # عرض رسالة إذا لم تكن هناك بيانات
            self.leaderboard_table.setRowCount(0)
            QMessageBox.information(self, "No Data", "No players on the leaderboard for the selected time period.")
    
    def update_leaderboard(self):
        """تحديث قائمة المتصدرين عند تغيير الفترة الزمنية"""
        selected_period = self.time_filter_combo.currentText()
        self.load_leaderboard(selected_period)