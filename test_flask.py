import subprocess
import time
import urllib.request
import sys
import os

def main():
    print("Starting Flask app...")
    # Run from the correct working directory so it finds the db and static files
    process = subprocess.Popen([sys.executable, "web_app.py"], cwd=os.path.join(os.getcwd(), "team_b_application"))
    time.sleep(4) # Wait for startup
    
    try:
        print("Testing dashboard route (GET /)...")
        response = urllib.request.urlopen("http://127.0.0.1:5000/")
        if response.status == 200:
            print("✅ Web app is running successfully! Received status 200.")
            html = response.read().decode('utf-8')
        else:
            print(f"❌ Web app returned status {response.status}")
            process.terminate()
            sys.exit(1)
            
        print("Testing exercise route (GET /exercises)...")
        response = urllib.request.urlopen("http://127.0.0.1:5000/exercises")
        if response.status == 200:
            print("✅ Exercises page is accessible.")
            
        print("Testing API route (GET /api/stats)...")
        response = urllib.request.urlopen("http://127.0.0.1:5000/api/stats")
        if response.status == 200:
            print("✅ API stats working.")
            
    except Exception as e:
        print(f"❌ Failed to connect to web app: {e}")
        process.terminate()
        sys.exit(1)
        
    print("Terminating Flask app...")
    process.terminate()
    print("✅ All web app tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
