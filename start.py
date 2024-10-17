import os
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_backend():
    print("Starting FastAPI backend...")
    subprocess.Popen(["python", "api/main.py"])

def start_frontend():
    print("Starting Vite development server...")
    subprocess.Popen(["npm", "run", "dev"])

if __name__ == "__main__":
    # Check if node_modules exists, if not, run npm install
    if not os.path.exists("node_modules"):
        print("Installing dependencies...")
        subprocess.run(["npm", "install"])

    # Start the backend
    start_backend()

    # Give the backend a moment to start
    time.sleep(2)

    # Start the frontend
    start_frontend()

    print("\nBoth servers are now running!")
    print(f"FastAPI backend is available at: {os.getenv('VITE_API_URL', 'http://localhost:8000')}")
    print("Vite development server will provide the frontend URL in the console output above.")
    print("\nPress CTRL+C to stop both servers.")

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")