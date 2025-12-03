"""WSGI entrypoint wrapper for deployment.

Expose a top-level `app` variable for WSGI servers and hosting platforms.
"""
from run import app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
