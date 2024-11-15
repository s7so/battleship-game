import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseError(Exception):
    """ايرور مخصوص للداتابيز"""
    pass

class DatabaseManager:
    def __init__(self, db_path: str = 'battleship.db'):
        """
        تهيئة مدير قاعدة البيانات
        Args:
            db_path: مسار ملف قاعدة البيانات (اختياري، القيمة الافتراضية 'battleship.db')
        """
        try:
            self.conn = sqlite3.connect(db_path)
            # نشغل دعم الفورين كيز
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(f"مقدرناش نعمل الداتابيز: {str(e)}")

    def execute_safe(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """ننفذ الكويري بأمان مع هاندلة الايرورز"""
        try:
            return self.conn.execute(query, params)
        except sqlite3.Error as e:
            raise DatabaseError(f"ايرور في الداتابيز: {str(e)}")

    def create_tables(self):
        """نعمل التيبلز اللي محتاجينها لو مش موجودة"""
        try:
            with self.conn:
                # نمسح التيبلز بالترتيب من الصغير للكبير
                self.conn.execute('DROP TABLE IF EXISTS ship_statistics')
                self.conn.execute('DROP TABLE IF EXISTS game_history')
                self.conn.execute('DROP TABLE IF EXISTS player_settings')
                self.conn.execute('DROP TABLE IF EXISTS players')
                
                # نعمل التيبلز بالترتيب من الكبير للصغير
                # 1. تيبل اللعيبة (الأساسي)
                self.conn.execute('''
                    CREATE TABLE players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        games_played INTEGER DEFAULT 0,
                        games_won INTEGER DEFAULT 0,
                        total_shots INTEGER DEFAULT 0,
                        total_hits INTEGER DEFAULT 0,
                        accuracy REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_played TIMESTAMP
                    )
                ''')
                
                # 2. تيبل الإعدادات بتاعت اللعيبة
                self.conn.execute('''
                    CREATE TABLE player_settings (
                        player_id INTEGER PRIMARY KEY,
                        grid_size INTEGER DEFAULT 10,
                        sound_enabled BOOLEAN DEFAULT 1,
                        music_enabled BOOLEAN DEFAULT 1,
                        FOREIGN KEY (player_id) REFERENCES players (id)
                            ON DELETE CASCADE
                    )
                ''')
                
                # 3. تيبل تاريخ اللعب
                self.conn.execute('''
                    CREATE TABLE game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id INTEGER,
                        result TEXT NOT NULL,
                        grid_size INTEGER DEFAULT 10,
                        moves INTEGER,
                        hits INTEGER,
                        misses INTEGER,
                        accuracy REAL,
                        duration INTEGER,
                        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (player_id) REFERENCES players (id)
                            ON DELETE CASCADE
                    )
                ''')
                
                # 4. تيبل احصائيات الراكب
                self.conn.execute('''
                    CREATE TABLE ship_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        ship_name TEXT NOT NULL,
                        was_sunk BOOLEAN,
                        hits_taken INTEGER,
                        turns_to_sink INTEGER,
                        FOREIGN KEY (game_id) REFERENCES game_history (id)
                            ON DELETE CASCADE
                    )
                ''')
                
        except sqlite3.Error as e:
            print(f"ايرور في عمل التيبلز: {e}")
            raise DatabaseError(f"مقدرناش نعمل تيبلز الداتابيز: {str(e)}")

    def create_player(self, name: str) -> int:
        """Create a new player and return their ID"""
        try:
            with self.conn:
                print(f"Creating new player with name: {name}")  # للتأكد
                cursor = self.conn.execute('''
                    INSERT INTO players 
                    (name, games_played, games_won, total_shots, total_hits, accuracy) 
                    VALUES (?, 0, 0, 0, 0, 0.0)
                ''', (name.strip(),))
                
                player_id = cursor.lastrowid
                print(f"Player created successfully with ID: {player_id}")  # للتأكد
                return player_id
        except sqlite3.IntegrityError:
            print("Error: Player name already exists")  # للتأكد
            raise DatabaseError("Player already exists")
        except Exception as e:
            print(f"Error in create_player: {e}")  # للتأكد
            raise DatabaseError(f"Failed to create player: {str(e)}")

    def get_player(self, player_id: int) -> Optional[Dict]:
        """نجيب معلومات اللعيب"""
        try:
            cursor = self.conn.execute(
                'SELECT * FROM players WHERE id = ?',
                (player_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'games_played': row[2] if row[2] is not None else 0,
                    'games_won': row[3] if row[3] is not None else 0,
                    'total_shots': row[4] if row[4] is not None else 0,
                    'total_hits': row[5] if row[5] is not None else 0,
                    'accuracy': row[6] if row[6] is not None else 0.0,
                    'created_at': row[7] if row[7] is not None else None,
                    'last_played': row[8] if row[8] is not None else None
                }
            return None
        except Exception as e:
            print(f"ايرور في جلب اللعيب: {e}")
            return None

    def save_game_result(self, player_id: int, result: Dict[str, Any]):
        """نحفظ نتيجة اللعبة ونحدث احصائيات اللعيب"""
        try:
            with self.conn:
                # نتأكد ان اللعيب موجود
                if not self.get_player(player_id):
                    raise ValueError(f"مفيش لعيب بالاي دي ده {player_id}")
                
                # نحسب الدقة
                accuracy = (result['hits'] / result['moves'] * 100) if result['moves'] > 0 else 0
                
                # ندخل نتيجة اللعبة
                cursor = self.execute_safe('''
                    INSERT INTO game_history 
                    (player_id, result, grid_size, moves, hits, misses, accuracy, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_id,
                    result['outcome'],
                    result.get('grid_size', 10),
                    result['moves'],
                    result['hits'],
                    result['misses'],
                    accuracy,
                    result['duration']
                ))
                
                # نحدث احصائيات اللعيب
                self.execute_safe('''
                    UPDATE players 
                    SET games_played = games_played + 1,
                        games_won = games_won + CASE WHEN ? = 'win' THEN 1 ELSE 0 END,
                        total_shots = total_shots + ?,
                        total_hits = total_hits + ?,
                        accuracy = (total_hits * 100.0 / NULLIF(total_shots, 0)),
                        last_played = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (result['outcome'], result['moves'], result['hits'], player_id))
                
        except Exception as e:
            print(f"ايرور في حفظ نتيجة اللعبة: {e}")
            raise

    def get_player_statistics(self, player_id: int) -> Dict[str, Any]:
        """جلب إحصائيات مفصلة للاعب مع تحليلات إضافية"""
        try:
            cursor = self.conn.execute('''
                WITH PlayerStats AS (
                    SELECT 
                        p.*,
                        COUNT(DISTINCT g.id) as total_games,
                        SUM(CASE WHEN g.result = 'win' THEN 1 ELSE 0 END) as wins,
                        AVG(g.accuracy) as avg_accuracy,
                        MIN(g.moves) as best_game_moves,
                        MAX(g.moves) as worst_game_moves,
                        AVG(g.duration) as avg_game_duration,
                        MAX(g.played_at) as last_played,
                        COUNT(DISTINCT CASE WHEN g.result = 'win' AND g.moves <= 30 THEN g.id END) as quick_wins
                    FROM players p
                    LEFT JOIN game_history g ON p.id = g.player_id
                    WHERE p.id = ?
                    GROUP BY p.id
                )
                SELECT 
                    *,
                    ROUND(CAST(wins AS FLOAT) / NULLIF(total_games, 0) * 100, 2) as win_rate,
                    ROUND(avg_accuracy, 2) as accuracy_rate
                FROM PlayerStats
            ''', (player_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'games_played': row[2],
                    'games_won': row[3],
                    'total_shots': row[4],
                    'total_hits': row[5],
                    'accuracy': row[6],
                    'best_game': row[12],
                    'worst_game': row[13],
                    'avg_duration': row[14],
                    'quick_wins': row[16],  # عدد المرات التي فاز فيها بسرعة
                    'win_rate': row[17],    # نسبة الفوز
                    'accuracy_rate': row[18] # معدل الدقة
                }
            return {}
        except Exception as e:
            print(f"Error getting player statistics: {e}")
            return {}

    def get_game_history(self, player_id: int, limit: int = 10) -> List[Dict]:
        """نجيب آخر تاريخ لعب للعيب"""
        cursor = self.conn.execute('''
            SELECT * FROM game_history 
            WHERE player_id = ?
            ORDER BY played_at DESC
            LIMIT ?
        ''', (player_id, limit))
        
        return [{
            'id': row[0],
            'result': row[2],
            'grid_size': row[3],
            'moves': row[4],
            'hits': row[5],
            'misses': row[6],
            'accuracy': row[7],
            'duration': row[8],
            'played_at': row[10]
        } for row in cursor.fetchall()]

    def close(self):
        """نقفل كونكشن الداتابيز"""
        self.conn.close()

    def get_leaderboard(self, limit: int = 10, time_period: str = 'all') -> List[Dict]:
        """
        جلب لوحة المتصدرين مع تصفية حسب الفترة الزمنية
        Args:
            limit: عدد النتائج المطلوبة
            time_period: 'all', 'week', 'month', 'year'
        """
        try:
            time_filter = ''
            if time_period == 'week':
                time_filter = "AND g.played_at >= date('now', '-7 days')"
            elif time_period == 'month':
                time_filter = "AND g.played_at >= date('now', '-1 month')"
            elif time_period == 'year':
                time_filter = "AND g.played_at >= date('now', '-1 year')"

            cursor = self.conn.execute(f'''
                WITH PlayerStats AS (
                    SELECT 
                        p.name,
                        COUNT(DISTINCT g.id) as games_played,
                        SUM(CASE WHEN g.result = 'win' THEN 1 ELSE 0 END) as games_won,
                        AVG(g.accuracy) as avg_accuracy,
                        MIN(g.moves) as best_game,
                        COUNT(DISTINCT CASE WHEN g.result = 'win' AND g.moves <= 30 THEN g.id END) as quick_wins
                    FROM players p
                    LEFT JOIN game_history g ON p.id = g.player_id
                    WHERE 1=1 {time_filter}
                    GROUP BY p.id, p.name
                    HAVING games_played > 0
                )
                SELECT 
                    name,
                    games_played,
                    games_won,
                    ROUND(CAST(games_won AS FLOAT) / games_played * 100, 2) as win_ratio,
                    ROUND(avg_accuracy, 2) as accuracy,
                    best_game,
                    quick_wins,
                    ROUND(CAST(quick_wins AS FLOAT) / games_won * 100, 2) as quick_win_ratio
                FROM PlayerStats
                ORDER BY win_ratio DESC, accuracy DESC
                LIMIT ?
            ''', (limit,))
            
            return [{
                'name': row[0],
                'games_played': row[1],
                'games_won': row[2],
                'win_ratio': row[3],
                'accuracy': row[4],
                'best_game': row[5],
                'quick_wins': row[6],
                'quick_win_ratio': row[7]
            } for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []

    def get_ship_statistics(self, player_id: int) -> Dict[str, Any]:
        """نجيب احصائيات تفصيلية عن أداء المراكب"""
        cursor = self.conn.execute('''
            SELECT 
                sh.ship_name,
                COUNT(*) as total_battles,
                SUM(CASE WHEN sh.was_sunk THEN 1 ELSE 0 END) as times_sunk,
                AVG(sh.hits_taken) as avg_hits_taken,
                AVG(sh.turns_to_sink) as avg_turns_to_sink
            FROM ship_statistics sh
            JOIN game_history gh ON sh.game_id = gh.id
            WHERE gh.player_id = ?
            GROUP BY sh.ship_name
        ''', (player_id,))
        
        return {row[0]: {
            'total_battles': row[1],
            'times_sunk': row[2],
            'avg_hits_taken': row[3],
            'avg_turns_to_sink': row[4]
        } for row in cursor.fetchall()}

    def save_game_settings(self, player_id: int, settings: Dict[str, Any]):
        """نحفظ إعدادات اللعبة بتاعت اللعيب"""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS player_settings (
                    player_id INTEGER PRIMARY KEY,
                    grid_size INTEGER DEFAULT 10,
                    sound_enabled BOOLEAN DEFAULT 1,
                    music_enabled BOOLEAN DEFAULT 1,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            ''')
            
            self.conn.execute('''
                INSERT OR REPLACE INTO player_settings 
                (player_id, grid_size, sound_enabled, music_enabled)
                VALUES (?, ?, ?, ?)
            ''', (
                player_id,
                settings.get('grid_size', 10),
                settings.get('sound_enabled', True),
                settings.get('music_enabled', True)
            ))

    def get_game_settings(self, player_id: int) -> Dict[str, Any]:
        """نجيب إعدادات اللعبة بتاعت اللعيب"""
        cursor = self.conn.execute('''
            SELECT grid_size, sound_enabled, music_enabled
            FROM player_settings
            WHERE player_id = ?
        ''', (player_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'grid_size': row[0],
                'sound_enabled': bool(row[1]),
                'music_enabled': bool(row[2])
            }
        return {
            'grid_size': 10,
            'sound_enabled': True,
            'music_enabled': True
        }

    def delete_player_data(self, player_id: int):
        """نمسح كل البيانات بتاعت اللعيب"""
        with self.conn:
            # نمسح من احصائيات المراكب (من خلال تاريخ اللعب)
            self.conn.execute('''
                DELETE FROM ship_statistics 
                WHERE game_id IN (
                    SELECT id FROM game_history WHERE player_id = ?
                )
            ''', (player_id,))
            
            # نمسح من تاريخ اللعب
            self.conn.execute('''
                DELETE FROM game_history 
                WHERE player_id = ?
            ''', (player_id,))
            
            # نمسح من إعدادات اللعيب
            self.conn.execute('''
                DELETE FROM player_settings 
                WHERE player_id = ?
            ''', (player_id,))
            
            # نمسح من اللعيبة
            self.conn.execute('''
                DELETE FROM players 
                WHERE id = ?
            ''', (player_id,))

    def check_connection(self) -> bool:
        """نشوف لو الكونكشن شغال ولا لأ"""
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def reconnect(self):
        """نحاول نعمل كونكشن تاني بالداتابيز"""
        try:
            if not self.check_connection():
                self.conn = sqlite3.connect('battleship.db')
                self.conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise DatabaseError(f"مقدرناش نعمل كونكشن تاني: {str(e)}")

    def backup_database(self, backup_path: str):
        """نعمل باكاب للداتابيز"""
        try:
            backup_conn = sqlite3.connect(backup_path)
            with backup_conn:
                self.conn.backup(backup_conn)
            backup_conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(f"الباكاب فشل: {str(e)}")

    def find_player_by_name(self, name: str) -> Optional[Dict]:
        """
        البحث عن لاعب باسمه
        Returns: معلومات اللاعب أو None إذا لم يوجد
        """
        try:
            cursor = self.conn.execute(
                'SELECT * FROM players WHERE LOWER(name) = LOWER(?)',  # تجاهل حالة الأحرف
                (name.strip(),)
            )
            row = cursor.fetchone()
            if row:
                # إرجاع معلومات اللاعب كاملة
                return {
                    'id': row[0],
                    'name': row[1],
                    'games_played': row[2] if row[2] is not None else 0,
                    'games_won': row[3] if row[3] is not None else 0,
                    'total_shots': row[4] if row[4] is not None else 0,
                    'total_hits': row[5] if row[5] is not None else 0,
                    'accuracy': row[6] if row[6] is not None else 0.0,
                    'created_at': row[7],
                    'last_played': row[8]
                }
            return None
        except Exception as e:
            print(f"Error in find_player_by_name: {e}")
            return None

    def get_player_achievements(self, player_id: int) -> List[Dict]:
        """جلب إنجازات اللاعب"""
        achievements = []
        try:
            stats = self.get_player_statistics(player_id)
            
            # إنجازات عدد الألعاب
            if stats['games_played'] >= 100:
                achievements.append({
                    'title': 'Veteran Player',
                    'description': 'Played 100 or more games',
                    'icon': '🎮'
                })
                
            # إنجازات نسبة الفوز
            if stats['win_rate'] >= 75:
                achievements.append({
                    'title': 'Master Commander',
                    'description': 'Maintained a 75% or higher win rate',
                    'icon': '👑'
                })
                
            # إنجازات الدقة
            if stats['accuracy_rate'] >= 50:
                achievements.append({
                    'title': 'Sharp Shooter',
                    'description': 'Maintained 50% or higher accuracy',
                    'icon': '🎯'
                })
                
            # إنجازات الفوز السريع
            if stats['quick_wins'] >= 10:
                achievements.append({
                    'title': 'Swift Victory',
                    'description': 'Won 10 or more games in under 30 moves',
                    'icon': '⚡'
                })
                
            return achievements
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []

    def get_player_progress(self, player_id: int) -> Dict[str, Any]:
        """جلب تقدم اللاعب وتحليل أدائه"""
        try:
            cursor = self.conn.execute('''
                WITH GameProgress AS (
                    SELECT 
                        DATE(played_at) as game_date,
                        COUNT(*) as games_played,
                        SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                        AVG(accuracy) as daily_accuracy
                    FROM game_history
                    WHERE player_id = ?
                    GROUP BY DATE(played_at)
                    ORDER BY game_date
                )
                SELECT 
                    game_date,
                    games_played,
                    wins,
                    daily_accuracy,
                    SUM(games_played) OVER (ORDER BY game_date) as total_games,
                    SUM(wins) OVER (ORDER BY game_date) as total_wins
                FROM GameProgress
            ''', (player_id,))
            
            progress_data = []
            for row in cursor.fetchall():
                progress_data.append({
                    'date': row[0],
                    'games_played': row[1],
                    'wins': row[2],
                    'accuracy': row[3],
                    'total_games': row[4],
                    'total_wins': row[5]
                })
                
            return {
                'daily_progress': progress_data,
                'improvement_rate': self._calculate_improvement_rate(progress_data)
            }
        except Exception as e:
            print(f"Error getting player progress: {e}")
            return {}

    def _calculate_improvement_rate(self, progress_data: List[Dict]) -> float:
        """حساب معدل تحسن اللاعب"""
        if len(progress_data) < 2:
            return 0.0
        
        try:
            # حساب معدل الفوز في أول 10 ألعاب
            early_games = progress_data[:10]
            early_win_rate = sum(game['wins'] for game in early_games) / sum(game['games_played'] for game in early_games)
            
            # حساب معدل الفوز في آخر 10 ألعاب
            recent_games = progress_data[-10:]
            recent_win_rate = sum(game['wins'] for game in recent_games) / sum(game['games_played'] for game in recent_games)
            
            # حساب نسبة التحسن
            improvement = ((recent_win_rate - early_win_rate) / early_win_rate) * 100
            return round(improvement, 2)
        except ZeroDivisionError:
            return 0.0