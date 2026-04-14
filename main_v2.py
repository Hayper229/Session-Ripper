import sqlite3
import os
import time
from colorama import init, Fore, Style

# Инициализация цветов
init(autoreset=True)

def rip_session(session_path):
    # Очищаем путь от случайных пробелов и кавычек
    session_path = session_path.strip().replace("'", "").replace('"', "")
    
    # Авто-добавление расширения, если пользователь его не ввел
    if not session_path.endswith('.session'):
        session_path += '.session'

    if not os.path.exists(session_path):
        print(f"{Fore.RED}[!] Ошибка: Файл {session_path} не найден в текущей директории.")
        return

    timestamp = time.asctime()
    print(f"\n{Fore.CYAN}[{timestamp}] {Fore.YELLOW}Начинаю криминалистический анализ...")

    try:
        conn = sqlite3.connect(session_path)
        cur = conn.cursor()

        # Парсим инфраструктуру
        cur.execute("SELECT dc_id, api_id, auth_key FROM sessions")
        meta = cur.fetchone()
        
        # Парсим кэш сущностей
        cur.execute("SELECT id, username, phone, name FROM entities")
        entities = cur.fetchall()

        print(f"\n{Fore.GREEN}=== ОТЧЕТ TraceDNA: {os.path.basename(session_path)} ===")
        print(f"{Fore.WHITE}Запуск: {timestamp}")
        
        if meta:
            dc, aid, key = meta
            print(f"{Fore.MAGENTA}Инфраструктура: DC {dc} | API ID: {aid if aid else 'N/A'}")
            print(f"{Fore.MAGENTA}Auth Key (HEX): {key.hex()[:48]}...")

        print(f"\n{Fore.BLUE}[*] Извлечено связей: {len(entities)}")
        print(f"{Fore.WHITE}{'-'*75}")

        # Вывод таблицы
        for e in entities:
            eid, nick, phone, name = e
            u_nick = f"@{nick}" if nick else f"{Fore.RED}unknown{Fore.RESET}"
            u_phone = f"+{phone}" if phone else f"{Fore.RED}hidden{Fore.RESET}"
            u_name = name if name else "NoName"
            
            print(f"{Fore.GREEN}[+] {Fore.WHITE}ID: {Fore.YELLOW}{str(eid):<14} "
                  f"{Fore.WHITE}| Ник: {u_nick:<18} "
                  f"{Fore.WHITE}| Имя: {u_name:<20} "
                  f"{Fore.WHITE}| Тел: {u_phone}")

        conn.close()
        print(f"\n{Fore.GREEN}=== АНАЛИЗ ЗАВЕРШЕН [{time.asctime()}] ===")

    except Exception as e:
        print(f"{Fore.RED}[!] Ошибка при парсинге: {e}")

if __name__ == "__main__":
    # Очистка экрана для Kali
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print(f"{Fore.RED}{Style.BRIGHT}--- ULTIMATE SESSION RIPPER v4.5 ---")
    filename = input(f"{Fore.WHITE}Введите название сессии (например, 1 или 1.session): ")
    
    rip_session(filename)
