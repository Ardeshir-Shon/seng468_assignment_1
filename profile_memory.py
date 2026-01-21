"""
Memory profiling script.
This script profiles memory usage of specific functions in the application.
"""

from memory_profiler import profile
import sqlite3
import random
import hashlib

# Simulate the database operations
DATABASE = 'users_profile.db'

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_test_db():
    """Initialize test database."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # Seed data
    cursor.execute('DELETE FROM posts')
    cursor.execute('DELETE FROM users')
    
    for i in range(100):
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (f'user{i}', f'user{i}@example.com', hashlib.sha256(f'password{i}'.encode()).hexdigest())
        )
    
    users = list(range(1, 101))
    for i in range(500):
        cursor.execute(
            'INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
            (random.choice(users), f'Post {i}', f'Content of post {i}. ' * 20)
        )
    
    conn.commit()
    conn.close()

@profile
def memory_intensive_get_users():
    """
    Simulate the get_users endpoint with N+1 query problem.
    This function demonstrates memory issues when loading data.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    result = []
    for user in users:
        user_dict = dict(user)
        # N+1 query problem
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE user_id = ?', (user['id'],))
        post_count = cursor.fetchone()[0]
        user_dict['post_count'] = post_count
        result.append(user_dict)
    
    conn.close()
    return result

@profile
def memory_intensive_search():
    """
    Simulate the inefficient search operation.
    Loads all data into memory unnecessarily.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Load all users into memory
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    
    # Convert to list
    usernames = [user[1] for user in all_users]  # username is at index 1
    
    # Simulate search
    target = 'user50'
    found = []
    
    # Inefficient O(n^2) search
    for i in range(len(usernames)):
        for j in range(len(usernames)):
            if i == j and usernames[i] == target:
                found.append(usernames[i])
    
    conn.close()
    return found

@profile
def inefficient_hash_function(password):
    """Profile the inefficient hashing function."""
    result = password
    for i in range(1000):
        result = hashlib.sha256(result.encode()).hexdigest()
    return result

if __name__ == '__main__':
    print("Initializing test database...")
    init_test_db()
    
    print("\n" + "="*80)
    print("Memory Profiling: get_users with N+1 query problem")
    print("="*80)
    result = memory_intensive_get_users()
    print(f"Retrieved {len(result)} users")
    
    print("\n" + "="*80)
    print("Memory Profiling: inefficient search operation")
    print("="*80)
    search_result = memory_intensive_search()
    print(f"Search found {len(search_result)} results")
    
    print("\n" + "="*80)
    print("Memory Profiling: inefficient hash function")
    print("="*80)
    hash_result = inefficient_hash_function("testpassword123")
    print(f"Hash result length: {len(hash_result)}")
    
    print("\n" + "="*80)
    print("Memory profiling completed!")
    print("="*80)
