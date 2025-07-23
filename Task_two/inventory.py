import json
import os
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from book import Book

class BookstoreInventory: 
    def __init__(self, json_file: str = 'books.json'):
        self.json_file = json_file
        self.books: Dict[str, Book] = {}
        self.transaction_log = []
        self.load_inventory()
    
    def save_inventory(self) -> bool:
        try:
            
            if os.path.exists(self.json_file):
                backup_file = f"{self.json_file}.backup"
                os.rename(self.json_file, backup_file)
            
            data = {
                'books': {title: book.to_dict() for title, book in self.books.items()},
                'transaction_log': self.transaction_log,
                'last_updated': datetime.now().isoformat(),
                'total_books': len(self.books),
                'total_inventory_value': self.calculate_total_inventory_value()
            }
            
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Inventory saved to {self.json_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving inventory: {e}")
            return False
    
    def load_inventory(self) -> bool:
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
                
                books_data = data.get('books', {})
                for title, book_data in books_data.items():
                    self.books[title] = Book.from_dict(book_data)
                
                self.transaction_log = data.get('transaction_log', [])
                
                print(f"✅ Loaded {len(self.books)} books from {self.json_file}")
                return True
            else:
                print(f"📁 No existing inventory file. Starting fresh.")
                return True
                
        except Exception as e:
            print(f"❌ Error loading inventory: {e}")
            return False
    
    def add_book(self, title: str, author: str, price: float, stock: int = 0) -> str:
        book = Book(title, author, price, stock)
        
        if book.title in self.books:
            print(f"📚 Book already exists: {book.title}")
            return book.title
        
        self.books[book.title] = book
        
        self.log_transaction('ADD_BOOK', book.title, {
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'initial_stock': stock
        })
        
        print(f"✅ Added book: {book}")
        return book.title
    
    def find_book(self, search_term: str) -> List[Book]:
        search_term = search_term.lower().strip()
        results = []
        
        for book in self.books.values():
            if (search_term in book.title.lower() or 
                search_term in book.author.lower() or 
                search_term in book.title.lower()):
                results.append(book)
        
        return results
    
    def get_book_by_title(self, title: str) -> Optional[Book]:
        return self.books.get(title)
    
    def update_stock(self, title: str, quantity_change: int, reason: str = "Manual Update") -> bool:
        book = self.get_book_by_title(title)
        if not book:
            print(f"❌ Book with title {title} not found")
            return False
        
        old_stock = book.stock
        if book.update_stock(quantity_change):
            self.log_transaction('STOCK_UPDATE', title, {
                'old_stock': old_stock,
                'new_stock': book.stock,
                'change': quantity_change,
                'reason': reason
            })
            print(f"✅ Updated stock for '{book.title}': {old_stock} → {book.stock}")
            return True
        else:
            print(f"❌ Insufficient stock. Current: {book.stock}, Requested: {-quantity_change}")
            return False
    
    def sell_book(self, title: str, quantity: int = 1) -> bool:
        return self.update_stock(title, -quantity, f"Sale of {quantity} units")
    
    def restock_book(self, title: str, quantity: int) -> bool:
        return self.update_stock(title, quantity, f"Restock of {quantity} units")
    
    def update_price(self, title: str, new_price: float) -> bool:
        book = self.get_book_by_title(title)
        if not book:
            print(f"❌ Book with title {title} not found")
            return False
        
        old_price = book.price
        book.update_price(new_price)
        
        self.log_transaction('PRICE_UPDATE', title, {
            'old_price': old_price,
            'new_price': book.price
        })
        
        print(f"✅ Updated price for '{book.title}': ${old_price:.2f} → ${book.price:.2f}")
        return True
    
    def remove_book(self, title: str) -> bool:
        book = self.get_book_by_title(title)
        if not book:
            print(f"❌ Book with title {title} not found")
            return False
        
        if book.stock > 0:
            confirm = input(f"⚠️  Book '{book.title}' has {book.stock} units in stock. Remove anyway? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Operation cancelled")
                return False
        
        self.log_transaction('REMOVE_BOOK', title, {
            'title': book.title,
            'author': book.author,
            'final_stock': book.stock
        })
        
        del self.books[title]
        print(f"✅ Removed book: {book.title}")
        return True

    def log_transaction(self, action: str, title: str, details: Dict[str]):
        self.transaction_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'title': title,
            'details': details
        })
    
    def view_transaction_log(self, limit: int = 10):
        if not self.transaction_log:
            print("📜 No transactions recorded")
            return
        
        print(f"\n{'='*60}")
        print(f"📜 RECENT TRANSACTIONS (Last {limit})")
        print(f"{'='*60}")
        
        recent_transactions = self.transaction_log[-limit:]
        for i, transaction in enumerate(reversed(recent_transactions), 1):
            timestamp = transaction['timestamp']
            action = transaction['action']
            title = transaction['title']
            details = transaction['details']
            
            print(f"{i}. {timestamp}")
            print(f"   Action: {action}")
            print(f"   title: {title}")
            
            if action == 'ADD_BOOK':
                print(f"   Added: '{details['title']}' by {details['author']}")
                print(f"   Price: ${details['price']:.2f}, Initial Stock: {details['initial_stock']}")
            
            elif action == 'STOCK_UPDATE':
                print(f"   Stock: {details['old_stock']} → {details['new_stock']} ({details['change']:+d})")
                print(f"   Reason: {details['reason']}")
            
            elif action == 'PRICE_UPDATE':
                print(f"   Price: ${details['old_price']:.2f} → ${details['new_price']:.2f}")
            
            elif action == 'REMOVE_BOOK':
                print(f"   Removed: '{details['title']}'")
            
            print()
        
        print(f"{'='*60}\n")

def main():
    inventory = BookstoreInventory()
    
    print("📚 Welcome to Bookstore Inventory Management System!")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            command = input("📖 Enter command: ").strip().lower()
            
            if command in ['quit', 'exit']:
                inventory.save_inventory()
                print("👋 Goodbye!")
                break
            
            elif command == 'add':
                add_book_interactive(inventory)
            
            elif command == 'search':
                search_books_interactive(inventory)
            
            elif command == 'stock':
                update_stock_interactive(inventory)
            
            elif command == 'sell':
                sell_book_interactive(inventory)
            
            elif command == 'restock':
                restock_book_interactive(inventory)
            
            elif command == 'price':
                update_price_interactive(inventory)
            
            elif command == 'remove':
                remove_book_interactive(inventory)
            
            elif command == 'list':
                list_all_books(inventory)
            
            elif command == 'save':
                inventory.save_inventory()
            
            else:
                print("❌ Unknown command")
        except Exception as e:
            print(f"❌ An error occurred: {e}")

def add_book_interactive(inventory: BookstoreInventory):
    try:
        title = input("Enter book title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        author = input("Enter author name: ").strip()
        if not author:
            print("❌ Author cannot be empty")
            return
        
        price = float(input("Enter price: $"))
        if price < 0:
            print("❌ Price cannot be negative")
            return
        
        stock = int(input("Enter initial stock (default 0): ") or "0")
        if stock < 0:
            print("❌ Stock cannot be negative")
            return
        
        inventory.add_book(title, author, price, stock)
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")


def search_books_interactive(inventory: BookstoreInventory):
    search_term = input("Enter search term (title, author, or title): ").strip()
    if not search_term:
        print("❌ Search term cannot be empty")
        return
    
    results = inventory.find_book(search_term)
    
    if not results:
        print(f"❌ No books found matching '{search_term}'")
        return
    
    print(f"\n🔍 Found {len(results)} book(s):")
    print(f"{'='*80}")
    
    for i, book in enumerate(results, 1):
        value = book.calculate_value()
        status = "✅ In Stock" if book.is_in_stock() else "❌ Out of Stock"
        if book.is_low_stock():
            status = "⚠️  Low Stock"
        
        print(f"{i}. {book}")
        print(f"   title: {book.title}")
        print(f"   Status: {status}")
        print(f"   Total Value: ${value:.2f}")
        print()


def update_stock_interactive(inventory: BookstoreInventory):
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ title cannot be empty")
        return
    
    book = inventory.get_book_by_title(title)
    if not book:
        print(f"❌ Book with title {title} not found")
        return
    
    print(f"Current stock for '{book.title}': {book.stock}")
    
    try:
        change = int(input("Enter stock change (+/- amount): "))
        reason = input("Enter reason (optional): ").strip() or "Manual Update"
        inventory.update_stock(title, change, reason)
    except ValueError:
        print("❌ Invalid quantity")


def sell_book_interactive(inventory: BookstoreInventory):
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ title cannot be empty")
        return
    
    try:
        quantity = int(input("Enter quantity to sell (default 1): ") or "1")
        if quantity <= 0:
            print("❌ Quantity must be positive")
            return
        
        if inventory.sell_book(title, quantity):
            book = inventory.get_book_by_title(title)
            total_sale = math.ceil(book.price * quantity * 100) / 100
            print(f"💰 Sale completed! Total: ${total_sale:.2f}")
        
    except ValueError:
        print("❌ Invalid quantity")


def restock_book_interactive(inventory: BookstoreInventory):
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ title cannot be empty")
        return
    
    try:
        quantity = int(input("Enter quantity to add: "))
        if quantity <= 0:
            print("❌ Quantity must be positive")
            return
        
        inventory.restock_book(title, quantity)
        
    except ValueError:
        print("❌ Invalid quantity")


def update_price_interactive(inventory: BookstoreInventory):
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ title cannot be empty")
        return
    
    book = inventory.get_book_by_title(title)
    if not book:
        print(f"❌ Book with title {title} not found")
        return
    
    print(f"Current price for '{book.title}': ${book.price:.2f}")
    
    try:
        new_price = float(input("Enter new price: $"))
        if new_price < 0:
            print("❌ Price cannot be negative")
            return
        
        inventory.update_price(title, new_price)
        
    except ValueError:
        print("❌ Invalid price")


def remove_book_interactive(inventory: BookstoreInventory):
    title = input("Enter book title: ").strip()
    if not title:
        print("❌ title cannot be empty")
        return
    
    inventory.remove_book(title)


def list_all_books(inventory: BookstoreInventory):
    if not inventory.books:
        print("📚 No books in inventory")
        return
    
    books = sorted(inventory.books.values(), key=lambda x: x.title)
    
    print(f"\n{'='*100}")
    print(f"📚 ALL BOOKS IN INVENTORY ({len(books)} books)")
    print(f"{'='*100}")
    print(f"{'Title':<30} {'Author':<20} {'Price':<10} {'Stock':<8} {'Value':<10} {'Status':<12}")
    print(f"{'-'*100}")
    
    for book in books:
        value = book.calculate_value()
        status = "In Stock" if book.is_in_stock() else "Out of Stock"
        if book.is_low_stock():
            status = "Low Stock"
        
        title = book.title[:28] + "..." if len(book.title) > 30 else book.title
        author = book.author[:18] + "..." if len(book.author) > 20 else book.author
        
        print(f"{title:<30} {author:<20} ${book.price:<9.2f} {book.stock:<8} ${value:<9.2f} {status:<12}")
    
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()