import RPi.GPIO as GPIO
import subprocess
import time
import os
import signal
import pyttsx3

# ========================
# GPIO SETUP
# ========================
BTN_MAIN = 17
BTN_BACK = 27

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BTN_MAIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_BACK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

HOLD_TIME = 1.2

# ========================
# SPEECH ENGINE
# ========================
tts = pyttsx3.init(driverName="espeak")
tts.setProperty("rate", 165)

def speak(text):
    print(text)
    tts.say(text)
    tts.runAndWait()

# ========================
# BUTTON DETECTION
# ========================
def wait_press(pin):
    while GPIO.input(pin) == GPIO.LOW:
        time.sleep(0.01)

    start = time.time()

    while GPIO.input(pin) == GPIO.HIGH:
        time.sleep(0.01)

    duration = time.time() - start

    if duration > HOLD_TIME:
        return "hold"
    else:
        return "tap"

# ========================
# SCRIPT PATHS
# ========================
BASE = "/home/pi/Python-3.9.18/yoloo"

INDOOR_ENV = f"{BASE}/env_in/bin/python"
YOLO_ENV   = f"{BASE}/yolo_env/bin/python"

INDOOR_SCRIPT = f"{BASE}/indoorai.py"
YOLO_SCRIPT   = f"{BASE}/detect.py"

# ========================
# MAIN LOOP
# ========================
current_mode = "online"
process = None

speak("Online mode")

try:
    while True:

        # BACK BUTTON: stop running process
        if GPIO.input(BTN_BACK) == GPIO.HIGH:
            wait_press(BTN_BACK)

            if process is not None:
                speak("Stopping")
                os.kill(process.pid, signal.SIGINT)
                process = None
                speak(f"{current_mode} mode")

        # MAIN BUTTON
        if GPIO.input(BTN_MAIN) == GPIO.HIGH:

            action = wait_press(BTN_MAIN)

            # -------- TAP = switch mode --------
            if action == "tap" and process is None:
                current_mode = "offline" if current_mode == "online" else "online"
                speak(f"{current_mode} mode")

            # -------- HOLD = launch script --------
            elif action == "hold" and process is None:

                if current_mode == "online":
                    speak("Starting assistant")
                    process = subprocess.Popen([INDOOR_ENV, INDOOR_SCRIPT])

                else:
                    speak("Starting detection")
                    process = subprocess.Popen([YOLO_ENV, YOLO_SCRIPT])

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()