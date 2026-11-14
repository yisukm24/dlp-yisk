import sys
import time
import os
import subprocess

target_file = sys.argv[1]
last_modified = 0
process = None

while True:
    try:
        current_modified = os.path.getmtime(target_file)
        if current_modified != last_modified:
            last_modified = current_modified
            if process:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process = subprocess.Popen(["py", target_file])
    except Exception:
        pass
    time.sleep(0.5)
