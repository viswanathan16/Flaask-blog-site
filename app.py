from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
DATABASE = '/data/blog.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with posts table"""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add sample post if table is empty
    if conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0] == 0:
        conn.execute(
            'INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
            ('Welcome to Flask Blog!', 
             'This is your first blog post. Data is persisted in SQLite database using Docker volumes.',
             'Admin')
        )
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Display all blog posts"""
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    """Create a new blog post"""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
                     (title, content, author))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    """Display a single blog post"""
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        return "Post not found", 404
    
    return render_template('post.html', post=post)

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
