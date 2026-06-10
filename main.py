from app.manager import Manager
from app.database.db import get_connection, init_db
from app.database.db import init_db

from app.epub_builder.builder import EPUBBuilder

def main():
    init_db()
    manager = Manager()
    
    print("Novel Crawler - Manager Started")
    print(f"Loaded extensions: {list(manager.extensions.keys())}")
    
    while True:
        print("\n1. Crawl by URL")
        print("2. Check extension updates")
        print("3. Build EPUB")
        print("4. Search by title")
        print("5. Exit")
        choice = input("Select option: ").strip()
        
        if choice == "1":
            url = input("Enter novel URL: ").strip()
            result = manager.crawl(url)
            print(f"Result: {result}")
        
        elif choice == "2":
            print("Checking for updates...")
            updates = manager.ext_manager.check_updates()
            if updates:
                print(f"Updates available: {updates}")
                install = input("Install? (y/n): ").strip().lower()
                if install == 'y':
                    results = manager.ext_manager.install_updates(updates)
                    print(f"Installation results: {results}")
            else:
                print("All extensions up to date")
        
        elif choice == "3":
            # List novels
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author FROM novels")
            novels = cursor.fetchall()
            conn.close()
            
            if not novels:
                print("No novels in database")
                continue
            
            print("\nAvailable novels:")
            for i, novel in enumerate(novels, 1):
                print(f"{i}. {novel['title']} by {novel['author']}")
            
            try:
                idx = int(input("Select novel (number): ")) - 1
                novel_id = novels[idx]['id']
                
                builder = EPUBBuilder(novel_id)
                epub_path = builder.build()
                print(f"EPUB saved to: {epub_path}")
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "4":
            title = input("Enter novel title: ").strip()
            print("Search not yet implemented")
        
        elif choice == "5":
            print("Exiting...")
            break
        
if __name__ == "__main__":
    main()