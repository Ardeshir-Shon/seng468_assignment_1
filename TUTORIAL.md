# SENG468 Assignment 1 Tutorial

## Performance Measurement & Profiling - Step-by-Step Guide

This tutorial walks you through the complete process of performance analysis and optimization for the assignment.

---

## Table of Contents

1. [Setup and Installation](#1-setup-and-installation)
2. [Understanding the Application](#2-understanding-the-application)
3. [Establishing Baseline Metrics](#3-establishing-baseline-metrics)
4. [CPU Profiling](#4-cpu-profiling)
5. [Memory Profiling](#5-memory-profiling)
6. [Load Testing](#6-load-testing)
7. [Identifying Bottlenecks](#7-identifying-bottlenecks)
8. [Implementing Optimizations](#8-implementing-optimizations)
9. [Validating Improvements](#9-validating-improvements)
10. [Writing the Report](#10-writing-the-report)

---

## 1. Setup and Installation

### Step 1.1: Clone and Navigate

```bash
git clone <repository-url>
cd seng468_assignment_1
```

### Step 1.2: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed flask-3.0.0 locust-2.20.0 memory-profiler-0.61.0 ...
```

### Step 1.3: Verify Installation

```bash
python3 -c "import flask, locust; print('All dependencies installed successfully')"
```

---

## 2. Understanding the Application

### Step 2.1: Review the Code Structure

```bash
ls -l *.py
```

Files you should see:
- `app.py` - Original application with bottlenecks
- `app_optimized.py` - Optimized version
- `locustfile.py` - Load testing script
- `profile_cpu.py` - CPU profiling script
- `profile_memory.py` - Memory profiling script

### Step 2.2: Start the Application

```bash
python3 app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 2.3: Test Basic Functionality

In another terminal:

```bash
# Initialize with sample data
curl -X POST http://localhost:5000/seed

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/users
curl http://localhost:5000/posts
curl "http://localhost:5000/search?q=user1"
```

**Key Observation:** Notice the response times. The `/users` endpoint should feel slightly slow.

---

## 3. Establishing Baseline Metrics

### Step 3.1: Manual Response Time Testing

Use `curl` with timing:

```bash
time curl -s http://localhost:5000/users > /dev/null
```

Record the "real" time. Run it 10 times and calculate average.

### Step 3.2: Automated Baseline Collection

Create a simple script `baseline.sh`:

```bash
#!/bin/bash
echo "Collecting baseline metrics..."

for i in {1..10}; do
    echo "Request $i:"
    time curl -s http://localhost:5000/users > /dev/null
done
```

Run it:
```bash
bash baseline.sh 2>&1 | grep real
```

### Step 3.3: Document Baseline Metrics

Create a file `baseline_metrics.txt`:

```
Baseline Performance Metrics
============================
Date: 2026-01-21
Application: app.py (original)

GET /users:
  Average response time: XXXms
  
GET /posts:
  Average response time: XXXms
  
POST /users:
  Average response time: XXXms
  
GET /search:
  Average response time: XXXms
```

---

## 4. CPU Profiling

### Step 4.1: Run CPU Profiler

```bash
python3 profile_cpu.py
```

This script will:
1. Start the Flask app
2. Make various API requests
3. Profile CPU usage
4. Save results to `profiling_results_cpu.txt`

### Step 4.2: Analyze CPU Profiling Results

Open `profiling_results_cpu.txt` and look for:

1. **Function call counts:** How many times each function is called
2. **Total time:** Time spent in function including sub-calls
3. **Cumulative time:** Total time including all nested calls

**What to look for:**

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1000    0.042    0.000    0.042    0.000 app.py:32(inefficient_hash)
```

This shows:
- Called 1000 times
- Takes 0.042 seconds total
- 42ms for a hash function is way too slow!

### Step 4.3: Identify Hot Paths

Hot paths are code sections that:
- Are called frequently (high ncalls)
- Take significant time (high tottime/cumtime)
- Are within your control (not in system libraries)

**Exercise:** List the top 5 functions by cumulative time from your results.

---

## 5. Memory Profiling

### Step 5.1: Run Memory Profiler

```bash
python3 -m memory_profiler profile_memory.py
```

This will show memory usage line-by-line.

### Step 5.2: Interpret Memory Results

Look for lines with high memory increment:

```
Line    Mem usage    Increment   Line Contents
================================================
50      45.2 MiB     0.0 MiB    all_users = cursor.fetchall()
51      52.8 MiB     7.6 MiB    usernames = [user['username'] for user in all_users]
```

**Analysis:**
- Line 51 allocates 7.6 MB
- For only 50 users, that's ~150 KB per user
- This doesn't scale!

### Step 5.3: Calculate Memory Efficiency

Formula: **Memory per record = Total increment / Number of records**

For the example above:
- 7.6 MB / 50 users = 156 KB per user
- A user object should be ~1-2 KB maximum
- **Finding:** 100x more memory than necessary!

---

## 6. Load Testing

### Step 6.1: Start Locust Web Interface

Terminal 1:
```bash
python3 app.py
```

Terminal 2:
```bash
locust -f locustfile.py --host=http://localhost:5000
```

Terminal 3:
```bash
# Open browser
http://localhost:8089
```

### Step 6.2: Configure Load Test

In the Locust web UI:
- Number of users: `10`
- Spawn rate: `2` (users per second)
- Host: `http://localhost:5000`

Click "Start swarming"

### Step 6.3: Observe Metrics

Watch these key metrics:
1. **RPS (Requests per second):** How many requests the app handles
2. **Response times:** P50, P95, P99 percentiles
3. **Failures:** Any errors or timeouts

**Expected Results (Original App):**
- RPS: ~5-10
- P95 response time: ~300-500ms
- Some failures at higher load

### Step 6.4: Export Results

After the test:
1. Click "Download Data" tab
2. Download "Statistics"
3. Save as `load_test_original.csv`

### Step 6.5: Run Headless Test

For automated testing:

```bash
locust -f locustfile.py \
  --host=http://localhost:5000 \
  --headless \
  -u 10 \
  -r 2 \
  -t 60s \
  --html=load_test_original.html
```

This generates a nice HTML report.

---

## 7. Identifying Bottlenecks

### Step 7.1: Combine Profiling Data

Create a bottleneck analysis document:

```markdown
# Bottleneck Analysis

## 1. N+1 Query Problem
- **Location:** app.py:85 (get_users function)
- **Evidence:** 51 queries for 50 users (from logs/profiling)
- **Impact:** 70% of response time
- **Priority:** HIGH

## 2. Inefficient Hashing
- **Location:** app.py:32 (inefficient_hash)
- **Evidence:** 42ms for single hash (CPU profiling)
- **Impact:** 95% of user creation time
- **Priority:** MEDIUM-HIGH

... continue for each bottleneck ...
```

### Step 7.2: Categorize by Type

**Database Issues:**
- N+1 queries
- Missing indexes
- Full table scans

**CPU Issues:**
- Inefficient algorithms
- Unnecessary computations
- Poor library usage

**Memory Issues:**
- Loading too much data
- Memory leaks
- Inefficient data structures

### Step 7.3: Prioritize by Impact

Use this formula to prioritize:

**Impact Score = Frequency × Duration × Scalability Factor**

Where:
- Frequency: How often this code runs (1-10)
- Duration: How long it takes (1-10)
- Scalability: How it grows with data (1-10)

Higher scores = higher priority.

---

## 8. Implementing Optimizations

### Step 8.1: Fix N+1 Query Problem

**Before:**
```python
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

for user in users:
    cursor.execute('SELECT COUNT(*) FROM posts WHERE user_id = ?', (user['id'],))
    post_count = cursor.fetchone()[0]
```

**After:**
```python
cursor.execute('''
    SELECT u.*, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id
''')
users = cursor.fetchall()
```

**Test the fix:**
```bash
# Count queries before and after
# You should see 1 query instead of 51
```

### Step 8.2: Optimize Hashing

**Before:**
```python
def inefficient_hash(password):
    result = password
    for i in range(1000):
        result = hashlib.sha256(result.encode()).hexdigest()
    return result
```

**After:**
```python
def efficient_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()
```

**Test the fix:**
```bash
time python3 -c "
from app import inefficient_hash
import time
start = time.time()
inefficient_hash('test')
print(f'Time: {time.time() - start:.4f}s')
"
```

### Step 8.3: Add Database Indexes

**Add to init_db():**
```python
cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
```

**Verify indexes:**
```bash
sqlite3 users_optimized.db "SELECT name FROM sqlite_master WHERE type='index';"
```

### Step 8.4: Optimize Search

**Before:**
```python
all_users = cursor.fetchall()  # Load all data
usernames = [u['username'] for u in all_users]
found = inefficient_search(usernames, query)  # O(n²) search
```

**After:**
```python
cursor.execute('SELECT * FROM users WHERE username = ?', (query,))
results = cursor.fetchall()
```

---

## 9. Validating Improvements

### Step 9.1: Re-run Load Tests

```bash
# Start optimized app
python3 app_optimized.py

# Run same load test
locust -f locustfile.py \
  --host=http://localhost:5000 \
  --headless \
  -u 10 \
  -r 2 \
  -t 60s \
  --html=load_test_optimized.html
```

### Step 9.2: Compare Results

Create comparison table:

```
Metric                | Original | Optimized | Improvement
----------------------|----------|-----------|------------
Avg Response Time     | 250ms    | 75ms      | 70%
P95 Response Time     | 450ms    | 130ms     | 71%
RPS                   | 8        | 28        | 250%
Database Queries      | 51       | 1         | 98%
```

### Step 9.3: Automated Comparison

```bash
bash compare_performance.sh
```

This script runs both versions and calculates improvements automatically.

### Step 9.4: Validate Correctness

Important: Ensure optimizations don't break functionality!

```bash
# Test all endpoints still work
curl http://localhost:5000/users | jq '.[]| .post_count'
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass"}'
```

---

## 10. Writing the Report

### Step 10.1: Report Structure

Your report should include:

1. **Executive Summary**
   - Brief overview of findings
   - Key performance improvements
   - Summary of recommendations

2. **Methodology**
   - Tools used
   - Testing approach
   - Environment details

3. **Baseline Metrics**
   - Initial performance measurements
   - Resource utilization
   - Identified issues

4. **Bottleneck Analysis**
   - Each bottleneck detailed
   - Evidence from profiling
   - Impact assessment

5. **Optimizations**
   - Changes made
   - Before/after comparison
   - Code examples

6. **Results**
   - Performance improvements
   - Scalability testing
   - Trade-offs discussed

7. **Recommendations**
   - Future optimizations
   - Production considerations
   - Best practices

### Step 10.2: Include Graphs and Charts

Create visualizations:
- Response time comparison (bar chart)
- Throughput improvement (line graph)
- Resource usage (before/after)

Tools: Excel, Google Sheets, or Python matplotlib

### Step 10.3: Document Trade-offs

For each optimization, discuss:
- **Benefits:** What improved
- **Costs:** Added complexity, memory, etc.
- **Alternatives:** Other approaches considered
- **Recommendations:** When to use this optimization

### Step 10.4: Self-Assessment Checklist

- [ ] All bottlenecks identified and documented
- [ ] Profiling data included as evidence
- [ ] Before/after metrics clearly shown
- [ ] Code changes explained
- [ ] Results validated with load tests
- [ ] Trade-offs discussed
- [ ] Future recommendations provided
- [ ] Report is well-organized and readable

---

## Tips for Success

### General Tips

1. **Measure everything:** Never optimize without data
2. **One change at a time:** Isolate the impact of each fix
3. **Document as you go:** Don't wait until the end
4. **Be systematic:** Follow a consistent process
5. **Consider real-world scenarios:** Think about production use

### Common Pitfalls to Avoid

1. **Premature optimization:** Profile first!
2. **Ignoring correctness:** Optimizations must preserve functionality
3. **Over-optimization:** Know when to stop
4. **Poor documentation:** Explain your reasoning
5. **Ignoring trade-offs:** Every optimization has costs

### Time Management

- Day 1-2: Setup, exploration, baseline testing
- Day 3-4: Profiling and bottleneck identification
- Day 5-6: Implement optimizations
- Day 7: Validation and report writing

---

## Additional Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- Locust: https://docs.locust.io/
- Python cProfile: https://docs.python.org/3/library/profile.html

### Tutorials
- Database optimization: https://use-the-index-luke.com/
- Python performance: https://wiki.python.org/moin/PythonSpeed
- SQL query tuning: https://www.sqlite.org/queryplanner.html

### Tools
- cProfile: Built-in CPU profiler
- memory_profiler: Line-by-line memory profiling
- Locust: Load testing framework
- sqlite3: Database inspection

---

## Getting Help

If you encounter issues:

1. **Check the logs:** Look for error messages
2. **Review profiling data:** Numbers don't lie
3. **Test incrementally:** Isolate the problem
4. **Consult documentation:** Often has the answer
5. **Ask for help:** Use course forums or office hours

---

## Submission Checklist

Before submitting:

- [ ] All code files included
- [ ] Requirements.txt is complete
- [ ] README is comprehensive
- [ ] Performance analysis report included
- [ ] Profiling results included
- [ ] Load test reports included
- [ ] Code is commented
- [ ] .gitignore excludes unnecessary files
- [ ] Repository is clean and organized

---

## Conclusion

This assignment teaches you to:
- Systematically analyze performance
- Use professional profiling tools
- Identify and fix real bottlenecks
- Validate your improvements
- Communicate technical findings

These skills are essential for building scalable, efficient applications in industry.

Good luck!

---

**Course:** SENG468 - Software Performance Engineering  
**Assignment:** Assignment 1 - Performance Measurement & Profiling  
**Term:** Spring 2026