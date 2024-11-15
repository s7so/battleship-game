from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum

# تعريف اتجاهات السفينة كـ Enum للتحكم في القيم المسموح بها
class ShipOrientation(Enum):
    HORIZONTAL = 'horizontal'  # السفينة في وضع أفقي
    VERTICAL = 'vertical'      # السفينة في وضع رأسي

@dataclass  # استخدام dataclass لتبسيط تعريف الفئة وتوفير الدوال الأساسية
class Ship:
    """
    فئة تمثل سفينة في لعبة Battleship
    تتحكم في موقع وحالة السفينة وتتبع الإصابات
    """
    # الخصائص الأساسية للسفينة
    name: str                                      # اسم السفينة
    size: int                                      # حجم السفينة (عدد الخلايا)
    position: List[Tuple[int, int]] = field(default_factory=list)  # مواقع السفينة على الشبكة
    orientation: ShipOrientation = ShipOrientation.HORIZONTAL      # اتجاه السفينة
    hits: List[Tuple[int, int]] = field(default_factory=list)     # مواقع الإصابات

    def __post_init__(self):
        """التحقق من صحة البيانات بعد إنشاء الكائن"""
        # التحقق من صحة الحجم
        if self.size <= 0:
            raise ValueError("Ship size must be positive")
            
        # التحقق من صحة الاسم
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Ship name must be a non-empty string")
        
        # التأكد من عدم تكرار المواقع
        self.position = list(dict.fromkeys(self.position))
        self.hits = list(dict.fromkeys(self.hits))
        
        # التحقق من تطابق طول المواقع مع حجم السفينة
        if self.position and len(self.position) != self.size:
            raise ValueError(f"Position length ({len(self.position)}) must match ship size ({self.size})")

    def is_sunk(self) -> bool:
        """التحقق مما إذا كانت السفينة قد غرقت (كل المواقع تم إصابتها)"""
        return len(self.hits) == self.size

    def take_hit(self, position: Tuple[int, int]) -> bool:
        """
        تسجيل إصابة على السفينة
        Returns: True إذا كانت الإصابة ناجحة (الموقع جزء من السفينة ولم يتم إصابته من قبل)
        """
        if not self.position:
            return False
            
        if position in self.position and position not in self.hits:
            self.hits.append(position)
            return True
        return False

    def get_positions(self) -> List[Tuple[int, int]]:
        """الحصول على جميع مواقع السفينة"""
        return self.position.copy()  # إرجاع نسخة لمنع التعديل المباشر

    def is_hit_at(self, position: Tuple[int, int]) -> bool:
        """التحقق مما إذا كانت السفينة قد أصيبت في موقع معين"""
        return position in self.hits

    def get_damage_percentage(self) -> float:
        """حساب نسبة الضرر الذي لحق بالسفينة"""
        if not self.size:
            return 0.0
        return (len(self.hits) / self.size) * 100

    def is_valid_position(self, position: List[Tuple[int, int]]) -> bool:
        """
        التحقق من صحة الموقع المقترح للسفينة
        - يجب أن يطابق حجم السفينة
        - يجب أن تكون المواقع متتالية
        - يجب أن تكون في الاتجاه الصحيح
        """
        if len(position) != self.size:
            return False

        # ترتيب المواقع للتحقق من التتالي
        sorted_pos = sorted(position)
        
        # التحقق من تتالي المواقع
        rows = [pos[0] for pos in sorted_pos]
        cols = [pos[1] for pos in sorted_pos]
        
        if len(set(rows)) == 1:  # أفقي
            return (max(cols) - min(cols) + 1 == self.size and 
                   self.orientation == ShipOrientation.HORIZONTAL)
        elif len(set(cols)) == 1:  # رأسي
            return (max(rows) - min(rows) + 1 == self.size and 
                   self.orientation == ShipOrientation.VERTICAL)
        
        return False

    def set_position(self, position: List[Tuple[int, int]], 
                    orientation: ShipOrientation) -> bool:
        """
        تعيين موقع واتجاه السفينة
        Returns: True إذا كان الموقع صالح وتم التعيين بنجاح
        """
        if not isinstance(orientation, ShipOrientation):
            return False
            
        self.orientation = orientation
        if self.is_valid_position(position):
            self.position = position
            return True
        return False

    def clear_hits(self):
        """إعادة تعيين إصابات السفينة"""
        self.hits.clear()

    def __str__(self) -> str:
        """تمثيل نصي للسفينة يوضح حالتها"""
        status = "SUNK" if self.is_sunk() else f"Health: {100 - self.get_damage_percentage()}%"
        return f"{self.name} ({self.size}) - {status}"