from flask import Flask, render_template

app = Flask(__name__, static_folder="static")


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # Logic for adding a new transaction (e.g., saving to the database)
        transaction_name = request.form['name']
        transaction_date = request.form['date']
        transaction_category = request.form['category']
        transaction_value = request.form['value']

        # Save to database (pseudo-code)
        # db.add_transaction(name=transaction_name, date=transaction_date, ...)

        return redirect(url_for('transactions'))

    # Render the Add Transaction form
    return render_template('add_transaction.html')



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