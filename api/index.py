import os
import sys
import traceback

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from app import app
    handler = app
except Exception as e:
    tb = traceback.format_exc()
    from flask import Flask, jsonify
    app = Flask(__name__)
    handler = app

    @app.route("/", defaults={"path": ""}, methods=["GET", "POST", "OPTIONS"])
    @app.route("/<path:path>", methods=["GET", "POST", "OPTIONS"])
    def catch_all(path):
        return jsonify({
            "error": "Startup error in Vercel function",
            "exception": str(e),
            "traceback": tb
        }), 500
