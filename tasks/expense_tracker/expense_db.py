# tasks/expense_tracker/expense_db.py
import os
import json
import datetime
from pathlib import Path

class ExpenseDatabase:
    def __init__(self):
        # Create a data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.expanduser('~'), '.assistant_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Path to the expense database file
        self.db_file = os.path.join(self.data_dir, 'expenses.json')
        
        # Initialize the database if it doesn't exist
        if not os.path.exists(self.db_file):
            self._initialize_db()
    
    def _initialize_db(self):
        """Initialize an empty expense database."""
        initial_data = {
            "expenses": [],
            "categories": [
                "Food", "Transportation", "Housing", "Entertainment", 
                "Utilities", "Healthcare", "Shopping", "Other"
            ]
        }
        with open(self.db_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def load_data(self):
        """Load expense data from the database file."""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._initialize_db()
            return self.load_data()
    
    def save_data(self, data):
        """Save expense data to the database file."""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_expense(self, amount, category, description=None, date=None):
        """Add a new expense to the database."""
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        expense = {
            "id": self._generate_id(),
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": date
        }
        
        data = self.load_data()
        data["expenses"].append(expense)
        self.save_data(data)
        return expense
    
    def get_expenses(self, category=None, start_date=None, end_date=None, limit=None):
        """Get expenses with optional filtering."""
        data = self.load_data()
        expenses = data["expenses"]
        
        # Apply filters
        if category:
            expenses = [e for e in expenses if e["category"] == category]
        
        if start_date:
            expenses = [e for e in expenses if e["date"] >= start_date]
        
        if end_date:
            expenses = [e for e in expenses if e["date"] <= end_date]
        
        # Sort by date (newest first)
        expenses.sort(key=lambda x: x["date"], reverse=True)
        
        # Apply limit
        if limit:
            expenses = expenses[:limit]
            
        return expenses
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID."""
        data = self.load_data()
        
        # Find and remove the expense
        for i, expense in enumerate(data["expenses"]):
            if expense["id"] == expense_id:
                del data["expenses"][i]
                self.save_data(data)
                return True
        
        return False
    
    def update_expense(self, expense_id, **kwargs):
        """Update an expense by ID with new values."""
        data = self.load_data()
        
        # Find and update the expense
        for expense in data["expenses"]:
            if expense["id"] == expense_id:
                for key, value in kwargs.items():
                    if key in expense:
                        expense[key] = value
                self.save_data(data)
                return True
        
        return False
    
    def get_categories(self):
        """Get all expense categories."""
        data = self.load_data()
        return data["categories"]
    
    def add_category(self, category):
        """Add a new expense category."""
        data = self.load_data()
        if category not in data["categories"]:
            data["categories"].append(category)
            self.save_data(data)
            return True
        return False
    
    def get_summary(self, period="month"):
        """Get a summary of expenses grouped by category for a time period."""
        data = self.load_data()
        expenses = data["expenses"]
        
        today = datetime.datetime.now()
        
        # Filter expenses based on the requested period
        if period == "day":
            start_date = today.strftime('%Y-%m-%d')
            filtered_expenses = [e for e in expenses if e["date"] == start_date]
        elif period == "week":
            # Start of the week (Monday)
            start_date = (today - datetime.timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            filtered_expenses = [e for e in expenses if e["date"] >= start_date]
        elif period == "month":
            start_date = today.strftime('%Y-%m-01')
            filtered_expenses = [e for e in expenses if e["date"] >= start_date]
        elif period == "year":
            start_date = today.strftime('%Y-01-01')
            filtered_expenses = [e for e in expenses if e["date"] >= start_date]
        else:
            filtered_expenses = expenses
        
        # Group by category
        summary = {}
        for expense in filtered_expenses:
            category = expense["category"]
            amount = expense["amount"]
            
            if category not in summary:
                summary[category] = 0
            
            summary[category] += amount
        
        # Calculate total
        total = sum(summary.values())
        
        return {
            "period": period,
            "total": total,
            "by_category": summary
        }
    
    def _generate_id(self):
        """Generate a unique ID for an expense."""
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


