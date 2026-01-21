#!/bin/bash

# Performance Testing Script
# This script runs the complete performance analysis pipeline

echo "========================================="
echo "Performance Measurement & Profiling"
echo "SENG468 Assignment 1"
echo "========================================="
echo ""

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 2: Initialize database
echo "Step 2: Initializing database..."
python3 -c "from app import init_db; init_db(); print('✓ Database initialized')"
echo ""

# Step 3: Run memory profiling
echo "Step 3: Running memory profiling..."
echo "This will analyze memory usage patterns..."
python3 -m memory_profiler profile_memory.py > profiling_results_memory.txt 2>&1
echo "✓ Memory profiling completed"
echo "  Results saved to: profiling_results_memory.txt"
echo ""

# Step 4: Run CPU profiling
echo "Step 4: Running CPU profiling..."
echo "This will analyze CPU usage and identify bottlenecks..."
python3 profile_cpu.py
echo "✓ CPU profiling completed"
echo "  Results saved to: profiling_results_cpu.txt"
echo ""

# Step 5: Instructions for load testing
echo "Step 5: Load Testing Instructions"
echo "========================================="
echo "To run load tests with Locust:"
echo ""
echo "1. Start the application in one terminal:"
echo "   python3 app.py"
echo ""
echo "2. In another terminal, run one of these options:"
echo ""
echo "   Option A - Web UI (recommended for visual analysis):"
echo "   locust -f locustfile.py --host=http://localhost:5000"
echo "   Then open http://localhost:8089 in your browser"
echo ""
echo "   Option B - Headless mode (for automated testing):"
echo "   locust -f locustfile.py --host=http://localhost:5000 --headless -u 10 -r 2 -t 60s --html=load_test_report.html"
echo "   This runs with 10 users, spawn rate of 2/sec, for 60 seconds"
echo ""
echo "========================================="
echo ""

echo "Performance analysis preparation completed!"
echo ""
echo "Generated files:"
echo "  - profiling_results_cpu.txt (CPU profiling results)"
echo "  - profiling_results_memory.txt (Memory profiling results)"
echo ""
echo "Next steps:"
echo "  1. Review profiling results"
echo "  2. Run load tests following instructions above"
echo "  3. Analyze bottlenecks"
echo "  4. Implement optimizations"
echo "  5. Re-run tests to measure improvements"
