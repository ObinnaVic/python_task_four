import json
import os
from datetime import datetime
from budget import Transaction, group_by_category, calculate_totals, calculate_grand_total

class BudgetTracker:
    def __init__(self, data_file: str = 'expenses.json'):
        self.data_file = data_file
        self.transactions = []
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.transactions = [Transaction.from_dict(t) for t in data]
                print(f"Loaded {len(self.transactions)} transactions")
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            print("No existing data file found")
    
    def save_data(self):
        try:
            data = [transaction.to_dict() for transaction in self.transactions]
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print("Data saved successfully")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_transaction(self):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            date = input(f"Enter date (YYYY-MM-DD) [{today}]: ").strip() or today
            
            category = input("Enter category: ").strip()
            if not category:
                print("Category cannot be empty")
                return
            
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be positive")
                return
            
            transaction = Transaction(date, category, amount)
            self.transactions.append(transaction)
            print(f"Added transaction: {date} - {category} - ${amount:.2f}")
            
        except ValueError:
            print("Invalid amount entered")
        except Exception as e:
            print(f"Error adding transaction: {e}")
    
    def view_by_category(self):
        if not self.transactions:
            print("No transactions found")
            return
        
        grouped = group_by_category(self.transactions)
        totals = calculate_totals(self.transactions)
        
        print("\n=== EXPENSES BY CATEGORY ===")
        for category, transactions in grouped.items():
            print(f"\n{category.upper()}:")
            for transaction in transactions:
                print(f"  {transaction.date} - ${transaction.amount:.2f}")
            print(f"  Total: ${totals[category]:.2f}")
    
    def view_totals(self):
        if not self.transactions:
            print("No transactions found")
            return
        
        totals = calculate_totals(self.transactions)
        grand_total = calculate_grand_total(self.transactions)
        
        print("\n=== CATEGORY TOTALS ===")
        for category, total in totals.items():
            print(f"{category}: ${total:.2f}")
        
        print(f"\nGRAND TOTAL: ${grand_total:.2f}")
    
    def run(self):
        print("Personal Budget Tracker")
        print("Commands: add, category, totals, save, quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                self.save_data()
                break
            elif command == 'add':
                self.add_transaction()
            elif command == 'category':
                self.view_by_category()
            elif command == 'totals':
                self.view_totals()
            elif command == 'save':
                self.save_data()
            else:
                print("Unknown command. Use: add, category, totals, save, quit")

if __name__ == "__main__":
    tracker = BudgetTracker()
    tracker.run()