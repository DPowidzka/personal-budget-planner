from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from models.database import BudgetDatabase
from flask_bcrypt import Bcrypt
from models.user import User
import logging

bcrypt = Bcrypt()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'

# Initialize database connection (using the BudgetDatabase instance)
db = BudgetDatabase(host="localhost", user="root", password="mysql!", database="budget_tracker")

# Initialize the User model with the database connection
user_model = User(db)

# Home route
@app.route('/')
def home():
    return redirect(url_for('login'))


# Flask route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get data from the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user_manager = User(db)
        user_id = user_manager.add_user(username, email, password)

        if user_id:
            # If user is successfully created, show the success page with user_id
            flash(f"User created successfully! Your user ID is {user_id}.", 'success')
            return redirect(url_for('login'))
        else:
            # If user creation failed, show an error message
            flash("Signup failed. Username or email might already exist.", 'danger')
    return render_template('signup.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Render a login template for GET requests
        return render_template('login.html')

    if request.method == 'POST':
        # Handle regular form submission
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        user = user_model.authenticate_user(username, password)
        if user:
            # Store user ID in session
            session['user_id'] = user['id']
            flash("Login successful", 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash("Invalid username or password", 'danger')
            return redirect(url_for('login'))  # Reload the login page

    return render_template('login.html')


# Dashboard route (protected, requires login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    accounts = db.get_all_accounts()  # Fetch all accounts with current balances
    return render_template('dashboard.html', accounts=accounts)

# Transactions route
@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    # Fetch all transactions
    transactions = db.get_all_transactions()
    return render_template('transactions.html', transactions=transactions)

# Add transaction route
@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract form data
        account_id = request.form.get('account_id')
        category_id = request.form.get('category_id')
        transaction_type_id = request.form.get('transaction_type_id')
        amount = request.form.get('amount')
        description = request.form.get('description', '')

        if not all([account_id, category_id, transaction_type_id, amount]):
            flash("All fields are required.", 'danger')
            return redirect(url_for('add_transaction'))

        try:
            amount = float(amount)  # Convert amount to float
        except ValueError:
            flash("Invalid amount.", 'danger')
            return redirect(url_for('add_transaction'))

        # Add transaction to the database
        success = db.add_transaction(account_id, category_id, transaction_type_id, amount, description)

        if success:
            flash("Transaction added successfully.", 'success')
            return redirect(url_for('transactions'))
        else:
            flash("Failed to add transaction. Please try again.", 'danger')

    # Fetch accounts and categories for the form
    accounts = db.get_all_accounts()
    categories = db.get_all_categories()
    return render_template('add_transaction.html', accounts=accounts, categories=categories)

# Other routes
@app.route('/budget-planner')
def budget_planner():
    return render_template('budget-planner.html')

@app.route('/savings')
def savings():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect('login.html')

    savings_goals = db.get_savings_goal()

    return render_template('savings.html', savings=savings)

# Add savings route
@app.route('/add_savings', methods=['GET', 'POST'])
def add_savings():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add_savings.html')

    goal_name = request.form.get('goal_name')
    goal_amount = request.form.get('goal_amount')
    target_date = request.form.get('target_date')

    if not all([goal_name, goal_amount, target_date]):
        flash("All fields are required.", 'danger')
        return redirect(url_for('add_savings'))

    try:
        goal_amount = float(goal_amount)
    except ValueError:
        flash("Invalid goal amount.", 'danger')
        return redirect(url_for('add_savings'))

    # Insert into database
    success = db.add_savings(goal_name, goal_amount, target_date)

    if success:
        flash("Savings goal created successfully!", 'success')
        return redirect(url_for('savings'))
    else:
        flash("Failed to create savings goal. Please try again.", 'danger')

    return render_template('add_savings.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Log out by clearing the session
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
