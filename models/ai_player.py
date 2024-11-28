from typing import Tuple, Optional, List
import random
from .player import Player
from .ship import Ship
from .grid import Grid
import logging

class AIPlayer(Player):
    """
    Battleship AI Strategy Documentation
    ==================================

   استراتيجيات الذكاء الاصطناعي المستخدمة في لعبة السفن الحربية

   1. الاستراتيجية العامة (Overall Strategy)
    ----------------------------------------
   يستخدم AI مزيجاً من أربع استراتيجيات رئيسية:
   - البحث الذكي (Smart Search)
   - التتبع الموجه (Directed Tracking)
   - تحليل الكثافة (Density Analysis)
   - التكيف مع حجم الشبكة (Grid Size Adaptation)

   2. مراحل اللعب (Game Phases)
    ---------------------------
   أ. مرحلة البحث (Search Phase):
      - استخدام نمط رقعة الشطرنج للبحث الأولي
      - تقسيم الشبكة إلى مناطق وتحليل كثافتها
      - اختيار الأهداف بناءً على احتملية وجود السفن

   ب. مرحلة التتبع (Hunt Phase):
      - تفعل عند إصابة سفينة
      - تركيز على المواقع المجاورة للإصابة
      - تحديد وتتبع اتجاه السفينة

   ج. مرحلة الإغراق (Sink Phase):
      - تتبع السفينة المكتشفة حتى إغراقها
      - استخدام معلومات الإصابات السابقة
      - تغيير الاتجاه عند الضرورة

   3. تقنيات تحسين الأداء (Performance Optimization)
   ----------------------------------------------
   أ. تحليل الكثافة:
      - تقسيم الشبكة إلى قطاعات
      - حساب كثافة الأهداف المحتملة في كل قطاع
      - ترجيح الاختيار نحو المناطق عالية الكثافة

   ب. التكيف مع حجم الشبكة:
      - تعديل حجم القطاعات حسب حجم الشبكة
      - توسيع نطاق البحث في الشبكات الكبيرة
      - تعديل استراتيجيات الاستهداف

   ج. نظام الأولويات:
      - حساب أولوية كل هدف محتمل
      - مراعاة المسافة من الإصابات السابقة
      - تحليل أنماط توزيع السفن

   4. خوارزميات القرار (Decision Algorithms)
   ---------------------------------------
   أ. اختيار الهدف:
      1. فحص وضع التتبع (Hunting Mode)
      2. فحص الأهداف المحتملة (Potential Targets)
      3. اختيار هدف عشوائي ذكي (Smart Random)

   ب. تحديد الأولويات:
      1. المسافة من الإصابات السابقة
      2. كثافة المنطقة المحيطة
      3. اتجاه السفينة المحتمل

   ج. تحليل النتائج:
      1. تحديث قائمة الإصابات
      2. تحديث الأهداف المحتملة
      3. تعديل الاستراتيجية حسب النتيجة

   5. التعامل مع الحالات الخاصة (Special Cases)
   ------------------------------------------
   أ. تغيير الاتجاه:
      - عند الوصول لحدود الشبكة
      - عند اكتشاف خطأ في الاتجاه
      - عند عدم إمكانية المتابعة في نفس الاتجاه

   ب. إعادة التقييم:
      - بعد إغراق سفينة
      - عند فشل استراتيجية معينة
      - عند تغير ظروف اللعب

   6. مؤشرات الأداء (Performance Metrics)
   ------------------------------------
   - متوسط عدد الطلقات لإغراق سفينة
   - نسبة الإصابات الناجحة
   - كفاءة التتبع بع الإصابة الأوى
   - سرعة اتشاف وإغراق السفن

   7. التحسينات المستمرة (Continuous Improvements)
   ---------------------------------------------
   - تحليل أنماط اللعب
   - تحسين خوارزميات اتخاذ القرار
   - تطوير استراتيجيات جديدة
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # متغيرات تتبع حالة اللعب
        self.last_hit = None  # آخر إصابة ناجحة
        self.potential_targets = []  # قائمة الأهداف المحتملة
        self.hit_positions = set()  # مواقع الإصابات
        self.hunting_mode = False  # وضع تتبع السفينة
        self.hunt_direction = None  # اتجاه تتبع السفينة
        self.first_hit = None  # أول إصابة في السفينة الحالية

    def get_shot_position(self) -> Tuple[int, int]:
        """Get next shot position with improved validation"""
        try:
            # First check if we're in hunting mode (following up on a hit)
            if self.hunting_mode and self.potential_targets:
                return self.potential_targets.pop(0)
            
            # Use probability map to find best shot
            probability_map = self._get_ship_probability_map()
            best_positions = []
            max_probability = 0

            # Find positions with highest probability
            for row in range(self.grid.size):
                for col in range(self.grid.size):
                    if (row, col) in self.shots:
                        continue
                    prob = probability_map[row][col]
                    if prob > max_probability:
                        max_probability = prob
                        best_positions = [(row, col)]
                    elif prob == max_probability:
                        best_positions.append((row, col))

            # Return random position from best available positions
            if best_positions:
                return random.choice(best_positions)
            
            raise ValueError("No available positions to shoot")

        except Exception as e:
            self.logger.error(f"Error in get_shot_position: {e}")
            # Fallback to safe random shot
            return self._get_safe_random_shot()

    def _get_safe_random_shot(self) -> Tuple[int, int]:
        """Get a random unshot position as fallback"""
        available = [
            (row, col)
            for row in range(self.grid.size)
            for col in range(self.grid.size)
            if (row, col) not in self.shots
        ]
        
        if not available:
            # If somehow no positions are available, return corner position
            # This should never happen in normal gameplay
            self.logger.error("No available positions for safe random shot")
            return (0, 0)
        
        return random.choice(available)

    def update_strategy(self, hit: bool, position: Tuple[int, int]):
        """Update AI strategy based on shot result"""
        # Add position to shots set
        self.shots.add(position)
        
        if hit:
            # Add to hit positions
            self.hit_positions.add(position)
            
            # Enter hunting mode if not already in it
            if not self.hunting_mode:
                self.hunting_mode = True
                self.first_hit = position
                
            # Add adjacent positions as potential targets
            row, col = position
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                new_pos = (row + dr, col + dc)
                if self._is_valid_target(new_pos) and new_pos not in self.shots:
                    self.potential_targets.append(new_pos)
        else:
            # If miss and in hunting mode, update hunt pattern
            if self.hunting_mode:
                self._update_hunt_pattern_for_miss(position)
            else:
                self._update_general_hunt_pattern()

    def _update_hunt_pattern_for_miss(self, miss_position: Tuple[int, int]):
        """Update hunting pattern when a shot misses"""
        if not self.first_hit:
            return
        
        # Determine direction of miss relative to first hit
        row_diff = miss_position[0] - self.first_hit[0] 
        col_diff = miss_position[1] - self.first_hit[1]
        
        # Remove potential targets in the miss direction
        self.potential_targets = [
            pos for pos in self.potential_targets
            if (pos[0] - self.first_hit[0]) * row_diff <= 0 and
               (pos[1] - self.first_hit[1]) * col_diff <= 0
        ]
        
        # If all directions exhausted, reset hunting mode
        if not self.potential_targets:
            self._reset_hunting()

    def _update_general_hunt_pattern(self):
        """Update general hunting pattern based on shot history"""
        if len(self.shots) > 10:  # After enough shots
            hit_ratio = len(self.hit_positions) / len(self.shots)
            
            if hit_ratio < 0.2:  # If hit rate is low
                self._switch_to_focused_search()
            elif hit_ratio > 0.4:  # If hit rate is high
                self._concentrate_on_current_area()

    def _add_adjacent_targets(self, position: Tuple[int, int]):
        """
        إضافة المواقع المجاورة للإصابة كأهداف محتملة
        """
        row, col = position
        adjacent_positions = [
            (row - 1, col),  # فوق
            (row + 1, col),  # تحت
            (row, col - 1),  # يسار
            (row, col + 1)  # يمين
        ]

        # إضافة المواقع الصالحة فقط
        for pos in adjacent_positions:
            if self._is_valid_target(pos):
                self.potential_targets.append(pos)

    def _add_directional_targets(self, position: Tuple[int, int], direction: str):
        """
        إضافة المواقع في نفس اتجاه السفينة كأهداف محتملة
        """
        row, col = position
        if direction == 'horizontal':
            # إضافة المواقع على نفس الصف
            targets = [(row, col - 1), (row, col + 1)]
        else:  # vertical
            # إضافة المواقع على نفس العمود
            targets = [(row - 1, col), (row + 1, col)]

        # إضافة المواقع الصالحة فقط
        for pos in targets:
            if self._is_valid_target(pos) and pos not in self.potential_targets:
                self.potential_targets.append(pos)

    def _try_new_direction(self):
        """
        محاولة اتجاه جديد عندما يفشل الاتجاه الحالي
        """
        if self.first_hit:
            # إعادة إضافة المواقع المجاورة لأول إصابة
            self._add_adjacent_targets(self.first_hit)

    def _adjust_hunting_strategy(self):
        """تعديل استراتيجية التتبع"""
        if self.hunt_direction:
            # تغيير الاتجاه إذا فشلت المحاولة الحالية
            self.hunt_direction = self._get_perpendicular_direction()
            if not self._get_next_directional_shot():
                self._reset_hunting()

    def _get_hunting_shot(self) -> Optional[Tuple[int, int]]:
        """
        تحديد الطلقة التالية في وضع التتبع
        """
        if not self.hit_positions:
            return None

        # الحصول على آخر إصابة
        last_hit = list(self.hit_positions)[-1]
        row, col = last_hit

        # المواقع المحتملة حول آخر إصابة
        possible_shots = [
            (row - 1, col),  # فوق
            (row + 1, col),  # تحت
            (row, col - 1),  # يسار
            (row, col + 1)  # يمين
        ]

        # تصفية المواقع غير الصالحة
        valid_shots = [
            pos for pos in possible_shots
            if self._is_valid_target(pos)
        ]

        return random.choice(valid_shots) if valid_shots else None

    def _get_smart_target(self) -> Tuple[int, int]:
        """
        اختيار الهدف الأعلى احتمالية من الأهداف المحتملة.
        
        الاستراتيجية:
        1. اختيار من قائمة الأهداف المتملة
        2. التحقق من صلاحية الهدف
        3. العود للطلقات العشوائية إذا لم تتوفر أهداف
        
        Returns:
            Tuple[int, int]: موقع الهدف المختار
        """
        while self.potential_targets:
            target = self.potential_targets.pop(0)
            if self._is_valid_target(target):
                return target
        return self._get_random_shot()

    def _get_random_shot(self) -> Tuple[int, int]:
        """
        اختيار موقع عشوائي للطلقة مع تحسينات للشبكات الكبيرة.
        
        استراتيجيات التحسين:
        1. تقسيم الشبكة إلى مناطق
        2. حساب كثافة كل منطقة
        3. اختيار المناطق ذات الكثافة الأعلى
        4. تجنب المناطق المحيطة بالسفن الغارقة
        
        Returns:
            Tuple[int, int]: موقع الطلقة العشوائية
        """
        grid_size = self.grid.size

        # تقسيم الشبكة إلى مناطق
        sector_size = 5 if grid_size > 10 else 3
        sectors = []

        # حساب كثافة كل منطقة
        for base_row in range(0, grid_size, sector_size):
            for base_col in range(0, grid_size, sector_size):
                sector_density = 0
                valid_positions = []

                # فحص كل موقع في المنطقة
                for r in range(base_row, min(base_row + sector_size, grid_size)):
                    for c in range(base_col, min(base_col + sector_size, grid_size)):
                        pos = (r, c)
                        if self._is_valid_target(pos):
                            # التحقق من عدم وجود سفن غارقة في المنطقة المحيطة
                            is_near_sunk = any(
                                self._is_adjacent_to_sunk_ship(pos, ship)
                                for ship in self.grid.ships
                                if ship.is_sunk()
                            )
                            if not is_near_sunk:
                                valid_positions.append(pos)
                                # زيادة الكثافة إذا كان الموقع مناسباً للسفن المتبقية
                                sector_density += self._calculate_position_value(pos)

                if valid_positions:
                    # حساب متوسط الكثافة للمنطقة
                    avg_density = sector_density / len(valid_positions)
                    sectors.append((valid_positions, avg_density))

        # اختيار منطقة بناءً على الكثافة
        if sectors:
            # حساب مجموع الكثافات
            total_density = sum(density for _, density in sectors)
            if total_density > 0:
                # اختيار نطقة عشوائياً مع ترجيح المناطق ذات الكثافة الأعلى
                r = random.random() * total_density
                current = 0
                for positions, density in sectors:
                    current += density
                    if r <= current:
                        return random.choice(positions)

        # إذا لم ند مواقع منابة، نختار أي موقع متاح
        available = [
            (r, c)
            for r in range(grid_size)
            for c in range(grid_size)
            if self._is_valid_target((r, c))
        ]
        return random.choice(available) if available else (0, 0)

    def _calculate_position_value(self, pos: Tuple[int, int]) -> float:
        """
        حساب قيمة الموقع بناءً على عدة عوامل.
        
        العوامل:
        1. المسافة من حدود الشبكة
        2. المسافة من الطلقات السابقة
        3. إمكانية وضع السفن المتبقية
        
        Returns:
            float: قيمة الموقع (أعلى = أفضل)
        """
        row, col = pos
        value = 1.0

        # المسافة من حدود الشبكة
        edge_distance = min(
            row,
            col,
            self.grid.size - 1 - row,
            self.grid.size - 1 - col
        )
        value *= (edge_distance + 1) / (self.grid.size / 2)

        # المسافة من الطلقات السابقة
        for shot_row, shot_col in self.shots:
            distance = abs(row - shot_row) + abs(col - shot_col)
            if distance <= 2:
                value *= 0.8  # تقليل القيمة للمواقع الريبة من الطلقات السابقة

        # إمكانية وضع السفن المتبقية
        for ship_name, ship_size in self.remaining_ships:
            # فحص الاتجاه الأفقي
            horizontal_fit = all(
                self._is_valid_target((row, c))
                for c in range(col, min(col + ship_size, self.grid.size))
            )
            # فحص الاتجاه الرأسي
            vertical_fit = all(
                self._is_valid_target((r, col))
                for r in range(row, min(row + ship_size, self.grid.size))
            )
            if horizontal_fit or vertical_fit:
                value *= 1.2  # زيادة القيمة إذا كان الموقع مناسباً لسفينة متبقية

        return value

    def _update_potential_targets(self, position: Tuple[int, int]):
        """
        تحديث قائمة الأهداف المحتملة بناءً على إصابة مع تحسينات للشبكات الكبيرة.
        
        استراتيجيات التحسين:
        1. تحليل الكثافة: تحديد المناطق ذات احتمالية أعلى لوجود السفن
        2. التحليل الإحصائي: استخدام نمط توزيع السفن المتبقية
        3. الأولوية الديناميكية: تعديل أولويات الأهداف بناءً على حجم الشبكة
        
        Args:
            position: موقع الإصابة الأخيرة
        """
        row, col = position
        grid_size = self.grid.size

        # تحديد نطاق البحث بناءً على حجم الشبكة
        search_radius = 2 if grid_size > 10 else 1

        # جمع المواقع المجاورة مع الأخذ في الاعتبار نطاق البحث
        adjacent = []
        for r in range(-search_radius, search_radius + 1):
            for c in range(-search_radius, search_radius + 1):
                if r == 0 and c == 0:
                    continue
                new_pos = (row + r, col + c)
                if self._is_valid_target(new_pos):
                    # حساب الأولوية بناءً على المسافة
                    priority = 1.0 / (abs(r) + abs(c))
                    adjacent.append((new_pos, priority))

        # ترتيب المواقع حسب الأولوية
        adjacent.sort(key=lambda x: x[1], reverse=True)
        new_targets = [pos for pos, _ in adjacent if pos not in self.potential_targets]

        # تحليل نمط توزيع السفن المتبقية
        if len(self.hit_positions) > 1:
            direction = self._determine_ship_direction()
            if direction:
                new_targets.sort(key=lambda pos:
                self._calculate_target_priority(pos, direction))

        self.potential_targets.extend(new_targets)

    def _calculate_target_priority(self, position: Tuple[int, int], direction: str) -> float:
        """
        حساب أولوية الهدف بناءً على عدة عوامل.
        
        عوامل لأولوية المحسنة:
        1. المسافة من الإصابات السابقة
        2. نط توزيع الإصابات
        3. احتمالية وجود سفن في المنطقة
        4. حج السفن المتبقية
        5. المسافة من حدود الشبكة
        
        Returns:
            float: قيمة الأولوية (أعلى = أفضل)
        """
        row, col = position
        priority = 1.0

        # المسافة من الإصابات السابقة
        if self.hit_positions:
            min_distance = float('inf')
            for hit_pos in self.hit_positions:
                distance = abs(row - hit_pos[0]) + abs(col - hit_pos[1])
                min_distance = min(min_distance, distance)
            # أولوية أعلى للمواقع القريبة من الإصابات
            priority *= (1.0 / (min_distance + 1)) * 2

        # نمط توزيع الإصابات
        if direction == 'horizontal':
            # أولوية أعلى للمواقع على نفس الصف
            if any(hit[0] == row for hit in self.hit_positions):
                priority *= 2.0
            # أولوية أقل للمواقع على نفس العمود
            if any(hit[1] == col for hit in self.hit_positions):
                priority *= 0.5
        else:  # vertical
            # أولوية أعلى للمواقع على نفس العمود
            if any(hit[1] == col for hit in self.hit_positions):
                priority *= 2.0
            # أولوية أقل للمواقع على نفس الصف
            if any(hit[0] == row for hit in self.hit_positions):
                priority *= 0.5

        # احتمالية وجود سفن في المنطقة
        for ship_name, ship_size in self.remaining_ships:
            # فحص إمكانية وضع السفينة أفقياً
            if direction == 'horizontal':
                can_fit = True
                for c in range(col - ship_size + 1, col + ship_size):
                    if not (0 <= c < self.grid.size) or (row, c) in self.shots:
                        can_fit = False
                        break
                if can_fit:
                    priority *= 1.5
            # فحص إمكانية وضع السفينة رأسياً
            else:
                can_fit = True
                for r in range(row - ship_size + 1, row + ship_size):
                    if not (0 <= r < self.grid.size) or (r, col) in self.shots:
                        can_fit = False
                        break
                if can_fit:
                    priority *= 1.5

        # المسافة من حدود الشبكة
        edge_distance = min(
            row,
            col,
            self.grid.size - 1 - row,
            self.grid.size - 1 - col
        )
        # أولوية أعلى للمواقع البعيدة عن الحدود
        priority *= (edge_distance + 1) / (self.grid.size / 2)

        # تعديل الأولوية بناءً على نمط اللعب
        if len(self.shots) > 0:
            hit_ratio = len(self.hit_positions) / len(self.shots)
            if hit_ratio > 0.3:  # إذا كان معدل الإصابة جيد
                # زيادة الأولوية للمواقع القريبة من الإصابات
                priority *= 1.5

        return priority

    def _calculate_area_density(self, position: Tuple[int, int], radius: int = 2) -> float:
        """
        حسا كثافة الأهداف المحتملة في منطقة محددة.
        
        Args:
            position: الموقع المركزي
            radius: نصف قطر البحث
        Returns:
            float: قيمة الكثافة (0.0 - 1.0)
        """
        row, col = position
        valid_positions = 0
        empty_positions = 0

        for r in range(row - radius, row + radius + 1):
            for c in range(col - radius, col + radius + 1):
                if self._is_valid_target((r, c)):
                    valid_positions += 1
                    if (r, c) not in self.shots:
                        empty_positions += 1

        return empty_positions / max(valid_positions, 1)

    def _determine_ship_direction(self) -> Optional[str]:
        """
        تحديد اتجاه السفينة من الإصابات المتعددة
        Returns: 'horizontal', 'vertical', أو None
        """
        hits = list(self.hit_positions)
        if len(hits) < 2:
            return None

        row_diff = hits[-1][0] - hits[-2][0]
        col_diff = hits[-1][1] - hits[-2][1]

        if row_diff != 0:
            return 'vertical'
        if col_diff != 0:
            return 'horizontal'
        return None

    def _get_next_directional_shot(self) -> Optional[Tuple[int, int]]:
        """
        تحديد اطلقة التالية في الاتجاه الحالي للتتبع.
        يأخذ في الاعتبار:
        - حدود الشبكة
        - الطلقات السابقة
        - اتجاه السفينة
        - أقصى حجم للسفينة المتبقية
        """
        if not self.hunt_direction or not self.first_hit:
            return None

        # ترتيب الإصابات حسب الموقع
        hits = sorted(self.hit_positions)
        last_hit = hits[-1]
        row, col = last_hit

        # تحديد المواقع المحتملة باءً على الاتجاه
        if self.hunt_direction == 'horizontal':
            # محاولة الضرب يميناً ويساراً
            possible = [
                (row, col + 1),  # يمين
                (row, col - 1),  # يسار
                (row, min(hit[1] for hit in hits) - 1),  # أقصى يسار
                (row, max(hit[1] for hit in hits) + 1)  # أقى يمين
            ]
        else:  # vertical
            # محاولة الضرب أعلى وأسفل
            possible = [
                (row + 1, col),  # أسفل
                (row - 1, col),  # أعلى
                (min(hit[0] for hit in hits) - 1, col),  # أقصى أعلى
                (max(hit[0] for hit in hits) + 1, col)  # أقصى أسفل
            ]

        # فلترة المواقع الصالحة
        valid_shots = [
            pos for pos in possible
            if self._is_valid_target(pos) and
               not self._is_adjacent_to_sunk_ship(pos, None)
        ]

        # ترتيب المواقع حسب الأولوية
        if valid_shots:
            return min(valid_shots, key=lambda pos: self._calculate_target_priority(pos, self.hunt_direction))

        return None

    def _is_valid_target(self, pos: Tuple[int, int]) -> bool:
        """
        التحقق من صلاحية الموقع كهدف
        Args:
            pos: الموقع المراد فحصه
        Returns:
            bool: True إذا كان المقع صالح للضرب
        """
        try:
            row, col = pos
            grid_size = self.grid.size

            # التحقق من أن الموقع داخل حدود الشبكة
            if not (0 <= row < grid_size and 0 <= col < grid_size):
                return False

            # التحقق من أن الموقع لم يتم ضربه من قبل
            if pos in self.shots:
                return False

            # التحقق من حالة الخلية في شبكة الخصم
            if hasattr(self, 'opponent_grid') and self.opponent_grid:
                cell_state = self.opponent_grid.get_cell_state(pos)
                if cell_state in ['hit', 'miss']:
                    return False

            # الحقق من أنه ليس بجوار سفينة غارقة
            for ship in self.grid.ships:
                if ship.is_sunk() and self._is_adjacent_to_sunk_ship(pos, ship):
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Error in _is_valid_target: {e}")
            return False

    def _reset_hunting(self):
        """Reset hunting mode state"""
        self.hunting_mode = False
        self.first_hit = None
        self.hunt_direction = None
        self.potential_targets = []

    def _is_adjacent_to_sunk_ship(self, pos: Tuple[int, int], ship: Optional[Ship]) -> bool:
        """
        التحقق مما إذا كان الموقع مجاوراً لسفينة غارقة
        Args:
            pos: الموقع المراد فحصه
            ship: السفينة الغارقة (يمكن أن تكون None)
        """
        if ship is None:
            # فحص جميع السفن الغارقة
            for s in self.grid.ships:
                if s.is_sunk():
                    for ship_pos in s.position:
                        if abs(pos[0] - ship_pos[0]) <= 1 and abs(pos[1] - ship_pos[1]) <= 1:
                            return True
            return False
        else:
            # فحص سفينة محددة
            for ship_pos in ship.position:
                if abs(pos[0] - ship_pos[0]) <= 1 and abs(pos[1] - ship_pos[1]) <= 1:
                    return True
            return False

    def _get_perpendicular_direction(self) -> str:
        """الحصول على الاتجاه العمودي على الاتجاه الحالي"""
        return 'vertical' if self.hunt_direction == 'horizontal' else 'horizontal'

    def _is_in_line_with_hits(self, pos: Tuple[int, int], direction: str) -> bool:
        """
        التحقق مما إذا كان الموقع في نفس خط الإصابات السابقة
        """
        for hit in self.hit_positions:
            if direction == 'horizontal' and pos[0] == hit[0]:
                return True
            if direction == 'vertical' and pos[1] == hit[1]:
                return True
        return False

    def to_dict(self) -> dict:
        """
        تحويل AI إلى قاموس لتسهيل عملية الحفظ
        """
        try:
            base_dict = super().to_dict()  # نحصل على بيانات الفئة الأساسية
            return {
                **base_dict,
                'last_hit': self.last_hit,
                'potential_targets': list(self.potential_targets),  # تحويل القائمة إلى list
                'hit_positions': list(self.hit_positions),  # تحويل المجموعة إلى list
                'hunting_mode': self.hunting_mode,
                'hunt_direction': self.hunt_direction,
                'first_hit': self.first_hit,
                'shots': list(self.shots)  # تأكد من حفظ الطلقات السابقة
            }
        except Exception as e:
            self.logger.error(f"Error in to_dict: {e}")
            # إرجاع حالة افتراضية آمنة
            return {
                'grid': self.grid.to_dict() if self.grid else None,
                'shots': [],
                'remaining_ships': [],
                'placed_ships': {},
                'last_hit': None,
                'potential_targets': [],
                'hit_positions': [],
                'hunting_mode': False,
                'hunt_direction': None,
                'first_hit': None
            }

    @classmethod
    def from_dict(cls, data: dict) -> 'AIPlayer':
        """إنشاء AI من قاموس البيانات المحفوظة"""
        try:
            # إنشاء كائن AI جديد
            ai = cls()
            
            # استعادة الشبكة
            if 'grid' in data and data['grid']:
                try:
                    ai.grid = Grid.from_dict(data['grid'])
                except Exception as e:
                    ai.logger.error(f"Error loading grid: {e}")
                    ai.grid = Grid()
                
            # استعادة الطلقات بشكل آمن
            try:
                ai.shots = {
                    tuple(shot) if isinstance(shot, list) else shot
                    for shot in data.get('shots', [])
                    if isinstance(shot, (list, tuple)) and len(shot) == 2
                }
            except Exception as e:
                ai.logger.error(f"Error loading shots: {e}")
                ai.shots = set()

            # استعادة السفن المتبقية
            ai.remaining_ships = data.get('remaining_ships', [])

            # استعادة السفن الموضوعة
            try:
                placed_ships_data = data.get('placed_ships', {})
                ai.placed_ships = {
                    name: Ship.from_dict(ship_data)
                    for name, ship_data in placed_ships_data.items()
                }
            except Exception as e:
                ai.logger.error(f"Error loading placed ships: {e}")
                ai.placed_ships = {}

            # استعادة حالة AI
            try:
                # تحويل الإحداثيات إلى tuples
                last_hit = data.get('last_hit')
                ai.last_hit = tuple(last_hit) if isinstance(last_hit, (list, tuple)) else None

                potential_targets = data.get('potential_targets', [])
                ai.potential_targets = [
                    tuple(pos) if isinstance(pos, list) else pos
                    for pos in potential_targets
                    if isinstance(pos, (list, tuple)) and len(pos) == 2
                ]

                hit_positions = data.get('hit_positions', [])
                ai.hit_positions = {
                    tuple(pos) if isinstance(pos, list) else pos
                    for pos in hit_positions
                    if isinstance(pos, (list, tuple)) and len(pos) == 2
                }

                ai.hunting_mode = bool(data.get('hunting_mode', False))
                ai.hunt_direction = data.get('hunt_direction')

                first_hit = data.get('first_hit')
                ai.first_hit = tuple(first_hit) if isinstance(first_hit, (list, tuple)) else None

            except Exception as e:
                ai.logger.error(f"Error loading AI state: {e}")
                ai._reset_hunting()

            # تنظيف وتحديث الحالة النهائية
            ai._clean_state()

            return ai

        except Exception as e:
            ai.logger.error(f"Critical error in from_dict: {e}")
            # إجاع AI جديد في حالة الفشل
            return cls()

    def _clean_state(self):
        """
        تنظيف وتحديث حالة AI
        """
        try:
            # التأكد من وجود كل المتغيرات الأساسية
            if not hasattr(self, 'grid'):
                self.grid = Grid()
            if not hasattr(self, 'shots'):
                self.shots = set()
            if not hasattr(self, 'hit_positions'):
                self.hit_positions = set()
            if not hasattr(self, 'potential_targets'):
                self.potential_targets = []

            # تحويل كل الإحداثيات إلى tuples
            self.shots = {
                tuple(pos) if isinstance(pos, list) else pos
                for pos in self.shots
                if isinstance(pos, (list, tuple)) and len(pos) == 2
            }

            self.hit_positions = {
                tuple(pos) if isinstance(pos, list) else pos
                for pos in self.hit_positions
                if isinstance(pos, (list, tuple)) and len(pos) == 2
            }

            self.potential_targets = [
                tuple(pos) if isinstance(pos, list) else pos
                for pos in self.potential_targets
                if isinstance(pos, (list, tuple)) and len(pos) == 2
            ]

            # تنظيف الأهداف المحتملة
            self.potential_targets = [
                pos for pos in self.potential_targets
                if pos not in self.shots
            ]

            # التحقق من حالة التتبع
            if not self.hit_positions:
                self.hunting_mode = False
                self.hunt_direction = None
                self.first_hit = None

            # التحقق من صحة last_hit و first_hit
            if self.last_hit and not isinstance(self.last_hit, tuple):
                self.last_hit = None
            if self.first_hit and not isinstance(self.first_hit, tuple):
                self.first_hit = None

        except Exception as e:
            self.logger.error(f"Error in _clean_state: {e}")
            self._reset_hunting()

    def _get_ship_probability_map(self) -> List[List[float]]:
        """
        إنشاء خريطة احتمالات لوجود السفن في كل موقع.
        
        Returns:
            List[List[float]]: مصفوفة تحتوي على احتمالية وجود سفينة في كل موقع
        """
        grid_size = self.grid.size
        probability_map = [[1.0] * grid_size for _ in range(grid_size)]

        # تقليل احتمالية المواقع القريبة من الحدود
        for row in range(grid_size):
            for col in range(grid_size):
                edge_distance = min(
                    row, col,
                    grid_size - 1 - row,
                    grid_size - 1 - col
                )
                probability_map[row][col] *= (edge_distance + 1) / (grid_size / 2)

        # تصفي احتمالية المواقع المستخدمة
        for row, col in self.shots:
            probability_map[row][col] = 0.0

        # زيادة احتمالية المواقع حول الإصابات
        for hit_pos in self.hit_positions:
            row, col = hit_pos
            for r in range(max(0, row - 2), min(grid_size, row + 3)):
                for c in range(max(0, col - 2), min(grid_size, col + 3)):
                    if self._is_valid_target((r, c)):
                        distance = abs(r - row) + abs(c - col)
                        probability_map[r][c] *= (3.0 / (distance + 1))

        return probability_map

    def _update_hunt_pattern(self):
        """
        تحديث نمط البحث بناءً على نتائج الطلقات السابقة
        """
        if len(self.shots) > 10:  # بعد عدد كافٍ من الطلقات
            hit_ratio = len(self.hit_positions) / len(self.shots)

            if hit_ratio < 0.2:  # إذا كان معدل الإصابة منفض
                # تغيير نمط البحث إلى نمط أكثر تركيزاً
                self._switch_to_focused_search()
            elif hit_ratio > 0.4:  # إذا كان معدل الإصابة مرتفع
                # الاستمرار في نفس المنطقة
                self._concentrate_on_current_area()

    def _switch_to_focused_search(self):
        """Switch to a more focused search pattern"""
        # Clear existing potential targets
        self.potential_targets = []
        
        # Get probability map
        prob_map = self._get_ship_probability_map()
        
        # Add high probability positions to potential targets
        for row in range(self.grid.size):
            for col in range(self.grid.size):
                if prob_map[row][col] > 1.5 and (row, col) not in self.shots:
                    self.potential_targets.append((row, col))
        
        # Sort targets by probability
        self.potential_targets.sort(
            key=lambda pos: prob_map[pos[0]][pos[1]], 
            reverse=True
        )

    def _concentrate_on_current_area(self):
        """Continue searching in the current successful area"""
        if not self.hit_positions:
            return
        
        # Get the most recent hit
        last_hit = list(self.hit_positions)[-1]
        row, col = last_hit
        
        # Add adjacent positions in a wider radius
        for r in range(max(0, row - 2), min(self.grid.size, row + 3)):
            for c in range(max(0, col - 2), min(self.grid.size, col + 3)):
                pos = (r, c)
                if (pos not in self.shots and 
                    pos not in self.potential_targets and 
                    self._is_valid_target(pos)):
                    self.potential_targets.append(pos)

    def _optimize_target_selection(self, targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        تحسين ترتيب الأهداف المحتملة
        
        Args:
            targets: قائمة الأهداف المحتملة
        Returns:
            List[Tuple[int, int]]: قائمة الأهداف مرتبة حسب الأولوية
        """
        probability_map = self._get_ship_probability_map()

        # حساب قيمة كل هدف
        target_values = []
        for pos in targets:
            row, col = pos
            value = probability_map[row][col]

            # زيادة القيمة إذا كان الموقع في نفس ط الإصابات السابقة
            if self.hunt_direction:
                if self._is_in_line_with_hits(pos, self.hunt_direction):
                    value *= 2.0

            target_values.append((pos, value))

        # ترتيب الأهداف حسب القيمة
        target_values.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, _ in target_values]

    def _update_probability_map(self):
        """
        تحديث خريطة احتمالات وجود السفن بناءً على نتائج الطلقات السابقة
        """
        try:
            grid_size = self.grid.size
            probability_map = [[1.0] * grid_size for _ in range(grid_size)]

            # تصفير احتمالية المواقع المستخدمة
            for row, col in self.shots:
                probability_map[row][col] = 0.0

            # زيادة احتمالية المواقع حول الإصابات
            for hit_pos in self.hit_positions:
                row, col = hit_pos
                for r in range(max(0, row - 2), min(grid_size, row + 3)):
                    for c in range(max(0, col - 2), min(grid_size, col + 3)):
                        if self._is_valid_target((r, c)):
                            distance = abs(r - row) + abs(c - col)
                            probability_map[r][c] *= (3.0 / (distance + 1))

            # تحديث الأهداف المحتملة بناءً على الخريطة
            new_targets = []
            for row in range(grid_size):
                for col in range(grid_size):
                    if probability_map[row][col] > 1.0 and self._is_valid_target((row, col)):
                        new_targets.append((row, col))

            # إضافة الأهداف الجديدة إلى القائمة
            for target in new_targets:
                if target not in self.potential_targets:
                    self.potential_targets.append(target)

        except Exception as e:
            self.logger.error(f"Error in _update_probability_map: {e}")
