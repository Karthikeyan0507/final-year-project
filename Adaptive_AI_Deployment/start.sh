#!/bin/bash

# Start the Flask Backend on port 5000 (background)
echo "🚀 Starting Backend Service on port 5000..."
python backend/app.py &

# Wait for 5 seconds to let the backend warm up
sleep 5

# Start the Streamlit Frontend on port 7860
echo "🎨 Starting Frontend UI on port 7860..."
streamlit run ui/dashboard.py --server.port 7860 --server.address 0.0.0.0
