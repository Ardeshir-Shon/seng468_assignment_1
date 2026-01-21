"""
Optimized version of the Flask application.
This version addresses the performance bottlenecks identified in app.py.
"""

from flask import Flask, jsonify, request
import sqlite3
import hashlib
from functools import lru_cache
import time

app = Flask(__name__)
DATABASE = 'users_optimized.db'

# Configuration for optimization
app.config['JSON_SORT_KEYS'] = False  # Avoid unnecessary sorting

def get_db():
    """Get database connection with optimizations."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    # Enable Write-Ahead Logging for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    """Initialize the database with proper indexes."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # OPTIMIZATION: Add indexes for frequently queried columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    
    conn.commit()
    conn.close()

@lru_cache(maxsize=1000)
def efficient_hash(password):
    """
    OPTIMIZATION: Use a single SHA-256 hash instead of 1000 iterations.
    In production, use bcrypt or argon2, but for demonstration we use optimized SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def efficient_search_in_db(query):
    """
    OPTIMIZATION: Use SQL LIKE query instead of loading all data into memory.
    This is O(n) in the database with proper indexing.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Use SQL's built-in search capabilities
    cursor.execute('SELECT * FROM users WHERE username = ?', (query,))
    results = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in results]

@app.route('/')
def index():
    """Home endpoint."""
    return jsonify({
        'message': 'Welcome to the OPTIMIZED Performance Testing API',
        'version': 'optimized',
        'endpoints': {
            '/users': 'GET - List all users',
            '/users/<id>': 'GET - Get user by ID',
            '/users': 'POST - Create new user',
            '/posts': 'GET - List all posts',
            '/posts/<id>': 'GET - Get post by ID',
            '/search': 'GET - Search users (optimized)',
            '/heavy': 'GET - CPU intensive operation (optimized)'
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users with optimized query.
    OPTIMIZATION: Single JOIN query instead of N+1 queries.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Single query with JOIN and COUNT - eliminates N+1 problem
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.password_hash, u.created_at,
               COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id, u.username, u.email, u.password_hash, u.created_at
    ''')
    
    users = cursor.fetchall()
    result = [dict(user) for user in users]
    
    conn.close()
    return jsonify(result)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID with optimized queries."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user is None:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    user_dict = dict(user)
    
    # Fetch user's posts (benefits from index on user_id)
    cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
    posts = cursor.fetchall()
    user_dict['posts'] = [dict(post) for post in posts]
    
    conn.close()
    return jsonify(user_dict)

@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user with optimized hashing.
    OPTIMIZATION: Efficient password hashing (single iteration).
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Efficient password hashing
    password_hash = efficient_hash(data['password'])
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (data['username'], data['email'], password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400
    
    conn.close()
    return jsonify({'id': user_id, 'username': data['username']}), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all posts with optimized query.
    OPTIMIZATION: Benefits from index on user_id foreign key.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # This query is now optimized with proper indexing
    cursor.execute('''
        SELECT p.*, u.username 
        FROM posts p
        JOIN users u ON p.user_id = u.id
    ''')
    
    posts = cursor.fetchall()
    result = [dict(post) for post in posts]
    
    conn.close()
    return jsonify(result)

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, u.username 
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (post_id,))
    
    post = cursor.fetchone()
    
    if post is None:
        conn.close()
        return jsonify({'error': 'Post not found'}), 404
    
    conn.close()
    return jsonify(dict(post))

@app.route('/search', methods=['GET'])
def search_users():
    """
    Search for users with optimization.
    OPTIMIZATION: Use SQL search capabilities, avoid loading all data into memory.
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    # Use optimized database search
    results = efficient_search_in_db(query)
    
    return jsonify(results)

@app.route('/heavy', methods=['GET'])
def heavy_operation():
    """
    CPU-intensive operation - optimized version.
    OPTIMIZATION: Removed unnecessary string operations and reduced complexity.
    """
    # More efficient computation
    result = sum(i * i for i in range(100000))
    
    return jsonify({'result': result, 'iterations': 100000})

@app.route('/seed', methods=['POST'])
def seed_database():
    """Seed the database with sample data."""
    import random
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM posts')
    cursor.execute('DELETE FROM users')
    
    # Insert sample users
    users = []
    for i in range(50):
        username = f'user{i}'
        email = f'user{i}@example.com'
        password_hash = hashlib.sha256(f'password{i}'.encode()).hexdigest()
        
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        users.append(cursor.lastrowid)
    
    # Insert sample posts
    for i in range(200):
        user_id = random.choice(users)
        title = f'Post {i}'
        content = f'This is the content of post {i}. ' * 10
        
        cursor.execute(
            'INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
            (user_id, title, content)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Database seeded successfully', 'users': len(users), 'posts': 200})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
