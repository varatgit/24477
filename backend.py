import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """
    Manages all database operations for the expense and budget management system.
    """
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("expense tracker"),
                user=os.getenv("postgres"),
                password=os.getenv("vardhini"),
                host=os.getenv("localhost"),
                port=os.getenv("5432")
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful.")
            self.create_tables()
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")

    def create_tables(self):
        """
        Creates the necessary tables if they don't exist.
        """
        commands = (
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                payment_method VARCHAR(50) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50) NOT NULL UNIQUE,
                monthly_budget DECIMAL(10, 2) NOT NULL,
                annual_budget DECIMAL(10, 2) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS income (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                source VARCHAR(100) NOT NULL
            )
            """
        )
        try:
            for command in commands:
                self.cursor.execute(command)
            self.conn.commit()
            print("Tables created successfully.")
        except psycopg2.Error as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()

    def add_expense(self, date, amount, category, payment_method):
        """
        Adds a new expense record.
        """
        sql = "INSERT INTO expenses (date, amount, category, payment_method) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(sql, (date, amount, category, payment_method))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error adding expense: {e}")
            self.conn.rollback()
            return False

    def get_expenses(self):
        """
        Retrieves all expense records.
        """
        sql = "SELECT id, date, amount, category, payment_method FROM expenses ORDER BY date DESC"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error retrieving expenses: {e}")
            return []

    def update_expense(self, expense_id, date, amount, category, payment_method):
        """
        Updates an existing expense record.
        """
        sql = "UPDATE expenses SET date = %s, amount = %s, category = %s, payment_method = %s WHERE id = %s"
        try:
            self.cursor.execute(sql, (date, amount, category, payment_method, expense_id))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error updating expense: {e}")
            self.conn.rollback()
            return False

    def delete_expense(self, expense_id):
        """
        Deletes an expense record.
        """
        sql = "DELETE FROM expenses WHERE id = %s"
        try:
            self.cursor.execute(sql, (expense_id,))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error deleting expense: {e}")
            self.conn.rollback()
            return False

    def add_budget(self, category, monthly_budget, annual_budget):
        """
        Adds or updates a budget for a specific category.
        """
        sql = """
        INSERT INTO budgets (category, monthly_budget, annual_budget)
        VALUES (%s, %s, %s)
        ON CONFLICT (category) DO UPDATE SET
        monthly_budget = EXCLUDED.monthly_budget,
        annual_budget = EXCLUDED.annual_budget
        """
        try:
            self.cursor.execute(sql, (category, monthly_budget, annual_budget))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error setting budget: {e}")
            self.conn.rollback()
            return False

    def get_budgets(self):
        """
        Retrieves all budget records.
        """
        sql = "SELECT category, monthly_budget, annual_budget FROM budgets"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error retrieving budgets: {e}")
            return []

    def get_monthly_spending_by_category(self, month, year):
        """
        Calculates total spending for each category for a given month and year.
        """
        sql = """
        SELECT category, SUM(amount) FROM expenses
        WHERE EXTRACT(MONTH FROM date) = %s AND EXTRACT(YEAR FROM date) = %s
        GROUP BY category
        """
        try:
            self.cursor.execute(sql, (month, year))
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error getting monthly spending by category: {e}")
            return []
    
    def get_total_income(self):
        """
        Calculates the total income from the income table.
        """
        sql = "SELECT SUM(amount) FROM income"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0] or 0.0
        except psycopg2.Error as e:
            print(f"Error calculating total income: {e}")
            return 0.0

    def get_business_insights(self):
        """
        Provides business insights using aggregate functions.
        """
        insights = {}
        try:
            # Total Expenses
            self.cursor.execute("SELECT SUM(amount) FROM expenses")
            insights['total_expenses'] = self.cursor.fetchone()[0] or 0.0

            # Average Daily Expense
            self.cursor.execute("SELECT AVG(amount) FROM expenses")
            insights['avg_daily_expense'] = self.cursor.fetchone()[0] or 0.0

            # Max Expense
            self.cursor.execute("SELECT MAX(amount) FROM expenses")
            insights['max_expense'] = self.cursor.fetchone()[0] or 0.0

            # Min Expense
            self.cursor.execute("SELECT MIN(amount) FROM expenses")
            insights['min_expense'] = self.cursor.fetchone()[0] or 0.0
            
            # Number of Transactions
            self.cursor.execute("SELECT COUNT(*) FROM expenses")
            insights['total_transactions'] = self.cursor.fetchone()[0] or 0

            # Total Budgeted Amount
            self.cursor.execute("SELECT SUM(monthly_budget) FROM budgets")
            insights['total_monthly_budget'] = self.cursor.fetchone()[0] or 0.0

            # Total Income
            self.cursor.execute("SELECT SUM(amount) FROM income")
            insights['total_income'] = self.cursor.fetchone()[0] or 0.0
            
            # Category with most expenses
            self.cursor.execute("SELECT category FROM expenses GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1")
            most_spent_category = self.cursor.fetchone()
            insights['most_spent_category'] = most_spent_category[0] if most_spent_category else "N/A"

            return insights

        except psycopg2.Error as e:
            print(f"Error getting business insights: {e}")
            return {}

    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")