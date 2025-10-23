"""
ChatApp Startup Script
Main entry point for running the application
"""

from server import app, init_database
from admin_routes import admin_bp
import os

# Register admin blueprint
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('user_uploads', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('extracted_files', exist_ok=True)

    # Initialize database
    print("Initializing database...")
    init_database()
    print("Database initialized!")

    print("\n" + "="*60)
    print("ChatApp Server Starting...")
    print("="*60)
    print("\nServer URL: http://localhost:5000")
    print("Frontend: http://localhost:5000/")
    print("Admin Dashboard: http://localhost:5000/admin/dashboard")
    print("\nDefault Credentials:")
    print("  Admin: admin / admin123")
    print("  User:  testuser / password")
    print("\nAPI Documentation: See API_DOCS.md")
    print("="*60 + "\n")

    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
