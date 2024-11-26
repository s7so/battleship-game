from typing import List, Tuple, Optional, Set
from .ship import Ship, ShipOrientation

class Grid:
    """
    الفئة دي بتمثل شبكة اللعب في لعبة Battleship
    المسؤوليات الرئيسية للفئة دي:
    1. إدارة أماكن السفن على الشبكة
    2. تتبع الطلقات والإصابات
    3. التحقق من صحة وضع السفن
    4. دعم تغيير حجم الشبكة (10×10 أو 15×15)
    """
    
    def __init__(self, size: int = 10):
        """
        دي دالة البداية اللي بتشتغل أول ما نعمل كائن من الفئة دي
        Args:
            size: حجم الشبكة (افتراضي 10)
        """
        self.size = size  # حجم الشبكة (10×10 أو 15×15)
        # مصفوفة ثنائية الأبعاد لتمثيل الشبكة
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships: List[Ship] = []          # قائمة السفن
        # استخدام Set للبحث السريع O(1)
        self.shots: Set[Tuple[int, int]] = set()    # مجموعة الطلقات
        self.hits: Set[Tuple[int, int]] = set()     # مجموعة الإصابات
        self.misses: Set[Tuple[int, int]] = set()   # مجموعة الطلقات الفاشلة

    def resize(self, new_size: int):
        """
        تغيير حجم الشبكة وإعادة تعيين كل البيانات
        Args:
            new_size: الحجم الجديد للشبكة
        """
        self.size = new_size
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships.clear()
        self.shots.clear()
        self.hits.clear()
        self.misses.clear()

    def place_ship(self, ship: Ship, start_pos: Tuple[int, int], orientation: str) -> bool:
        """
        محاولة وضع سفينة في موقع واتجاه محددين
        Args:
            ship: السفينة المراد وضعها
            start_pos: موقع البداية (صف، عمود)
            orientation: الاتجاه ('horizontal' أو 'vertical')
        Returns:
            bool: True إذا تم الوضع بنجاح
        """
        if not self._is_valid_orientation(orientation):
            return False
            
        positions = self._calculate_ship_positions(ship.size, start_pos, orientation)
        if not positions:
            return False

        if not self._is_valid_placement(positions):
            return False

        # وضع السفينة
        ship.position = positions
        ship.orientation = ShipOrientation.HORIZONTAL if orientation == 'horizontal' else ShipOrientation.VERTICAL
        self.ships.append(ship)
        
        # تحديث الشبكة
        for pos in positions:
            self.grid[pos[0]][pos[1]] = ship
            
        return True

    def _calculate_ship_positions(self, size: int, start_pos: Tuple[int, int], 
                                orientation: str) -> Optional[List[Tuple[int, int]]]:
        """
        حساب جميع المواقع التي ستشغلها السفينة
        Args:
            size: حجم السفينة
            start_pos: موقع البداية (صف، عمود)
            orientation: الاتجاه ('horizontal' أو 'vertical')
        Returns:
            List[Tuple[int, int]] | None: قائمة المواقع أو None إذا كان الوضع غير صالح
        """
        if not self._is_within_grid(start_pos):
            return None
            
        positions = []
        row, col = start_pos

        for i in range(size):
            if orientation == 'horizontal':
                new_pos = (row, col + i)
            else:  # vertical
                new_pos = (row + i, col)

            if not self._is_within_grid(new_pos):
                return None
            positions.append(new_pos)

        return positions

    def _is_within_grid(self, pos: Tuple[int, int]) -> bool:
        """
        التحقق من أن الموقع داخل حدود الشبكة
        Args:
            pos: الموقع (صف، عمود)
        Returns:
            bool: True إذا كان الموقع داخل الشبكة
        """
        row, col = pos
        return 0 <= row < self.size and 0 <= col < self.size

    def receive_shot(self, pos: Tuple[int, int]) -> Tuple[bool, Optional[Ship]]:
        """
        معالجة طلقة وإرجاع النتيجة
        Args:
            pos: الموقع (صف، عمود)
        Returns:
            - bool: نجاح الإصابة
            - Optional[Ship]: السفينة إذا غرقت
        Time Complexity: O(1) باستخدام Set للبحث
        """
        if not self._is_within_grid(pos) or pos in self.shots:
            return False, None

        self.shots.add(pos)
        row, col = pos
        ship = self.grid[row][col]

        if ship is None:
            self.misses.add(pos)
            return False, None

        self.hits.add(pos)
        ship.take_hit(pos)
        return True, ship if ship.is_sunk() else None

    def get_cell_state(self, pos: Tuple[int, int]) -> str:
        """
        الحصول على حالة خلية في موقع معين
        Args:
            pos: الموقع (صف، عمود)
        Returns:
            str: 'empty', 'ship', 'hit', 'miss', أو 'invalid'
        """
        if not self._is_within_grid(pos):
            return 'invalid'
            
        if pos in self.hits:
            return 'hit'
        if pos in self.misses:
            return 'miss'
        if self.grid[pos[0]][pos[1]] is not None:
            return 'ship'
        return 'empty'

    def _is_valid_placement(self, positions: List[Tuple[int, int]]) -> bool:
        """
        التحقق من صحة وضع السفينة:
        - لا تداخل مع سفن أخرى
        - لا تجاور مع سفن أخرى (حتى قطرياً)
        - داخل حدود الشبكة
        Args:
            positions: قائمة المواقع (صف، عمود)
        Returns:
            bool: True إذا كان الوضع صالح
        """
        for row, col in positions:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    adj_pos = (row + i, col + j)
                    if (self._is_within_grid(adj_pos) and 
                        self.grid[adj_pos[0]][adj_pos[1]] is not None):
                        return False
        return True

    def _is_valid_orientation(self, orientation: str) -> bool:
        """
        التحقق من صحة الاتجاه
        Args:
            orientation: الاتجاه ('horizontal' أو 'vertical')
        Returns:
            bool: True إذا كان الاتجاه صالح
        """
        return orientation in ['horizontal', 'vertical']

    def all_ships_sunk(self) -> bool:
        """
        التحقق من غرق جميع السفن
        Returns:
            bool: True إذا كانت كل السفن غرقت
        """
        return all(ship.is_sunk() for ship in self.ships)

    def get_all_ship_positions(self) -> Set[Tuple[int, int]]:
        """
        الحصول على جميع مواقع السفن
        Returns:
            Set[Tuple[int, int]]: مجموعة من المواقع (صف، عمود)
        """
        positions = set()
        for ship in self.ships:
            positions.update(ship.get_positions())
        return positions

    def get_shots_fired(self) -> Set[Tuple[int, int]]:
        """
        الحصول على جميع الطلقات
        Returns:
            Set[Tuple[int, int]]: مجموعة من المواقع (صف، عمود)
        """
        return self.shots.copy()

    def get_hits(self) -> Set[Tuple[int, int]]:
        """
        الحصول على جميع الإصابت الناجحة
        Returns:
            Set[Tuple[int, int]]: مجموعة من المواقع (صف، عمود)
        """
        return self.hits.copy()

    def get_misses(self) -> Set[Tuple[int, int]]:
        """
        الحصول على جميع الطلقات الفاشلة
        Returns:
            Set[Tuple[int, int]]: مجموعة من المواقع (صف، عمود)
        """
        return self.misses.copy()

    def clear(self):
        """
        إعادة تعيين الشبكة وكل البيانات
        """
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships.clear()
        self.shots.clear()
        self.hits.clear()
        self.misses.clear()

    def to_dict(self) -> dict:
        """
        تحويل الشبكة إلى قاموس لتسهيل عملية الحفظ
        """
        return {
            'size': self.size,
            'ships': [ship.to_dict() for ship in self.ships],
            'shots': list(self.shots),
            'hits': list(self.hits),
            'misses': list(self.misses)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Grid':
        """
        إنشاء شبكة من قاموس البيانات المحفوظة
        """
        grid = cls(data['size'])
        grid.shots = set(data['shots'])
        grid.hits = set(data['hits'])
        grid.misses = set(data['misses'])
        
        for ship_data in data['ships']:
            ship = Ship.from_dict(ship_data)
            grid.ships.append(ship)
            for pos in ship.position:
                grid.grid[pos[0]][pos[1]] = ship
                
        return grid

# مثال على استخدام الفئة
grid = Grid(size=15)  # إنشاء شبكة 15×15
ship = Ship("Battleship", 4)  # إنشاء سفينة
success = grid.place_ship(ship, (0, 0), "horizontal")  # وضع السفينة
hit, sunk_ship = grid.receive_shot((0, 0))  # تنفيذ طلقة
state = grid.get_cell_state((0, 0))  # الحصول على حالة خلية