from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

class InstructionsScreen(QWidget):
    """
    شاشة التعليمات التي تعرض كيفية لعب اللعبة
    المسؤوليات:
    - عرض نظرة عامة على اللعبة
    - شرح السفن وكيفية وضعها
    - شرح قواعد اللعب
    - عرض شروط الفوز
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """
        تهيئة عناصر واجهة المستخدم
        - إنشاء منطقة قابلة للتمرير
        - إضافة العنوان الرئيسي
        - إضافة أقسام التعليمات
        - إضافة زر العودة
        """
        self.setWindowTitle("Battleship Instructions")
        self.setMinimumSize(800, 600)
        
        main_layout = QVBoxLayout(self)
        
        # إنشاء منطقة تمرير للتعليمات
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # إنشاء عنصر المحتوى
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # إضافة العنوان
        title = QLabel("How to Play Battleship")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        # إضافة الأقسام
        sections = [
            self._create_game_overview_section(),
            self._create_ships_section(),
            self._create_placement_section(),
            self._create_gameplay_section(),
            self._create_winning_section()
        ]
        
        for section in sections:
            content_layout.addWidget(section)
            
        # إضافة زر العودة
        back_btn = QPushButton("Back to Menu")
        back_btn.setMinimumSize(200, 50)
        back_btn.clicked.connect(self.close)
        back_btn.setFont(QFont("Arial", 12))
        content_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # تعيين عنصر المحتوى لمنطقة التمرير
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
    def _create_section_title(self, text: str) -> QLabel:
        """
        إنشاء تسمية عنوان القسم
        المدخلات:
            text: نص العنوان
        المخرجات:
            QLabel: تسمية العنوان المنسقة
        """
        label = QLabel(text)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        return label
        
    def _create_section_content(self, text: str) -> QLabel:
        """
        إنشاء تسمية محتوى القسم
        المدخلات:
            text: نص المحتوى
        المخرجات:
            QLabel: تسمية المحتوى المنسقة
        """
        label = QLabel(text)
        font = QFont()
        font.setPointSize(12)
        label.setFont(font)
        label.setWordWrap(True)
        return label
        
    def _create_game_overview_section(self) -> QWidget:
        """
        إنشاء قسم النظرة العامة على اللعبة
        المخرجات:
            QWidget: عنصر يحتوي على نظرة عامة عن اللعبة
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        
        layout.addWidget(self._create_section_title("Game Overview"))
        content = """
        Battleship is a strategy type guessing game for two players. It is played on ruled grids 
        on which each player's fleet of ships are marked. The locations of the fleets are 
        concealed from the other player. Players alternate turns calling "shots" at the other 
        player's ships, and the objective of the game is to destroy the opposing player's fleet.
        """
        layout.addWidget(self._create_section_content(content))
        
        return section
        
    def _create_ships_section(self) -> QWidget:
        """
        إنشاء قسم معلومات السفن
        المخرجات:
            QWidget: عنصر يحتوي على معلومات السفن
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        
        layout.addWidget(self._create_section_title("Ships"))
        content = """
        Your fleet consists of 5 ships:
        • Aircraft Carrier - 5 cells long
        • Battleship - 4 cells long
        • Submarine - 3 cells long
        • Destroyer - 3 cells long
        • Patrol Boat - 2 cells long

        Each ship occupies a number of consecutive spaces on the grid, arranged either 
        horizontally or vertically.
        """
        layout.addWidget(self._create_section_content(content))
        
        return section
        
    def _create_placement_section(self) -> QWidget:
        """
        إنشاء قسم وضع السفن
        المخرجات:
            QWidget: عنصر يحتوي على تعليمات وضع السفن
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        
        layout.addWidget(self._create_section_title("Placing Your Ships"))
        content = """
        To place your ships:
        1. Select a ship from the ship buttons on the right
        2. Use the 'Rotate Ship' button to change orientation (horizontal/vertical)
        3. Click on your grid where you want to place the ship
        
        Rules for placement:
        • Ships cannot overlap
        • Ships cannot be placed diagonally
        • Ships cannot extend beyond the grid
        • Ships cannot touch each other (including diagonally)
        
        You can also use the 'Random Ship Placement' button to automatically place all ships.
        """
        layout.addWidget(self._create_section_content(content))
        
        return section
        
    def _create_gameplay_section(self) -> QWidget:
        """
        إنشاء قسم طريقة اللعب
        المخرجات:
            QWidget: عنصر يحتوي على تعليمات اللعب
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        
        layout.addWidget(self._create_section_title("How to Play"))
        content = """
        Once all ships are placed, the game begins:
        1. Click on a cell in the enemy's grid to attack that position
        2. Red marks indicate hits
        3. White marks indicate misses
        4. The AI will automatically take its turn after yours
        5. When you sink a ship, you'll be notified
        
        The game status will be shown in the middle panel, keeping you informed of:
        • Whose turn it is
        • Hit or miss results
        • Ships that have been sunk
        """
        layout.addWidget(self._create_section_content(content))
        
        return section
        
    def _create_winning_section(self) -> QWidget:
        """
        إنشاء قسم شروط الفوز
        المخرجات:
            QWidget: عنصر يحتوي على شروط الفوز
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        
        layout.addWidget(self._create_section_title("Winning the Game"))
        content = """
        The game ends when either you or the AI has sunk all of the opponent's ships. 
        The first player to sink all of their opponent's ships wins the game!
        
        After the game ends, you can:
        • Start a new game
        • View your game statistics
        • Return to the main menu
        """
        layout.addWidget(self._create_section_content(content))
        
        return section 