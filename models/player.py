from typing import List, Tuple, Optional, Dict
import random
from .grid import Grid
from .ship import Ship
from utils.constants import SHIPS

class Player:
    """
    الفئة دي بتمثل اللاعب في لعبة Battleship.
    الفئة دي مسؤولة عن:
    - إدارة شبكة اللاعب (اللوحة اللي بيتم وضع السفن عليها)
    - وضع السفن على الشبكة
    - متابعة الطلقات اللي اتضربت والإصابات اللي حصلت
    """
    
    def __init__(self, grid_size: int = 10):
        """
        دي دالة البداية للاعب.
        بتعمل شبكة (لوحة) عشان اللاعب يحط السفن عليها.
        
        المدخلات:
            grid_size: حجم الشبكة (ممكن تكون 10x10 أو 15x15)
        """
        self.grid = Grid(grid_size)                      # شبكة اللاعب
        self.shots: List[Tuple[int, int]] = []          # قائمة لمتابعة الطلقات اللي اتضربت
        self.remaining_ships = list(SHIPS.items())       # السفن اللي لسه متحطتش على الشبكة
        self.placed_ships: Dict[str, Ship] = {}         # السفن اللي اتحطت على الشبكة

    def place_ship(self, ship_name: str, size: int, start_pos: Tuple[int, int], 
                  orientation: str) -> bool:
        """
        الدالة دي بتحط سفينة على الشبكة في مكان محدد.
        
        المدخلات:
            ship_name: اسم السفينة
            size: حجم السفينة (بتاخد كام خانة في الشبكة)
            start_pos: المكان اللي هتبدأ منه السفينة على الشبكة (صف، عمود)
            orientation: اتجاه السفينة ('horizontal' أفقي أو 'vertical' رأسي)
        
        المخرجات:
            bool: True لو السفينة اتحطت بنجاح، False لو محصلش
        """
        # بنتأكد إن السفينة متاحة عشان تتحط
        if ship_name not in [s[0] for s in self.remaining_ships]:
            return False
            
        # بنعمل سفينة جديدة
        ship = Ship(ship_name, size)
        
        # بنحاول نحط السفينة على الشبكة
        if self.grid.place_ship(ship, start_pos, orientation):
            # بنحدث قوائم السفن
            self.placed_ships[ship_name] = ship
            self.remaining_ships.remove((ship_name, size))
            return True
            
        return False

    def place_ships_randomly(self) -> bool:
        """
        الدالة دي بتحاول تحط كل السفن بشكل عشوائي على الشبكة.
        
        المخرجات:
            bool: True لو كل السفن اتحطت بنجاح، False لو محصلش
        """
        attempts = 0
        max_attempts = 200  # أقصى عدد محاولات لوضع السفن، خاصة للشبكات الكبيرة
        original_remaining = self.remaining_ships.copy()
        
        while self.remaining_ships and attempts < max_attempts:
            ship_name, size = self.remaining_ships[0]
            orientation = random.choice(['horizontal', 'vertical'])
            
            # بنحاول نحط السفينة في مكان عشوائي صحيح
            valid_positions = self._get_valid_positions(size, orientation)
            if valid_positions:
                pos = random.choice(valid_positions)
                if self.place_ship(ship_name, size, pos, orientation):
                    continue
                    
            attempts += 1
            
            # لو المحاولات كتير فشلت، بنعيد المحاولة من الأول
            if attempts % 50 == 0:
                self.grid.clear()
                self.remaining_ships = original_remaining.copy()
                self.placed_ships.clear()
                attempts = 0
        
        # لو فشلنا في وضع السفن، بنرجع للحالة الأصلية
        if self.remaining_ships:
            self.remaining_ships = original_remaining
            self.placed_ships.clear()
            self.grid = Grid(self.grid.size)
            return False
            
        return True

    def receive_shot(self, position: Tuple[int, int]) -> Tuple[bool, Optional[Ship]]:
        """
        الدالة دي بتتعامل مع الطلقة اللي اتضربت من الخصم.
        
        المدخلات:
            position: المكان اللي اتضربت فيه الطلقة على الشبكة (صف، عمود)
        
        المخرجات:
            مجموعة بتحتوي على:
            - قيمة منطقية بتوضح إذا كانت الطلقة أصابت هدف ولا لأ
            - السفينة اللي اتغرقت، لو في سفينة اتغرقت
        """
        self.shots.append(position)
        return self.grid.receive_shot(position)

    def all_ships_sunk(self) -> bool:
        """بنتأكد إذا كانت كل سفن اللاعب اتغرقت."""
        return all(ship.is_sunk() for ship in self.placed_ships.values())

    def _get_valid_positions(self, ship_size: int, orientation: str) -> List[Tuple[int, int]]:
        """
        الدالة دي بتلاقي كل الأماكن الصحيحة على الشبكة اللي ممكن نحط فيها سفينة.
        
        المدخلات:
            ship_size: حجم السفينة
            orientation: اتجاه السفينة ('horizontal' أفقي أو 'vertical' رأسي)
        
        المخرجات:
            قائمة بالأماكن الصحيحة (صف، عمود) اللي ممكن نحط فيها السفينة
        """
        valid_positions = []
        grid_size = self.grid.size
        
        # بنحسب الحدود بناءً على الاتجاه
        if orientation == 'horizontal':
            max_row = grid_size
            max_col = grid_size - ship_size + 1
        else:  # vertical
            max_row = grid_size - ship_size + 1
            max_col = grid_size
        
        # بنفحص كل مكان ممكن
        for row in range(max_row):
            for col in range(max_col):
                positions = self.grid._calculate_ship_positions(ship_size, (row, col), orientation)
                if positions and self.grid._is_valid_placement(positions):
                    valid_positions.append((row, col))
                    
        return valid_positions

    # دوال مساعدة للحصول على معلومات اللعبة
    def get_remaining_ships(self) -> List[Tuple[str, int]]:
        """بنجيب قائمة بالسفن اللي لسه متحطتش على الشبكة."""
        return self.remaining_ships

    def get_ship_positions(self, ship_name: str) -> List[Tuple[int, int]]:
        """بنجيب أماكن سفينة معينة على الشبكة."""
        if ship_name in self.placed_ships:
            return self.placed_ships[ship_name].get_positions()
        return []

    def get_shots_fired(self) -> List[Tuple[int, int]]:
        """بنجيب قائمة بكل الطلقات اللي اللاعب ضربها."""
        return self.shots.copy()

    def get_hits(self) -> List[Tuple[int, int]]:
        """بنجيب قائمة بكل الإصابات الناجحة اللي اللاعب عملها."""
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'hit']

    def get_misses(self) -> List[Tuple[int, int]]:
        """بنجيب قائمة بكل الطلقات اللي اللاعب فشل فيها."""
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'miss']