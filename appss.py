from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'omnicode_world_secret_key_2026'

# Database Setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Articles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# HTML Template with Login/Signup, Code Runner & Database Articles Feed
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniCode World Ultimate Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .glass-panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .code-editor {
            font-family: 'Fira Code', 'Courier New', Courier, monospace;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col">

    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-r from-blue-500 to-indigo-600 p-2 rounded-xl text-white">
                    <i class="fa-solid fa-code text-xl"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg text-white leading-none">OmniCode World</h1>
                    <span class="text-xs text-indigo-400">Database CMS | Code Runners | Ads Engine</span>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                {% if username %}
                    <span class="text-xs text-emerald-400 font-semibold">👤 Welcome, {{ username }}</span>
                    <a href="/logout" class="bg-rose-600 hover:bg-rose-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition">Logout</a>
                {% else %}
                    <a href="#auth-section" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition">Login / Signup</a>
                {% endif %}
                <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full text-xs font-semibold animate-pulse">
                    ● DB Online
                </span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-6 flex-grow grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">

        <!-- Left Column (Code Runner & Articles CMS) -->
        <main class="lg:col-span-8 space-y-6">

            <!-- Multi-Language Code Playground -->
            <div class="glass-panel rounded-2xl p-5 shadow-2xl">
                <div class="flex justify-between items-center mb-4 border-b border-slate-800 pb-3">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid fa-terminal text-blue-400"></i>
                        <h2 class="font-bold text-lg">Multi-Language Code Runner (HTML, JS, C++, Java)</h2>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs text-slate-400 mb-2 font-semibold uppercase">Source Code Input</label>
                        <textarea id="code-input" class="w-full h-48 bg-slate-900 border border-slate-800 rounded-xl p-3 code-editor text-sm text-indigo-300 focus:outline-none focus:border-indigo-500 resize-none"><div style="color:#10b981;"><h2>Hello World from OmniCode Portal!</h2><p>Live rendered web output.</p></div></textarea>
                        <button onclick="runCode()" class="mt-3 w-full bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded-xl text-sm font-bold flex items-center justify-center space-x-2 transition">
                            <i class="fa-solid fa-play"></i>
                            <span>Execute Code</span>
                        </button>
                    </div>

                    <div>
                        <label class="block text-xs text-slate-400 mb-2 font-semibold uppercase">Live Output / Preview</label>
                        <div id="output-box" class="w-full h-48 bg-slate-900 border border-slate-800 rounded-xl p-3 code-editor text-xs text-emerald-400 overflow-auto">
                            Click 'Execute Code' to run...
                        </div>
                    </div>
                </div>
            </div>

            <!-- Publish Article Form (Database Connected) -->
            <div class="glass-panel rounded-2xl p-5 shadow-2xl" id="publish-section">
                <h2 class="font-bold text-lg mb-4 text-indigo-400 flex items-center space-x-2">
                    <i class="fa-solid fa-pen-nib"></i>
                    <span>Publish New Article to Database</span>
                </h2>
                {% if username %}
                <form action="/add_article" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs text-slate-400 mb-1 font-semibold uppercase">Article Title</label>
                        <input type="text" name="title" required class="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500" placeholder="Enter article title...">
                    </div>
                    <div>
                        <label class="block text-xs text-slate-400 mb-1 font-semibold uppercase">Category</label>
                        <input type="text" name="category" required class="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500" placeholder="e.g. C++, Web Dev, Monetization">
                    </div>
                    <div>
                        <label class="block text-xs text-slate-400 mb-1 font-semibold uppercase">Content</label>
                        <textarea name="content" required rows="3" class="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none" placeholder="Write your article description..."></textarea>
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl text-sm font-bold transition shadow-lg">
                        Publish to Global Feed
                    </button>
                </form>
                {% else %}
                <p class="text-xs text-amber-400 bg-amber-500/10 border border-amber-500/30 p-3 rounded-xl text-center">
                    ⚠️ Please Login or Signup first to publish articles to the database!
                </p>
                {% endif %}
            </div>

            <!-- Database Articles Feed -->
            <div class="glass-panel rounded-2xl p-5 shadow-2xl">
                <h2 class="font-bold text-lg mb-4 text-indigo-400 flex items-center space-x-2">
                    <i class="fa-solid fa-newspaper"></i>
                    <span>Live Database Articles Feed</span>
                </h2>
                <div class="space-y-3">
                    {% for article in articles %}
                    <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs text-blue-400 font-mono">📂 {{ article[3] }}</span>
                            <span class="text-[10px] text-slate-500">Author: {{ article[4] }}</span>
                        </div>
                        <h3 class="font-bold text-white text-base mt-1">{{ article[1] }}</h3>
                        <p class="text-xs text-slate-400 mt-1">{{ article[2] }}</p>
                    </div>
                    {% else %}
                    <p class="text-xs text-slate-500 text-center py-4">No articles published yet. Be the first to publish!</p>
                    {% endfor %}
                </div>
            </div>

        </main>

        <!-- Right Column (Monetization & Auth) -->
        <aside class="lg:col-span-4 space-y-6">

            <!-- Authentication Box -->
            <div class="glass-panel rounded-2xl p-5 border border-indigo-500/30 shadow-2xl" id="auth-section">
                <h3 class="font-bold text-indigo-400 text-sm tracking-wider uppercase mb-3 flex items-center space-x-2">
                    <i class="fa-solid fa-user-lock"></i>
                    <span>User Portal Access</span>
                </h3>

                {% if not username %}
                <form action="/login" method="POST" class="space-y-3">
                    <div>
                        <label class="block text-[10px] text-slate-400 uppercase font-semibold mb-1">Username</label>
                        <input type="text" name="username" required class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500">
                    </div>
                    <div>
                        <label class="block text-[10px] text-slate-400 uppercase font-semibold mb-1">Password</label>
                        <input type="password" name="password" required class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500">
                    </div>
                    <div class="flex space-x-2 pt-1">
                        <button type="submit" class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg text-xs font-bold transition">Login</button>
                        <button formaction="/signup" type="submit" class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 rounded-lg text-xs font-bold transition">Sign Up</button>
                    </div>
                </form>
                {% else %}
                <div class="text-center py-2">
                    <p class="text-xs text-slate-300">You are logged in as <b class="text-emerald-400">{{ username }}</b></p>
                </div>
                {% endif %}
            </div>

            <!-- Monetization & Ad Links -->
            <div class="glass-panel rounded-2xl p-5 border border-amber-500/20 shadow-2xl">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="font-bold text-amber-400 text-sm tracking-wider uppercase flex items-center space-x-2">
                        <i class="fa-solid fa-rectangle-ad"></i>
                        <span>Monetization Center</span>
                    </h3>
                </div>

                <div class="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-xl p-4 mb-4 text-center">
                    <span class="text-xs font-semibold text-amber-400 block mb-1">🔥 Premium Sponsor Slot</span>
                    <p class="text-sm font-bold text-white mb-2">Cloud Hosting & Domain Deal</p>
                    <a href="https://google.com" target="_blank" class="inline-block bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs px-4 py-2 rounded-lg transition shadow-lg">
                        Claim Client Ad Link
                    </a>
                </div>

                <div class="space-y-2">
                    <span class="text-xs text-slate-400 font-semibold uppercase block mb-2">Active Partner Links</span>
                    <a href="https://google.com" target="_blank" class="block bg-slate-900/80 hover:bg-slate-800 border border-slate-800 p-3 rounded-xl text-xs flex justify-between items-center transition">
                        <span class="text-slate-300">Java Developer Certification</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-slate-500 text-[10px]"></i>
                    </a>
                    <a href="https://google.com" target="_blank" class="block bg-slate-900/80 hover:bg-slate-800 border border-slate-800 p-3 rounded-xl text-xs flex justify-between items-center transition">
                        <span class="text-slate-300">C++ Programming Course</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-slate-500 text-[10px]"></i>
                    </a>
                </div>
            </div>

        </aside>

    </div>

    <script>
        function runCode() {
            const code = document.getElementById('code-input').value;
            const outputBox = document.getElementById('output-box');
            outputBox.innerHTML = code;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    username = session.get('username')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, category, author FROM articles ORDER BY id DESC')
    articles = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, username=username, articles=articles)

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
    except:
        pass
    return redirect(url_for('home'))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        session['username'] = username
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/add_article", methods=["POST"])
def add_article():
    if 'username' not in session:
        return redirect(url_for('home'))
    title = request.form.get('title')
    category = request.form.get('category')
    content = request.form.get('content')
    author = session['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO articles (title, content, category, author) VALUES (?, ?, ?, ?)', (title, content, category, author))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
