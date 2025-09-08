#!/usr/bin/env python3
"""
🚀 AI Job Autopilot - Main Application
Simplified, user-friendly automated job application system
"""

import sys
import os
from pathlib import Path
import streamlit as st

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def main():
    """Main application entry point"""
    # Page config will be set by the UI module
    
    # Check for required dependencies
    missing_deps = []
    required_modules = ['streamlit', 'pandas', 'plotly']
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        st.error(f"Missing required dependencies: {', '.join(missing_deps)}")
        st.info("Please run: pip install -r requirements.txt")
        return
    
    # Import and run the premium UI
    try:
        from ui.premium_ui import main as run_premium_ui
        run_premium_ui()
    except ImportError as e:
        st.error(f"Could not load Premium UI module: {e}")
        st.info("Falling back to standard UI...")
        # Fallback to standard UI
        try:
            from ui.modern_job_autopilot_ui import main as run_ui
            run_ui()
        except ImportError:
            st.error("No UI modules available")
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please check the logs for more details")

if __name__ == "__main__":
    main()