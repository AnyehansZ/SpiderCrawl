from app.manager import Manager
from app.database.db import init_db
import sys

def main():
    """CLI entry point"""
    init_db()
    manager = Manager()
    
    print("Novel Crawler - Manager Started")
    print(f"Loaded extensions: {list(manager.extensions.keys())}")
    
    while True:
        print("\n1. Crawl by URL")
        print("2. Search by title")
        print("3. Exit")
        choice = input("Select option: ").strip()
        
        if choice == "1":
            url = input("Enter novel URL: ").strip()
            result = manager.crawl(url)
            print(f"Result: {result}")
        
        elif choice == "2":
            title = input("Enter novel title: ").strip()
            # Will implement after extension setup
            print("Search not yet implemented")
        
        elif choice == "3":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()