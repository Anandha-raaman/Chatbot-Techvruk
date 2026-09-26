"""
Main entry point for Gemini Task Planner Agent application.
Runs the Flask web server.
"""
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"* Starting Gemini Task Planner Agent at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
