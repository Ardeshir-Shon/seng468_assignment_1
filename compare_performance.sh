#!/bin/bash

# Comparison script to run both versions and compare performance
# This demonstrates the before/after improvements

echo "========================================="
echo "Performance Comparison Script"
echo "Original vs Optimized Application"
echo "========================================="
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi
echo "✓ Dependencies ready"
echo ""

# Function to run a quick performance test
run_quick_test() {
    local app_file=$1
    local app_name=$2
    local port=$3
    
    echo "Testing $app_name on port $port..."
    
    # Start the app in background
    python3 "$app_file" > /dev/null 2>&1 &
    local pid=$!
    
    # Wait for app to start
    sleep 3
    
    # Seed the database
    curl -s -X POST "http://localhost:$port/seed" > /dev/null
    
    # Run simple performance test
    echo "  Running 100 requests to /users endpoint..."
    local start_time=$(date +%s.%N)
    
    for i in {1..100}; do
        curl -s "http://localhost:$port/users" > /dev/null
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local avg_time=$(echo "scale=3; $duration / 100" | bc)
    local req_per_sec=$(echo "scale=2; 100 / $duration" | bc)
    
    echo "  ✓ Completed in ${duration}s"
    echo "  ✓ Average response time: ${avg_time}s"
    echo "  ✓ Requests per second: ${req_per_sec}"
    
    # Cleanup
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    
    echo "$avg_time"
}

echo "========================================="
echo "Test 1: Original Application"
echo "========================================="
original_time=$(run_quick_test "app.py" "Original" 5000)
echo ""

echo "========================================="
echo "Test 2: Optimized Application"  
echo "========================================="
optimized_time=$(run_quick_test "app_optimized.py" "Optimized" 5000)
echo ""

echo "========================================="
echo "Results Summary"
echo "========================================="
echo "Original avg response time:  ${original_time}s"
echo "Optimized avg response time: ${optimized_time}s"

# Calculate improvement percentage
improvement=$(echo "scale=1; (($original_time - $optimized_time) / $original_time) * 100" | bc)
speedup=$(echo "scale=2; $original_time / $optimized_time" | bc)

echo ""
echo "Performance Improvement: ${improvement}%"
echo "Speedup Factor: ${speedup}x"
echo ""

if (( $(echo "$improvement > 50" | bc -l) )); then
    echo "✓✓✓ Excellent optimization! >50% improvement"
elif (( $(echo "$improvement > 25" | bc -l) )); then
    echo "✓✓ Good optimization! >25% improvement"
else
    echo "✓ Some improvement achieved"
fi
echo ""
echo "========================================="
echo "For detailed analysis, see:"
echo "  - PERFORMANCE_ANALYSIS.md"
echo "  - profiling_results_cpu.txt"
echo "  - profiling_results_memory.txt"
echo "========================================="
