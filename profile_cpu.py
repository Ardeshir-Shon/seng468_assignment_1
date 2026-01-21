"""
CPU Profiling script using cProfile.
This script profiles the Flask application to identify CPU bottlenecks.
"""

import cProfile
import pstats
import io
from app import app, init_db
import requests
import threading
import time

def start_app():
    """Start the Flask app in a thread."""
    init_db()
    app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)

def run_load_test():
    """Run a series of requests to profile."""
    base_url = 'http://127.0.0.1:5001'
    
    # Wait for server to start
    time.sleep(2)
    
    # Seed database
    print("Seeding database...")
    requests.post(f'{base_url}/seed')
    
    print("Running profiling load test...")
    
    # Make various requests
    for i in range(10):
        requests.get(f'{base_url}/users')
        requests.get(f'{base_url}/posts')
        requests.get(f'{base_url}/users/{i % 50 + 1}')
        requests.get(f'{base_url}/search?q=user{i % 50}')
        requests.post(f'{base_url}/users', json={
            'username': f'testuser{i}',
            'email': f'test{i}@example.com',
            'password': 'testpassword'
        })
    
    # Heavy operations
    for i in range(5):
        requests.get(f'{base_url}/heavy')
    
    print("Profiling load test completed")

if __name__ == '__main__':
    print("Starting Flask app for profiling...")
    
    # Start the app in a separate thread
    app_thread = threading.Thread(target=start_app, daemon=True)
    app_thread.start()
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Start profiling
    profiler.enable()
    
    # Run load test
    run_load_test()
    
    # Stop profiling
    profiler.disable()
    
    # Create a string stream to capture the output
    s = io.StringIO()
    
    # Sort by cumulative time and print stats
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    
    # Save full statistics
    print("\n" + "="*80)
    print("PROFILING RESULTS - Top 30 functions by cumulative time")
    print("="*80)
    ps.print_stats(30)
    
    # Save to file
    with open('profiling_results_cpu.txt', 'w') as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.strip_dirs()
        ps.sort_stats('cumulative')
        f.write("="*80 + "\n")
        f.write("CPU PROFILING RESULTS - Sorted by Cumulative Time\n")
        f.write("="*80 + "\n\n")
        ps.print_stats(50)
        
        f.write("\n\n" + "="*80 + "\n")
        f.write("CPU PROFILING RESULTS - Sorted by Total Time\n")
        f.write("="*80 + "\n\n")
        ps.sort_stats('tottime')
        ps.print_stats(50)
    
    print("\nProfiling results saved to profiling_results_cpu.txt")
