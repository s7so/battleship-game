from typing import List, Tuple, Optional, Dict
import random
from .grid import Grid
from .ship import Ship
from utils.constants import SHIPS

class Player:
    """
    فئة تمثل اللاعب في لعبة Battleship
    مسؤولة عن:
    - إدارة شبكة اللاعب
    - وضع السفن
    - تتبع الطلقات والإصابات
    """
    
    def __init__(self, grid_size: int = 10):
        """
        تهيئة اللاعب
        Args:
            grid_size: حجم الشبكة (10×10 أو 15×15)
        """
        self.grid = Grid(grid_size)                      # شبكة اللاعب
        self.shots: List[Tuple[int, int]] = []          # قائمة الطلقات
        self.remaining_ships = list(SHIPS.items())       # السفن المتبقية للوضع
        self.placed_ships: Dict[str, Ship] = {}         # السفن التي تم وضعها

    def place_ship(self, ship_name: str, size: int, start_pos: Tuple[int, int], 
                  orientation: str) -> bool:
        """
        وضع سفينة في موقع محدد
        Args:
            ship_name: اسم السفينة
            size: حجم السفينة
            start_pos: موقع البداية (صف، عمود)
            orientation: الاتجاه ('horizontal' أو 'vertical')
        Returns:
            bool: True إذا تم الوضع بنجاح
        """
        # التحقق من أن السفينة متاحة للوضع
        if ship_name not in [s[0] for s in self.remaining_ships]:
            return False
            
        # إنشاء سفينة جديدة
        ship = Ship(ship_name, size)
        
        # محاولة وضع السفينة
        if self.grid.place_ship(ship, start_pos, orientation):
            # تحديث قوائم السفن
            self.placed_ships[ship_name] = ship
            self.remaining_ships.remove((ship_name, size))
            return True
            
        return False

    def place_ships_randomly(self) -> bool:
        """
        وضع جميع السفن بشكل عشوائي
        Returns:
            bool: True إذا تم وضع جميع السفن بنجاح
        """
        attempts = 0
        max_attempts = 200  # زيادة عدد المحاولات للشبكات الكبيرة
        original_remaining = self.remaining_ships.copy()
        
        while self.remaining_ships and attempts < max_attempts:
            ship_name, size = self.remaining_ships[0]
            orientation = random.choice(['horizontal', 'vertical'])
            
            # محاولة وضع السفينة في موقع عشوائي صالح
            valid_positions = self._get_valid_positions(size, orientation)
            if valid_positions:
                pos = random.choice(valid_positions)
                if self.place_ship(ship_name, size, pos, orientation):
                    continue
                    
            attempts += 1
            
            # إعادة المحاولة إذا فشلت محاولات كثيرة
            if attempts % 50 == 0:
                self.grid.clear()
                self.remaining_ships = original_remaining.copy()
                self.placed_ships.clear()
                attempts = 0
        
        # إذا فشل الوضع، إعادة التعيين للحالة الأصلية
        if self.remaining_ships:
            self.remaining_ships = original_remaining
            self.placed_ships.clear()
            self.grid = Grid(self.grid.size)
            return False
            
        return True

    def receive_shot(self, position: Tuple[int, int]) -> Tuple[bool, Optional[Ship]]:
        """
        معالجة طلقة من الخصم
        Returns:
            (hit_success, ship_if_sunk)
        """
        self.shots.append(position)
        return self.grid.receive_shot(position)

    def all_ships_sunk(self) -> bool:
        """التحقق من غرق جميع السفن"""
        return all(ship.is_sunk() for ship in self.placed_ships.values())

    def _get_valid_positions(self, ship_size: int, orientation: str) -> List[Tuple[int, int]]:
        """
        الحصول على جميع المواقع الصالحة لوضع سفينة
        Args:
            ship_size: حجم السفينة
            orientation: الاتجاه
        Returns:
            قائمة بالمواقع الصالحة
        """
        valid_positions = []
        grid_size = self.grid.size
        
        # حساب الحدود حسب الاتجاه
        if orientation == 'horizontal':
            max_row = grid_size
            max_col = grid_size - ship_size + 1
        else:  # vertical
            max_row = grid_size - ship_size + 1
            max_col = grid_size
        
        # فحص كل موقع محتمل
        for row in range(max_row):
            for col in range(max_col):
                positions = self.grid._calculate_ship_positions(ship_size, (row, col), orientation)
                if positions and self.grid._is_valid_placement(positions):
                    valid_positions.append((row, col))
                    
        return valid_positions

    # دوال مساعدة للحصول على معلومات اللعب
    def get_remaining_ships(self) -> List[Tuple[str, int]]:
        """الحصول على قائمة السفن المتبقية للوضع"""
        return self.remaining_ships

    def get_ship_positions(self, ship_name: str) -> List[Tuple[int, int]]:
        """الحصول على مواقع سفينة محددة"""
        if ship_name in self.placed_ships:
            return self.placed_ships[ship_name].get_positions()
        return []

    def get_shots_fired(self) -> List[Tuple[int, int]]:
        """الحصول على قائمة الطلقات"""
        return self.shots.copy()

    def get_hits(self) -> List[Tuple[int, int]]:
        """الحصول على قائمة الإصابات الناجحة"""
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'hit']

    def get_misses(self) -> List[Tuple[int, int]]:
        """الحصول على قائمة الطلقات الفاشلة"""
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'miss']