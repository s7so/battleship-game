# استيراد بعض الأدوات اللي هنحتاجها
from dataclasses import dataclass, field  # دي بتساعدنا نعمل كائنات بسهولة
from typing import List, Tuple  # دي بتساعدنا نحدد نوع البيانات اللي هنستخدمها
from enum import Enum  # دي بتساعدنا نعمل قائمة خيارات ثابتة

# هنا بنعرف اتجاهات السفينة، يعني السفينة ممكن تكون أفقية أو رأسية
class ShipOrientation(Enum):
    HORIZONTAL = 'horizontal'  # السفينة بتكون نايمة
    VERTICAL = 'vertical'      # السفينة بتكون واقفة

# هنا بنعمل فئة اسمها Ship بتمثل السفينة في اللعبة
@dataclass
class Ship:
    """
    الفئة دي بتمثل السفينة في لعبة Battleship
    وبتساعدنا نعرف مكانها وحالتها ونتابع الإصابات اللي حصلت لها
    """
    # الخصائص الأساسية للسفينة
    name: str  # اسم السفينة
    size: int  # حجم السفينة، يعني بتاخد كام خانة
    position: List[Tuple[int, int]] = field(default_factory=list)  # الأماكن اللي السفينة موجودة فيها
    orientation: ShipOrientation = ShipOrientation.HORIZONTAL  # اتجاه السفينة
    hits: List[Tuple[int, int]] = field(default_factory=list)  # الأماكن اللي السفينة اتضربت فيها

    def __post_init__(self):
        """هنا بنتأكد إن البيانات اللي دخلت صح"""
        # بنتأكد إن حجم السفينة أكبر من صفر
        if self.size <= 0:
            raise ValueError("Ship size must be positive")
            
        # بنتأكد إن اسم السفينة مش فاضي
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Ship name must be a non-empty string")
        
        # بنتأكد إن مفيش أماكن مكررة
        self.position = list(dict.fromkeys(self.position))
        self.hits = list(dict.fromkeys(self.hits))
        
        # بنتأكد إن عدد الأماكن بيساوي حجم السفينة
        if self.position and len(self.position) != self.size:
            raise ValueError(f"Position length ({len(self.position)}) must match ship size ({self.size})")

    def is_sunk(self) -> bool:
        """بنشوف إذا كانت السفينة غرقت ولا لأ"""
        return len(self.hits) == self.size

    def take_hit(self, position: Tuple[int, int]) -> bool:
        """
        هنا بنسجل ضربة على السفينة
        بنرجع True لو الضربة كانت في مكان من السفينة ومكانش مضروب قبل كده
        """
        if not self.position:
            return False
            
        if position in self.position and position not in self.hits:
            self.hits.append(position)
            return True
        return False

    def get_positions(self) -> List[Tuple[int, int]]:
        """بناخد كل الأماكن اللي السفينة موجودة فيها"""
        return self.position.copy()  # بنرجع نسخة عشان محدش يغيرها

    def is_hit_at(self, position: Tuple[int, int]) -> bool:
        """بنشوف إذا كانت السفينة اتضربت في مكان معين"""
        return position in self.hits

    def get_damage_percentage(self) -> float:
        """بنحسب نسبة الضرر اللي حصل للسفينة"""
        if not self.size:
            return 0.0
        return (len(self.hits) / self.size) * 100

    def is_valid_position(self, position: List[Tuple[int, int]]) -> bool:
        """
        بنتأكد إن الأماكن المقترحة للسفينة صح
        - لازم يكون عدد الأماكن زي حجم السفينة
        - لازم تكون الأماكن ورا بعض
        - لازم تكون في الاتجاه الصح
        """
        if len(position) != self.size:
            return False

        # بنرتب الأماكن عشان نتأكد إنها ورا بعض
        sorted_pos = sorted(position)
        
        # بنتأكد إن الأماكن ورا بعض
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
        بنحدد مكان واتجاه السفينة
        بنرجع True لو المكان صح وتم التحديد بنجاح
        """
        if not isinstance(orientation, ShipOrientation):
            return False
            
        self.orientation = orientation
        if self.is_valid_position(position):
            self.position = position
            return True
        return False

    def clear_hits(self):
        """بنعيد تعيين الضربات اللي حصلت للسفينة"""
        self.hits.clear()

    def __str__(self) -> str:
        """بنعمل تمثيل نصي للسفينة يوضح حالتها"""
        status = "SUNK" if self.is_sunk() else f"Health: {100 - self.get_damage_percentage()}%"
        return f"{self.name} ({self.size}) - {status}"