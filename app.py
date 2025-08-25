"""
Flask backend for the Pretium Investment portal.

This application exposes a small set of endpoints to support a simple
front‑end portal.  Users can log in, view a list of accounts (pulled
from the provided chart of accounts spreadsheet) and view a dashboard
with a few aggregate metrics.  In a production system these views
would be secured, connect to a real database and perform full
accounting calculations.  For demonstration purposes the data is
loaded from the `cchart_of_accounts.xlsx` file and no persistent
storage is used.

To run the app:
    pip install flask pandas openpyxl
    python app.py

Access the portal at http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "pretium_secret_key")

# Load chart of accounts once on startup.  The file must be in the
# current working directory.  It is assumed to have at least the
# columns: code, name, type and description.
try:
    chart_path = os.path.join(os.path.dirname(__file__), "cchart_of_accounts.xlsx")
    chart_df = pd.read_excel(chart_path)
except Exception as e:
    # If the file cannot be loaded we fall back to an empty DataFrame.
    print(f"Warning: could not read cchart_of_accounts.xlsx: {e}")
    chart_df = pd.DataFrame(columns=["code", "name", "type", "description"])

# In‑memory user store.  In a real application use a database and
# password hashing.  The default admin user is provided for
# demonstration.
USERS = {
    "Admin": "PretiumAdmin007",
}

# Additional in-memory storage for customers, vendors, invoices, bills,
# bank transactions and journal entries.  In a production system these
# would be persisted in a database.
CUSTOMERS = []
VENDORS = []
INVOICES = []
BILLS = []
BANK_TRANSACTIONS = []
JOURNAL_ENTRIES = []

def _generate_id(data_list):
    """Generate a simple incremental ID based on the length of a list."""
    return len(data_list) + 1

def _get_current_user():
    """Return the current user record if logged in."""
    username = session.get('username')
    if not username:
        return None
    return {'username': username, 'role': 'admin' if username == 'Admin' else 'client'}

def create_journal_entry(debit_account, credit_account, amount, description, user):
    """Create a simple journal entry.  Debit and credit are account codes."""
    JOURNAL_ENTRIES.append({
        'id': _generate_id(JOURNAL_ENTRIES),
        'date': pd.Timestamp.today(),
        'debit_account': debit_account,
        'credit_account': credit_account,
        'amount': amount,
        'description': description,
        'user': user
    })

def compute_income_statement():
    """Compute a simple income statement from journal entries.
    Returns revenue, expenses and net income."""
    revenue_total = 0
    expense_total = 0
    for entry in JOURNAL_ENTRIES:
        # Simplistic logic: if credit account is revenue, add to revenue_total.
        # if debit account is expense, add to expense_total.
        credit_ac = entry['credit_account']
        debit_ac = entry['debit_account']
        # Find account types from chart
        credit_row = chart_df[chart_df['code'] == credit_ac]
        debit_row = chart_df[chart_df['code'] == debit_ac]
        if not credit_row.empty and credit_row.iloc[0]['type'] == 'Revenue':
            revenue_total += entry['amount']
        if not debit_row.empty and debit_row.iloc[0]['type'] == 'Expense':
            expense_total += entry['amount']
    net_income = revenue_total - expense_total
    return {
        'revenue': revenue_total,
        'expenses': expense_total,
        'net_income': net_income
    }

def compute_balance_sheet():
    """Compute a simple balance sheet from journal entries.
    Returns assets, liabilities and equity balances."""
    # Build a dict of account balances
    balances = {}
    for acc_code in chart_df['code']:
        balances[acc_code] = 0.0
    for entry in JOURNAL_ENTRIES:
        balances[entry['debit_account']] += entry['amount']
        balances[entry['credit_account']] -= entry['amount']
    assets = 0
    liabilities = 0
    equity = 0
    for acc_code, balance in balances.items():
        row = chart_df[chart_df['code'] == acc_code]
        if row.empty:
            continue
        acc_type = row.iloc[0]['type']
        if acc_type == 'Asset':
            assets += balance
        elif acc_type == 'Liability':
            liabilities += balance
        elif acc_type == 'Equity':
            equity += balance
    return {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity
    }

def compute_cash_flow():
    """Compute a very simple cash flow statement based on cash account."""
    # Identify cash account code(s)
    cash_accounts = chart_df[chart_df['name'].str.contains('Cash', case=False)]['code'].tolist()
    cash_inflow = 0
    cash_outflow = 0
    for entry in JOURNAL_ENTRIES:
        if entry['debit_account'] in cash_accounts:
            cash_inflow += entry['amount']
        if entry['credit_account'] in cash_accounts:
            cash_outflow += entry['amount']
    net_cash = cash_inflow - cash_outflow
    return {
        'cash_inflow': cash_inflow,
        'cash_outflow': cash_outflow,
        'net_cash': net_cash
    }

def is_authenticated() -> bool:
    """Helper to check whether the current session has an authenticated user."""
    return 'username' in session

@app.route("/")
def home():
    """Landing page redirects to dashboard if logged in or login page otherwise."""
    if is_authenticated():
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login():
    """Authenticate the user via JSON or form data.  Returns JSON."""
    data = request.get_json() or request.form
    username = data.get("username")
    password = data.get("password")
    if username in USERS and USERS[username] == password:
        session['username'] = username
        return jsonify({'status': 'success', 'message': 'Login successful'})
    return jsonify({'status': 'fail', 'message': 'Invalid username or password'}), 401

@app.route("/logout", methods=["POST"])
def logout():
    """Log out the current user."""
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': 'Logged out'})

@app.route("/accounts", methods=["GET"])
def accounts():
    """Return the list of accounts as JSON.  Requires authentication."""
    if not is_authenticated():
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    # Convert DataFrame to list of dicts for JSON response
    accounts_list = chart_df.to_dict(orient='records')
    return jsonify(accounts_list)

@app.route("/dashboard", methods=["GET"])
def dashboard_data():
    """Return aggregate dashboard metrics as JSON."""
    if not is_authenticated():
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    # Compute simple aggregates from the chart of accounts
    total_accounts = len(chart_df)
    asset_accounts = int((chart_df['type'] == 'Asset').sum())
    liability_accounts = int((chart_df['type'] == 'Liability').sum())
    equity_accounts = int((chart_df['type'] == 'Equity').sum())
    metrics = {
        'total_accounts': total_accounts,
        'asset_accounts': asset_accounts,
        'liability_accounts': liability_accounts,
        'equity_accounts': equity_accounts,
    }
    return jsonify(metrics)

@app.route("/dashboard-page")
def dashboard_page():
    """Render the dashboard page.  Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route("/accounts-page")
def accounts_page():
    """Render the accounts page.  Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('accounts.html')

# ------------------- Customer Endpoints -------------------
@app.route("/customers-page")
def customers_page():
    """Render the customers page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('customers.html')

@app.route("/customers", methods=["GET", "POST"])
def customers_api():
    """List or create customers.
    GET returns all customers for admin or the current user's customers.
    POST creates a new customer."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    if request.method == "GET":
        if current['role'] == 'admin':
            return jsonify(CUSTOMERS)
        # client: filter by owner
        user_customers = [c for c in CUSTOMERS if c.get('owner') == current['username']]
        return jsonify(user_customers)
    # POST: create customer
    data = request.get_json() or request.form
    name = data.get('name')
    contact = data.get('contact')
    if not name:
        return jsonify({'status': 'fail', 'message': 'Name is required'}), 400
    customer = {
        'id': _generate_id(CUSTOMERS),
        'name': name,
        'contact': contact or '',
        'owner': current['username']
    }
    CUSTOMERS.append(customer)
    return jsonify({'status': 'success', 'customer': customer})

# ------------------- Vendor Endpoints -------------------
@app.route("/vendors-page")
def vendors_page():
    """Render the vendors page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('vendors.html')

@app.route("/vendors", methods=["GET", "POST"])
def vendors_api():
    """List or create vendors."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    if request.method == "GET":
        if current['role'] == 'admin':
            return jsonify(VENDORS)
        # clients see vendors assigned to them? For simplicity return all.
        return jsonify(VENDORS)
    # POST: create vendor
    data = request.get_json() or request.form
    name = data.get('name')
    contact = data.get('contact')
    if not name:
        return jsonify({'status': 'fail', 'message': 'Name is required'}), 400
    vendor = {
        'id': _generate_id(VENDORS),
        'name': name,
        'contact': contact or '',
        'owner': current['username']
    }
    VENDORS.append(vendor)
    return jsonify({'status': 'success', 'vendor': vendor})

# ------------------- Invoice Endpoints -------------------
@app.route("/invoices-page")
def invoices_page():
    """Render the invoices page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('invoices.html')

@app.route("/invoices", methods=["GET", "POST"])
def invoices_api():
    """List or create invoices."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    if request.method == "GET":
        if current['role'] == 'admin':
            return jsonify(INVOICES)
        # clients see only their invoices
        user_invoices = [inv for inv in INVOICES if inv.get('owner') == current['username']]
        return jsonify(user_invoices)
    # POST: create invoice
    data = request.get_json() or request.form
    customer_id = data.get('customer_id')
    items = data.get('items')  # expects a list of {description, account, amount}
    if not customer_id or not items:
        return jsonify({'status': 'fail', 'message': 'Customer and items required'}), 400
    total = 0
    for item in items:
        total += float(item.get('amount', 0))
    invoice = {
        'id': _generate_id(INVOICES),
        'customer_id': int(customer_id),
        'items': items,
        'total': total,
        'date': pd.Timestamp.today().strftime('%Y-%m-%d'),
        'status': 'draft',
        'owner': current['username']
    }
    INVOICES.append(invoice)
    # Create a journal entry: debit Accounts Receivable, credit revenue accounts
    # Find AR account. If not present, skip JE.
    ar_account = None
    ar_row = chart_df[chart_df['name'].str.contains('Accounts Receivable', case=False)]
    if not ar_row.empty:
        ar_account = ar_row.iloc[0]['code']
    if ar_account:
        for item in items:
            credit_acc = item.get('account')
            amt = float(item.get('amount', 0))
            create_journal_entry(debit_account=ar_account,
                                 credit_account=credit_acc,
                                 amount=amt,
                                 description=f"Invoice {invoice['id']} - {item.get('description')}",
                                 user=current['username'])
    return jsonify({'status': 'success', 'invoice': invoice})

# ------------------- Bill Endpoints -------------------
@app.route("/bills-page")
def bills_page():
    """Render the bills page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('bills.html')

@app.route("/bills", methods=["GET", "POST"])
def bills_api():
    """List or create bills."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    if request.method == "GET":
        if current['role'] == 'admin':
            return jsonify(BILLS)
        user_bills = [b for b in BILLS if b.get('owner') == current['username']]
        return jsonify(user_bills)
    data = request.get_json() or request.form
    vendor_id = data.get('vendor_id')
    items = data.get('items')
    if not vendor_id or not items:
        return jsonify({'status': 'fail', 'message': 'Vendor and items required'}), 400
    total = 0
    for item in items:
        total += float(item.get('amount', 0))
    bill = {
        'id': _generate_id(BILLS),
        'vendor_id': int(vendor_id),
        'items': items,
        'total': total,
        'date': pd.Timestamp.today().strftime('%Y-%m-%d'),
        'status': 'draft',
        'owner': current['username']
    }
    BILLS.append(bill)
    # Create journal entry: debit expense accounts, credit Accounts Payable
    ap_account = None
    ap_row = chart_df[chart_df['name'].str.contains('Accounts Payable', case=False)]
    if not ap_row.empty:
        ap_account = ap_row.iloc[0]['code']
    if ap_account:
        for item in items:
            debit_acc = item.get('account')
            amt = float(item.get('amount', 0))
            create_journal_entry(debit_account=debit_acc,
                                 credit_account=ap_account,
                                 amount=amt,
                                 description=f"Bill {bill['id']} - {item.get('description')}",
                                 user=current['username'])
    return jsonify({'status': 'success', 'bill': bill})

# ------------------- Statements Endpoints -------------------
@app.route("/statements-page")
def statements_page():
    """Render the statements page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('statements.html')

@app.route("/statements/income", methods=["GET"])
def income_statement():
    """Return the income statement as JSON."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    return jsonify(compute_income_statement())

@app.route("/statements/balance", methods=["GET"])
def balance_statement():
    """Return the balance sheet as JSON."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    return jsonify(compute_balance_sheet())

@app.route("/statements/cashflow", methods=["GET"])
def cashflow_statement():
    """Return the cash flow statement as JSON."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    return jsonify(compute_cash_flow())

# ------------------- Bank Upload and Reconciliation Endpoints -------------------
@app.route("/bank-page")
def bank_page():
    """Render the bank reconciliation page. Requires authentication."""
    if not is_authenticated():
        return redirect(url_for('home'))
    return render_template('bank.html')

@app.route("/bank/upload", methods=["POST"])
def upload_bank_statement():
    """Upload bank transactions. Accepts a JSON list of transactions with date, amount, description."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'status': 'fail', 'message': 'Expecting a JSON array of transactions'}), 400
    for tx in data:
        BANK_TRANSACTIONS.append({
            'id': _generate_id(BANK_TRANSACTIONS),
            'date': tx.get('date'),
            'amount': float(tx.get('amount', 0)),
            'description': tx.get('description', ''),
            'owner': current['username']
        })
    return jsonify({'status': 'success', 'imported': len(data)})

@app.route("/bank/reconcile", methods=["GET"])
def reconcile_bank():
    """Return unmatched bank transactions and unmatched journal entries for reconciliation."""
    current = _get_current_user()
    if not current:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    # Gather user-specific bank transactions and journal entries
    user_bank = [tx for tx in BANK_TRANSACTIONS if tx.get('owner') == current['username']]
    user_entries = [je for je in JOURNAL_ENTRIES if je.get('user') == current['username']]
    # Match by amount and description: simple matching
    matched_bank_ids = set()
    matched_entry_ids = set()
    for tx in user_bank:
        for je in user_entries:
            if je['amount'] == tx['amount'] and je['description'][:50] == tx['description'][:50]:
                matched_bank_ids.add(tx['id'])
                matched_entry_ids.add(je['id'])
    unmatched_bank = [tx for tx in user_bank if tx['id'] not in matched_bank_ids]
    unmatched_entries = [je for je in user_entries if je['id'] not in matched_entry_ids]
    return jsonify({
        'unmatched_bank_transactions': unmatched_bank,
        'unmatched_journal_entries': unmatched_entries
    })

# ------------------- Account Management and Journal Entry Endpoints -------------------
@app.route("/accounts/add", methods=["POST"])
def add_account():
    """Add a new account to the chart of accounts. Admin only."""
    current = _get_current_user()
    if not current or current['role'] != 'admin':
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    data = request.get_json() or request.form
    code = data.get('code')
    name = data.get('name')
    acc_type = data.get('type')
    description = data.get('description', '')
    if not code or not name or not acc_type:
        return jsonify({'status': 'fail', 'message': 'Code, name and type are required'}), 400
    # Ensure code is unique
    if code in chart_df['code'].values:
        return jsonify({'status': 'fail', 'message': 'Account code already exists'}), 400
    # Append the new account to chart_df in place. Because pandas DataFrame
    # objects are mutable, we can assign to a new row without reassigning
    # the global variable. This avoids the need for a global declaration.
    chart_df.loc[len(chart_df)] = {
        'code': code,
        'name': name,
        'type': acc_type,
        'description': description
    }
    return jsonify({'status': 'success', 'account': {
        'code': code,
        'name': name,
        'type': acc_type,
        'description': description
    }})

@app.route("/journal/new", methods=["POST"])
def new_journal_entry():
    """Create a new journal entry. Admin only."""
    current = _get_current_user()
    if not current or current['role'] != 'admin':
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401
    data = request.get_json() or request.form
    debit = data.get('debit_account')
    credit = data.get('credit_account')
    amount = data.get('amount')
    description = data.get('description', '')
    if not debit or not credit or not amount:
        return jsonify({'status': 'fail', 'message': 'Debit, credit and amount required'}), 400
    create_journal_entry(debit_account=debit,
                         credit_account=credit,
                         amount=float(amount),
                         description=description,
                         user=current['username'])
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    # When run directly, start the Flask development server.
    app.run(debug=True)