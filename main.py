"""Application launcher for backend and frontend services.

This module manages the lifecycle of both FastAPI backend and Streamlit frontend,
including process spawning, health checks, graceful shutdown, and signal handling.
"""

import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from threading import Event
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Configuration
ROOT = Path(__file__).resolve().parent
API_APP = "backend.interface.api.main:app"
STREAMLIT_ENTRY = ROOT / "frontend" / "app.py"

# Constants
HEALTH_CHECK_TIMEOUT = 25.0
HEALTH_CHECK_INTERVAL = 0.5
GRACEFUL_SHUTDOWN_WAIT = 0.5
PROCESS_POLL_INTERVAL = 0.5


def spawn_process(cmd: list[str], *, env: dict | None = None, cwd: str | None = None) -> subprocess.Popen:
    """Spawn a subprocess with appropriate platform-specific configuration.
    
    Args:
        cmd: Command and arguments to execute.
        env: Environment variables dictionary. If None, uses current environment.
        cwd: Working directory for the process.
        
    Returns:
        Popen instance representing the spawned process.
    """
    kwargs = {"env": env or os.environ.copy(), "cwd": cwd}
    
    if os.name != "nt":
        kwargs["preexec_fn"] = os.setsid
    
    return subprocess.Popen(cmd, **kwargs)


def terminate_process(process: subprocess.Popen) -> None:
    """Terminate a process gracefully, with fallback to force kill.
    
    Attempts graceful termination first, then forces kill if necessary.
    Handles both Windows and Unix systems appropriately.
    
    Args:
        process: The process to terminate.
    """
    if not process or process.poll() is not None:
        return
    
    try:
        if os.name == "nt":
            _terminate_windows(process)
        else:
            _terminate_unix(process)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


def _terminate_windows(process: subprocess.Popen) -> None:
    """Terminate process on Windows."""
    try:
        process.terminate()
        time.sleep(GRACEFUL_SHUTDOWN_WAIT)
        
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
                check=False,
            )
    except Exception:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False,
        )


def _terminate_unix(process: subprocess.Popen) -> None:
    """Terminate process on Unix-like systems."""
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        time.sleep(GRACEFUL_SHUTDOWN_WAIT)
        
        if process.poll() is None:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except Exception:
        process.terminate()


def wait_for_http_ready(url: str, timeout: float = HEALTH_CHECK_TIMEOUT, interval: float = HEALTH_CHECK_INTERVAL) -> bool:
    """Wait until a URL responds with a successful HTTP status code.
    
    Args:
        url: The URL to check.
        timeout: Maximum time to wait in seconds.
        interval: Time between checks in seconds.
        
    Returns:
        True if the URL becomes ready within timeout, False otherwise.
    """
    deadline = time.time() + timeout
    request = Request(url, headers={"User-Agent": "healthcheck"})
    
    while time.time() < deadline:
        try:
            with urlopen(request, timeout=3) as response:
                if 200 <= response.status < 300:
                    return True
        except (URLError, HTTPError):
            pass
        
        time.sleep(interval)
    
    return False


def run() -> None:
    """Main application entry point.
    
    Orchestrates the startup, monitoring, and shutdown of backend and frontend services.
    """
    env = os.environ.copy()
    
    # Configure ports
    backend_port = env.setdefault("PORT_BACKEND", "8000")
    frontend_port = env.setdefault("PORT_FRONTEND", "8501")
    
    # Build URLs
    backend_url = f"http://127.0.0.1:{backend_port}"
    frontend_url_127 = f"http://127.0.0.1:{frontend_port}"
    frontend_url_localhost = f"http://localhost:{frontend_port}"
    
    # Set environment variables for services
    env["BACKEND_URL"] = backend_url
    env["ALLOWED_ORIGINS"] = f"{frontend_url_127},{frontend_url_localhost}"
    
    # Build commands
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        API_APP,
        "--host",
        "127.0.0.1",
        "--port",
        backend_port,
    ]
    
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(STREAMLIT_ENTRY),
        "--server.port",
        frontend_port,
        "--server.headless",
        "true",
        "--server.address",
        "127.0.0.1",
    ]
    
    # Start backend
    backend = spawn_process(backend_cmd, env=env, cwd=str(ROOT))
    
    if not wait_for_http_ready(f"{backend_url}/health", timeout=HEALTH_CHECK_TIMEOUT):
        print("Error: Backend failed to start or did not respond to health check.", file=sys.stderr)
        terminate_process(backend)
        sys.exit(1)
    
    # Start frontend
    frontend = spawn_process(frontend_cmd, env=env, cwd=str(ROOT))
    
    if not wait_for_http_ready(frontend_url_127, timeout=HEALTH_CHECK_TIMEOUT):
        print("Error: Frontend failed to start or did not respond.", file=sys.stderr)
        terminate_process(frontend)
        terminate_process(backend)
        sys.exit(1)
    
    # Open browser
    try:
        webbrowser.open(frontend_url_127)
    except Exception:
        pass
    
    # Setup shutdown handling
    shutdown_flag = Event()
    
    def shutdown_handler(*_) -> None:
        """Handle shutdown signals and cleanup processes."""
        if shutdown_flag.is_set():
            os._exit(1)
        
        shutdown_flag.set()
        print("\nShutting down services...")
        terminate_process(frontend)
        terminate_process(backend)
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown_handler)
    
    # Monitor processes
    try:
        while not shutdown_flag.is_set():
            frontend_exited = frontend.poll() is not None
            backend_exited = backend.poll() is not None
            
            if frontend_exited or backend_exited:
                exit_codes = []
                if frontend_exited:
                    exit_codes.append(frontend.returncode or 0)
                if backend_exited:
                    exit_codes.append(backend.returncode or 0)
                
                shutdown_handler()
                sys.exit(max(exit_codes) if exit_codes else 0)
            
            time.sleep(PROCESS_POLL_INTERVAL)
    
    except KeyboardInterrupt:
        shutdown_handler()
    finally:
        if not shutdown_flag.is_set():
            shutdown_handler()


if __name__ == "__main__":
    run()
