from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "yousif_key_123" # مفتاح لتأمين الجلسات

# --- إنشاء قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('social.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, content TEXT, author TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- الواجهة البرمجية (HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>موقعي للتواصل الاجتماعي</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .box { background: white; padding: 20px; border-radius: 8px; max-width: 500px; margin: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, textarea { width: 95%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
        button { background: #1877f2; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .post { border-bottom: 1px solid #eee; padding: 10px 0; }
    </style>
</head>
<body>
    <div class="box">
        {% if not session.get('user') %}
            <h2>إنشاء حساب / دخول</h2>
            <form action="/auth" method="post">
                <input type="text" name="user" placeholder="اسم المستخدم" required>
                <input type="password" name="pass" placeholder="كلمة السر" required>
                <button type="submit">دخول / تسجيل</button>
            </form>
        {% else %}
            <h2>مرحباً، {{ session['user'] }}!</h2>
            <form action="/post" method="post">
                <textarea name="content" placeholder="بماذا تفكر؟" required></textarea>
                <button type="submit">نشر</button>
            </form>
            <hr>
            <h3>المنشورات:</h3>
            {% for post in posts %}
                <div class="post"><b>{{ post[2] }}:</b> {{ post[1] }}</div>
            {% endfor %}
            <br>
            <a href="/logout">تسجيل الخروج</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('social.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, posts=posts)

@app.route('/auth', methods=['POST'])
def auth():
    user = request.form.get('user')
    password = request.form.get('pass')
    conn = sqlite3.connect('social.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (user,))
    account = c.fetchone()
    
    if account: # إذا الحساب موجود، سجل دخول
        if check_password_hash(account[2], password):
            session['user'] = user
    else: # إذا غير موجود، أنشئ حساباً جديداً
        hashed_pw = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, hashed_pw))
        conn.commit()
        session['user'] = user
    
    conn.close()
    return redirect(url_for('home'))

@app.route('/post', methods=['POST'])
def post():
    if session.get('user'):
        content = request.form.get('content')
        conn = sqlite3.connect('social.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (content, author) VALUES (?, ?)", (content, session['user']))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

