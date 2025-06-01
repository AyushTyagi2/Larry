# tasks/expense_tracker/expense_manager.py
from .expense_db import ExpenseDatabase
import datetime
import calendar
from tabulate import tabulate

class ExpenseManager:
    def __init__(self):
        self.db = ExpenseDatabase()
    
    def add_expense(self, amount, category=None, description=None, date=None):
        """Add a new expense."""
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Amount must be greater than zero."
        except ValueError:
            return False, "Invalid amount. Please enter a number."
        
        # Get categories if not provided or validate the provided category
        categories = self.db.get_categories()
        
        if category is None:
            # Show categories and let user choose
            print("Available categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            try:
                choice = int(input("Select category (number) or enter 0 to create new: "))
                if choice == 0:
                    category = input("Enter new category name: ")
                    self.db.add_category(category)
                else:
                    category = categories[choice - 1]
            except (ValueError, IndexError):
                return False, "Invalid category selection."
        else:
            # Validate the provided category
            if category not in categories:
                create_new = input(f"Category '{category}' doesn't exist. Create it? (y/n): ")
                if create_new.lower() == 'y':
                    self.db.add_category(category)
                else:
                    return False, "Invalid category."
        
        # Validate date if provided
        if date:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD."
        
        # Add the expense
        expense = self.db.add_expense(amount, category, description, date)
        
        return True, f"Expense of ${amount:.2f} added to '{category}'."
    
    def list_expenses(self, category=None, start_date=None, end_date=None, limit=10):
        """List expenses with optional filtering."""
        expenses = self.db.get_expenses(category, start_date, end_date, limit)
        
        if not expenses:
            print("No expenses found matching your criteria.")
            return
        
        # Format for tabulate
        headers = ["ID", "Date", "Category", "Amount", "Description"]
        rows = []
        
        for expense in expenses:
            rows.append([
                expense["id"],
                expense["date"],
                expense["category"],
                f"${expense['amount']:.2f}",
                expense["description"] or "-"
            ])
        
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        
        # Display total
        total = sum(expense["amount"] for expense in expenses)
        print(f"\nTotal: ${total:.2f}")
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID."""
        success = self.db.delete_expense(expense_id)
        
        if success:
            return True, f"Expense {expense_id} deleted successfully."
        else:
            return False, f"Expense {expense_id} not found."
    
    def update_expense(self, expense_id, amount=None, category=None, description=None, date=None):
        """Update an expense by ID."""
        # Prepare update data
        update_data = {}
        
        if amount is not None:
            try:
                update_data["amount"] = float(amount)
                if update_data["amount"] <= 0:
                    return False, "Amount must be greater than zero."
            except ValueError:
                return False, "Invalid amount. Please enter a number."
        
        if category is not None:
            categories = self.db.get_categories()
            if category not in categories:
                create_new = input(f"Category '{category}' doesn't exist. Create it? (y/n): ")
                if create_new.lower() == 'y':
                    self.db.add_category(category)
                else:
                    return False, "Invalid category."
            update_data["category"] = category
        
        if description is not None:
            update_data["description"] = description
        
        if date is not None:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
                update_data["date"] = date
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD."
        
        # Update the expense
        success = self.db.update_expense(expense_id, **update_data)
        
        if success:
            return True, f"Expense {expense_id} updated successfully."
        else:
            return False, f"Expense {expense_id} not found."
    
    def show_summary(self, period="month"):
        """Show expense summary for a given period."""
        summary = self.db.get_summary(period)
        
        # Period name for display
        period_names = {
            "day": "Today",
            "week": "This Week",
            "month": "This Month",
            "year": "This Year",
            "all": "All Time"
        }
        
        period_name = period_names.get(period, period.capitalize())
        
        print(f"\n=== Expense Summary: {period_name} ===")
        
        if not summary["by_category"]:
            print("No expenses recorded for this period.")
            return
        
        # Format for tabulate
        headers = ["Category", "Amount", "% of Total"]
        rows = []
        
        for category, amount in sorted(summary["by_category"].items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / summary["total"]) * 100 if summary["total"] > 0 else 0
            rows.append([
                category,
                f"${amount:.2f}",
                f"{percentage:.1f}%"
            ])
        
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print(f"\nTotal Expenses: ${summary['total']:.2f}")
    
    def get_monthly_report(self, year=None, month=None):
        """Generate a report for a specific month."""
        # Default to current year and month
        if year is None or month is None:
            today = datetime.datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month
        
        # Validate inputs
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                return False, "Month must be between 1 and 12."
        except ValueError:
            return False, "Invalid year or month."
        
        # Get month name and days in month
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Start and end dates for the month
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{days_in_month}"
        
        # Get expenses for the month
        expenses = self.db.get_expenses(start_date=start_date, end_date=end_date)
        
        if not expenses:
            return False, f"No expenses found for {month_name} {year}."
        
        # Group by category
        categories = {}
        daily_totals = {day: 0 for day in range(1, days_in_month + 1)}
        
        for expense in expenses:
            # Update category totals
            category = expense["category"]
            amount = expense["amount"]
            
            if category not in categories:
                categories[category] = 0
            
            categories[category] += amount
            
            # Update daily totals
            day = int(expense["date"].split('-')[2])
            daily_totals[day] += amount
        
        # Calculate total
        total = sum(categories.values())
        
        # Print report
        print(f"\n=== Expense Report: {month_name} {year} ===")
        
        # Category breakdown
        headers = ["Category", "Amount", "% of Total"]
        rows = []
        
        for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            rows.append([
                category,
                f"${amount:.2f}",
                f"{percentage:.1f}%"
            ])
        
        print("\nCategory Breakdown:")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        
        # Daily spending graph (simple ASCII)
        print("\nDaily Spending Pattern:")
        
        # Find maximum daily total for scaling
        max_total = max(daily_totals.values())
        scale_factor = 40 / max_total if max_total > 0 else 0
        
        for day, daily_total in daily_totals.items():
            bar_length = int(daily_total * scale_factor)
            bar = '█' * bar_length
            print(f"{day:2d}: {bar} ${daily_total:.2f}")
        
        print(f"\nTotal Expenses: ${total:.2f}")
        print(f"Average Daily Expense: ${total / days_in_month:.2f}")
        
        return True, "Report generated successfully."
        
    def export_data(self, format="csv", start_date=None, end_date=None):
        """Export expense data to CSV or JSON."""
        expenses = self.db.get_expenses(start_date=start_date, end_date=end_date)
        
        if not expenses:
            return False, "No expenses found to export."
        
        # Determine time period for filename
        if start_date and end_date:
            period = f"{start_date}_to_{end_date}"
        elif start_date:
            period = f"from_{start_date}"
        elif end_date:
            period = f"until_{end_date}"
        else:
            period = "all"
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"expenses_{period}_{timestamp}"
        
        try:
            if format.lower() == "csv":
                import csv
                
                filename = f"{filename}.csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Date", "Category", "Amount", "Description"])
                    
                    for expense in expenses:
                        writer.writerow([
                            expense["id"],
                            expense["date"],
                            expense["category"],
                            expense["amount"],
                            expense["description"] or ""
                        ])
            elif format.lower() == "json":
                import json
                
                filename = f"{filename}.json"
                with open(filename, 'w') as f:
                    json.dump(expenses, f, indent=2)
            else:
                return False, f"Unsupported format: {format}"
                
            return True, f"Data exported to {filename}"
            
        except Exception as e:
            return False, f"Export failed: {str(e)}"