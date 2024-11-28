from typing import Tuple, Optional, Dict, Any, List, Union
from models.player import Player
from models.ai_player import AIPlayer
from models.grid import Grid
from models.ship import Ship, ShipOrientation
from database.db_manager import DatabaseManager
from utils.constants import (
    GRID_SIZE, 
    HIT_COLOR, 
    MISS_COLOR, 
    WATER_COLOR, 
    SHIP_COLOR,
    SHIPS  # إضافة استيراد SHIPS
)
from PyQt6.QtCore import QTimer
import random  # إضافة استيراد random
import logging

class GameController:
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة تحكم اللعبة
        
        Args:
            db_manager (DatabaseManager): كائن مدير قاعدة البيانات للتعامل مع حفظ وتحميل البيانات
            
        Attributes:
            db_manager: مدير قاعدة البيانات
            player: كائن اللاعب
            ai_player: كائن الخصم (الكمبيوتر)
            current_turn: دور اللاعب الحالي ('player' أو 'ai')
            game_over: حالة انتهاء اللعبة
            selected_position: الموقع المدد الياً
            grid_size: حجم شبكة اللعب (10×10 افتراضياً)
            main_window: النافذة الرئيسية للعبة
            game_state: حالة اللعبة ('setup', 'playing', 'ended')
            stats: إحصائيات اللعبة الحالية والسابقة
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.player = None
        self.ai_player = None
        self.current_turn = None
        self.game_over = False
        self.selected_position = None
        self.grid_size = 10  # Default grid size
        self.main_window = None
        self.game_state = 'setup'  # 'setup', 'playing', 'ended'
        self.stats = {
            'total_shots': 0,
            'hits': 0,
            'misses': 0,
            'games_played': 0,
            'games_won': 0,
            'current_game_duration': 0
        }
        self.logger.info("Game controller initialized")
        
    def start_new_game(self) -> bool:
        """
        تهيئة لعبة جديدة
        
        تقوم هذه الوظيفة بإنشاء لاعب جديد وخصم كمبيوتر جديد، وتعيين حالة اللعبة الأولية،
        وإعادة تعيين الإحصائيات، ووضع سفن الكمبيوتر بشكل عشوائي.
        
        Returns:
            bool: True دائماً لنجاح إشاء اللعبة الجديدة
            
        تأثيرات جانبية:
            - إنشاء كائنات اللاعب والخصم
            - تعيين دور اللاعب الحالي إلى 'player'
            - تعيين حالة اللعبة إلى 'setup'
            - إعادة تعيين الإحصائيات
            - وضع سفن الكمبيوتر بشكل عشوائي
        """
        self.player = Player(grid_size=self.grid_size)
        self.ai_player = AIPlayer()
        self.ai_player.grid.resize(self.grid_size)
        
        self.current_turn = 'player'
        self.game_over = False
        self.selected_position = None
        self.game_state = 'setup'
        
        # Reset statistics for new game
        self.stats.update({
            'total_shots': 0,
            'hits': 0,
            'misses': 0,
            'current_game_duration': 0
        })
        
        # AI places its ships randomly
        self.ai_player.place_ships_randomly()
        return True
        
    def start_gameplay(self) -> bool:
        """
        بدء اللعب الفعلي بعد مرحلة الإعداد
        
        تتحقق هذه الوظيفة من أن اللاعبين موجودين وأن جميع السفن د تم وضعها،
        ثم تبدأ مرحلة اللعب وتعين دور اللاعب الأول.
        
        Returns:
            bool: True إذا تم بدء اللعب بنجاح، False إذا لم تكتمل شروط بدء اللعب
            
        تأثيرات جانبية:
            - تغيير حالة اللعبة إلى 'playing'
            - تعيين الدور الحالي إلى 'player'
        """
        if not self.player or not self.ai_player:
            return False
            
        if self.player.remaining_ships or self.ai_player.remaining_ships:
            return False
            
        self.game_state = 'playing'
        self.current_turn = 'player'
        return True
        
    def place_player_ship(self, ship_name: str, start_pos: Tuple[int, int], 
                         orientation: str) -> bool:
        """
        محاولة وضع سفينة اللاعب على الشبكة
        
        Parameters:
            ship_name (str): اسم السفينة المراد وضعها
            start_pos (Tuple[int, int]): إحداثيات نقطة البداية للسفينة
            orientation (str): اتجاه السفينة ('horizontal' أو 'vertical')
            
        Returns:
            bool: True إذا تم وضع السفينة بنجاح، False إذا فشلت العملية
            
        تأثيرات جانبية:
            - وضع السفينة على شبكة اللاعب إذا كان الموضع صالحاً
            - بدء اللعب إذا تم وضع جميع السفن
            
        شروط:
            - يجب أن تكون حالة اللعبة في مرحلة الإعداد ('setup')
            - يجب أن يكون اللاعب موجوداً
        """
        if self.game_state != 'setup' or not self.player:
            return False
            
        success = self.player.place_ship(ship_name, SHIPS[ship_name], start_pos, orientation)       
        
        # Check if all ships are placed
        if success and not self.player.remaining_ships:
            self.start_gameplay()
            
        return success
        
    def place_player_ships_randomly(self) -> bool:
        """Place all player ships randomly"""
        if self.game_state != 'setup' or not self.player:
            return False
            
        success = self.player.place_ships_randomly()
        if success:
            self.start_gameplay()
        return success
        
    def process_player_shot(self, position: Tuple[int, int]) -> Dict[str, Any]:
        """Process a player's shot and return the result"""
        if self.game_state != 'playing' or self.current_turn != 'player':
            return {'valid': False, 'message': 'Not your turn'}
            
        if self.ai_player.grid.get_cell_state(position) in ['hit', 'miss']:
            return {'valid': False, 'message': 'Position already targeted'}
            
        hit, sunk_ship = self.ai_player.receive_shot(position)
        self.stats['total_shots'] += 1
        if hit:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1
            
        result = {
            'valid': True,
            'hit': hit,
            'sunk': sunk_ship is not None,
            'ship_name': sunk_ship.name if sunk_ship else None,
            'game_over': False,
            'winner': None,
            'message': ''
        }
        
        if hit:
            result['message'] = f"Hit! "
            if sunk_ship:
                result['message'] += f"You sunk the {sunk_ship.name}!"
        else:
            result['message'] = "Miss!"
            
        # Check victory condition
        if self.ai_player.all_ships_sunk():
            self.end_game('player')
            result['game_over'] = True
            result['winner'] = 'player'
        else:
            self.current_turn = 'ai'
            
        return result
        
    def process_ai_turn(self) -> Dict[str, Any]:
        """Process AI turn with improved validation"""
        if self.game_state != 'playing' or self.current_turn != 'ai':
            return {'valid': False, 'message': 'Not AI turn'}
        
        try:
            # Get AI's shot position
            position = self.ai_player.get_shot_position()
            
            # Validate the position hasn't been shot before
            if position in self.ai_player.shots:
                self.logger.error(f"AI attempted to shoot already targeted position: {position}")
                return {
                    'valid': False,
                    'message': 'Position already shot',
                    'position': position
                }
            
            # Process the shot
            hit, sunk_ship = self.player.receive_shot(position)
            
            # Update AI's knowledge and strategy
            self.ai_player.update_strategy(hit, position)
            
            if sunk_ship:
                # Clear potential targets if ship sunk
                self.ai_player.potential_targets = [
                    pos for pos in self.ai_player.potential_targets
                    if pos not in sunk_ship.position
                ]
                self.ai_player._reset_hunting()
            
            # Update stats
            self.stats['total_shots'] += 1
            if hit:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
            
            # Prepare result
            result = {
                'valid': True,
                'hit': hit,
                'sunk': sunk_ship is not None,
                'position': position,
                'ship_name': sunk_ship.name if sunk_ship else None,
                'game_over': False,
                'winner': None,
                'message': ''
            }

            # Update message
            if hit:
                result['message'] = "💥 AI Hit! "
                if sunk_ship:
                    result['message'] += f"AI sunk your {sunk_ship.name}! 🚢"
            else:
                result['message'] = "AI Missed! 💨"

            # Check victory condition
            if self.player.all_ships_sunk():
                self.end_game('ai')
                result['game_over'] = True
                result['winner'] = 'ai'
            else:
                self.current_turn = 'player'

            # Log the turn
            self.logger.info(f"AI turn - pos:{position} hit:{hit} sunk:{sunk_ship is not None}")
            
            return result

        except Exception as e:
            self.logger.error(f"Error in AI turn: {e}")
            return {
                'valid': False,
                'message': 'Error during AI turn',
                'position': (0,0)
            }

    def _get_smart_target_position(self, available_positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        تحديد أفضل موقع للهجوم باستخدام استراتيجيات متقدمة
        """
        if not available_positions:
            raise ValueError("No available positions")

        # إذا كان هناك إصابة سابقة، نركز على المواقع المحيطة
        if hasattr(self.ai_player, 'hit_positions') and self.ai_player.hit_positions:
            for hit_pos in self.ai_player.hit_positions:
                # البحث عن نمط في الإصابات
                ship_pattern = self._detect_ship_pattern(hit_pos)
                if ship_pattern:
                    next_pos = self._get_next_position_in_pattern(ship_pattern, available_positions)
                    if next_pos:
                        return next_pos

                # فحص المواقع المجاورة للإصابة
                adjacent_positions = [
                    (hit_pos[0] + dx, hit_pos[1] + dy)
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                ]
                
                valid_adjacent = [
                    pos for pos in adjacent_positions
                    if pos in available_positions
                ]
                
                if valid_adjacent:
                    return self._choose_best_adjacent_position(valid_adjacent, hit_pos)

        # تحليل كثافة المواقع المتاحة
        density_scores = self._analyze_position_density(available_positions)
        
        # اختيار الموقع ذو أعلى كثافة
        if density_scores:
            best_position = max(density_scores, key=density_scores.get)
            return best_position

        # استراتيجية النمط المتقاطع للبحث
        checkerboard_positions = [
            pos for pos in available_positions
            if (pos[0] + pos[1]) % 2 == 0  # نمط متقاطع
        ]
        if checkerboard_positions:
            return self._choose_strategic_position(checkerboard_positions)

        # اختيار موقع عشوائي من المواقع المتاحة
        return random.choice(available_positions)

    def _analyze_position_density(self, positions: List[Tuple[int, int]]) -> Dict[Tuple[int, int], float]:
        """
        تحليل كثافة المواقع وحساب درجة الأهمية لكل موقع
        """
        density_scores = {}
        for pos in positions:
            # حساب عدد المواقع المجاورة
            adjacent_count = sum(
                1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                if (pos[0] + dx, pos[1] + dy) in positions
            )
            
            # حساب المسافة من مركز الشبكة
            center_x, center_y = self.grid_size // 2, self.grid_size // 2
            distance = abs(pos[0] - center_x) + abs(pos[1] - center_y)
            
            # حساب درجة الكثافة
            density_score = adjacent_count / (distance + 1)
            density_scores[pos] = density_score
        
        return density_scores

    def _detect_ship_pattern(self, hit_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        اكتشاف نمط السفينة من الإصابات السابقة
        """
        pattern = [hit_pos]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            current_pos = hit_pos
            while True:
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if next_pos not in self.ai_player.hit_positions:
                    break
                pattern.append(next_pos)
                current_pos = next_pos
        
        return pattern if len(pattern) > 1 else []

    def _get_next_position_in_pattern(self, pattern: List[Tuple[int, int]], 
                                    available_positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        تحديد الموقع التالي في نمط السفينة
        """
        if len(pattern) < 2:
            return None
            
        # تحديد اتجاه النمط
        dx = pattern[1][0] - pattern[0][0]
        dy = pattern[1][1] - pattern[0][1]
        
        # فحص الموقعين على طرفي النمط
        start_pos = (pattern[0][0] - dx, pattern[0][1] - dy)
        end_pos = (pattern[-1][0] + dx, pattern[-1][1] + dy)
        
        # اختيار الموقع المتاح
        if start_pos in available_positions:
            return start_pos
        if end_pos in available_positions:
            return end_pos
            
        return None

    def _choose_best_adjacent_position(self, adjacent_positions: List[Tuple[int, int]], 
                                     hit_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        اختيار أفضل موقع مجاور بناءً على الاتجاه المحتمل للسفينة
        """
        if not adjacent_positions:
            raise ValueError("No adjacent positions available")

        # إذا كان هناك إصابات متعددة، نحاول تحديد اتجاه السفينة
        ship_direction = None
        for other_hit in self.ai_player.hit_positions:
            if other_hit != hit_pos:
                if other_hit[0] == hit_pos[0]:  # نفس الصف
                    ship_direction = 'horizontal'
                elif other_hit[1] == hit_pos[1]:  # نفس العمود
                    ship_direction = 'vertical'
        
        if ship_direction:
            # اختيار المواقع التي تتوافق مع اتجاه السفينة
            aligned_positions = [
                pos for pos in adjacent_positions
                if (ship_direction == 'horizontal' and pos[0] == hit_pos[0]) or
                   (ship_direction == 'vertical' and pos[1] == hit_pos[1])
            ]
            if aligned_positions:
                return random.choice(aligned_positions)
        
        return random.choice(adjacent_positions)

    def _choose_strategic_position(self, positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        اختي��ر موقع استراتيجي بناءً على حجم السفن المتبقية
        """
        if not positions:
            raise ValueError("No positions available")

        # تحديد أكبر سفينة لم يتم إغراقها
        max_ship_size = 0
        for ship in self.player.grid.ships:
            if not all(pos in self.ai_player.hit_positions for pos in ship.position):
                max_ship_size = max(max_ship_size, len(ship.position))
        
        # اختيار موقع يسمح بوضع أكبر سفينة
        best_positions = []
        for pos in positions:
            space_available = self._check_available_space(pos)
            if space_available >= max_ship_size:
                best_positions.append(pos)
        
        if best_positions:
            return random.choice(best_positions)
            
        return random.choice(positions)

    def _check_available_space(self, position: Tuple[int, int]) -> int:
        """
        حساب المساحة المتاحة حول موقع معين
        """
        max_space = 1
        directions = [(0, 1), (1, 0)]  # نفحص الاتجاه الأفقي والعمودي
        
        for dx, dy in directions:
            space = 1
            current_pos = position
            # فحص المساحة في الاتجاه الموجب
            while True:
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if not self._is_valid_position(next_pos) or next_pos in self.ai_player.shots:
                    break
                space += 1
                current_pos = next_pos
            
            current_pos = position
            # فحص المساحة في الاتجاه السالب
            while True:
                next_pos = (current_pos[0] - dx, current_pos[1] - dy)
                if not self._is_valid_position(next_pos) or next_pos in self.ai_player.shots:
                    break
                space += 1
                current_pos = next_pos
            
            max_space = max(max_space, space)
        
        return max_space

    def _update_ai_strategy(self, position: Tuple[int, int], hit: bool, sunk_ship: Optional[Ship]):
        """
        تحديث استراتيجية AI بناءً على نتيجة الطلقة
        """
        if not hasattr(self.ai_player, 'strategy_state'):
            self.ai_player.strategy_state = {
                'last_hit': None,
                'hunt_mode': False,
                'hunt_direction': None,
                'successful_hits': []
            }
        
        if hit:
            self.ai_player.strategy_state['last_hit'] = position
            self.ai_player.strategy_state['successful_hits'].append(position)
            
            if sunk_ship:
                # إعادة تعيين الاستراتيجية بعد إغراق السفينة
                self.ai_player.strategy_state['hunt_mode'] = False
                self.ai_player.strategy_state['hunt_direction'] = None
                self.ai_player.strategy_state['successful_hits'] = [
                    hit for hit in self.ai_player.strategy_state['successful_hits']
                    if hit not in sunk_ship.position
                ]
            else:
                # تفعيل وضع المطاردة
                self.ai_player.strategy_state['hunt_mode'] = True
        elif self.ai_player.strategy_state['hunt_mode']:
            # تغيير اتجاه المطاردة إذا فشلت الطلقة
            if self.ai_player.strategy_state['hunt_direction']:
                self.ai_player.strategy_state['hunt_direction'] = self._get_next_hunt_direction(
                    self.ai_player.strategy_state['hunt_direction']
                )

    def _get_next_hunt_direction(self, current_direction: Tuple[int, int]) -> Tuple[int, int]:
        """
        تحديد الاتجاه التالي للمطاردة
        """
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_index = directions.index(current_direction)
        return directions[(current_index + 1) % 4]

    def _is_valid_position(self, position: Union[Tuple[int, int], List[int]]) -> bool:
        """
        التحقق من صحة وقع في الشبكة
        
        Args:
            position: موقع في الشبكة (صف، عمود) يمكن أن يكون tuple أو list
            
        Returns:
            bool: True إذا كان الموقع صالح
        """
        try:
            # التحقق من نوع البيانات
            if not isinstance(position, (tuple, list)) or len(position) != 2:
                return False
                
            # تحويل الموقع إلى صف وعمود
            row, col = position
            
            # التحقق من أن القيم أعداد صحيحة
            if not isinstance(row, int) or not isinstance(col, int):
                return False
                
            # التحقق من أن الموقع داخل حدود الشبكة
            return (0 <= row < self.grid_size and 
                   0 <= col < self.grid_size)
                   
        except Exception as e:
            print(f"Error in _is_valid_position: {e}")
            return False

    def _get_valid_random_position(self) -> Tuple[int, int]:
        """
        الحصول على موقع عشوائي صالح للهجوم
        Returns:
            Tuple[int, int]: موقع صالح (صف، عمود)
        """
        import random
        valid_positions = [
            (row, col) 
            for row in range(self.grid_size) 
            for col in range(self.grid_size)
            if self._is_valid_position((row, col))
        ]
        return random.choice(valid_positions) if valid_positions else (0, 0)

    def end_game(self, winner: str):
        """
        End the game and update game state
        Args:
            winner: 'player' or 'ai'
        """
        self.game_state = 'ended'
        self.current_turn = None
        
        # Update stats
        self.stats['games_played'] += 1
        if winner == 'player':
            self.stats['games_won'] += 1
        
        # Save game result
        self._save_game_result('win' if winner == 'player' else 'loss')

    def force_end_game(self):
        """
        إنهاء اللعبة قسراً وحفظ النتيجة كخسارة
        Returns:
            bool: True إذا تم إنهاء اللعبة بنجاح
        """
        if self.game_state != 'ended':
            try:
                # حفظ نتيجة اللعبة كخسارة
                self.end_game('ai')  # اعتبار الإنهاء اليدوي خسارة
                
                # تنظيف الحالة
                self.current_turn = None
                self.selected_position = None
                self.game_state = 'ended'
                
                return True
            except Exception as e:
                print(f"Error ending game: {e}")
                return False
        return False

    def _save_game_result(self, outcome: str):
        """Save the game result to the database"""
        if not hasattr(self, 'current_player_id'):
            print("Warning: No player ID found")
            return
        
        result = {
            'outcome': outcome,
            'moves': self.stats['total_shots'],
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'duration': self.stats['current_game_duration'],
            'grid_size': self.grid_size
        }
        self.db_manager.save_game_result(self.current_player_id, result)

    def get_cell_state(self, is_player_grid: bool, position: Tuple[int, int]) -> str:
        """Get the state of a cell at the given position"""
        grid = self.player.grid if is_player_grid else self.ai_player.grid
        return grid.get_cell_state(position)

    def update_settings(self, new_settings: dict):
        """Update game settings"""
        if 'grid_size' in new_settings:
            new_size = new_settings['grid_size']
            if new_size != self.grid_size:
                # حفظ معرف اللاعب الحالي
                current_player_id = getattr(self, 'current_player_id', None)
                
                # تحديث الحجم وإعادة تهيئة اللعبة
                self.grid_size = new_size
                self.start_new_game()
                
                # استعادة معرف اللاعب
                if current_player_id:
                    self.current_player_id = current_player_id
                
                # تحديث الواجهة
                if self.main_window:
                    self.main_window.reset_ui()

    def _update_grid_size_in_modules(self):
        """Update grid size in all necessary modules"""
        import utils.constants as constants
        constants.GRID_SIZE = self.grid_size

    def set_main_window(self, main_window):
        """Set reference to main window"""
        self.main_window = main_window
        # إضافة مرجع عكسي في النافذة الرئيسية
        main_window.game_controller = self

    def get_game_state(self) -> str:
        """Get current game state"""
        return self.game_state

    def get_current_turn(self) -> str:
        """Get current player's turn"""
        return self.current_turn

    def set_current_player(self, player_data: dict):
        """Set current player data"""
        self.current_player_id = player_data['id']
        self.current_player_name = player_data['name']
        
        # تحديث الإحصائيات من بيانات اللاعب
        self.stats.update({
            'games_played': player_data['games_played'],
            'games_won': player_data['games_won'],
            'total_shots': player_data['total_shots'],
            'hits': player_data['total_hits']
        })

    def save_game(self) -> bool:
        """
        حفظ حالة اللعبة الحالية
        """
        if not self.current_player_id or self.game_state != 'playing':
            return False
        
        game_state = {
            'player_grid': {
                'ships': [(ship.name, ship.size, ship.position, ship.orientation.value) 
                         for ship in self.player.grid.ships],
                'shots': list(self.player.grid.shots),
                'hits': list(self.player.grid.hits),
                'misses': list(self.player.grid.misses)
            },
            'ai_grid': {
                'ships': [(ship.name, ship.size, ship.position, ship.orientation.value) 
                         for ship in self.ai_player.grid.ships],
                'shots': list(self.ai_player.grid.shots),
                'hits': list(self.ai_player.grid.hits),
                'misses': list(self.ai_player.grid.misses)
            },
            'ai_state': {
                'shots': list(self.ai_player.shots),
                'hit_positions': list(getattr(self.ai_player, 'hit_positions', set())),
                'hunting_mode': getattr(self.ai_player, 'hunting_mode', False),
                'last_hit': getattr(self.ai_player, 'last_hit', None)
            },
            'current_turn': self.current_turn,
            'game_state': self.game_state,
            'stats': self.stats,
            'grid_size': self.grid_size,
            'version': '1.1'  # Increment version for new save format
        }
        
        return self.db_manager.save_game_state(self.current_player_id, game_state)

    def load_game(self) -> bool:
        """
        تحميل آخر لعبة محفوظة
        """
        if not self.current_player_id:
            return False
        
        saved_state = self.db_manager.load_game_state(self.current_player_id)
        if not saved_state:
            return False
        
        try:
            # تحميل الحالة الأساسية
            self.grid_size = saved_state['grid_size']
            self.current_turn = saved_state['current_turn']
            self.game_state = saved_state['game_state']
            self.stats = saved_state['stats']
            
            # إعادة إنشاء اللاعبين
            self._recreate_player_from_state(saved_state['player_grid'])
            self._recreate_ai_from_state(saved_state['ai_grid'], saved_state.get('ai_state', {}))
            
            # التحقق من صحة الحالة المحملة
            self._validate_loaded_state()
            
            return True
            
        except Exception as e:
            print(f"Error loading game: {e}")
            self.start_new_game()
            return False

    def _recreate_player_from_state(self, player_state: dict):
        """
        إعادة إنشاء حالة اللاعب من البيانات المحفوظة
        """
        self.player = Player(self.grid_size)
        self.player.remaining_ships = []
        
        # إعادة إنشاء السفن
        for ship_data in player_state['ships']:
            name, size, position, orientation = ship_data
            ship = Ship(name, size)
            ship.position = [tuple(pos) for pos in position]
            ship.orientation = ShipOrientation(orientation)
            
            self.player.grid.ships.append(ship)
            self.player.placed_ships[name] = ship
            
            for pos in ship.position:
                self.player.grid.grid[pos[0]][pos[1]] = ship
        
        # استعادة الطلقات والإصابات
        self.player.grid.shots = set(tuple(pos) for pos in player_state['shots'])
        self.player.grid.hits = set(tuple(pos) for pos in player_state['hits'])
        self.player.grid.misses = set(tuple(pos) for pos in player_state['misses'])
        self.player.shots = self.player.grid.shots.copy()
        
        # تحديث حالة الإصابات للسفن
        for ship in self.player.grid.ships:
            ship.hits = [pos for pos in ship.position if pos in self.player.grid.hits]

    def _recreate_ai_from_state(self, ai_grid_state: dict, ai_state: dict = None):
        """
        إعادة إنشاء حالة الكمبيوتر من البيانات المحفوظة
        """
        self.ai_player = AIPlayer()
        self.ai_player.grid = Grid(self.grid_size)
        self.ai_player.remaining_ships = []
        
        # إعادة إنشاء السفن
        for ship_data in ai_grid_state['ships']:
            name, size, position, orientation = ship_data
            ship = Ship(name, size)
            ship.position = [tuple(pos) for pos in position]
            ship.orientation = ShipOrientation(orientation)
            
            self.ai_player.grid.ships.append(ship)
            self.ai_player.placed_ships[name] = ship
            
            for pos in ship.position:
                self.ai_player.grid.grid[pos[0]][pos[1]] = ship
        
        # استعادة الطلقات والإصابات
        self.ai_player.grid.shots = set(tuple(pos) for pos in ai_grid_state['shots'])
        self.ai_player.grid.hits = set(tuple(pos) for pos in ai_grid_state['hits'])
        self.ai_player.grid.misses = set(tuple(pos) for pos in ai_grid_state['misses'])
        self.ai_player.shots = self.ai_player.grid.shots.copy()
        
        # تحديث حالة الإصابات للسفن
        for ship in self.ai_player.grid.ships:
            ship.hits = [pos for pos in ship.position if pos in self.ai_player.grid.hits]
            
        # استعادة حالة AI الإضافية
        if ai_state:
            self.ai_player.shots = set(tuple(pos) for pos in ai_state.get('shots', []))
            self.ai_player.hit_positions = set(tuple(pos) for pos in ai_state.get('hit_positions', []))
            self.ai_player.hunting_mode = ai_state.get('hunting_mode', False)
            self.ai_player.last_hit = ai_state.get('last_hit')

    def _determine_orientation(self, positions: List[Tuple[int, int]]) -> str:
        """
        تحديد اتجاه السفينة بناءً على المواقع.
        Args:
            positions: قائمة المواقع (صف، عمود)
        Returns:
            str: 'horizontal' أو 'vertical'
        """
        if len(positions) < 2:
            return 'horizontal'  # افتراضياً
        if positions[0][0] == positions[1][0]:
            return 'horizontal'
        return 'vertical'

    def get_save_state(self) -> dict:
        """
        تجهيز حالة اللعبة للحفظ
        
        Returns:
            dict: قاموس يحتوي على حالة اللعبة. إذا لم تكن اللعبة في حالة صالحة للحفظ،
                 يتم إرجاع قاموس فارغ مع رسالة خطأ.
        """
        if not self.current_player_id or self.game_state != 'playing':
            return {
                'valid': False,
                'error': 'Game not in valid state for saving',
                'game_state': self.game_state,
                'has_player': bool(self.current_player_id)
            }
        
        try:
            return {
                'valid': True,
                'player': self.player.to_dict() if self.player else {},
                'ai': self.ai_player.to_dict() if self.ai_player else {},
                'current_turn': self.current_turn,
                'game_state': self.game_state,
                'stats': self.stats,
                'grid_size': self.grid_size,
                'version': '1.0'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'game_state': self.game_state
            }

    def restore_save_state(self, save_state: dict) -> bool:
        """
        استعادة حالة اللعبة من البيانات المحفوظة
        """
        try:
            # استعادة حالة اللاعب
            self.player = Player.from_dict(save_state['player'])
            
            # استعادة حالة AI
            self.ai_player = AIPlayer.from_dict(save_state['ai'])
            
            # استعادة حالة اللعبة
            self.current_turn = save_state['current_turn']
            self.game_state = save_state['game_state']
            self.stats = save_state['stats']
            self.grid_size = save_state['grid_size']
            
            return True
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False

    def _update_ui(self, message: str = None, stats: bool = True) -> bool:
        """
        تحديث واجهة المستخدم إذا كانت النافذة الرئيسية موجودة
        
        Args:
            message: الرسالة المراد عرضها (اختياري)
            stats: ما إذا كا يجب تحديث الإحصائيات (افتراضياً True)
            
        Returns:
            bool: True إذا تم التحديث بنجاح، False إذا لم تكن النافذة الرئيسية موجودة
        """
        if hasattr(self, 'main_window') and self.main_window:
            if message:
                self.main_window.update_status(message)
            if stats:
                self.main_window.update_stats_display()
            return True
        return False

    def _execute_ai_turn(self):
        """Execute AI turn with proper UI updates"""
        try:
            # Process AI turn
            result = self.process_ai_turn()
            if not result['valid']:
                self.logger.error("Invalid AI turn")
                return

            # Get shot position and button
            row, col = result['position']
            if not (0 <= row < len(self.player_grid_buttons) and 
                    0 <= col < len(self.player_grid_buttons[0])):
                self.logger.error(f"Invalid AI shot position: {row}, {col}")
                return

            button = self.player_grid_buttons[row][col]

            # Update UI based on result
            if result['hit']:
                button.setStyleSheet(f"background-color: {HIT_COLOR};")
                message = "💥 AI Hit! "
                if result['sunk']:
                    message += f"AI sunk your {result['ship_name']}! 🚢"
                    # Update UI for sunk ship
                    ship = next((s for s in self.player.grid.ships 
                               if s.name == result['ship_name']), None)
                    if ship:
                        for ship_pos in ship.position:
                            self.player_grid_buttons[ship_pos[0]][ship_pos[1]].setStyleSheet(
                                f"background-color: {HIT_COLOR};"
                            )
            else:
                button.setStyleSheet(f"background-color: {MISS_COLOR};")
                message = "AI Missed! 💨"

            # Update game status
            self._update_ui(message)

            # Handle game end or continue
            if result['game_over']:
                if self._update_ui():
                    self.main_window.game_over(result['winner'])
            else:
                if self._update_ui():
                    self.main_window._enable_ai_grid()
                    QTimer.singleShot(200, lambda: self.main_window.update_status("Your turn! Select a target"))

        except Exception as e:
            self.logger.error(f"Error executing AI turn: {e}")
            # Retry after delay
            QTimer.singleShot(50, self._execute_ai_turn)

    def set_grid_buttons(self, player_grid_buttons, ai_grid_buttons):
        """
        تعيين مراجع لأزرار الشبكة
        Args:
            player_grid_buttons: مصفوفة أزرار شبكة اللاعب
            ai_grid_buttons: مصفوفة أزرار شبكة AI
        """
        self.player_grid_buttons = player_grid_buttons
        self.ai_grid_buttons = ai_grid_buttons

    def save_game_state(self) -> Dict[str, Any]:
        """
        حفظ حالة اللعبة الحالية
        
        Returns:
            Dict[str, Any]: قاموس يحتوي على حالة اللعبة. في حالة حدوث خطأ،
                           يتم إرجاع قاموس يحتوي على معلومات الخطأ.
        """
        try:
            if not self.player or not self.ai_player:
                return {
                    'valid': False,
                    'error': 'Players not initialized',
                    'game_state': self.game_state
                }
                
            return {
                'valid': True,
                'player': self.player.to_dict(),
                'ai_player': self.ai_player.to_dict(),
                'current_turn': self.current_turn,
                'game_state': self.game_state,
                'game_over': self.game_over,
                'grid_size': self.grid_size,
                'stats': self.stats.copy(),
                'version': '1.0'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'game_state': self.game_state,
                'traceback': str(e.__traceback__)
            }

    def load_game_state(self, state: Dict[str, Any]) -> bool:
        """
        تحميل الة لعبة محفوظة
        Args:
            state: قاموس يحتوي على حالة اللعبة
        Returns:
            bool: True إذا تم التحميل بنجاح
        """
        try:
            if not state or not isinstance(state, dict):
                raise ValueError("Invalid game state data")

            # التحقق من الإصدار
            if state.get('version', '0.0') != '1.0':
                print("Warning: Loading game from different version")

            # تحميل حجم الشبكة أولاً
            self.grid_size = state.get('grid_size', 10)

            # إنشاء اللاعبين
            if 'player' in state and state['player']:
                self.player = Player.from_dict(state['player'])
            else:
                self.player = Player(grid_size=self.grid_size)

            if 'ai_player' in state and state['ai_player']:
                self.ai_player = AIPlayer.from_dict(state['ai_player'])
            else:
                self.ai_player = AIPlayer()
                self.ai_player.grid.resize(self.grid_size)

            # تحميل حالة اللعبة
            self.current_turn = state.get('current_turn', 'player')
            self.game_state = state.get('game_state', 'playing')
            self.game_over = state.get('game_over', False)
            
            # تحميل الإحصائيات
            saved_stats = state.get('stats', {})
            self.stats.update(saved_stats)

            # التحقق من صحة الحالة المحملة
            self._validate_loaded_state()
            
            return True

        except Exception as e:
            print(f"Error loading game state: {e}")
            # إعادة تعيين اللعبة في حالة الفشل
            self.start_new_game()
            return False

    def _validate_loaded_state(self):
        """
        التحقق من صحة حالة اللعبة بعد التحميل
        """
        try:
            # التحقق من وجود اللاعبين
            if not self.player or not self.ai_player:
                raise ValueError("Missing players after load")

            # التحقق من حجم الشبكة
            if self.player.grid.size != self.grid_size or self.ai_player.grid.size != self.grid_size:
                self.player.grid.resize(self.grid_size)
                self.ai_player.grid.resize(self.grid_size)

            # التحقق من حالة اللعب
            if self.game_state not in ['setup', 'playing', 'ended']:
                self.game_state = 'playing'

            # التحقق من الدور الحالي
            if self.current_turn not in ['player', 'ai']:
                self.current_turn = 'player'

            # تنظيف وتحديث حالة الطلقات
            if not hasattr(self.ai_player, 'shots'):
                self.ai_player.shots = set()
            if not hasattr(self.ai_player, 'hit_positions'):
                self.ai_player.hit_positions = set()

            # تحويل الطلقات والإصابات إلى مجموعات
            self.ai_player.shots = {tuple(pos) if isinstance(pos, list) else pos 
                                  for pos in self.ai_player.shots}
            self.ai_player.hit_positions = {tuple(pos) if isinstance(pos, list) else pos 
                                          for pos in getattr(self.ai_player, 'hit_positions', set())}

            # مزامنة حالة الطلقات مع حالة الشبكة
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    pos = (row, col)
                    cell_state = self.player.grid.get_cell_state(pos)
                    if cell_state in ['hit', 'miss']:
                        self.ai_player.shots.add(pos)
                        if cell_state == 'hit':
                            self.ai_player.hit_positions.add(pos)

            # تنظيف حالة AI
            if hasattr(self.ai_player, '_clean_state'):
                self.ai_player._clean_state()

            # التحقق من الطلقات والإصابات
            self._validate_shots_and_hits()

        except Exception as e:
            print(f"Error validating loaded state: {e}")
            self.start_new_game()

    def _validate_shots_and_hits(self):
        """
        التحقق من صحة الطلقات والإصابات
        """
        try:
            # التحقق من طلقات AI
            if not hasattr(self.ai_player, 'shots'):
                self.ai_player.shots = set()
            if not hasattr(self.ai_player, 'hit_positions'):
                self.ai_player.hit_positions = set()

            # تحويل الطلقات والإصابات إلى tuples
            self.ai_player.shots = {
                tuple(pos) if isinstance(pos, list) else pos 
                for pos in self.ai_player.shots 
                if self._is_valid_position(pos)
            }
            self.ai_player.hit_positions = {
                tuple(pos) if isinstance(pos, list) else pos 
                for pos in self.ai_player.hit_positions 
                if self._is_valid_position(pos)
            }

            # تنظيف الأهداف المحتملة
            if hasattr(self.ai_player, 'potential_targets'):
                self.ai_player.potential_targets = [
                    tuple(pos) if isinstance(pos, list) else pos 
                    for pos in self.ai_player.potential_targets 
                    if self._is_valid_position(pos)
                ]

        except Exception as e:
            print(f"Error validating shots and hits: {e}")
            self.ai_player.shots = set()
            self.ai_player.hit_positions = set()
            self.ai_player.potential_targets = []

    def validate_game_state(self) -> bool:
        """Validate entire game state"""
        try:
            # Basic state validation
            if self.game_state not in ['setup', 'playing', 'ended']:
                return False
            if self.current_turn not in ['player', 'ai']:
                return False
            
            # Grid size validation    
            if self.grid_size not in [10, 15]:
                return False
            
            # Player validation
            if not self.player or not self.ai_player:
                return False
            
            # Grid validation
            if not (self.player.grid.validate_grid_state() and 
                    self.ai_player.grid.validate_grid_state()):
                return False
            
            return True
        
        except Exception as e:
            logging.error(f"Game state validation error: {e}")
            return False