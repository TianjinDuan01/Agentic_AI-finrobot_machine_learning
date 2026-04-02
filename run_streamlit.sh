#!/bin/bash
# Launch FinRobot Streamlit Web Interface

echo "🚀 Launching FinRobot Investment Decision System..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found, installing..."
    pip install streamlit
fi

# Launch Streamlit
echo "✅ Starting Web Interface..."
echo "📱 The browser will automatically open at http://localhost:8501"
echo ""
streamlit run streamlit_app.py
