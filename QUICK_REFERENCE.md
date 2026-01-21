# SENG468 Assignment 1 - Quick Reference Guide

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated profiling
bash run_tests.sh

# 3. Start original app
python3 app.py

# 4. Start optimized app
python3 app_optimized.py

# 5. Compare performance
bash compare_performance.sh
```

## Load Testing Commands

### Interactive Mode (Web UI)
```bash
# Terminal 1: Start app
python3 app.py

# Terminal 2: Start Locust
locust -f locustfile.py --host=http://localhost:5000

# Terminal 3: Open browser
http://localhost:8089
```

### Headless Mode (Automated)
```bash
# Light load test (10 users, 60 seconds)
locust -f locustfile.py --host=http://localhost:5000 --headless -u 10 -r 2 -t 60s --html=report.html

# Heavy load test (50 users, 120 seconds)
locust -f locustfile.py --host=http://localhost:5000 --headless -u 50 -r 5 -t 120s --html=report_heavy.html
```

## Profiling Commands

### CPU Profiling
```bash
python3 profile_cpu.py
# Results: profiling_results_cpu.txt
```

### Memory Profiling
```bash
python3 -m memory_profiler profile_memory.py > profiling_results_memory.txt
# Results: profiling_results_memory.txt
```

## Testing Endpoints

### Seed Database
```bash
curl -X POST http://localhost:5000/seed
```

### Test Endpoints
```bash
# List users
curl http://localhost:5000/users

# Get specific user
curl http://localhost:5000/users/1

# Create user
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"pass123"}'

# Search users
curl "http://localhost:5000/search?q=user1"

# Heavy operation
curl http://localhost:5000/heavy

# List posts
curl http://localhost:5000/posts
```

## Performance Bottlenecks

### 1. N+1 Query Problem
- **File:** app.py, line ~85
- **Fix:** Use JOIN with GROUP BY (see app_optimized.py)
- **Impact:** 90% reduction in queries

### 2. Inefficient Hashing
- **File:** app.py, line ~32
- **Fix:** Single hash iteration (see app_optimized.py)
- **Impact:** 99% faster hashing

### 3. Poor Search Algorithm
- **File:** app.py, line ~164
- **Fix:** SQL WHERE clause (see app_optimized.py)
- **Impact:** 90% faster search

### 4. Missing Indexes
- **File:** app.py, init_db()
- **Fix:** Add indexes on foreign keys (see app_optimized.py)
- **Impact:** 80% faster JOINs

### 5. Unnecessary Computation
- **File:** app.py, line ~196
- **Fix:** Use generator expression (see app_optimized.py)
- **Impact:** 60% faster execution

## Key Metrics to Track

### Response Times
- Average response time
- P50, P95, P99 percentiles
- Maximum response time

### Throughput
- Requests per second (RPS)
- Transactions per second (TPS)

### Resource Utilization
- CPU usage percentage
- Memory usage (MB)
- Database query count

### Reliability
- Error rate percentage
- Timeout count
- Success rate

## Expected Results

### Original App (Baseline)
- GET /users: ~200-300ms
- POST /users: ~800-1000ms
- RPS: ~5-10
- Database queries for /users: 51

### Optimized App
- GET /users: ~50-100ms (70% faster)
- POST /users: ~10-20ms (98% faster)
- RPS: ~20-40 (3-4x increase)
- Database queries for /users: 1 (98% reduction)

## File Structure

```
├── app.py                      # Original app with bottlenecks
├── app_optimized.py            # Optimized version
├── locustfile.py               # Load testing scenarios
├── profile_cpu.py              # CPU profiling script
├── profile_memory.py           # Memory profiling script
├── run_tests.sh                # Automated test runner
├── compare_performance.sh      # Performance comparison
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
├── PERFORMANCE_ANALYSIS.md     # Detailed analysis report
├── TUTORIAL.md                 # Step-by-step tutorial
└── QUICK_REFERENCE.md          # This file
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Database Locked
```bash
# Remove database files and reinitialize
rm users.db users_optimized.db
python3 -c "from app import init_db; init_db()"
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Important Notes

1. **Always profile before optimizing** - Don't guess where the bottleneck is
2. **Make one change at a time** - Isolate the impact of each optimization
3. **Measure after each change** - Validate your improvements
4. **Consider trade-offs** - Document complexity vs performance gains
5. **Test correctness** - Ensure optimizations don't break functionality

## Additional Resources

- **Flask Docs:** https://flask.palletsprojects.com/
- **Locust Docs:** https://docs.locust.io/
- **Python Profiling:** https://docs.python.org/3/library/profile.html
- **SQLite Optimization:** https://www.sqlite.org/optoverview.html

## Quick Tips

### Viewing Profiling Results
```bash
# Sort by cumulative time
python3 -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('cumulative').print_stats(20)"

# Sort by total time
python3 -c "import pstats; p = pstats.Stats('profile.prof'); p.sort_stats('tottime').print_stats(20)"
```

### Database Inspection
```bash
# View tables
sqlite3 users.db ".tables"

# View schema
sqlite3 users.db ".schema users"

# View indexes
sqlite3 users.db "SELECT name, sql FROM sqlite_master WHERE type='index';"

# Count records
sqlite3 users.db "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM posts;"
```

### Quick Performance Test
```bash
# Time a single request
time curl -s http://localhost:5000/users > /dev/null

# Run 100 requests
for i in {1..100}; do curl -s http://localhost:5000/users > /dev/null; done
```

---

**Course:** SENG468 - Software Performance Engineering  
**Assignment:** Assignment 1 - Performance Measurement & Profiling  
**Term:** Spring 2026
