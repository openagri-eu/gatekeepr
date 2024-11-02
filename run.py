import uvicorn
import psutil
import time
import sqlalchemy
from sqlalchemy import create_engine, text
import subprocess

from app.config.settings import Settings

settings = Settings()


def kill_existing_process(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            try:
                process = psutil.Process(conn.pid)
                process.kill()
                print(f"Killed process {conn.pid} on port {port}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue


def check_database_connection():
    """Check if the database is up and accessible."""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful.")
    except sqlalchemy.exc.OperationalError:
        print("Could not connect to the database. Retrying...")
        time.sleep(3)
        check_database_connection()


def run_migrations():
    """Run migrations using Alembic or equivalent tool."""
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], check=True)
        if result.returncode == 0:
            print("Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print("Error running migrations:", e)
        exit(1)


if __name__ == "__main__":
    port = 8001
    kill_existing_process(port)
    check_database_connection()
    run_migrations()
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
