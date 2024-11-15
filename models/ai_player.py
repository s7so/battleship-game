from typing import Tuple, List, Optional, Set
import random
from .player import Player
from .ship import Ship
from utils.constants import GRID_SIZE

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
      - اختيار الأهداف بناءً على احتمالية وجود السفن

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
   - كفاءة التتبع بعد الإصابة الأولى
   - سرعة اكتشاف وإغراق السفن

   7. التحسينات المستمرة (Continuous Improvements)
   ---------------------------------------------
   - تحليل أنماط اللعب
   - تحسين خوارزميات اتخاذ القرار
   - تطوير استراتيجيات جديدة
    """
    
    def __init__(self):
        super().__init__()
        # متغيرات تتبع حالة اللعب
        self.last_hit = None                         # آخر إصابة ناجحة
        self.potential_targets = []                  # قائمة الأهداف المحتملة
        self.hit_positions: Set[Tuple[int, int]] = set()  # مواقع الإصابات
        self.hunting_mode = False                    # وضع تتبع السفينة
        self.hunt_direction = None                   # اتجاه تتبع السفينة
        self.first_hit = None                       # أول إصابة في السفينة الحالية
        
    def get_shot_position(self) -> Tuple[int, int]:
        """
        تحديد موقع الطلقة التالية باستخدام استراتيجية متقدمة.
        
        الخوارزمية:
        1. إذا كان في وضع التتبع (hunting_mode):
           - استخدام استراتيجية التتبع الموجه
           - محاولة إغراق السفينة المكتشفة
        
        2. إذا كان لديه أهداف محتملة:
           - اختيار الهدف الأعلى احتمالية
           - الأهداف المجاورة للإصابات السابقة
        
        3. في حالة عدم وجود معلومات:
           - استخدام نمط رقعة الشطرنج للطلقات العشوائية
           - تحسين فرص العثور على سفينة جديدة
        
        Returns:
            Tuple[int, int]: إحداثيات الموقع المستهدف (صف، عمود)
        """
        if self.hunting_mode:
            return self._get_hunting_shot()
        if self.potential_targets:
            return self._get_smart_target()
        return self._get_random_shot()
                
    def receive_shot(self, position: Tuple[int, int]) -> Tuple[bool, Optional['Ship']]:
        """
        معالجة استقبال طلقة وتحديث استراتيجية AI.
        
        عملية التحديث:
        1. عند إصابة سفينة:
           - تفعيل وضع التتبع إذا لم يكن مفعلاً
           - تحديث قائمة الإصابات
           - تحديث الأهداف المحتملة
        
        2. عند إغراق سفينة:
           - إعادة تعيين وضع التتبع
           - إزالة الأهداف المحتملة حول السفينة الغارقة
           - الانتقال للبحث عن سفينة جديدة
        
        Args:
            position: موقع الطلقة
        Returns:
            Tuple[bool, Optional[Ship]]: (نجاح الإصابة، السفينة إذا غرقت)
        """
        hit, ship = super().receive_shot(position)
        
        if hit:
            if not ship:  # إصابة بدون غرق
                if not self.hunting_mode:
                    self.first_hit = position
                    self.hunting_mode = True
                self.hit_positions.add(position)
                self._update_potential_targets(position)
            else:  # غرق السفينة
                self._reset_hunting()
                self.potential_targets = [
                    pos for pos in self.potential_targets 
                    if not self._is_adjacent_to_sunk_ship(pos, ship)
                ]
        return hit, ship
        
    def _get_hunting_shot(self) -> Tuple[int, int]:
        """
        تحديد الطلقة التالية في وضع التتبع.
        
        استراتيجية التتبع:
        1. إذا لم يتم تحديد الاتجاه:
           - فحص الإصابات المتعددة لتحديد اتجاه السفينة
           - اختيار هدف ذكي حول أول إصابة
        
        2. إذا تم تحديد الاتجاه:
           - متابعة الطلقات في نفس الاتجاه
           - تغيير الاتجاه عند الوصول لنهاية السفينة
        
        3. إذا فشلت جميع المحاولات:
           - العودة للطلقات العشوائية
        
        Returns:
            Tuple[int, int]: موقع الطلقة التالية
        """
        if not self.hunt_direction:
            if len(self.hit_positions) > 1:
                self.hunt_direction = self._determine_ship_direction()
                return self._get_next_directional_shot()
            return self._get_smart_target()
        
        next_shot = self._get_next_directional_shot()
        if next_shot:
            return next_shot
            
        self.hunt_direction = self._get_perpendicular_direction()
        next_shot = self._get_next_directional_shot()
        if next_shot:
            return next_shot
            
        self._reset_hunting()
        return self._get_random_shot()
        
    def _get_smart_target(self) -> Tuple[int, int]:
        """
        اختيار الهدف الأعلى احتمالية من الأهداف المحتملة.
        
        الاستراتيجية:
        1. اختيار من قائمة الأهداف المحتملة
        2. التحقق من صلاحية الهدف
        3. العودة للطلقات العشوائية إذا لم تتوفر أهداف
        
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
        2. استهداف المناطق ذات الكثافة الأعلى
        3. توازن بين الاستكشاف والاستغلال
        
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
                
                for r in range(base_row, min(base_row + sector_size, grid_size)):
                    for c in range(base_col, min(base_col + sector_size, grid_size)):
                        if (r, c) not in self.shots:
                            valid_positions.append((r, c))
                            sector_density += self._calculate_area_density((r, c))
                
                if valid_positions:
                    sectors.append((valid_positions, sector_density / len(valid_positions)))
        
        # اختيار منطقة بناءً على الكثافة
        if sectors:
            # استخدام خوارزمية الاختيار المرجح
            total_density = sum(density for _, density in sectors)
            if total_density > 0:
                r = random.random() * total_density
                current = 0
                for positions, density in sectors:
                    current += density
                    if r <= current:
                        return random.choice(positions)
        
        # العودة إلى الاختيار العشوائي البسيط إذا فشلت الاستراتيجيات المتقدمة
        available_positions = [
            (row, col) for row in range(grid_size) for col in range(grid_size)
            if (row, col) not in self.shots
        ]
        return random.choice(available_positions) if available_positions else (0, 0)
        
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
        
        عوامل الأولوية:
        1. المسافة من الإصابات السابقة
        2. احتمالية وجود سفينة بناءً على الحجم المتبقي
        3. الكثافة في المنطقة المحيطة
        
        Returns:
            float: قيمة الأولوية (أعلى = أفضل)
        """
        priority = 0.0
        
        # المسافة من الإصابات السابقة
        for hit_pos in self.hit_positions:
            distance = abs(position[0] - hit_pos[0]) + abs(position[1] - hit_pos[1])
            priority += 1.0 / (distance + 1)
        
        # تحليل الكثافة في المنطقة المحيطة
        density = self._calculate_area_density(position)
        priority += density * 2
        
        # تعديل الأولوية بناءً على الاتجاه
        if direction == 'horizontal' and any(pos[0] == position[0] for pos in self.hit_positions):
            priority *= 1.5
        elif direction == 'vertical' and any(pos[1] == position[1] for pos in self.hit_positions):
            priority *= 1.5
            
        return priority

    def _calculate_area_density(self, position: Tuple[int, int], radius: int = 2) -> float:
        """
        حساب كثافة الأهداف المحتملة في منطقة محددة.
        
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
        تحديد الطلقة التالية في الاتجاه الحالي للتتبع
        """
        if not self.hunt_direction or not self.first_hit:
            return None
            
        row, col = self.first_hit
        if self.hunt_direction == 'horizontal':
            possible = [(row, col + 1), (row, col - 1)]
        else:  # vertical
            possible = [(row + 1, col), (row - 1, col)]
            
        valid_shots = [pos for pos in possible if self._is_valid_target(pos)]
        return valid_shots[0] if valid_shots else None
        
    def _is_valid_target(self, pos: Tuple[int, int]) -> bool:
        """
        التحقق من صلاحية الموقع كهدف
        Args:
            pos: الموقع المراد فحصه
        """
        row, col = pos
        grid_size = self.grid.size
        return (0 <= row < grid_size and 
                0 <= col < grid_size and 
                pos not in self.shots)
                
    def _reset_hunting(self):
        """إعادة تعيين متغيرات وضع التتبع"""
        self.hunting_mode = False
        self.hunt_direction = None
        self.first_hit = None
        self.hit_positions.clear()
        
    def _is_adjacent_to_sunk_ship(self, pos: Tuple[int, int], ship) -> bool:
        """
        التحقق مما إذا كان الموقع مجاوراً لسفينة غارقة
        """
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