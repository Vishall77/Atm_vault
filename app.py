from flask import Flask, render_template, request, redirect, session
from main import Atm

app = Flask(__name__)
app.secret_key = "secret123"

atm = Atm()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        acc = atm.create_account(
            request.form['name'],
            int(request.form['pin']),
            float(request.form['balance']),
            request.form['answer']
        )
        return f"Account created: {acc}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        success, msg = atm.login(
            request.form['acc'],
            int(request.form['pin'])
        )
        if success:
            session['user'] = request.form['acc']
            return redirect('/dashboard')
        return msg
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    acc = session['user']
    balance = atm.get_balance(acc)

    return render_template('dashboard.html', acc=acc, balance=balance)

@app.route('/deposit', methods=['POST'])
def deposit():
    atm.deposit(session['user'], float(request.form['amount']))
    return redirect('/dashboard')

@app.route('/withdraw', methods=['POST'])
def withdraw():
    atm.withdraw(session['user'], float(request.form['amount']))
    return redirect('/dashboard')

@app.route('/transfer', methods=['POST'])
def transfer():
    atm.transfer(
        session['user'],
        request.form['receiver'],
        float(request.form['amount'])
    )
    return redirect('/dashboard')

@app.route('/history')
def history():
    data = atm.get_transactions(session['user'])
    return render_template('history.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)