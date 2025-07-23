import math
from typing import Dict, Any

class Book:
    
    def __init__(self, title: str, author: str, price: float, stock: int = 0):
        self.title = title.strip()
        self.author = author.strip()
        self.price = math.ceil(price * 100) / 100 
        self.stock = max(0, stock)  
    
    def update_stock(self, quantity: int) -> bool:
        new_stock = self.stock + quantity
        if new_stock < 0:
            return False
        self.stock = new_stock
        return True
    
    def update_price(self, new_price: float):
        self.price = math.ceil(new_price * 100) / 100
    
    def calculate_value(self) -> float:
        return math.ceil(self.price * self.stock * 100) / 100
    
    def is_in_stock(self) -> bool:
        return self.stock > 0
    
    def is_low_stock(self, threshold: int = 5) -> bool:
        return 0 < self.stock <= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'author': self.author,
            'price': self.price,
            'stock': self.stock,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        return cls(
            title=data['title'],
            author=data['author'],
            price=data['price'],
            stock=data['stock'],
        )
    
    def __str__(self) -> str:
        stock_status = "In Stock" if self.is_in_stock() else "Out of Stock"
        return f"'{self.title}' by {self.author} - ${self.price:.2f} ({self.stock} units - {stock_status})"
    
    def __repr__(self) -> str:
        return f"Book(title='{self.title}', author='{self.author}', price={self.price}, stock={self.stock})"


