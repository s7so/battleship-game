from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from utils.constants import GRID_SIZE, CELL_SIZE, WATER_COLOR, SHIP_COLOR, HIT_COLOR, MISS_COLOR
from models.ship import ShipOrientation
import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class MainWindow(QMainWindow):
    """
    النافذة الرئيسية للعبة Battleship
    المسؤوليات الرئيسية:
    1. عرض شبكتي اللعب (اللاعب و AI)
    2. التحكم في وضع السفن
    3. إدارة الهجمات وتناوب الأدوار
    4. عرض حالة اللعبة والإحصائيات
    """

    def __init__(self, game_controller):
        """
        تهيئة النافذة الرئيسية مع وحدة التحكم في اللعبة
        المدخلات:
            game_controller: وحدة التحكم في اللعبة التي تدير المنطق والحالة
        المسؤوليات:
            - تهيئة الخصائص الأساسية للنافذة
            - تخزين مراجع لأزرار الشبكة
            - إعداد متغيرات حالة وضع السفن
            - بدء تهيئة واجهة المستخدم
        """
        super().__init__()
        self.game_controller = game_controller  # وحدة التحكم في اللعبة
        self.player_grid_buttons = []  # مصفوفة تخزن أزرار شبكة اللاعب
        self.ai_grid_buttons = []  # مصفوفة تخزن أزرار شبكة الخصم
        self.selected_ship = None  # السفينة المحددة حالياً للوضع
        self.selected_orientation = 'horizontal'  # اتجاه وضع السفينة (أفقي/رأسي)
        self.selected_attack_pos = None  # Initialize selected_attack_pos
        self.init_ui()  # بدء تهيئة واجهة المستخدم

    # Extract CSS styles into constants
    BUTTON_STYLE = """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """

    def init_ui(self):
        """
        تهيئة واجهة المستخدم وتصميمها
        """
        # تعيين عنوان النافذة وحجمها الأدنى
        self.setWindowTitle("Battleship Game")
        self.setMinimumSize(1200, 800)  # زيادة الحجم الأدنى للنافذة
        
        # إنشاء العنصر المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # إنشاء التخطيط الرئيسي للعنصر المركزي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)  # زيادة المسافة بين العناصر
        
        # إنشاء الأقسام الثلاثة
        player_section = self.create_grid_section("Your Fleet", is_player=True)
        control_section = QVBoxLayout()
        ai_section = self.create_grid_section("Enemy Waters", is_player=False)
        
        # تنسيق قسم التحكم
        control_section.setSpacing(15)
        control_section.setContentsMargins(20, 20, 20, 20)
        
        # إضافة الأزرار إلى قسم التحكم
        # زر اللعبة الجديدة
        new_game_btn = QPushButton("New Game")
        new_game_btn.setFixedSize(200, 50)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        control_section.addWidget(new_game_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # زر Fire
        self.fire_btn = QPushButton("Fire!")
        self.fire_btn.setFixedSize(200, 50)
        self.fire_btn.setEnabled(False)
        self.fire_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        control_section.addWidget(self.fire_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # زر حفظ اللعبة
        save_btn = QPushButton("Save Game")
        save_btn.setFixedSize(200, 50)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d4ac0d;
            }
        """)
        control_section.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # زر تحميل اللعبة
        load_btn = QPushButton("Load Game")
        load_btn.setFixedSize(200, 50)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        control_section.addWidget(load_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # زر إنهاء اللعبة
        end_btn = QPushButton("End Game")
        end_btn.setFixedSize(200, 50)
        end_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        control_section.addWidget(end_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # إضافة مسافة مرنة في النهاية
        control_section.addStretch()
        
        # ربط الأزرار بالوظائف المناسبة
        new_game_btn.clicked.connect(self.start_new_game)
        self.fire_btn.clicked.connect(self.confirm_attack)
        save_btn.clicked.connect(self.save_game)
        load_btn.clicked.connect(self.load_game)
        end_btn.clicked.connect(self.confirm_end_game)
        
        # إضافة الأقسام الثلاثة إلى التخطيط الرئيسي
        main_layout.addLayout(player_section)
        main_layout.addLayout(control_section)
        main_layout.addLayout(ai_section)

    def create_grid_section(self, title: str, is_player: bool) -> QVBoxLayout:
        """
        إنشاء قسم الشبكة (للاعب أو للذكاء الاصطناعي) مع العنوان والأزرار
        
        المعاملات:
            title: عنوان القسم
            is_player: مؤشر يحدد ما إذا كان القسم للاعب أم للذكاء الاصطناعي
            
        المخرجات:
            QVBoxLayout: تخطيط عمودي يحتوي على الشبكة وعنوانها
        """
        # إنشاء التخطيط الرئيسي
        layout = QVBoxLayout()

        # إضافة العنوان
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # إنشاء الشبكة بالحجم الحالي من وحدة التحكم
        grid = QGridLayout()
        grid.setSpacing(1)  # تعيين المسافة بين الخلايا

        # الحصول على حجم الشبكة الحالي
        current_size = self.game_controller.grid_size
        buttons = []  # مصفوفة لتخزين الأزرار

        # إنشاء أزرار الشبكة
        for row in range(current_size):
            row_buttons = []  # صف من الأزرار
            for col in range(current_size):
                # إنشاء زر جديد
                button = QPushButton()
                # ضبط حجم الزر بناءً على حجم الشبكة (بحد أقصى 600 بكسل)
                button_size = min(40, 600 // current_size)
                button.setFixedSize(button_size, button_size)
                button.setStyleSheet(f"background-color: {WATER_COLOR};")

                # ربط الحدث المناسب بالزر حسب نوع الشبكة
                if not is_player:
                    # ربط حدث الهجوم لشبكة الخصم
                    button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_attack(r, c))
                else:
                    # ربط حدث وضع السفن لشبكة اللاعب
                    button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_ship_placement(r, c))

                # إضافة الزر للشبكة والمصفوفة
                grid.addWidget(button, row, col)
                row_buttons.append(button)
            buttons.append(row_buttons)

        # تخزين الأزرار في المتغير المناسب
        if is_player:
            self.player_grid_buttons = buttons
        else:
            self.ai_grid_buttons = buttons

        # إضافة الشبكة للتخطيط الرئيسي
        layout.addLayout(grid)
        return layout

    def create_control_panel(self) -> QVBoxLayout:
        """
        إنشاء لوحة التحكم في اللعبة مع جميع عناصر التحكم وشاشات الحالة
        Returns:
            QVBoxLayout: تخطيط عمودي يحتوي على لوحة التحكم
        """
        layout = QVBoxLayout()
        layout.setSpacing(15)  # تعيين المسافة بين العناصر

        # لوحة الحالة
        status_panel = QVBoxLayout()

        # تسمية حالة اللعبة
        self.status_label = QLabel("Welcome to Battleship!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # محاذاة النص للوسط
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        status_panel.addWidget(self.status_label)

        # مؤشر الدور الحالي
        self.turn_label = QLabel("Game not started")
        self.turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        status_panel.addWidget(self.turn_label)

        # تسمية آخر إجراء
        self.action_label = QLabel("")
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_label.setWordWrap(True)  # السماح بالتفاف النص
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                margin: 5px;
                min-height: 50px;
            }
        """)
        status_panel.addWidget(self.action_label)

        layout.addLayout(status_panel)

        # مجموعة عناصر التحكم في اللعبة
        game_controls = QVBoxLayout()
        game_controls.setSpacing(10)

        # زر لعبة جديدة
        new_game_btn = QPushButton("New Game")
        new_game_btn.setMinimumSize(200, 50)
        new_game_btn.clicked.connect(self.start_new_game)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        game_controls.addWidget(new_game_btn)

        # عناصر التحكم في وضع السفن
        self.ship_placement_group = QVBoxLayout()

        # أزار اختيار السن
        self.ship_buttons = {}
        if self.game_controller.player:
            for ship_name, size in self.game_controller.player.remaining_ships:
                btn = QPushButton(f"{ship_name} ({size} cells)")
                btn.clicked.connect(lambda checked, name=ship_name: self.select_ship(name))
                self.ship_buttons[ship_name] = btn
                self.ship_placement_group.addWidget(btn)

        # زر تغيير الاتجاه
        self.orientation_btn = QPushButton("Rotate Ship (Horizontal)")
        self.orientation_btn.clicked.connect(self.toggle_orientation)
        self.ship_placement_group.addWidget(self.orientation_btn)

        # زر الوضع العشوائي
        random_placement_btn = QPushButton("Random Ship Placement")
        random_placement_btn.clicked.connect(self.random_ship_placement)
        random_placement_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.ship_placement_group.addWidget(random_placement_btn)

        game_controls.addLayout(self.ship_placement_group)

        # زر إطلاق النار
        self.fire_btn = QPushButton("Fire!")
        self.fire_btn.setMinimumSize(200, 50)
        self.fire_btn.clicked.connect(self.confirm_attack)
        self.fire_btn.setEnabled(False)  # معطل في البداية
        self.fire_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        game_controls.addWidget(self.fire_btn)

        # زضافة زر حفظ اللعبة
        save_game_btn = QPushButton("Save Game")
        save_game_btn.setMinimumSize(200, 50)
        save_game_btn.clicked.connect(self.save_game)
        save_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d4ac0d;
            }
        """)
        game_controls.addWidget(save_game_btn)

        # زر تحميل اللعبة
        load_game_btn = QPushButton("Load Game")
        load_game_btn.setMinimumSize(200, 50)
        load_game_btn.clicked.connect(self.load_game)
        load_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #71368a;
            }
        """)
        game_controls.addWidget(load_game_btn)

        # زر إنهاء اللعبة
        self.end_game_btn = QPushButton("End Game")
        self.end_game_btn.clicked.connect(self.confirm_end_game)
        self.end_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        game_controls.addWidget(self.end_game_btn)

        layout.addLayout(game_controls)

        # عرض الإحصائيات
        self.stats_label = QLabel()
        self.update_stats_display()
        layout.addWidget(self.stats_label)

        layout.addStretch()  # إضافة مسافة مرنة في النهاية
        return layout

    def handle_attack(self, row: int, col: int):
        """
        معالجة هجوم اللاعب على شبكة AI
        التحقق من:
        1. أن اللعبة في مرحلة اللعب
        2. أنه دور اللاعب
        3. أن الموقع لم يتم استهدافه من قبل
        """
        # Input validation
        if not (0 <= row < self.game_controller.grid_size) or not (0 <= col < self.game_controller.grid_size):
            self.update_status("Invalid target position!")
            return

        # التحقق من حالة اللعبة ودور اللاعب
        if self.game_controller.get_game_state() != 'playing':
            self.action_label.setText("Game hasn't started yet!")
            return

        if self.game_controller.current_turn != 'player':
            self.action_label.setText("Wait for your turn!")
            return

        # التحقق من صلاحية الهدف
        if self.game_controller.get_cell_state(False, (row, col)) in ['hit', 'miss']:
            self.action_label.setText("You already fired at this position!")
            return

        # تحديد الهدف وتفعيل زر Fire
        self.selected_attack_pos = (row, col)
        self.fire_btn.setEnabled(True)
        self._highlight_selected_cell(row, col)

        # تحديث حالة اللعبة
        self.action_label.setText("Press Fire! to attack selected position")
        self.turn_label.setText("Your Turn")
        self.turn_label.setStyleSheet("""
            QLabel {
                background-color: #2ecc71;
                color: white;
            }
        """)

    def _highlight_selected_cell(self, row: int, col: int):
        """
        تمييز الخلية المحددة مع الحفاظ على لونها الأصلي
        """
        # ادة تعيين تنسيق كل الخلايا لحاتها الأصلية
        for r in range(len(self.ai_grid_buttons)):
            for c in range(len(self.ai_grid_buttons[r])):
                cell_state = self.game_controller.get_cell_state(False, (r, c))
                if cell_state == 'hit':
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {HIT_COLOR};")
                elif cell_state == 'miss':
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {MISS_COLOR};")
                else:
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {WATER_COLOR};")

        # تمييز الخلية المحددة مع الحفاظ على لونها الأصلي
        cell_state = self.game_controller.get_cell_state(False, (row, col))
        base_color = {
            'hit': HIT_COLOR,
            'miss': MISS_COLOR,
            'empty': WATER_COLOR,
        }.get(cell_state, WATER_COLOR)

        # تطبيق تنسيق الـ hover مع الحفاظ على اللون الأصلي
        self.ai_grid_buttons[row][col].setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                border: 2px solid #e74c3c;
            }}
            QPushButton:hover {{
                background-color: {base_color};
                border: 3px solid #c0392b;
            }}
        """)

    def confirm_attack(self):
        """
        تنفيذ الهجوم على الموقع المحدد
        - تحديث حالة الشبكة
        - تحديث الإحصائيات
        - معالجة نتيجة الهجوم
        """
        if not hasattr(self, 'selected_attack_pos'):
            return

        row, col = self.selected_attack_pos
        # تنفيذ الهجوم
        result = self.game_controller.process_player_shot((row, col))
        if not result['valid']:
            self.update_status(result['message'])
            return

        # تحديث شبكة AI
        button = self.ai_grid_buttons[row][col]
        if result['hit']:
            button.setStyleSheet(f"background-color: {HIT_COLOR};")
        else:
            button.setStyleSheet(f"background-color: {MISS_COLOR};")

        # تعطيل زر Fire وإزالة الموقع المحدد
        self.fire_btn.setEnabled(False)
        delattr(self, 'selected_attack_pos')

        self.update_status(result['message'])
        self.update_stats_display()

        # تحقق من انتهاء اللعبة
        if result['game_over']:
            self.game_over(result['winner'])
        else:
            # تعطيل شبكة AI أثناء دور AI
            self._disable_ai_grid()
            # معالجة دور AI بعد تأخير قصير
            QTimer.singleShot(1000, self.process_ai_turn)

    def process_ai_turn(self):
        """
        معالجة دور AI
        - إظهار رسالة "AI يفكر"
        - تنفيذ الهجوم بعد تأخير قصير
        """
        self.update_status("AI is thinking...")
        QTimer.singleShot(500, self._execute_ai_turn)

    def _execute_ai_turn(self):
        """
        تنفيذ هجوم AI
        - تحديث شبكة اللاعب
        - عرض نتيجة الهجوم
        - التحقق من انتهاء اللعبة
        """
        # معالجة دور AI وتخزين النتيجة
        result = self.game_controller.process_ai_turn()

        # التحقق من صحة الهجوم
        if not result['valid']:
            return

        # الحصول على إحداثيات الهجوم وزر الخلية المستهدفة
        row, col = result['position']
        button = self.player_grid_buttons[row][col]

        # معالجة نتيجة الهجوم وتحديث الواجهة
        if result['hit']:
            # في حالة الإصابة
            button.setStyleSheet(f"background-color: {HIT_COLOR};")
            message = "💥 AI Hit! "
            if result['sunk']:
                # في حالة إغراق سفينة
                message += f"AI sunk your {result['ship_name']}! 🚢"
        else:
            # في حالة الخطأ
            button.setStyleSheet(f"background-color: {MISS_COLOR};")
            message = "AI Missed! 💨"

        # تحديث حالة اللعبة والإحصائيات
        self.update_status(message)
        self.update_stats_display()

        # التحقق من انتهاء اللعبة
        if result['game_over']:
            self.game_over(result['winner'])
        else:
            # تمكين شبكة AI للدور التالي
            self._enable_ai_grid()
            # عرض رسالة دور اللاعب بعد تأخير قصير
            QTimer.singleShot(500, lambda: self.update_status("Your turn! Select a target"))

    def _disable_ai_grid(self):
        """
        تعطيل شبكة AI أثناء دور AI
        - تعطيل جميع الأزرار في شبكة AI
        - منع اللاعب من اختيار موقع للهجوم أثناء دور AI
        """
        self.set_ai_grid_enabled(False)

    def _enable_ai_grid(self):
        """
        تمكين شبكة AI لدور اللاعب
        - تمكين جميع الأزرار في شبكة AI
        - يسمح للاعب باختار موقع للهجوم
        """
        self.set_ai_grid_enabled(True)

    def set_ai_grid_enabled(self, enabled: bool):
        for row in self.ai_grid_buttons:
            for button in row:
                button.setEnabled(enabled)

    def confirm_end_game(self):
        """
        تأكيد نهاء اللعبة الحالية
        - التحقق من حالة اللعبة
        - عرض رسالة تأكيد
        - إنهاء اللعبة أو بد لعبة جديدة
        """
        # إذا كانت اللعبة منتهية بالفعل، نبدأ لعبة جديدة
        if self.game_controller.get_game_state() == 'ended':
            self.start_new_game()
            return

        # عرض رسالة تأكيد
        reply = QMessageBox.question(
            self, 
            'End Game',
            'Are you sure you want to end the current game?\nThis will count as a loss.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # إنهاء اللعبة الحالية
            if self.game_controller.force_end_game():
                # تعطيل عناصر التحكم
                self._disable_all_controls()
                # تحديث حالة اللعبة
                self.update_status("Game ended manually")
                # تحديث الإحصائيات
                self.update_stats_display()
                # عرض رسالة تأكيد
                QMessageBox.information(self, 'Game Ended', 'The game has been ended.')
                # بدء لعبة جديدة بعد تأخير قصير
                QTimer.singleShot(1000, self.start_new_game)

    def _disable_all_controls(self):
        """
        تعطيل جميع عناصر التحكم في اللعبة
        - تعطيل شبكة AI
        - تعطيل زر Fire
        - تعطيل أزرار السفن
        - تعطيل زر تغيير الاتجاه
        """
        # تعطيل شبكة AI
        self._disable_ai_grid()
        
        # تعطيل زر Fire
        self.fire_btn.setEnabled(False)
        
        # تعطيل أزرار السفن
        for btn in self.ship_buttons.values():
            btn.setEnabled(False)
        
        # تعطيل زر تغيير الاتجاه
        self.orientation_btn.setEnabled(False)

    def update_game_phase(self):
        """
        تحديث واجهة المستخدم بناءً على مرحلة اللعبة الالية
        
        المسؤوليات:
        - تحديث حالة أزرار السفن وزر الاتجاه
        - تفعيل/تعطيل شبكة الخصم
        - تحديث رسائل الحالة المعروضة للاعب
        """
        game_state = self.game_controller.get_game_state()

        # تحديث حالة الأزرار بناءً على مرحلة للعبة
        # تفعيل أزرار السفن وزر الاتجاه فقط في مرحلة الإعداد
        for btn in self.ship_buttons.values():
            btn.setEnabled(game_state == 'setup')
        self.orientation_btn.setEnabled(game_state == 'setup')

        # تعطيل/تفعيل الشبكة المقابلة بناءً على مرحلة اللعبة
        # تفعيل شبكة الخصم فقط أثناء اللعب
        for row in self.ai_grid_buttons:
            for button in row:
                button.setEnabled(game_state == 'playing')

        # تحديث رسالة الحالة حسب مرحلة اللعبة
        if game_state == 'setup':
            # في مرحلة الإعداد - طلب وضع السفن
            self.update_status("Place your ships!")
        elif game_state == 'playing':
            if self.game_controller.current_turn == 'player':
                # دور اللاعب - طلب اختيار هدف
                self.update_status("Your turn! Select a target")
            else:
                # دور الخصم - إظهار رسالة انتظار
                self.update_status("AI's turn...")
        elif game_state == 'ended':
            # عند انتهاء اللعبة - تعطيل زر الهجوم
            self.fire_btn.setEnabled(False)

    def handle_ship_placement(self, row: int, col: int):
        """
        معالجة وضع السفن على شبكة اللاعب
        المدخلات:
            row: رقم الصف في الشبكة
            col: رقم العمود ف الشبكة
        الوظائف:
            - التحقق من اختيار سفينة
            - محاولة وضع السفينة في الموقع المحدد
            - تحديث حالة لشبكة والأزرار
            - التحقق من اكتمال وضع السفن وبدء اللعبة
        """
        # التحقق من اختيار سفينة قبل محاولة الوضع
        if not self.selected_ship:
            self.update_status("Select a ship first!")
            return

        # محاولة وضع السفينة في الموقع المحدد باستخدام وحدة التحكم
        if self.game_controller.place_player_ship(
                self.selected_ship, (row, col), self.selected_orientation):
            # تحديث عرض شبكة اللاعب بعد وضع السفينة بنجاح
            self.update_player_grid()
            # تعطيل زر السفينة التي تم وضعها
            self.ship_buttons[self.selected_ship].setEnabled(False)
            # إعادة تعيين السفينة المحددة
            self.selected_ship = None

            # التحقق من اكتمال وضع جميع السفن
            if not self.game_controller.player.remaining_ships:
                # بدء اللعبة عند اكتمال وضع السفن
                self.start_game()
                self.update_status("All ships placed! Game started - Your turn!")
            else:
                # طلب اختيار السفينة التالية
                self.update_status("Select next ship to place")
        else:
            # إظهار رسالة خطأ عند فشل وضع السفينة
            self.update_status("Invalid placement! Try another position")

    def select_ship(self, ship_name: str):
        """
        اختيار سفينة لوضعها على الشبكة
        Args:
            ship_name: اسم السفينة المراد اختيارها
        التأثيرات:
        - تحديث السفينة المختارة حالياً
        - تحديث رسالة الحالة لإرشاد اللاعب
        """
        self.selected_ship = ship_name
        self.update_status(f"Place your {ship_name}")

    def toggle_orientation(self):
        """
        تبديل اتجاه وضع السفينة بين الأفقي والعمودي
        - يغير قيمة selected_orientation بين 'horizontal' و 'vertical'
        - يحدث نص زر التدوير ليعكس الاتجاه الحالي
        """
        self.selected_orientation = 'vertical' if self.selected_orientation == 'horizontal' else 'horizontal'
        self.orientation_btn.setText(f"Rotate Ship ({self.selected_orientation})")

    def random_ship_placement(self):
        """
        وضع السفن بشكل عشوائي على شبكة اللاعب
        - يستدعي دالة وضع السفن العشوائي من وحدة التحكم
        - يحدث عرض شبكة اللاعب
        - يعطل أزرار اختيار السفن
        - يبدأ اللعبة
        """
        if self.game_controller.place_player_ships_randomly():  # محاولة وضع السفن عشوائياً
            self.update_player_grid()  # تحديث عرض شبكة اللاعب
            for btn in self.ship_buttons.values():  # تعطيل جميع أزرار اختيار السفن
                btn.setEnabled(False)
            self.start_game()  # بدء اللعبة بعد وضع اسفن

    def update_player_grid(self):
        """
        تحديث عرض شبكة اللاعب
        - يحصل على حجم الشبكة لحالي
        - يتحقق من حالة كل خلية (سفينة، إصابة، خطأ)
        - يحدث لون الخلية حسب حالتها
        """
        # الحصول على حجم الشبكة الحالي
        current_size = self.game_controller.grid_size

        # تحديث كل خلية في الشبكة فقط إذا تغيرت حالتها
        for row in range(current_size):
            for col in range(current_size):
                # الحصول على حالة الخلية من وحدة التحكم
                state = self.game_controller.get_cell_state(True, (row, col))
                # الحصول على زر الخلية من المصفوفة
                button = self.player_grid_buttons[row][col]

                # تحديد النمط الجديد بناءً على الحالة
                new_style = ""
                if state == 'ship':
                    new_style = f"background-color: {SHIP_COLOR};"
                elif state == 'hit':
                    new_style = f"background-color: {HIT_COLOR};"
                elif state == 'miss':
                    new_style = f"background-color: {MISS_COLOR};"
                else:
                    new_style = f"background-color: {WATER_COLOR};"

                # Update style only if it's different
                if button.styleSheet() != new_style:
                    button.setStyleSheet(new_style)

    def start_new_game(self):
        """
        بدء لعبة جديدة
        - عرض رسالة تأكيد
        - إعادة تعيين حالة اللعبة
        - إعادة تعيين واجهة المستخدم
        """
        # عرض مربع حوار للتأكيد
        reply = QMessageBox.question(
            self, 
            'New Game',
            'Are you sure you want to start a new game?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # إعادة تعيين حالة اللعبة
            self.game_controller.start_new_game()
            # إعادة تعيين واجهة لمستخدم
            self.reset_ui()
            # تحديث رسالة الحالة
            self.update_status("Place your ships!")

    def start_game(self):
        """بدء اللعبة بعد وضع السفن"""
        # تعطيل عناصر التحكم في وضع السفن
        self.orientation_btn.setEnabled(False)
        for btn in self.ship_buttons.values():
            btn.setEnabled(False)

        # إعادة تعيين عناصر التحكم في الهجوم
        self.fire_btn.setEnabled(False)
        if hasattr(self, 'selected_attack_pos'):
            delattr(self, 'selected_attack_pos')

        # تمكين شبكة AI للدور الأول
        self._enable_ai_grid()

        # بدء اللعب
        if self.game_controller.start_gameplay():
            self.update_status("Game started - Select a target and press Fire!")
        else:
            self.update_status("Error starting game!")

    def reset_ui(self):
        """Reset the UI for a new game"""
        # إعادة تعيين واجهة المستخدم لبدء لعبة جديدة

        # إنشاء عنصر واجهة مستخدم مركزي جديد وتعيينه كعنصر مركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # إنشاء أقسام الشبكة للاعب و AI بالحجم الجديد
        player_section = self.create_grid_section("Your Fleet", is_player=True)
        ai_section = self.create_grid_section("Enemy Waters", is_player=False)

        # إنشاء لوحة التحكم
        control_panel = self.create_control_panel()

        # إضافة الأقسام إلى التخطيط الرئيسي
        main_layout.addLayout(player_section)
        main_layout.addLayout(control_panel)
        main_layout.addLayout(ai_section)

        # إعادة تعيين عناصر واجهة المستخدم الأخرى
        self.orientation_btn.setEnabled(True)  # تمكين زر الاتجاه
        self.selected_ship = None  # إعادة تعيين السفينة المحددة
        self.selected_orientation = 'horizontal'  # إعادة تعيين الاتجاه المحدد
        self.update_status("Place your ships!")  # تحديث حالة اللعبة

        # إعادة تعيين المتغيرات المتعلقة بالهجوم
        if hasattr(self, 'selected_attack_pos'):
            delattr(self, 'selected_attack_pos')  # إزالة موقع الهجوم المحدد إذا كان موجودًا
        self.fire_btn.setEnabled(False)  # تعطيل زر الهجوم

    def game_over(self, winner: str):
        """Handle game over"""
        if winner == 'player':
            message = "🎉 Congratulations! You Won! 🎉"
            color = "#2ecc71"  # Green
        else:
            message = "Game Over! AI Wins!"
            color = "#e74c3c"  # Red

        # تحديث حالة اللعبة
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background-color: {color};
                color: white;
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        self.status_label.setText(message)
        self.turn_label.setText("Game Over")
        self.action_label.setText(f"Final Score:\nHits: {self.game_controller.stats['hits']}\n"
                                  f"Total Shots: {self.game_controller.stats['total_shots']}")

        # عرض رسالة النتيجة
        QMessageBox.information(self, 'Game Over', message)

        # إعادة تشغيل اللعبة بعد تأخير قصير
        QTimer.singleShot(2000, self.start_new_game)

    def update_status(self, message: str):
        """
        تحديث عرض حالة اللعبة
        - تحديث رسالة الحالة
        - تحديث مؤشر الدور الحالي مع اللون المناسب
        """
        self.action_label.setText(message)

        # تحديث مؤشر الدور
        if self.game_controller.get_game_state() == 'playing':
            current_turn = "Your Turn" if self.game_controller.current_turn == 'player' else "AI's Turn"
            self.turn_label.setText(current_turn)

            # تغيير لون مؤشر الدور
            if self.game_controller.current_turn == 'player':
                self.turn_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        padding: 10px;
                        background-color: #2ecc71;  /* أخضر للاعب */
                        color: white;
                        border-radius: 5px;
                        margin: 5px;
                    }
                """)
            else:
                self.turn_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        padding: 10px;
                        background-color: #e74c3c;  /* أحمر للخصم */
                        color: white;
                        border-radius: 5px;
                        margin: 5px;
                    }
                """)
        else:
            self.turn_label.setText("Game not started")
            self.turn_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    background-color: #95a5a6;
                    color: white;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)

    def update_stats_display(self):
        """تحديث عرض إحصائيات اللعبة"""
        stats = self.game_controller.stats
        player_name = getattr(self.game_controller, 'current_player_name', 'Unknown Player')

        if stats['total_shots'] > 0:
            accuracy = (stats['hits'] / stats['total_shots']) * 100
        else:
            accuracy = 0

        stats_text = f"""
        Player: {player_name}
        ---------------
        Total Games: {stats['games_played']}
        Games Won: {stats['games_won']}
        Win Rate: {(stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0:.1f}%
        
        Current Game:
        - Shots: {stats['total_shots']}
        - Hits: {stats['hits']}
        - Misses: {stats['misses']}
        - Accuracy: {accuracy:.1f}%
        """
        self.stats_label.setText(stats_text)

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # عرض رسالة تأكيد قبل الإغلاق
            reply = QMessageBox.question(
                self, 'Exit Game',
                'Are you sure you want to exit the game?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # حفظ حالة اللعبة إذا كانت جارية
                if self.game_controller.game_state == 'playing':
                    self.game_controller.force_end_game()
                
                # تنظيف الموارد
                for row in self.player_grid_buttons:
                    for button in row:
                        button.deleteLater()
                for row in self.ai_grid_buttons:
                    for button in row:
                        button.deleteLater()
                    
                event.accept()
            else:
                event.ignore()  # إلغاء الإغلاق إذا اختار المستخدم "لا"
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            QMessageBox.critical(self, 'Error', 'An error occurred while closing the game.')
            event.accept()

    def show_confirm_dialog(self, message: str) -> bool:
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self,
            'Confirm Action',
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def save_game(self):
        """
        دالة لحفظ حالة اللعبة الحالية.
        """
        success = self.game_controller.save_game()
        if success:
            QMessageBox.information(self, "Save Game", "Game has been saved successfully!")
        else:
            QMessageBox.critical(self, "Save Game", "Failed to save the game. Please try again.")

    def load_game(self):
        """
        دالة لتحميل حالة اللعبة المحفوظة.
        """
        success = self.game_controller.load_game()
        if success:
            QMessageBox.information(self, "Load Game", "Game has been loaded successfully!")
            
            # تحديث حالة الأزرار
            self.fire_btn.setEnabled(True)
            for btn in self.ship_buttons.values():
                btn.setEnabled(False)
            self.orientation_btn.setEnabled(False)
            
            # تحديث الشبكات والإحصائيات
            self.update_player_grid()
            self.update_ai_grid()  # تحديث شبكة AI
            self.update_stats_display()
            
            # تحديث حالة اللعبة
            if self.game_controller.current_turn == 'player':
                self.update_status("Your turn! Select a target and press Fire!")
            else:
                self.update_status("AI's turn...")
        else:
            QMessageBox.warning(self, "Load Game", "No saved game found or failed to load.")

    def update_ai_grid(self):
        """
        تحديث شبكة AI
        """
        current_size = self.game_controller.grid_size
        for row in range(current_size):
            for col in range(current_size):
                button = self.ai_grid_buttons[row][col]
                state = self.game_controller.get_cell_state(False, (row, col))
                
                if state == 'hit':
                    button.setStyleSheet(f"background-color: {HIT_COLOR};")
                elif state == 'miss':
                    button.setStyleSheet(f"background-color: {MISS_COLOR};")
                else:
                    button.setStyleSheet(f"background-color: {WATER_COLOR};")
                
                # تمكين/تعطيل الزر بناءً على حالة اللعبة
                button.setEnabled(
                    self.game_controller.game_state == 'playing' and 
                    self.game_controller.current_turn == 'player' and
                    state not in ['hit', 'miss']
                )
