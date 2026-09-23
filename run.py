import subprocess
import sys
import time


BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "8000"
FRONTEND_PORT = "8501"


def main():

    print()
    print("=" * 60)
    print("                 ⚖️  LEGALEASE AI")
    print("=" * 60)
    print("🚀 Starting LegalEase services...")
    print()


    # ========================================================
    # BACKEND
    # ========================================================

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "LegalEaseAPI.main:app",
        "--host",
        BACKEND_HOST,
        "--port",
        BACKEND_PORT,
        "--reload",
    ]

    print(
        f"⚙️  Backend  : "
        f"http://{BACKEND_HOST}:{BACKEND_PORT}"
    )

    backend_process = subprocess.Popen(
        backend_cmd
    )


    # Give FastAPI time to start.
    time.sleep(3)


    # ========================================================
    # FRONTEND
    # ========================================================

    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port",
        FRONTEND_PORT,
    ]

    print(
        f"🎨 Frontend : "
        f"http://localhost:{FRONTEND_PORT}"
    )

    frontend_process = subprocess.Popen(
        frontend_cmd
    )


    print()
    print("-" * 60)
    print("🟢 LegalEase is starting")
    print("🧠 AI Engine  : Gemini 3.6 Flash")
    print(
        "🔗 API Health : "
        "http://localhost:8000/health"
    )
    print(
        "🖥️  Web App    : "
        "http://localhost:8501"
    )
    print("-" * 60)
    print()
    print("Press Ctrl+C to stop LegalEase.")
    print()


    try:

        while True:

            time.sleep(1)


            if backend_process.poll() is not None:

                print(
                    "❌ Backend process stopped."
                )

                break


            if frontend_process.poll() is not None:

                print(
                    "❌ Frontend process stopped."
                )

                break


    except KeyboardInterrupt:

        print()
        print(
            "🛑 Shutting down LegalEase..."
        )


    finally:

        if backend_process.poll() is None:

            backend_process.terminate()


        if frontend_process.poll() is None:

            frontend_process.terminate()


        print(
            "✅ LegalEase services stopped."
        )


if __name__ == "__main__":
    main()