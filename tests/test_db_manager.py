import os
import sys
import unittest

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager, DatabaseError


class TestDatabaseManager(unittest.TestCase):
    """اختبارات لفئة DatabaseManager"""

    def setUp(self):
        """يتم تنفيذه قبل كل اختبار"""
        try:
            # استخدام قاعدة بيانات اختبار مؤقتة
            self.test_db_path = 'test_battleship.db'
            # إزالة قاعدة البيانات القديمة إذا كانت موجودة
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
            self.db_manager = DatabaseManager(self.test_db_path)
        except Exception as e:
            self.fail(f"Failed to setup test database: {str(e)}")

    def tearDown(self):
        """يتم تنفيذه بعد كل اختبار"""
        try:
            # إغلاق الاتصال
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
            # حذف قاعدة البيانات المؤقتة
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
        except Exception as e:
            print(f"Warning: Error during cleanup: {str(e)}")

    def test_create_tables(self):
        """اختبار إنشاء الجداول"""
        try:
            self.db_manager.create_tables()
            # التحقق من وجود الجداول
            tables = self.db_manager.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [table[0] for table in tables]

            expected_tables = ['players', 'game_history', 'ship_statistics', 'player_settings']
            for table in expected_tables:
                self.assertIn(table, table_names)
        except Exception as e:
            self.fail(f"فشل إنشاء الجداول: {str(e)}")

    def test_create_and_get_player(self):
        """اختبار إنشاء واسترجاع بيانات اللاعب"""
        # إنشاء لاعب جديد
        player_name = "TestPlayer"
        player_id = self.db_manager.create_player(player_name)
        self.assertIsNotNone(player_id)

        # استرجاع بيانات اللاعب
        player = self.db_manager.get_player(player_id)
        self.assertIsNotNone(player)
        self.assertEqual(player['name'], player_name)
        self.assertEqual(player['games_played'], 0)

    def test_duplicate_player_name(self):
        """اختبار منع تكرار اسم اللاعب"""
        player_name = "TestPlayer"
        self.db_manager.create_player(player_name)

        # محاولة إنشاء لاعب بنفس الاسم
        with self.assertRaises(DatabaseError):
            self.db_manager.create_player(player_name)

    def test_save_game_result(self):
        """اختبار حفظ نتيجة اللعبة"""
        # إنشاء لاعب
        player_id = self.db_manager.create_player("TestPlayer")

        # حفظ نتيجة لعبة
        result = {
            'outcome': 'win',
            'moves': 30,
            'hits': 15,
            'misses': 15,
            'duration': 300,
            'grid_size': 10
        }

        try:
            self.db_manager.save_game_result(player_id, result)

            # التحقق من تحديث إحصائيات اللاعب
            player = self.db_manager.get_player(player_id)
            self.assertEqual(player['games_played'], 1)
            self.assertEqual(player['games_won'], 1)
            self.assertEqual(player['total_shots'], 30)
            self.assertEqual(player['total_hits'], 15)
        except Exception as e:
            self.fail(f"فشل حفظ نتيجة اللعبة: {str(e)}")

    def test_get_player_statistics(self):
        """اختبار استرجاع إحصائيات اللاعب"""
        # إنشاء لاعب وحفظ بعض النتائج
        player_id = self.db_manager.create_player("TestPlayer")

        # حفظ عدة نتائج
        results = [
            {'outcome': 'win', 'moves': 20, 'hits': 10, 'misses': 10, 'duration': 200},
            {'outcome': 'loss', 'moves': 25, 'hits': 12, 'misses': 13, 'duration': 250}
        ]

        for result in results:
            self.db_manager.save_game_result(player_id, result)

        # استرجاع الإحصائيات
        stats = self.db_manager.get_player_statistics(player_id)
        self.assertEqual(stats['total_games'], 2)
        self.assertEqual(stats['wins'], 1)

    def test_find_player_by_name(self):
        """اختبار البحث عن لاعب بالاسم"""
        player_name = "TestPlayer"
        original_id = self.db_manager.create_player(player_name)

        # البحث عن اللاعب
        found_player = self.db_manager.find_player_by_name(player_name)
        self.assertIsNotNone(found_player)
        self.assertEqual(found_player['id'], original_id)

        # البحث عن لاعب غير موجود
        not_found = self.db_manager.find_player_by_name("NonExistentPlayer")
        self.assertIsNone(not_found)

    def test_get_leaderboard(self):
        """اختبار استرجاع لوحة المتصدرين"""
        # إنشاء عدة لاعبين مع نتائج مختلفة
        players = [
            ("Player1", [{'outcome': 'win'}, {'outcome': 'win'}]),
            ("Player2", [{'outcome': 'win'}, {'outcome': 'loss'}]),
            ("Player3", [{'outcome': 'loss'}, {'outcome': 'loss'}])
        ]

        for name, results in players:
            player_id = self.db_manager.create_player(name)
            for result in results:
                result.update({'moves': 20, 'hits': 10, 'misses': 10, 'duration': 200})
                self.db_manager.save_game_result(player_id, result)

        # استرجاع لوحة المتصدرين
        leaderboard = self.db_manager.get_leaderboard()
        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]['name'], "Player1")  # أعلى نسبة فوز

    def test_delete_player_data(self):
        """اختبار حذف بيانات اللاعب"""
        player_id = self.db_manager.create_player("TestPlayer")

        # حفظ بعض النتائج
        result = {
            'outcome': 'win',
            'moves': 20,
            'hits': 10,
            'misses': 10,
            'duration': 200
        }
        self.db_manager.save_game_result(player_id, result)

        # حذف بيانات اللاعب
        self.db_manager.delete_player_data(player_id)

        # التحقق من حذف البيانات
        player = self.db_manager.get_player(player_id)
        self.assertIsNone(player)

    def test_connection_management(self):
        """اختبار إدارة الاتصال بقاعدة البيانات"""
        # التحقق من الاتصال
        self.assertTrue(self.db_manager.check_connection())

        # إغلاق الاتصال وإعادة الاتصال
        self.db_manager.close()
        self.assertFalse(self.db_manager.check_connection())

        self.db_manager.reconnect()
        self.assertTrue(self.db_manager.check_connection())

    def test_backup_database(self):
        """اختبار عمل نسخة احتياطية"""
        backup_path = 'backup_test.db'

        try:
            # إنشاء بعض البيانات
            self.db_manager.create_player("TestPlayer")

            # عمل نسخة احتياطية
            self.db_manager.backup_database(backup_path)

            # التحقق من وجود ملف النسخة الاحتياطية
            self.assertTrue(os.path.exists(backup_path))
        finally:
            # تنظيف
            if os.path.exists(backup_path):
                os.remove(backup_path)


if __name__ == '__main__':
    unittest.main()
