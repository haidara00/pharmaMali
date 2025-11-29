# waitress_server.py
import os
import sys
from waitress import serve

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmagestion.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

if __name__ == '__main__':
    # Windows-friendly startup banner
    print("="*60)
    print("🚀 Starting PharmaGestion Production Server...")
    print("📍 Server running on: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("="*60)

    # Read port and threads from environment for flexibility
    port = int(os.environ.get('PORT', 8000))
    threads = int(os.environ.get('WAITRESS_THREADS', 4))
    host = os.environ.get('HOST', '0.0.0.0')

    # Windows: ensure static files are served by Django/WhiteNoise
    # (WhiteNoise is enabled in settings.py)

    # Waitress does not support HTTPS directly; use a reverse proxy for SSL in production
    serve(
        application,
        host=host,
        port=port,
        threads=threads,
        url_prefix=''
    )