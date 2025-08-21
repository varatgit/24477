import streamlit as st
import pandas as pd
import datetime
import calendar
from backend import DatabaseManager

# --- Initialize ---
db = DatabaseManager()

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Expense & Budget Management",
    page_icon="💸",
    layout="wide",
)

# --- Helper Functions for Displaying Sections ---

def display_dashboard():
    """Displays the main financial dashboard with key insights and charts."""
    st.header("Financial Dashboard & Business Insights 📊")
    insights = db.get_business_insights()
    
    if not insights:
        st.warning("No data available for insights. Please add some expenses.")
        return

    # Display key metrics using columns
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.metric(label="Total Expenses", value=f"${insights.get('total_expenses', 0):,.2f}")
    with col2:
        st.metric(label="Avg Daily Expense", value=f"${insights.get('avg_daily_expense', 0):,.2f}")
    with col3:
        st.metric(label="Max Expense", value=f"${insights.get('max_expense', 0):,.2f}")
    with col4:
        st.metric(label="Min Expense", value=f"${insights.get('min_expense', 0):,.2f}")
    with col5:
        st.metric(label="Total Transactions", value=insights.get('total_transactions', 0))
    with col6:
        st.metric(label="Most Spent Category", value=insights.get('most_spent_category', "N/A"))
    
    # Calculate and display savings
    total_income = insights.get('total_income', 0)
    total_expenses = insights.get('total_expenses', 0)
    savings = total_income - total_expenses
    with col7:
        st.metric(label="Total Savings", value=f"${savings:,.2f}")

    st.markdown("---")

    # Display charts
    expenses_data = db.get_expenses()
    if expenses_data:
        df = pd.DataFrame(expenses_data, columns=["ID", "Date", "Amount", "Category", "Payment Method"])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Pie Chart for category breakdown
        st.subheader("Category-wise Expense Breakdown")
        category_spending = df.groupby('Category')['Amount'].sum().reset_index()
        st.bar_chart(category_spending.set_index('Category'))
        
        # Line Chart for spending trends
        st.subheader("Spending Trends Over Time")
        monthly_spending = df.set_index('Date').resample('M')['Amount'].sum().reset_index()
        monthly_spending['Month'] = monthly_spending['Date'].dt.strftime('%Y-%m')
        st.line_chart(monthly_spending, x='Month', y='Amount')

def display_add_expense_form():
    """Displays a form to add a new expense."""
    st.subheader("Add a New Expense")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.date.today())
            category = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Cash", "Online Transfer"])
        
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            if db.add_expense(date, amount, category, payment_method):
                st.success("Expense added successfully! 🎉")
            else:
                st.error("Failed to add expense. Please try again. 😥")

def display_manage_budgets():
    """Displays budget management forms and alerts."""
    st.subheader("Set Budgets")
    with st.form("budget_form", clear_on_submit=True):
        category = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"])
        col1, col2 = st.columns(2)
        with col1:
            monthly_budget = st.number_input("Monthly Budget", min_value=0.0, format="%.2f")
        with col2:
            annual_budget = st.number_input("Annual Budget", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Set Budget")
        if submitted:
            if db.add_budget(category, monthly_budget, annual_budget):
                st.success(f"Budget for {category} set successfully! 💰")
            else:
                st.error("Failed to set budget. Please try again. 😥")

    st.markdown("---")
    st.subheader("Budget Tracking & Alerts")
    budgets = db.get_budgets()
    
    if not budgets:
        st.info("Please set budgets above to view your budget status.")
        return

    current_month = datetime.date.today().month
    current_year = datetime.date.today().year

    for budget_category, monthly_budget, annual_budget in budgets:
        spending = db.get_monthly_spending_by_category(current_month, current_year)
        current_spending = next((amount for category, amount in spending if category == budget_category), 0)
        remaining_budget = monthly_budget - current_spending
        
        st.markdown(f"**{budget_category}**")
        st.markdown(f"**Monthly Budget:** ${monthly_budget:,.2f} | **Current Spending:** ${current_spending:,.2f} | **Remaining:** ${remaining_budget:,.2f}")
        
        if remaining_budget < 0:
            st.warning(f"🚨 **Alert:** You have exceeded your {budget_category} budget by ${-remaining_budget:,.2f}!")
        elif remaining_budget < monthly_budget * 0.2:
            st.warning(f"⚠️ **Alert:** You are nearing your {budget_category} budget. Only ${remaining_budget:,.2f} remaining.")
        else:
            st.success(f"✅ You are within your {budget_category} budget.")

def display_transactions_crud():
    """Displays a list of all transactions with edit and delete options."""
    st.subheader("All Transactions")
    expenses_data = db.get_expenses()
    if not expenses_data:
        st.info("No expenses recorded yet.")
        return

    df = pd.DataFrame(expenses_data, columns=["ID", "Date", "Amount", "Category", "Payment Method"])
    
    # Display transactions
    st.dataframe(df.set_index('ID'))

    # Edit/Delete form
    st.markdown("---")
    st.subheader("Edit or Delete an Expense")
    expense_ids = df['ID'].tolist()
    
    selected_id = st.selectbox("Select Expense ID", expense_ids)
    
    if selected_id:
        selected_expense = df[df['ID'] == selected_id].iloc[0]
        with st.form("edit_delete_form"):
            new_date = st.date_input("Date", value=selected_expense['Date'])
            new_amount = st.number_input("Amount", value=float(selected_expense['Amount']), min_value=0.0, format="%.2f")
            new_category = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"], index=["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"].index(selected_expense['Category']))
            new_payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Cash", "Online Transfer"], index=["Credit Card", "Debit Card", "Cash", "Online Transfer"].index(selected_expense['Payment Method']))

            col1, col2 = st.columns(2)
            with col1:
                update_btn = st.form_submit_button("Update Expense")
            with col2:
                delete_btn = st.form_submit_button("Delete Expense")

            if update_btn:
                if db.update_expense(selected_id, new_date, new_amount, new_category, new_payment_method):
                    st.success("Expense updated successfully! 🎉")
                    st.rerun()
                else:
                    st.error("Failed to update expense. 😥")
            
            if delete_btn:
                if db.delete_expense(selected_id):
                    st.success("Expense deleted successfully! 🗑️")
                    st.rerun()
                else:
                    st.error("Failed to delete expense. 😥")

# --- Main App Logic ---

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "Manage Budgets", "All Transactions"])

    if page == "Dashboard":
        display_dashboard()
    elif page == "Add Expense":
        display_add_expense_form()
    elif page == "Manage Budgets":
        display_manage_budgets()
    elif page == "All Transactions":
        display_transactions_crud()

if __name__ == "__main__":
    main()