from typing import List, Dict
from datetime import datetime

class Transaction:
    def __init__(self, date: str, category: str, amount: float):
        self.date = date
        self.category = category
        self.amount = amount
    
    def to_dict(self) -> dict:
        return {
            'date': self.date,
            'category': self.category,
            'amount': self.amount
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['date'], data['category'], data['amount'])

def group_by_category(transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
    grouped = {}
    for transaction in transactions:
        if transaction.category not in grouped:
            grouped[transaction.category] = []
        grouped[transaction.category].append(transaction)
    return grouped

def calculate_totals(transactions: List[Transaction]) -> Dict[str, float]:
    totals = {}
    for transaction in transactions:
        if transaction.category not in totals:
            totals[transaction.category] = 0
        totals[transaction.category] += transaction.amount
    return totals

def calculate_grand_total(transactions: List[Transaction]) -> float:
    return sum(transaction.amount for transaction in transactions)

