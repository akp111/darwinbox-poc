#!/bin/bash

# Load Testing Setup and Execution Script for DarwinBox POC

set -e  # Exit on any error

echo "🚀 DarwinBox POC Load Testing Setup"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install load testing dependencies if needed
echo "📦 Installing load testing dependencies..."
if [ -f ".venv/bin/python" ]; then
    .venv/bin/pip install -r load_test_requirements.txt
else
    pip install -r load_test_requirements.txt
fi

echo "✅ Dependencies installed successfully"
echo ""

# Check if API server is running
echo "🔍 Checking API server status..."
if curl -s http://127.0.0.1:4000/ > /dev/null; then
    echo "✅ API server is running"
else
    echo "⚠️  API server not detected. Please start it first:"
    echo "   python -m src.main"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🧪 Available Load Test Scenarios:"
echo ""
echo "1. Light Load (5 users, 30s)    - Basic functionality test"
echo "2. Medium Load (10 users, 60s)  - Standard load test"  
echo "3. Heavy Load (25 users, 120s)  - Stress test"
echo "4. Spike Test (50 users, 30s)   - Peak load simulation"
echo "5. Custom Load                   - Define your own parameters"
echo ""

read -p "Select test scenario (1-5): " choice

case $choice in
    1)
        echo "🔄 Running Light Load Test..."
        if [ -f ".venv/bin/python" ]; then
            .venv/bin/python load_test.py --users 5 --duration 30 --delay 0.2
        else
            python3 load_test.py --users 5 --duration 30 --delay 0.2
        fi
        ;;
    2)
        echo "🔄 Running Medium Load Test..."
        if [ -f ".venv/bin/python" ]; then
            .venv/bin/python load_test.py --users 10 --duration 60 --delay 0.1
        else
            python3 load_test.py --users 10 --duration 60 --delay 0.1
        fi
        ;;
    3)
        echo "🔄 Running Heavy Load Test..."
        if [ -f ".venv/bin/python" ]; then
            .venv/bin/python load_test.py --users 25 --duration 120 --delay 0.05
        else
            python3 load_test.py --users 25 --duration 120 --delay 0.05
        fi
        ;;
    4)
        echo "🔄 Running Spike Test..."
        if [ -f ".venv/bin/python" ]; then
            .venv/bin/python load_test.py --users 50 --duration 30 --delay 0.02
        else
            python3 load_test.py --users 50 --duration 30 --delay 0.02
        fi
        ;;
    5)
        echo "📝 Custom Load Test Configuration:"
        read -p "Number of concurrent users: " users
        read -p "Test duration (seconds): " duration
        read -p "Delay between requests (seconds): " delay
        echo "🔄 Running Custom Load Test..."
        if [ -f ".venv/bin/python" ]; then
            .venv/bin/python load_test.py --users $users --duration $duration --delay $delay
        else
            python3 load_test.py --users $users --duration $duration --delay $delay
        fi
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Load test completed! Check the results above."
echo ""
echo "💡 Tips for better testing:"
echo "   - Ensure database has sample data (run: python scripts/populate_data.py)"
echo "   - Monitor system resources during tests"
echo "   - Test different load patterns for comprehensive analysis"
