import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseError(Exception):
    """استثناء مخصص للتعامل مع أخطاء قاعدة البيانات"""
    def __init__(self, message: str):
        """
        تهيئة استثناء قاعدة البيانات مع رسالة خطأ.

        Args:
            message (str): رسالة الخطأ التي تصف المشكلة
        """
        super().__init__(message)

class DatabaseManager:
    def __init__(self, db_path: str = 'battleship.db'):
        """
        دي دالة بتبدأ قاعدة البيانات وبتجهزها للاستخدام.
        
        المدخلات:
            db_path: ده مسار الملف اللي هنحط فيه قاعدة البيانات
                    لو مكتبناش حاجة هيبقى اسمه 'battleship.db'
        """
        # هنحاول نعمل الخطوات دي
        try:
            # أول حاجة هنفتح اتصال بقاعدة البيانات
            self.conn = sqlite3.connect(db_path)
            
            # هنشغل خاصية المفاتيح الخارجية عشان نربط الجداول ببعض
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # هننشئ الجداول اللي هنحتاجها
            self.create_tables()
            
        # لو حصل أي مشكلة
        except sqlite3.Error as e:
            # هنرمي رسالة خطأ توضح المشكلة
            raise DatabaseError(f"مقدرناش ننشئ قاعدة البيانات: {str(e)}")

    def execute_safe(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        دي وظيفة بتنفذ استعلام SQL بطريقة آمنة وبتتعامل مع الأخطاء لو حصلت

        المدخلات:
            query: ده الاستعلام اللي عايزين ننفذه في قاعدة البيانات
            params: دي البيانات اللي هنحطها في الاستعلام (اختياري)

        المخرجات:
            بترجع نتيجة تنفيذ الاستعلام

        الأخطاء:
            لو حصل مشكلة، هترمي DatabaseError مع رسالة بتوضح المشكلة
        """
        # هنحاول ننفذ الاستعلام
        try:
            # هننفذ الاستعلام ونرجع النتيجة
            result = self.conn.execute(query, params)
            return result
            
        # لو حصل أي مشكلة في قاعدة البيانات
        except sqlite3.Error as e:
            # هنرمي رسالة خطأ توضح المشكلة
            raise DatabaseError(f"خطأ في قاعدة البيانات: {str(e)}")

    def create_tables(self):
        """
        دي وظيفة بتعمل الجداول اللي هنحتاجها في قاعدة البيانات
        لو الجداول مش موجودة، هتعملها
        لو موجودة، مش هتعمل حاجة
        """
        try:
            # هنفتح اتصال مع قاعدة البيانات
            with self.conn:
                # هنعمل جدول اللاعبين
                # ده أهم جدول عندنا
                # فيه كل معلومات اللاعب زي:
                # - الاسم بتاعه
                # - عدد المرات اللي لعبها
                # - عدد المرات اللي كسب فيها
                # - عدد الطلقات اللي ضربها
                # - عدد المرات اللي صاب فيها
                # - نسبة التصويب بتاعته
                # - وقت ما عمل حساب
                # - آخر مرة لعب فيها
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS players (
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
                
                # هنعمل جدول إعدادات كل لاعب
                # زي حجم الشبكة اللي بيلعب عليها
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS player_settings (
                        player_id INTEGER PRIMARY KEY,
                        grid_size INTEGER DEFAULT 10,
                        FOREIGN KEY (player_id) REFERENCES players (id)
                            ON DELETE CASCADE
                    )
                ''')
                
                # هنعمل جدول تاريخ اللعب
                # عشان نحفظ فيه كل لعبة اللاعب لعبها
                # وإيه اللي حصل فيها
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS game_history (
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
                
                # هنعمل جدول إحصائيات السفن
                # عشان نعرف كل سفينة حصلها إيه في كل لعبة
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS ship_statistics (
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
                
        # لو حصل أي مشكلة
        except sqlite3.Error as e:
            # هنطبع الخطأ ونرميه للي استدعى الوظيفة
            print(f"في مشكلة حصلت وإحنا بنعمل الجداول: {e}")
            raise DatabaseError(f"مقدرناش نعمل الجداول: {str(e)}")

    def create_player(self, name: str) -> int:
        """
        الوظيفة دي بتعمل لاعب جديد في قاعدة البيانات وبترجع رقمه.
        
        بتاخد:
            name: اسم اللاعب اللي عايزين نضيفه
            
        بترجع:
            رقم اللاعب الجديد في قاعدة البيانات
            
        ممكن تطلع أخطاء:
            - لو الاسم ده موجود قبل كده
            - لو حصل أي مشكلة تانية
        """
        # هنحاول نضيف اللاعب الجديد
        try:
            # هنفتح اتصال مع قاعدة البيانات
            with self.conn:
                # هنطبع رسالة للتأكد
                print(f"إنشاء لاعب جديد بالاسم: {name}")
                
                # هنشيل المسافات الزيادة من الاسم
                clean_name = name.strip()
                
                # هنضيف اللاعب في الجدول
                # كل الأرقام هتبدأ بصفر (ما لعبش أي لعبة لسه)
                cursor = self.conn.execute('''
                    INSERT INTO players 
                    (name, games_played, games_won, total_shots, total_hits, accuracy) 
                    VALUES (?, 0, 0, 0, 0, 0.0)
                ''', (clean_name,))
                
                # هناخد رقم اللاعب اللي اتضاف
                player_id = cursor.lastrowid
                
                # هنطبع رسالة للتأكد
                print(f"تم إنشاء اللاعب بنجاح بالمعرف: {player_id}")
                
                # هنرجع رقم اللاعب
                return player_id
                
        # لو الاسم موجود قبل كده
        except sqlite3.IntegrityError:
            print("خطأ: اسم اللاعب موجود بالفعل")
            raise DatabaseError("اللاعب موجود بالفعل")
            
        # لو في أي مشكلة تانية
        except Exception as e:
            print(f"خطأ في إنشاء اللاعب: {e}")
            raise DatabaseError(f"فشل في إنشاء اللاعب: {str(e)}")

    def get_player(self, player_id: int) -> Optional[Dict]:
        """
        الوظيفة دي بتجيب معلومات اللاعب من قاعدة البيانات
        
        بتاخد:
            player_id: رقم اللاعب اللي عايزين نجيب معلوماته
            
        بترجع:
            معلومات اللاعب في شكل قاموس، أو None لو مش موجود
        """
        # هنحاول نجيب بيانات اللاعب
        try:
            # هنسأل قاعدة البيانات عن اللاعب ده
            cursor = self.conn.execute(
                'SELECT * FROM players WHERE id = ?',
                (player_id,)
            )
            
            # هنجيب أول صف من النتيجة
            بيانات_اللاعب = cursor.fetchone()
            
            # لو لقينا اللاعب
            if بيانات_اللاعب:
                # هنرجع معلوماته في قاموس
                # لو في أي معلومة مش موجودة هنحط قيمة افتراضية
                return {
                    'id': بيانات_اللاعب[0],                    # رقم اللاعب
                    'name': بيانات_اللاعب[1],                  # اسم اللاعب
                    'games_played': بيانات_اللاعب[2] or 0,     # عدد المرات اللي لعبها
                    'games_won': بيانات_اللاعب[3] or 0,        # عدد المرات اللي كسب فيها
                    'total_shots': بيانات_اللاعب[4] or 0,      # عدد الطلقات الكلي
                    'total_hits': بيانات_اللاعب[5] or 0,       # عدد الإصابات
                    'accuracy': بيانات_اللاعب[6] or 0.0,       # نسبة الدقة
                    'created_at': بيانات_اللاعب[7] or None,    # وقت إنشاء الحساب
                    'last_played': بيانات_اللاعب[8] or None    # آخر مرة لعب فيها
                }
            
            # لو مش موجود هنرجع None
            return None
            
        # لو حصل أي مشكلة
        except Exception as e:
            # هنطبع رسالة الخطأ
            print(f"خطأ في جلب اللاعب: {e}")
            return None
            return None

    def save_game_result(self, player_id: int, result: Dict[str, Any]):
        """
        الوظيفة دي بتحفظ نتيجة اللعبة وبتحدث معلومات اللاعب

        بتاخد:
            player_id: رقم اللاعب
            result: معلومات نتيجة اللعبة (عدد الضربات، عدد الإصابات، إلخ)

        لو حصل مشكلة هترجع خطأ
        """
        try:
            # هنتأكد الأول إن اللاعب موجود
            if not self.get_player(player_id):
                raise ValueError(f"مفيش لاعب برقم {player_id}")
            
            # هنحسب نسبة الدقة (كام إصابة من كل الضربات)
            if result['moves'] > 0:
                accuracy = (result['hits'] / result['moves']) * 100
            else:
                accuracy = 0
            
            # هنحفظ نتيجة اللعبة في جدول التاريخ
            self.execute_safe('''
                INSERT INTO game_history 
                (player_id, result, grid_size, moves, hits, misses, accuracy, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_id,                  # رقم اللاعب
                result['outcome'],          # نتيجة اللعبة (فوز أو خسارة)
                result.get('grid_size', 10),# حجم الشبكة
                result['moves'],            # عدد الضربات
                result['hits'],             # عدد الإصابات
                result['misses'],           # عدد المحاولات الفاشلة
                accuracy,                   # نسبة الدقة
                result['duration']          # مدة اللعبة
            ))
            
            # هنحدث معلومات اللاعب
            self.execute_safe('''
                UPDATE players 
                SET games_played = games_played + 1,
                    games_won = games_won + CASE WHEN ? = 'win' THEN 1 ELSE 0 END,
                    total_shots = total_shots + ?,
                    total_hits = total_hits + ?,
                    accuracy = (total_hits * 100.0 / NULLIF(total_shots, 0)),
                    last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                result['outcome'],  # نتيجة اللعبة
                result['moves'],    # عدد الضربات
                result['hits'],     # عدد الإصابات
                player_id          # رقم اللاعب
            ))
                
        except Exception as e:
            # لو حصل أي مشكلة هنطبع رسالة الخطأ
            print(f"في مشكلة حصلت وأنا بحفظ نتيجة اللعبة: {e}")
            raise

    def get_player_statistics(self, player_id: int) -> Dict[str, Any]:
        """
        بتجيب معلومات وإحصائيات عن اللاعب

        Args:
            player_id: رقم اللاعب اللي عايزين نجيب معلوماته

        Returns:
            قاموس فيه كل المعلومات والإحصائيات بتاعت اللاعب
        """
        try:
            # هنجيب المعلومات من قاعدة البيانات
            cursor = self.conn.execute('''
                SELECT 
                    p.games_played,
                    p.games_won,
                    p.total_shots,
                    p.total_hits,
                    p.accuracy,
                    MIN(g.moves) as best_game,
                    MAX(g.moves) as worst_game,
                    AVG(g.duration) as avg_duration,
                    COUNT(CASE WHEN g.result = 'win' AND g.moves <= 30 THEN 1 END) as quick_wins,
                    ROUND(CAST(p.games_won AS FLOAT) / NULLIF(p.games_played, 0) * 100, 2) as win_rate,
                    ROUND(AVG(g.accuracy), 2) as accuracy_rate
                FROM players p
                LEFT JOIN game_history g ON p.id = g.player_id
                WHERE p.id = ?
                GROUP BY p.id
            ''', (player_id,))
            
            # هنجيب النتيجة
            row = cursor.fetchone()
            
            # لو لقينا معلومات هنرجعها
            if row:
                return {
                    'games_played': row[0],     # عدد المرات اللي لعب فيها
                    'games_won': row[1],        # عدد المرات اللي كسب فيها
                    'total_shots': row[2],      # عدد الضربات الكلي
                    'total_hits': row[3],       # عدد الإصابات الكلي
                    'accuracy': row[4],         # نسبة التصويب
                    'best_game': row[5],        # أفضل لعبة (أقل عدد ضربات)
                    'worst_game': row[6],       # أسوأ لعبة (أكبر عدد ضربات)
                    'avg_duration': row[7],     # متوسط وقت اللعب
                    'quick_wins': row[8],       # عدد المرات اللي كسب فيها بسرعة
                    'win_rate': row[9],         # نسبة الفوز
                    'accuracy_rate': row[10]    # متوسط نسبة التصويب
                }
            
            # لو مفيش معلومات هنرجع قاموس فاضي
            return {}
            
        except Exception as e:
            # لو في مشكلة هنطبع الخطأ ونرجع قاموس فاضي
            print(f"في مشكلة حصلت وأنا بجيب معلومات اللاعب: {e}")
            return {}

    def get_game_history(self, player_id: int, limit: int = 10) -> List[Dict]:
        """
        الدالة دي بتجيب تاريخ آخر كام لعبة اللاعب لعبها
        
        بتاخد:
            - رقم اللاعب (player_id)
            - عدد الألعاب اللي عايز تجيبها (limit) - لو مكتبتش حاجة هتجيب آخر 10 ألعاب
            
        بترجع:
            - قايمة فيها معلومات عن كل لعبة (زي النتيجة وعدد الحركات والتاريخ)
        """
        try:
            # هنجيب البيانات من جدول تاريخ الألعاب
            cursor = self.conn.execute('''
                SELECT * FROM game_history 
                WHERE player_id = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (player_id, limit))
            
            # هنجيب كل الصفوف اللي لقيناها
            all_games = cursor.fetchall()
            
            # هنعمل قايمة فاضية نحط فيها معلومات كل لعبة
            games_list = []
            
            # هنلف على كل لعبة ونجهز معلوماتها
            for row in all_games:
                game_info = {
                    'id': row[0],               # رقم اللعبة
                    'result': row[2],           # نتيجة اللعبة (فوز ولا خسارة)
                    'grid_size': row[3],        # حجم الشبكة
                    'moves': row[4],            # عدد الحركات
                    'hits': row[5],             # عدد المرات اللي ضرب فيها صح
                    'misses': row[6],           # عدد المرات اللي ضرب فيها غلط
                    'accuracy': row[7],         # نسبة التصويب
                    'duration': row[8],         # مدة اللعبة
                    'played_at': row[10]        # تاريخ اللعب
                }
                # هنضيف معلومات اللعبة للقايمة
                games_list.append(game_info)
            
            return games_list
            
        except Exception as e:
            # لو في مشكلة حصلت هنطبع الخطأ ونرجع قايمة فاضية
            print(f"في مشكلة حصلت وأنا بجيب تاريخ الألعاب: {e}")
            return []

    def close(self):
        """
        الدالة دي بتقفل الاتصال بقاعدة البيانات
        لازم نستخدمها لما نخلص شغل عشان نحافظ على قاعدة البيانات
        وكمان عشان منضيعش موارد الكمبيوتر
        
        مثال للاستخدام:
        db = DatabaseManager()
        # نعمل شغلنا هنا
        db.close()  # نقفل الاتصال لما نخلص
        """
        # هنا بنقول لقاعدة البيانات اننا خلصنا شغل وعايزين نقفل الاتصال
        self.conn.close()

    def get_leaderboard(self, limit: int = 10, time_period: str = 'all') -> List[Dict]:
        """
        بتجيب قائمة أحسن اللاعبين في اللعبة.
        
        المدخلات:
            limit: عدد اللاعبين اللي عايزين نجيبهم (افتراضياً 10)
            time_period: الفترة الزمنية ('all' لكل الوقت، 'week' لآخر أسبوع، 'month' لآخر شهر، 'year' لآخر سنة)
        
        المخرجات:
            قائمة فيها معلومات كل لاعب (اسمه، عدد مرات اللعب، عدد مرات الفوز، إلخ)
        """
        try:
            # هنحدد الفترة الزمنية اللي هنجيب فيها النتائج
            time_filter = ''
            if time_period == 'week':
                time_filter = "AND g.played_at >= date('now', '-7 days')"  # آخر 7 أيام
            elif time_period == 'month':
                time_filter = "AND g.played_at >= date('now', '-1 month')"  # آخر شهر
            elif time_period == 'year':
                time_filter = "AND g.played_at >= date('now', '-1 year')"  # آخر سنة

            # هنجيب البيانات من قاعدة البيانات
            cursor = self.conn.execute(f'''
                WITH PlayerStats AS (
                    SELECT 
                        p.name,                                                    -- اسم اللاعب
                        COUNT(DISTINCT g.id) as games_played,                      -- عدد مرات اللعب
                        SUM(CASE WHEN g.result = 'win' THEN 1 ELSE 0 END) as games_won,  -- عدد مرات الفوز
                        AVG(g.accuracy) as avg_accuracy,                           -- متوسط الدقة
                        MIN(g.moves) as best_game,                                -- أفضل لعبة (أقل عدد حركات)
                        COUNT(DISTINCT CASE WHEN g.result = 'win' AND g.moves <= 30 
                            THEN g.id END) as quick_wins                          -- عدد مرات الفوز السريع
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
                    ROUND(CAST(games_won AS FLOAT) / games_played * 100, 2) as win_ratio,  -- نسبة الفوز
                    ROUND(avg_accuracy, 2) as accuracy,                                     -- الدقة
                    best_game,
                    quick_wins,
                    ROUND(CAST(quick_wins AS FLOAT) / games_won * 100, 2) as quick_win_ratio  -- نسبة الفوز السريع
                FROM PlayerStats
                ORDER BY win_ratio DESC, accuracy DESC
                LIMIT ?
            ''', (limit,))
            
            # هنحول النتائج لقائمة من القواميس عشان تكون أسهل في الاستخدام
            results = []
            for row in cursor.fetchall():
                player_info = {
                    'name': row[0],             # اسم اللاعب
                    'games_played': row[1],     # عدد مرات اللعب
                    'games_won': row[2],        # عدد مرات الفوز
                    'win_ratio': row[3],        # نسبة الفوز
                    'accuracy': row[4],         # الدقة
                    'best_game': row[5],        # أفضل لعبة
                    'quick_wins': row[6],       # عدد مرات الفوز السريع
                    'quick_win_ratio': row[7]   # نسبة الفوز السريع
                }
                results.append(player_info)
            
            return results

        except Exception as e:
            # لو في مشكلة حصلت هنطبع الخطأ ونرجع قائمة فاضية
            print(f"في مشكلة حصلت وأنا بجيب قائمة المتصدرين: {e}")
            return []

    def get_ship_statistics(self, player_id: int) -> Dict[str, Any]:
        """
        الدالة دي بتجيب معلومات عن أداء السفن بتاعة اللاعب في كل المعارك اللي لعبها
        
        بتاخد:
            player_id: رقم اللاعب في قاعدة البيانات
        
        بترجع:
            معلومات عن كل سفينة زي:
            - عدد المعارك اللي شاركت فيها
            - عدد المرات اللي غرقت فيها
            - متوسط عدد الضربات اللي أكلتها
            - متوسط عدد الأدوار اللي استغرقتها عشان تغرق
        """
        # هنجهز استعلام قاعدة البيانات
        cursor = self.conn.execute('''
            SELECT 
                sh.ship_name,                   -- اسم السفينة
                COUNT(*) as total_battles,      -- عدد المعارك
                -- عدد مرات الغرق
                SUM(CASE WHEN sh.was_sunk THEN 1 ELSE 0 END) as times_sunk,
                AVG(sh.hits_taken) as avg_hits_taken,        -- متوسط الضربات
                AVG(sh.turns_to_sink) as avg_turns_to_sink   -- متوسط أدوار الغرق
            FROM ship_statistics sh
            JOIN game_history gh ON sh.game_id = gh.id
            WHERE gh.player_id = ?
            GROUP BY sh.ship_name
        ''', (player_id,))
        
        # هنحول النتائج لشكل سهل نتعامل معاه
        ship_stats = {}
        for row in cursor.fetchall():
            ship_name = row[0]
            ship_stats[ship_name] = {
                'total_battles': row[1],      # كل المعارك
                'times_sunk': row[2],         # مرات الغرق
                'avg_hits_taken': row[3],     # متوسط الضربات
                'avg_turns_to_sink': row[4]   # متوسط الأدوار للغرق
            }
        
        return ship_stats

    def save_game_settings(self, player_id: int, settings: Dict[str, Any]):
        """
        الدالة دي بتحفظ إعدادات اللعبة بتاعة اللاعب في قاعدة البيانات
        
        بتاخد:
            player_id: رقم اللاعب في قاعدة البيانات
            settings: قاموس فيه الإعدادات اللي عايزين نحفظها:
                     - حجم الشبكة (grid_size)
                     - الصوت شغال ولا لا (sound_enabled) 
                     - الموسيقى شغالة ولا لا (music_enabled)
        
        مثال للإعدادات:
        {
            'grid_size': 10,      # حجم الشبكة 10×10
            'sound_enabled': True, # الصوت شغال
            'music_enabled': True  # الموسيقى شغالة
        }
        """
        # هنجيب الإعدادات من القاموس، ولو مش موجودة هناخد القيم الافتراضية
        grid_size = settings.get('grid_size', 10)         # لو مش موجودة هتكون 10
        sound_on = settings.get('sound_enabled', True)    # لو مش موجودة هتكون True
        music_on = settings.get('music_enabled', True)    # لو مش موجودة هتكون True
        
        # هنحفظ الإعدادات في قاعدة البيانات
        # لو الإعدادات موجودة قبل كده هيتم تحديثها
        # لو مش موجودة هيتم إضافتها جديد
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO player_settings 
                (player_id, grid_size, sound_enabled, music_enabled)
                VALUES (?, ?, ?, ?)
            ''', (player_id, grid_size, sound_on, music_on))

    def get_game_settings(self, player_id: int) -> Dict[str, Any]:
        """
        الدالة دي بتجيب إعدادات اللعبة بتاعة اللاعب من قاعدة البيانات
        
        بتاخد:
            player_id: رقم اللاعب في قاعدة البيانات
        
        بترجع:
            قاموس فيه الإعدادات دي:
            - حجم الشبكة (grid_size) 
            - الصوت شغال ولا لا (sound_enabled)
            - الموسيقى شغالة ولا لا (music_enabled)
        """
        # هنجيب إعدادات اللاعب من قاعدة البيانات
        cursor = self.conn.execute('''
            SELECT grid_size, sound_enabled, music_enabled
            FROM player_settings
            WHERE player_id = ?
        ''', (player_id,))
        
        # هنشوف لو لقينا إعدادات للاعب ده
        settings_from_db = cursor.fetchone()
        
        # لو لقينا إعدادات، هنرجعها
        if settings_from_db:
            game_settings = {
                'grid_size': settings_from_db[0],  # حجم الشبكة
                'sound_enabled': bool(settings_from_db[1]),  # الصوت شغال ولا لا 
                'music_enabled': bool(settings_from_db[2])   # الموسيقى شغالة ولا لا
            }
            return game_settings
            
        # لو مفيش إعدادات، هنرجع الإعدادات الافتراضية
        default_settings = {
            'grid_size': 10,       # حجم الشبكة الافتراضي 10×10
            'sound_enabled': True,  # الصوت شغال افتراضياً
            'music_enabled': True   # الموسيقى شغالة افتراضياً
        }
        return default_settings

    def delete_player_data(self, player_id: int):
        """
        حذف جميع البيانات المتعلقة باللاعب من قاعدة البيانات.

        Args:
            player_id (int): معرف اللاعب.
        """
        with self.conn:
            # حذف من إحصائيات السفن عبر تاريخ اللعب
            self.conn.execute('''
                DELETE FROM ship_statistics 
                WHERE game_id IN (
                    SELECT id FROM game_history WHERE player_id = ?
                )
            ''', (player_id,))
            
            # حذف من تاريخ اللعب
            self.conn.execute('''
                DELETE FROM game_history 
                WHERE player_id = ?
            ''', (player_id,))
            
            # حذف من إعدادات اللاعبين
            self.conn.execute('''
                DELETE FROM player_settings 
                WHERE player_id = ?
            ''', (player_id,))
            
            # حذف من جدول اللاعبين
            self.conn.execute('''
                DELETE FROM players 
                WHERE id = ?
            ''', (player_id,))

    def check_connection(self) -> bool:
        """
        الوظيفة دي بتتأكد إن قاعدة البيانات شغالة ولا لأ
        بتعمل كده عن طريق إنها بتحاول تنفذ أمر بسيط جداً
        لو نجح الأمر يبقى قاعدة البيانات شغالة
        لو فشل يبقى في مشكلة في الاتصال

        Returns:
            bool: بترجع True لو قاعدة البيانات شغالة، False لو مش شغالة
        """
        # هنحاول ننفذ أمر بسيط جداً (اختيار الرقم 1)
        try:
            # لو الأمر ده نجح يبقى الاتصال شغال
            self.conn.execute("SELECT 1")
            # فنرجع True
            return True
            
        # لو حصل أي مشكلة في تنفيذ الأمر
        except sqlite3.Error:
            # يبقى في مشكلة في الاتصال فنرجع False
            return False

    def reconnect(self):
        """
        الوظيفة دي بتحاول تعيد الاتصال بقاعدة البيانات لو الاتصال اتقطع
        
        خطوات الوظيفة:
        1. بتتأكد الأول إن الاتصال مقطوع فعلاً
        2. لو مقطوع، بتحاول توصل تاني
        3. لو محاولة الاتصال فشلت، بتظهر رسالة خطأ
        """
        # هنجرب نعمل الخطوات دي
        try:
            # نشوف الأول - الاتصال شغال ولا لأ؟
            اتصال_شغال = self.check_connection()
            
            # لو الاتصال مش شغال
            if not اتصال_شغال:
                # نحاول نتصل تاني بقاعدة البيانات
                self.conn = sqlite3.connect('battleship.db')
                # نشغل خاصية الـ foreign keys
                self.conn.execute("PRAGMA foreign_keys = ON")
                
        # لو حصل أي مشكلة في الاتصال
        except sqlite3.Error as e:
            # نظهر رسالة خطأ للمستخدم
            raise DatabaseError(f"تعذر إعادة الاتصال: {str(e)}")

    def backup_database(self, backup_path: str):
        """
        الوظيفة دي بتعمل نسخة احتياطية من قاعدة البيانات وبتحفظها في مكان تاني
        عشان لو حصل أي مشكلة نقدر نرجع البيانات تاني

        المدخلات:
            backup_path: المكان اللي عايزين نحفظ فيه النسخة الاحتياطية
            مثال: "C:/backups/my_backup.db"

        لو حصل مشكلة:
            هتظهر رسالة خطأ توضح إيه المشكلة اللي حصلت
        """
        # هنحاول نعمل النسخة الاحتياطية
        try:
            # هنفتح ملف جديد عشان نحط فيه النسخة الاحتياطية
            ملف_النسخة = sqlite3.connect(backup_path)
            
            # هننسخ كل البيانات من قاعدة البيانات الأصلية للملف الجديد
            with ملف_النسخة:
                self.conn.backup(ملف_النسخة)
            
            # نقفل الملف بعد ما نخلص
            ملف_النسخة.close()
            
        # لو حصلت أي مشكلة
        except sqlite3.Error as المشكلة:
            # نقول للمستخدم إن في مشكلة حصلت
            raise DatabaseError(f"مقدرناش نعمل النسخة الاحتياطية: {str(المشكلة)}")

    def find_player_by_name(self, name: str) -> Optional[Dict]:
        """
        الوظيفة دي بتدور على لاعب معين في قاعدة البيانات عن طريق اسمه.
        بتاخد اسم اللاعب وبتدور عليه وبترجع كل المعلومات بتاعته.
        
        لو لقت اللاعب هترجع معلوماته كاملة.
        لو ملقتوش هترجع None يعني مفيش حاجة.
        """
        # هنحاول نعمل البحث ونشوف هنلاقي اللاعب ولا لأ
        try:
            # هننظف الاسم من المسافات الزيادة في الأول والآخر
            اسم_نظيف = name.strip()
            
            # هندور على اللاعب في قاعدة البيانات
            # مش هنفرق بين الحروف الكبيرة والصغيرة
            نتيجة_البحث = self.conn.execute(
                'SELECT * FROM players WHERE LOWER(name) = LOWER(?)', 
                (اسم_نظيف,)
            )
            
            # هنجيب أول نتيجة لقيناها
            بيانات_اللاعب = نتيجة_البحث.fetchone()
            
            # لو لقينا اللاعب
            if بيانات_اللاعب:
                # هنرجع كل المعلومات بتاعته في قاموس
                return {
                    'id': بيانات_اللاعب[0],  # الرقم التعريفي
                    'name': بيانات_اللاعب[1],  # الاسم
                    'games_played': بيانات_اللاعب[2] if بيانات_اللاعب[2] is not None else 0,  # عدد المرات اللي لعبها
                    'games_won': بيانات_اللاعب[3] if بيانات_اللاعب[3] is not None else 0,  # عدد المرات اللي كسب فيها
                    'total_shots': بيانات_اللاعب[4] if بيانات_اللاعب[4] is not None else 0,  # عدد الطلقات الكلي
                    'total_hits': بيانات_اللاعب[5] if بيانات_اللاعب[5] is not None else 0,  # عدد الإصابات
                    'accuracy': بيانات_اللاعب[6] if بيانات_اللاعب[6] is not None else 0.0,  # نسبة الدقة
                    'created_at': بيانات_اللاعب[7],  # تاريخ إنشاء الحساب
                    'last_played': بيانات_اللاعب[8]  # آخر مرة لعب فيها
                }
            
            # لو ملقيناش اللاعب
            return None
            
        # لو حصل أي مشكلة في البحث
        except Exception as المشكلة:
            # هنطبع المشكلة ونرجع None
            print(f"خطأ في البحث عن اللاعب بالاسم: {المشكلة}")
            return None

    def get_player_achievements(self, player_id: int) -> List[Dict]:
        """
        بتجيب إنجازات اللاعب من قاعدة البيانات
        
        بتاخد:
            player_id: رقم اللاعب في قاعدة البيانات
            
        بترجع:
            قائمة فيها كل الإنجازات اللي حققها اللاعب
        """
        # قائمة فاضية نحط فيها الإنجازات
        achievements = []
        
        try:
            # نجيب إحصائيات اللاعب الأول
            stats = self.get_player_statistics(player_id)
            
            # نشوف لو اللاعب لعب كتير
            if stats['games_played'] >= 100:
                # نضيف إنجاز اللعب الكتير
                achievements.append({
                    'title': 'لاعب مخضرم',
                    'description': 'لعب 100 لعبة أو أكثر',
                    'icon': '🎮'
                })
            
            # نشوف لو اللاعب بيكسب كتير
            if stats['win_rate'] >= 75:
                # نضيف إنجاز الفوز الكتير
                achievements.append({
                    'title': 'قائد محترف', 
                    'description': 'حافظ على نسبة فوز 75% أو أكثر',
                    'icon': '👑'
                })
            
            # نشوف لو اللاعب بيصيب كتير
            if stats['accuracy_rate'] >= 50:
                # نضيف إنجاز الدقة العالية
                achievements.append({
                    'title': 'رامي دقيق',
                    'description': 'حافظ على دقة 50% أو أكثر', 
                    'icon': '🎯'
                })
            
            # نشوف لو اللاعب بيكسب بسرعة
            if stats['quick_wins'] >= 10:
                # نضيف إنجاز الفوز السريع
                achievements.append({
                    'title': 'فوز سريع',
                    'description': 'حقق 10 انتصارات أو أكثر في أقل من 30 حركة',
                    'icon': '⚡'
                })
            
            # نرجع كل الإنجازات
            return achievements
            
        except Exception as e:
            # لو حصل أي مشكلة نطبعها ونرجع قائمة فاضية
            print(f"خطأ في جلب إنجازات اللاعب: {e}")
            return []

    def get_player_progress(self, player_id: int) -> Dict[str, Any]:
        """
        الدالة دي بتجيب معلومات عن تقدم اللاعب في اللعبة وبتحلل أداءه.
        بتجيب معلومات زي:
        - عدد المرات اللي لعبها في كل يوم
        - عدد المرات اللي كسب فيها 
        - نسبة دقة التصويب
        - إجمالي عدد المرات اللي لعبها
        - إجمالي عدد مرات الفوز

        المدخلات:
            player_id: رقم اللاعب في قاعدة البيانات

        المخرجات:
            قاموس فيه كل المعلومات دي، ولو حصل مشكلة بيرجع قاموس فاضي
        """
        try:
            # نجيب معلومات اللعب بتاعت اللاعب ده من قاعدة البيانات
            # هنجمع المعلومات دي حسب كل يوم لعب فيه
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
            
            # نخزن المعلومات في قائمة
            progress_data = []
            
            # نمشي على كل صف في النتيجة ونحط المعلومات في القائمة
            for row in cursor.fetchall():
                progress_data.append({
                    'date': row[0],             # التاريخ
                    'games_played': row[1],      # عدد المرات اللي لعبها
                    'wins': row[2],             # عدد مرات الفوز
                    'accuracy': row[3],         # نسبة الدقة
                    'total_games': row[4],      # إجمالي عدد اللعب
                    'total_wins': row[5]        # إجمالي عدد الفوز
                })
            
            # نرجع القاموس النهائي
            return {
                'daily_progress': progress_data,  # معلومات التقدم اليومي
                'improvement_rate': self._calculate_improvement_rate(progress_data)  # نسبة التحسن
            }
            
        except Exception as e:
            # لو حصل أي مشكلة نطبع الخطأ ونرجع قاموس فاضي
            print(f"خطأ في جلب تقدم اللاعب: {e}")
            return {}

    def _calculate_improvement_rate(self, progress_data: List[Dict]) -> float:
        """
        بتحسب نسبة تحسن اللاعب عن طريق مقارنة نتايجه في أول 10 ألعاب مع آخر 10 ألعاب

        Args:
            progress_data: قائمة فيها معلومات عن كل يوم لعب فيه اللاعب

        Returns:
            رقم بيمثل نسبة التحسن
        """
        # لو اللاعب معندوش على الأقل لعبتين، يبقى منقدرش نحسب التحسن
        if len(progress_data) < 2:
            return 0.0
        
        try:
            # هناخد أول 10 ألعاب
            early_games = progress_data[:10]
            
            # هنعد كام مرة كسب في أول 10 ألعاب
            early_total_wins = 0
            early_total_games = 0
            for game in early_games:
                early_total_wins = early_total_wins + game['wins']
                early_total_games = early_total_games + game['games_played']
            
            # نحسب نسبة الفوز في أول 10 ألعاب
            early_win_rate = early_total_wins / early_total_games
            
            # هناخد آخر 10 ألعاب
            recent_games = progress_data[-10:]
            
            # هنعد كام مرة كسب في آخر 10 ألعاب
            recent_total_wins = 0
            recent_total_games = 0
            for game in recent_games:
                recent_total_wins = recent_total_wins + game['wins']
                recent_total_games = recent_total_games + game['games_played']
            
            # نحسب نسبة الفوز في آخر 10 ألعاب
            recent_win_rate = recent_total_wins / recent_total_games
            
            # نحسب الفرق بين النسبتين ونحوله لنسبة مئوية
            improvement = ((recent_win_rate - early_win_rate) / early_win_rate) * 100
            
            # نقرب الرقم لخانتين عشرية
            return round(improvement, 2)
            
        except ZeroDivisionError:
            # لو حصل قسمة على صفر نرجع صفر
            return 0.0
