#!/bin/bash
# Run all tests for NanoEditor

cd "$(dirname "$0")"

echo "Running NanoEditor Tests..."
echo "============================"
echo ""

# Run all tests
python3 -m pytest tests/ -v --tb=short 2>/dev/null || python3 -m unittest discover -s tests -p "test_*.py" -v

echo ""
echo "============================"
echo "Tests completed!"
