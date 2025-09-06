
#!/bin/bash
echo "[🔧] Installing dependencies..."
pip install -r requirements.txt

echo "[🚀] Starting Streamlit Dashboard on http://localhost:8501 ..."
streamlit run ui/dashboard_ui.py
