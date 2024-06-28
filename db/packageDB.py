import sqlite3

def store_package(packages):

    # SQLite 데이터베이스 파일 생성 또는 연결
    conn = sqlite3.connect('packages.db')
    cursor = conn.cursor()

    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name TEXT
    )
    '''
    cursor.execute(create_table_sql)
    conn.commit()

    for package_name in packages:
        insert_sql = 'INSERT INTO packages (package_name) VALUES (?)'
        cursor.execute(insert_sql, (package_name,))
        conn.commit()
    conn.close()
    print('finish\n')