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
            flash(f"User created successfully!", 'success')
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


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch user's name
    db.cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user = db.cursor.fetchone()
    user_name = user['username'] if user else "User"

    # Fetch savings goals
    savings_goals = db.get_savings_goal(user_id)

    # Ensure `progress` is always defined
    for goal in savings_goals:
        if goal['goal_amount'] > 0:
            goal['progress'] = (goal['saved_amount'] / goal['goal_amount']) * 100
        else:
            goal['progress'] = 0  # Default to 0% if no valid goal amount

    # Fetch last 5 transactions
    recent_transactions = db.get_recent_transactions(user_id, limit=10)

    return render_template('dashboard.html', user_name=user_name, savings_goals=savings_goals, recent_transactions=recent_transactions)





# Transactions route
@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Search criteria
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Fetch transactions based on criteria
    transactions = db.search_transactions(
    start_date=start_date if start_date else None,
    end_date=end_date if end_date else None,
    category_id=category if category else None,
    search_query=search_query if search_query else None
    )


    return render_template('transactions.html', transactions=transactions, search=search_query, category=category)


# Add transaction route
@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        account_id = request.form.get('account_id')
        category_id = request.form.get('category_id')
        transaction_type_id = request.form.get('transaction_type_id')
        amount = request.form.get('amount')
        description = request.form.get('description', '')

        if not all([account_id, category_id, transaction_type_id, amount]):
            flash("All fields are required.", 'danger')
            return redirect(url_for('add_transaction'))

        try:
            amount = float(amount)
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



@app.route('/add-expense', methods=['GET','POST'])
def add_expense():
    """
    Trasa obsługująca dodawanie wydatków do bazy danych.
    """

    category = request.form.get('category')
    amount = request.form.get('amount')


    if not category or not amount:
        flash("All fields are required.", "danger")
        return redirect(url_for('budget-planner'))

    try:

        amount = float(amount)
        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for('budget_planner'))
    except ValueError:
        flash("Invalid amount.", "danger")
        return redirect(url_for('budget_planner'))


    try:
        success = db.add_expense(category=category, amount=amount)
    except Exception as e:
        app.logger.error(f"Error adding expense: {e}")
        flash("Failed to add expense. Please try again.", "danger")
        return redirect(url_for('budget_planner'))


    if success:
        flash("Expense added successfully.", "success")
    else:
        flash("Failed to add expense. Please try again.", "danger")


    return redirect(url_for('budget_planner'))


    # Other routes
@app.route('/budget-planner')
def budget_planner():
    return render_template('budget-planner.html')

@app.route('/savings')
def savings():
    if 'user_id' not in session:
        flash("You must log in to access this page.", 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    savings_goals = db.get_savings_goal(user_id)  # Get the latest data from DB

    return render_template('savings.html', savings_goals=savings_goals)



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

    user_id = session['user_id']

    success = db.add_savings(goal_name, goal_amount, target_date, user_id)

    if success:
        flash("Savings goal created successfully!", 'success')
        return redirect(url_for('savings'))
    else:
        flash("Failed to create savings goal. Please try again.", 'danger')

    return render_template('add_savings.html')

@app.route('/add_contribution/<int:id>', methods=['POST'])
def add_contribution(id):
    if 'user_id' not in session:
        flash("You must log in to add a contribution.", 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    amount = request.form['amount']

    goal = db.get_savings_goal_by_id(id, user_id)

    if goal:
        new_saved_amount = float(goal['saved_amount']) + float(amount)
        db.update_saved_amount(id, new_saved_amount)

        flash("Contribution added successfully!", 'success')
    else:
        flash("Goal not found.", 'danger')

    return redirect(url_for('savings'))

# Route to edit savings goal
@app.route('/edit_savings/<int:id>', methods=['GET'])
def edit_savings(id):
    if 'user_id' not in session:
        flash("You must log in to edit a savings goal.", 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    goal = db.get_savings_goal_by_id(id, user_id)

    if goal:
        return render_template('edit_savings.html', goal=goal)
    else:
        flash("Savings goal not found.", 'danger')
        return redirect(url_for('savings'))

# Route to update savings goal
@app.route('/update_savings_goal/<int:id>', methods=['POST'])
def update_savings_goal(id):
    if 'user_id' not in session:
        flash("You must log in to update a savings goal.", 'warning')
        return redirect(url_for('login'))

    goal_name = request.form['goal_name']
    goal_amount = request.form['goal_amount']
    target_date = request.form['target_date']

    try:
        goal_amount = float(goal_amount)
    except ValueError:
        flash("Invalid goal amount.", 'danger')
        return redirect(url_for('edit_savings', id=id))

    # Update the goal in the database
    success = db.update_savings_goal(id, goal_name, goal_amount, target_date)

    if success:
        flash("Savings goal updated successfully!", 'success')
        return redirect(url_for('savings'))
    else:
        flash("Failed to update savings goal. Please try again.", 'danger')
        return redirect(url_for('edit_savings', id=id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear session to log out the user
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
