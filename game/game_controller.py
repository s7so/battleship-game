from typing import Tuple, Optional, Dict, Any
from models.player import Player
from models.ai_player import AIPlayer
from models.grid import Grid
from database.db_manager import DatabaseManager
from utils.constants import SHIPS

class GameController:
    def __init__(self, db_manager: DatabaseManager):
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
        
    def start_new_game(self) -> bool:
        """Initialize a new game"""
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
        """Start the actual gameplay after setup"""
        if not self.player or not self.ai_player:
            return False
            
        if self.player.remaining_ships or self.ai_player.remaining_ships:
            return False
            
        self.game_state = 'playing'
        self.current_turn = 'player'
        return True
        
    def place_player_ship(self, ship_name: str, start_pos: Tuple[int, int], 
                         orientation: str) -> bool:
        """Attempt to place a player's ship"""
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
            'message': ''
        }
        
        if hit:
            result['message'] = f"Hit! "
            if sunk_ship:
                result['message'] += f"You sunk the {sunk_ship.name}!"
        else:
            result['message'] = "Miss!"
            
        if self.ai_player.all_ships_sunk():
            self.end_game('player')
            result['game_over'] = True
            result['winner'] = 'player'
        else:
            self.current_turn = 'ai'
            
        return result
        
    def process_ai_turn(self) -> Dict[str, Any]:
        """معالجة دور AI"""
        if self.game_state != 'playing' or self.current_turn != 'ai':
            return {'valid': False, 'message': 'Not AI turn'}
        
        try:
            # الحصول على موقع الهجوم
            position = self.ai_player.get_shot_position()
            
            # التحقق من صحة الموقع
            if not isinstance(position, tuple) or len(position) != 2:
                position = (0, 0)  # موقع افتراضي آمن
            
            # التأكد من أن الموقع داخل حدود الشبكة
            row, col = position
            if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
                position = (0, 0)  # موقع افتراضي آمن
            
            # تنفيذ الهجوم
            hit, sunk_ship = self.player.receive_shot(position)
            
            # إعداد النتيجة
            result = {
                'valid': True,
                'position': position,
                'hit': hit,
                'sunk': sunk_ship is not None,
                'ship_name': sunk_ship.name if sunk_ship else None,
                'game_over': False,
                'message': ''
            }
            
            # تحديث الرسالة
            if hit:
                result['message'] = "AI Hit! "
                if sunk_ship:
                    result['message'] += f"AI sunk your {sunk_ship.name}!"
            else:
                result['message'] = "AI Missed!"
            
            # التحقق من انتهاء اللعبة
            if self.player.all_ships_sunk():
                self.end_game('ai')
                result['game_over'] = True
                result['winner'] = 'ai'
            else:
                self.current_turn = 'player'
            
            return result
            
        except Exception as e:
            print(f"Error in AI turn: {e}")
            # إرجاع نتيجة آمنة في حالة الخطأ
            return {
                'valid': True,
                'position': (0, 0),
                'hit': False,
                'message': "AI Missed!",
                'game_over': False
            }

    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """
        التحقق من صحة موقع الهجوم
        Args:
            position: موقع الهجوم (صف، عمود)
        Returns:
            bool: True إذا كان الموقع صالح
        """
        row, col = position
        return (0 <= row < self.grid_size and 
                0 <= col < self.grid_size and 
                self.get_cell_state(True, position) != 'hit' and
                self.get_cell_state(True, position) != 'miss')

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

    def end_game(self, winner: str = None):
        """End the game and update statistics"""
        self.game_state = 'ended'
        self.game_over = True
        self.stats['games_played'] += 1
        
        if winner:  # في حالة انتهاء اللعبة بفائز
            if winner == 'player':
                self.stats['games_won'] += 1
            self._save_game_result(winner)
        else:  # في حالة إنهاء اللعبة يدوياً
            self._save_game_result('forfeit')
        
        # تنظيف حالة اللعبة
        self.current_turn = None
        self.selected_position = None

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