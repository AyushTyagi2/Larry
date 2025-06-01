import sqlite3
import datetime
import os
import json
import matplotlib.pyplot as plt
from pathlib import Path

class CalorieTracker:
    def __init__(self, db_path="data/calorie_tracker.db"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_db()
        
        # Load food database
        self.food_db = self._load_food_database()
    
    def _initialize_db(self):
        """Initialize the database tables if they don't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS calorie_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            food_name TEXT,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fat REAL,
            meal_type TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            weight REAL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS calorie_goals (
            id INTEGER PRIMARY KEY,
            daily_calorie_goal INTEGER,
            protein_goal REAL,
            carbs_goal REAL,
            fat_goal REAL
        )
        ''')
        
        # Insert default goals if they don't exist
        self.cursor.execute('SELECT COUNT(*) FROM calorie_goals')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
            INSERT INTO calorie_goals (id, daily_calorie_goal, protein_goal, carbs_goal, fat_goal)
            VALUES (1, 2000, 150, 200, 65)
            ''')
        
        self.conn.commit()
    
    def _load_food_database(self):
        """Load the food database from a JSON file."""
        default_food_db = {
            "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
            "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4},
            "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "egg": {"calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3},
            "white rice": {"calories": 205, "protein": 4.3, "carbs": 44.5, "fat": 0.4},
            "broccoli": {"calories": 55, "protein": 3.7, "carbs": 11.2, "fat": 0.6},
            "salmon": {"calories": 206, "protein": 22.1, "carbs": 0, "fat": 13.4},
            "bread": {"calories": 265, "protein": 9.1, "carbs": 49, "fat": 3.2},
            "milk": {"calories": 103, "protein": 8.1, "carbs": 12.2, "fat": 2.4},
            "potato": {"calories": 161, "protein": 4.3, "carbs": 37, "fat": 0.2},
            "pasta": {"calories": 221, "protein": 8.1, "carbs": 43.2, "fat": 1.3},
            "oatmeal": {"calories": 166, "protein": 5.9, "carbs": 28.4, "fat": 3.6}
        }
        
        food_db_path = Path("data/food_database.json")
        
        # Create directory if it doesn't exist
        if not food_db_path.parent.exists():
            food_db_path.parent.mkdir(parents=True)
        
        # Create with default values if doesn't exist
        if not food_db_path.exists():
            with open(food_db_path, 'w') as f:
                json.dump(default_food_db, f, indent=4)
            return default_food_db
        
        # Load existing database
        try:
            with open(food_db_path, 'r') as f:
                return json.load(f)
        except:
            return default_food_db
    
    def save_food_database(self):
        """Save the food database to a JSON file."""
        with open("data/food_database.json", 'w') as f:
            json.dump(self.food_db, f, indent=4)
    
    def add_food_to_database(self, food_name, calories, protein, carbs, fat):
        """Add a new food item to the database."""
        food_name = food_name.lower()
        
        self.food_db[food_name] = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
        
        self.save_food_database()
        return True, f"Added {food_name} to food database."
    
    def search_food(self, query):
        """Search for food in the database."""
        query = query.lower()
        results = {}
        
        for food, data in self.food_db.items():
            if query in food:
                results[food] = data
        
        return results
    
    def log_meal(self, food_name, quantity=1, meal_type="Other", date=None):
        """Log a meal to the database."""
        food_name = food_name.lower()
        
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if food exists in database
        if food_name in self.food_db:
            food_data = self.food_db[food_name]
            calories = food_data["calories"] * quantity
            protein = food_data["protein"] * quantity
            carbs = food_data["carbs"] * quantity
            fat = food_data["fat"] * quantity
            
            self.cursor.execute('''
            INSERT INTO calorie_intake (date, food_name, calories, protein, carbs, fat, meal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, food_name, calories, protein, carbs, fat, meal_type))
            
            self.conn.commit()
            return True, f"Logged {quantity} {food_name} ({calories} calories) as {meal_type}."
        else:
            # Get user input for custom food
            try:
                print(f"'{food_name}' not found in database. Please enter nutritional information:")
                calories = float(input("Calories per serving: "))
                protein = float(input("Protein (g) per serving: "))
                carbs = float(input("Carbs (g) per serving: "))
                fat = float(input("Fat (g) per serving: "))
                
                # Save to database if user wishes
                save_to_db = input("Save this food to database for future use? (y/n): ").lower() == 'y'
                if save_to_db:
                    self.add_food_to_database(food_name, calories, protein, carbs, fat)
                
                # Calculate for quantity
                calories *= quantity
                protein *= quantity
                carbs *= quantity
                fat *= quantity
                
                self.cursor.execute('''
                INSERT INTO calorie_intake (date, food_name, calories, protein, carbs, fat, meal_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date, food_name, calories, protein, carbs, fat, meal_type))
                
                self.conn.commit()
                return True, f"Logged {quantity} {food_name} ({calories} calories) as {meal_type}."
            except ValueError:
                return False, "Invalid nutritional information. Please enter numeric values."
    
    def log_weight(self, weight, date=None):
        """Log user weight."""
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO weight_tracking (date, weight)
            VALUES (?, ?)
            ''', (date, weight))
            
            self.conn.commit()
            return True, f"Logged weight: {weight} kg on {date}"
        except Exception as e:
            return False, f"Error logging weight: {e}"
    
    def get_today_summary(self):
        """Get a summary of today's calorie intake."""
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return self.get_day_summary(date)
    
    def get_day_summary(self, date):
        """Get a summary of calorie intake for a specific day."""
        self.cursor.execute('''
        SELECT SUM(calories) as total_calories, 
               SUM(protein) as total_protein,
               SUM(carbs) as total_carbs,
               SUM(fat) as total_fat
        FROM calorie_intake
        WHERE date = ?
        ''', (date,))
        
        result = self.cursor.fetchone()
        
        if result[0] is None:
            return {
                "date": date,
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0,
                "meals": []
            }
        
        # Get individual meals
        self.cursor.execute('''
        SELECT food_name, calories, protein, carbs, fat, meal_type
        FROM calorie_intake
        WHERE date = ?
        ORDER BY meal_type
        ''', (date,))
        
        meals = []
        for row in self.cursor.fetchall():
            meals.append({
                "food": row[0],
                "calories": row[1],
                "protein": row[2],
                "carbs": row[3],
                "fat": row[4],
                "meal_type": row[5]
            })
        
        # Get calorie goals
        self.cursor.execute('SELECT daily_calorie_goal, protein_goal, carbs_goal, fat_goal FROM calorie_goals WHERE id = 1')
        goals = self.cursor.fetchone()
        
        return {
            "date": date,
            "total_calories": result[0],
            "total_protein": result[1],
            "total_carbs": result[2],
            "total_fat": result[3],
            "calorie_goal": goals[0],
            "protein_goal": goals[1],
            "carbs_goal": goals[2],
            "fat_goal": goals[3],
            "remaining_calories": goals[0] - result[0],
            "meals": meals
        }
    
    def get_weight_history(self, days=30):
        """Get weight history for the past number of days."""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        self.cursor.execute('''
        SELECT date, weight FROM weight_tracking
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        ''', (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        return self.cursor.fetchall()
    
    def update_goals(self, calories=None, protein=None, carbs=None, fat=None):
        """Update nutrition goals."""
        # Get current values first
        self.cursor.execute('SELECT daily_calorie_goal, protein_goal, carbs_goal, fat_goal FROM calorie_goals WHERE id = 1')
        current = self.cursor.fetchone()
        
        # Replace None with current values
        calories = calories if calories is not None else current[0]
        protein = protein if protein is not None else current[1]
        carbs = carbs if carbs is not None else current[2]
        fat = fat if fat is not None else current[3]
        
        self.cursor.execute('''
        UPDATE calorie_goals
        SET daily_calorie_goal = ?, protein_goal = ?, carbs_goal = ?, fat_goal = ?
        WHERE id = 1
        ''', (calories, protein, carbs, fat))
        
        self.conn.commit()
        return True, f"Updated goals: {calories} calories, {protein}g protein, {carbs}g carbs, {fat}g fat"
    
    def generate_report(self, days=7):
        """Generate a nutrition report for the past days."""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days-1)  # inclusive of today
        
        dates = []
        calories = []
        proteins = []
        carbs = []
        fats = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            summary = self.get_day_summary(date_str)
            
            dates.append(date_str)
            calories.append(summary["total_calories"])
            proteins.append(summary["total_protein"])
            carbs.append(summary["total_carbs"])
            fats.append(summary["total_fat"])
            
            current_date += datetime.timedelta(days=1)
        
        # Get goals for reference lines
        self.cursor.execute('SELECT daily_calorie_goal, protein_goal, carbs_goal, fat_goal FROM calorie_goals WHERE id = 1')
        goals = self.cursor.fetchone()
        
        # Create a report directory if it doesn't exist
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate calorie chart
        plt.figure(figsize=(10, 6))
        plt.plot(dates, calories, marker='o', linestyle='-', color='blue')
        plt.axhline(y=goals[0], color='r', linestyle='--', alpha=0.7)
        plt.title('Daily Calories')
        plt.xlabel('Date')
        plt.ylabel('Calories')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        calorie_chart_path = f"{report_dir}/calorie_report.png"
        plt.savefig(calorie_chart_path)
        plt.close()
        
        # Generate macros chart
        plt.figure(figsize=(10, 6))
        plt.plot(dates, proteins, marker='o', linestyle='-', label='Protein')
        plt.plot(dates, carbs, marker='s', linestyle='-', label='Carbs')
        plt.plot(dates, fats, marker='^', linestyle='-', label='Fat')
        plt.axhline(y=goals[1], color='r', linestyle='--', alpha=0.5, label='Protein Goal')
        plt.axhline(y=goals[2], color='g', linestyle='--', alpha=0.5, label='Carbs Goal')
        plt.axhline(y=goals[3], color='b', linestyle='--', alpha=0.5, label='Fat Goal')
        plt.title('Daily Macronutrients')
        plt.xlabel('Date')
        plt.ylabel('Grams')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        macros_chart_path = f"{report_dir}/macros_report.png"
        plt.savefig(macros_chart_path)
        plt.close()
        
        report_text = f"Nutrition Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})\n\n"
        report_text += f"Daily Goals: {goals[0]} calories, {goals[1]}g protein, {goals[2]}g carbs, {goals[3]}g fat\n\n"
        
        # Calculate averages
        avg_calories = sum(calories) / len(calories)
        avg_protein = sum(proteins) / len(proteins)
        avg_carbs = sum(carbs) / len(carbs)
        avg_fat = sum(fats) / len(fats)
        
        report_text += f"Average Daily Intake:\n"
        report_text += f"  Calories: {avg_calories:.1f} ({(avg_calories/goals[0])*100:.1f}% of goal)\n"
        report_text += f"  Protein: {avg_protein:.1f}g ({(avg_protein/goals[1])*100:.1f}% of goal)\n"
        report_text += f"  Carbs: {avg_carbs:.1f}g ({(avg_carbs/goals[2])*100:.1f}% of goal)\n"
        report_text += f"  Fat: {avg_fat:.1f}g ({(avg_fat/goals[3])*100:.1f}% of goal)\n\n"
        
        report_text += "Daily Breakdown:\n"
        for i in range(len(dates)):
            report_text += f"  {dates[i]}: {calories[i]} calories, {proteins[i]:.1f}g protein, {carbs[i]:.1f}g carbs, {fats[i]:.1f}g fat\n"
        
        report_path = f"{report_dir}/nutrition_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        return True, f"Report generated. Charts saved to {calorie_chart_path} and {macros_chart_path}. Text report saved to {report_path}."
    
    def delete_meal(self, meal_id):
        """Delete a meal entry."""
        try:
            self.cursor.execute('DELETE FROM calorie_intake WHERE id = ?', (meal_id,))
            self.conn.commit()
            return True, f"Deleted meal with ID {meal_id}."
        except Exception as e:
            return False, f"Error deleting meal: {e}"
    
    def get_meals_for_day(self, date=None):
        """Get all meals for a specific day with their IDs."""
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.cursor.execute('''
        SELECT id, food_name, calories, protein, carbs, fat, meal_type
        FROM calorie_intake
        WHERE date = ?
        ORDER BY meal_type
        ''', (date,))
        
        meals = []
        for row in self.cursor.fetchall():
            meals.append({
                "id": row[0],
                "food": row[1],
                "calories": row[2],
                "protein": row[3],
                "carbs": row[4],
                "fat": row[5],
                "meal_type": row[6]
            })
        
        return meals
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

def main():
    """Main function to run the calorie tracker independently."""
    tracker = CalorieTracker()
    
    while True:
        print("\n===== Calorie Tracker =====")
        print("1. Log a meal")
        print("2. Log weight")
        print("3. Get today's summary")
        print("4. Get summary for specific day")
        print("5. Generate nutrition report")
        print("6. Update nutrition goals")
        print("7. View weight history")
        print("8. Add food to database")
        print("9. Search food database")
        print("10. Delete meal")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            food = input("Enter food name: ").strip()
            try:
                quantity = float(input("Enter quantity (default: 1): ") or "1")
            except ValueError:
                quantity = 1
            
            print("Meal types: Breakfast, Lunch, Dinner, Snack, Other")
            meal_type = input("Enter meal type (default: Other): ").strip() or "Other"
            
            success, message = tracker.log_meal(food, quantity, meal_type)
            print(message)
        
        elif choice == "2":
            try:
                weight = float(input("Enter your weight (kg): "))
                success, message = tracker.log_weight(weight)
                print(message)
            except ValueError:
                print("Please enter a valid weight.")
        
        elif choice == "3":
            summary = tracker.get_today_summary()
            
            print(f"\nSummary for {summary['date']}:")
            print(f"Total Calories: {summary['total_calories']} / {summary['calorie_goal']} ({summary['remaining_calories']} remaining)")
            print(f"Protein: {summary['total_protein']:.1f}g / {summary['protein_goal']}g")
            print(f"Carbs: {summary['total_carbs']:.1f}g / {summary['carbs_goal']}g")
            print(f"Fat: {summary['total_fat']:.1f}g / {summary['fat_goal']}g")
            
            if summary['meals']:
                print("\nMeals:")
                for meal in summary['meals']:
                    print(f"- {meal['meal_type']}: {meal['food']} ({meal['calories']} cal, {meal['protein']:.1f}g protein)")
        
        elif choice == "4":
            date = input("Enter date (YYYY-MM-DD): ")
            try:
                # Validate date format
                datetime.datetime.strptime(date, "%Y-%m-%d")
                summary = tracker.get_day_summary(date)
                
                print(f"\nSummary for {summary['date']}:")
                print(f"Total Calories: {summary['total_calories']} / {summary['calorie_goal']} ({summary['remaining_calories']} remaining)")
                print(f"Protein: {summary['total_protein']:.1f}g / {summary['protein_goal']}g")
                print(f"Carbs: {summary['total_carbs']:.1f}g / {summary['carbs_goal']}g")
                print(f"Fat: {summary['total_fat']:.1f}g / {summary['fat_goal']}g")
                
                if summary['meals']:
                    print("\nMeals:")
                    for meal in summary['meals']:
                        print(f"- {meal['meal_type']}: {meal['food']} ({meal['calories']} cal, {meal['protein']:.1f}g protein)")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        
        elif choice == "5":
            try:
                days = int(input("Number of days for report (default: 7): ") or "7")
                success, message = tracker.generate_report(days)
                print(message)
            except ValueError:
                print("Please enter a valid number of days.")
        
        elif choice == "6":
            print("Enter new nutrition goals (leave blank to keep current values):")
            try:
                calories_input = input("Daily calorie goal: ")
                calories = int(calories_input) if calories_input.strip() else None
                
                protein_input = input("Daily protein goal (g): ")
                protein = float(protein_input) if protein_input.strip() else None
                
                carbs_input = input("Daily carbs goal (g): ")
                carbs = float(carbs_input) if carbs_input.strip() else None
                
                fat_input = input("Daily fat goal (g): ")
                fat = float(fat_input) if fat_input.strip() else None
                
                success, message = tracker.update_goals(calories, protein, carbs, fat)
                print(message)
            except ValueError:
                print("Please enter valid numeric values.")
        
        elif choice == "7":
            try:
                days = int(input("Show weight history for how many days? (default: 30): ") or "30")
                weight_history = tracker.get_weight_history(days)
                
                if not weight_history:
                    print("No weight entries found for this period.")
                else:
                    print("\nWeight History:")
                    for date, weight in weight_history:
                        print(f"{date}: {weight} kg")
            except ValueError:
                print("Please enter a valid number of days.")
        
        elif choice == "8":
            food_name = input("Enter food name: ").strip().lower()
            
            try:
                calories = float(input("Calories per serving: "))
                protein = float(input("Protein (g) per serving: "))
                carbs = float(input("Carbs (g) per serving: "))
                fat = float(input("Fat (g) per serving: "))
                
                success, message = tracker.add_food_to_database(food_name, calories, protein, carbs, fat)
                print(message)
            except ValueError:
                print("Please enter valid nutritional values.")
        
        elif choice == "9":
            query = input("Enter food name to search: ").strip()
            results = tracker.search_food(query)
            
            if not results:
                print(f"No foods found matching '{query}'")
            else:
                print(f"\nFound {len(results)} matching foods:")
                for food, data in results.items():
                    print(f"- {food}: {data['calories']} cal, P: {data['protein']}g, C: {data['carbs']}g, F: {data['fat']}g")
        
        elif choice == "10":
            date_input = input("Date for meal deletion (YYYY-MM-DD, or leave blank for today): ").strip()
            date = date_input if date_input else datetime.datetime.now().strftime("%Y-%m-%d")
            
            try:
                # Validate date format
                datetime.datetime.strptime(date, "%Y-%m-%d")
                
                meals = tracker.get_meals_for_day(date)
                
                if not meals:
                    print(f"No meals found for {date}")
                else:
                    print(f"\nMeals for {date}:")
                    for meal in meals:
                        print(f"ID {meal['id']}: {meal['meal_type']} - {meal['food']} ({meal['calories']} cal)")
                    
                    try:
                        meal_id = int(input("\nEnter ID of meal to delete: "))
                        confirm = input(f"Are you sure you want to delete meal ID {meal_id}? (yes/no): ")
                        
                        if confirm.lower() == "yes":
                            success, message = tracker.delete_meal(meal_id)
                            print(message)
                    except ValueError:
                        print("Please enter a valid meal ID.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        
        elif choice == "0":
            tracker.close()
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()