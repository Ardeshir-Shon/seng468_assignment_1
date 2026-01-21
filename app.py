"""
Simple Flask web application for performance measurement and profiling.
This application intentionally includes performance bottlenecks for demonstration purposes.
"""

from flask import Flask, jsonify, request
import sqlite3
import time
import random
import hashlib

app = Flask(__name__)
DATABASE = 'users.db'

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with sample data."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
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
    
    conn.commit()
    conn.close()

def inefficient_hash(password):
    """
    Intentionally inefficient password hashing for demonstration.
    BOTTLENECK: Multiple unnecessary hash iterations.
    """
    result = password
    for i in range(1000):  # Excessive iterations
        result = hashlib.sha256(result.encode()).hexdigest()
    return result

def inefficient_search(data, target):
    """
    Intentionally inefficient search algorithm.
    BOTTLENECK: O(n^2) complexity when O(n) would suffice.
    """
    found = []
    for i in range(len(data)):
        for j in range(len(data)):
            if i == j and data[i] == target:
                found.append(data[i])
    return found

@app.route('/')
def index():
    """Home endpoint."""
    return jsonify({
        'message': 'Welcome to the Performance Testing API',
        'endpoints': {
            '/users': 'GET - List all users',
            '/users/<id>': 'GET - Get user by ID',
            '/users': 'POST - Create new user',
            '/posts': 'GET - List all posts',
            '/posts/<id>': 'GET - Get post by ID',
            '/search': 'GET - Search users (inefficient)',
            '/heavy': 'GET - CPU intensive operation'
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users.
    BOTTLENECK: N+1 query problem - fetches posts for each user individually.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    result = []
    for user in users:
        user_dict = dict(user)
        # N+1 query problem: fetching posts for each user separately
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE user_id = ?', (user['id'],))
        post_count = cursor.fetchone()['count']
        user_dict['post_count'] = post_count
        result.append(user_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user is None:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    user_dict = dict(user)
    
    # Fetch user's posts
    cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
    posts = cursor.fetchall()
    user_dict['posts'] = [dict(post) for post in posts]
    
    conn.close()
    return jsonify(user_dict)

@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.
    BOTTLENECK: Inefficient password hashing.
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Inefficient password hashing
    password_hash = inefficient_hash(data['password'])
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
        (data['username'], data['email'], password_hash)
    )
    
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': user_id, 'username': data['username']}), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all posts.
    BOTTLENECK: Missing indexes on foreign keys.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Without proper indexing, this query can be slow
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
    Search for users.
    BOTTLENECK: Inefficient search algorithm and loading all data into memory.
    """
    query = request.args.get('q', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Load all users into memory (inefficient for large datasets)
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    
    # Convert to list of usernames for inefficient search
    usernames = [user['username'] for user in all_users]
    
    # Use inefficient search algorithm
    found = inefficient_search(usernames, query)
    
    # Now fetch the actual user data (another inefficiency)
    results = []
    for username in found:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            results.append(dict(user))
    
    conn.close()
    return jsonify(results)

@app.route('/heavy', methods=['GET'])
def heavy_operation():
    """
    CPU-intensive operation for load testing.
    BOTTLENECK: Unnecessary computational complexity.
    """
    # Simulate heavy computation
    result = 0
    iterations = 100000
    
    for i in range(iterations):
        result += i * i
        if i % 1000 == 0:
            # Unnecessary string operations
            temp = str(result) * 10
            temp = temp[:100]
    
    return jsonify({'result': result, 'iterations': iterations})

@app.route('/seed', methods=['POST'])
def seed_database():
    """Seed the database with sample data."""
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
