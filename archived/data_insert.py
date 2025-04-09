import sqlite3

conn = sqlite3.connect('novel_data.db')
cursor = conn.cursor()

# 执行上述INSERT语句

slq_lang = '''
SELECT * FROM cultivation_realms ORDER BY realm_level;
'''
# with open(sql, 'r') as f:
#     cursor.executescript(f.read())
cursor.executescript(slq_lang)
conn.commit()
conn.close()