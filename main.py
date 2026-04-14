import sqlite3

def rip_session(session_path):
    conn = sqlite3.connect(session_path)
    cur = conn.cursor()
    
    # Вытягиваем всех, кто когда-либо попадал в поле зрения аккаунта (кэш)
    cur.execute("SELECT id, username, phone, name FROM entities")
    entities = cur.fetchall()
    
    # Данные самой сессии (дата последнего входа, IP и т.д. иногда в поле 'version')
    cur.execute("SELECT * FROM sessions")
    meta = cur.fetchone()
    
    print(f"--- РЕЗУЛЬТАТЫ СЕССИИ ---")
    for e in entities:
        print(f"ID: {e[0]} | Nick: @{e[1]} | Phone: {e[2]} | Name: {e[3]}")
    
    conn.close()

if __name__ == __main__:
   filename = input('name your session: ')
   filename = filename.rstrip('.session')
   filename = f'{filename}.session'
   rip_session(filename)
