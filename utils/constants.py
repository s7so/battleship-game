"""
ملف الثوابت الخاص بلعبة Battleship
يحتوي على كل القيم الثابتة المستخدمة في اللعبة
"""

# أحجام الشبكة المتاحة
GRID_SIZES = [10, 15]  # يمكن للاعب الاختيار بين شبكة 10×10 أو 15×15

# الحجم الافتراضي للشبكة
GRID_SIZE = 10  # يتم استخدامه عند بدء اللعبة لأول مرة

# حجم الخلية في الواجهة الرسومية (بالبكسل)
CELL_SIZE = 40  # يحدد حجم كل خلية في شبكة اللعب

# تكوين السفن
# مفتاح: اسم السفينة
# قيمة: طول السفينة (عدد الخلايا)
SHIPS = {
    'Aircraft Carrier': 5,  # حاملة الطائرات - أكبر سفينة
    'Battleship': 4,       # السفينة الحربية
    'Submarine': 3,        # الغواصة
    'Destroyer': 3,        # المدمرة
    'Patrol Boat': 2       # قارب الدورية - أصغر سفينة
}

# ألوان الواجهة
WATER_COLOR = '#1E90FF'  # لون الماء (الخلايا الفارغة)
SHIP_COLOR = '#808080'   # لون السفن
HIT_COLOR = '#FF0000'    # لون الإصابة (أحمر)
MISS_COLOR = '#FFFFFF'   # لون الطلقة الفاشلة (أبيض)

# إعدادات قاعدة البيانات
DB_NAME = 'battleship.db'  # اسم ملف قاعدة البيانات SQLite