import uvicorn
import psutil


def kill_existing_process(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            try:
                process = psutil.Process(conn.pid)
                process.kill()
                print(f"Killed process {conn.pid} on port {port}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue


if __name__ == "__main__":
    port = 8001
    kill_existing_process(port)
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
