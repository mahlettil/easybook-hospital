"""WSGI entrypoint wrapper for deployment.

This file exposes a top-level `app` variable so hosting platforms
that look for `app.py` can import the Flask application object.
"""
from run import app


if __name__ == '__main__':
    # Optional local run for debugging
    app.run(debug=True, host='0.0.0.0', port=5000)
