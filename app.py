from flask import Flask, render_template, request, redirect, url_for
from models.database import BudgetDatabase
app = Flask(__name__, static_folder="static")

# Initialize database connection (update credentials as needed)
db = BudgetDatabase(host="localhost", user="root", password="PracaProjekt00#", database="budget_tracker")


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # Fetch accounts and their balances
    accounts = db.get_all_accounts()  # return all accounts with current balances
    return render_template('dashboard.html', accounts=accounts)


@app.route('/transactions')
def transactions():
    # Fetch all transactions
    transactions = db.get_all_transactions()
    return render_template('transactions.html', transactions=transactions)


@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # Extract form data
        account_id = request.form['account_id']
        category_id = request.form['category_id']
        transaction_type_id = request.form['transaction_type_id']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')

        # Add transaction to the database
        success = db.add_transaction(account_id, category_id, transaction_type_id, amount, description)

        if success:
            return redirect(url_for('transactions'))
        else:
            return "Failed to add transaction. Please try again."

    # Fetch accounts and categories for the form
    accounts = db.get_all_accounts()
    categories = db.get_all_categories()
    return render_template('add_transaction.html', accounts=accounts, categories=categories)


@app.route('/budget-planner')
def budget_planner():
    return render_template('budget-planner.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/alerts')
def alerts():
    return render_template('alerts.html')


@app.route('/logout')
def logout():
    return "You have been logged out. <a href='/'>Login again</a>"


if __name__ == '__main__':
    app.run(debug=True)
