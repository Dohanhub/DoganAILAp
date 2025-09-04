"""
DoganAI Compliance Platform - FastAPI Backend Only
NO STREAMLIT - Preparing for React Native + Expo Frontend
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from src.main import app

# FastAPI backend ready for React Native frontend
if __name__ == "__main__":
    import uvicorn
    print("🚀 DoganAI Platform Backend Starting...")
    print("📱 Ready for React Native + Expo Frontend")
    print("🚫 NO STREAMLIT - As agreed")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )