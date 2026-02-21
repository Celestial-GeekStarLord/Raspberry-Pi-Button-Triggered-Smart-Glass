import RPi.GPIO as GPIO
import time
import subprocess
import os
import signal

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button_1 = 17   
button_2 = 27   

GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("🔘 Button controller ready")

process = None   

try:
    while True:

        # START BUTTON 
        if GPIO.input(button_1) == GPIO.HIGH:
            if process is None:
                print("▶ Starting detect.py ...")

                process = subprocess.Popen([
                    "/home/pi/Python-3.9.18/yoloo/yolo_env/bin/python",
                    "/home/pi/Python-3.9.18/yoloo/detect.py"
                ])

            else:
                print("⚠ detect.py already running")

            time.sleep(0.5)  # debounce

        # STOP BUTTON 
        if GPIO.input(button_2) == GPIO.HIGH:
            if process is not None:
                print("⏹ Stopping detect.py ...")

                os.kill(process.pid, signal.SIGINT)  # like Ctrl+C
                process = None

            else:
                print("⚠ No running process to stop")

            time.sleep(0.5)  # debounce

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nCleaning up...")
    GPIO.cleanup()