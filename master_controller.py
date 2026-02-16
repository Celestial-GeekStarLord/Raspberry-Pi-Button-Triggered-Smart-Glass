#!/usr/bin/env python3
import RPi.GPIO as GPIO
import subprocess
import time
import os
import signal
import sys

# ========================
# GPIO SETUP
# ========================
BTN_MAIN = 17
BTN_BACK = 27
HOLD_TIME = 1.2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BTN_MAIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_BACK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# ========================
# SPEECH OUTPUT
# ========================
speech_process = None

def speak(text):
    global speech_process
    
    print(text)
    
    # Kill any ongoing speech
    if speech_process is not None:
        try:
            speech_process.kill()
        except:
            pass
    
    # Start new speech
    try:
        speech_process = subprocess.Popen(
            ['espeak', '-a', '200', '-s', '165', text, '--stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        subprocess.Popen(
            ['aplay'],
            stdin=speech_process.stdout,
            stderr=subprocess.DEVNULL
        )
        
        speech_process.stdout.close()
        time.sleep(len(text) * 0.05)  # Rough timing
        
    except Exception as e:
        print(f"Speech error: {e}")

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
    return "hold" if duration > HOLD_TIME else "tap"

# ========================
# SCRIPT PATHS
# ========================
BASE = "/home/pi/Python-3.9.18/yoloo"
INDOOR_ENV = f"{BASE}/env_in/bin/python"
YOLO_ENV = f"{BASE}/yolo_env/bin/python"
INDOOR_SCRIPT = f"{BASE}/indoorai.py"
YOLO_SCRIPT = f"{BASE}/detect.py"

# ========================
# MAIN LOOP
# ========================
def main():
    current_mode = "online"
    process = None
    
    speak("Assistant initialized")
    time.sleep(0.5)
    speak(f"{current_mode} mode")
    
    try:
        while True:
            # BACK BUTTON = stop running script
            if GPIO.input(BTN_BACK) == GPIO.HIGH:
                wait_press(BTN_BACK)
                
                if process is not None:
                    speak("Stopping")
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        process.wait(timeout=3)
                    except:
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        except:
                            pass
                    process = None
                    time.sleep(0.5)
                    speak(f"{current_mode} mode")
            
            # MAIN BUTTON
            if GPIO.input(BTN_MAIN) == GPIO.HIGH:
                action = wait_press(BTN_MAIN)
                
                # TAP = change mode
                if action == "tap" and process is None:
                    current_mode = "offline" if current_mode == "online" else "online"
                    speak(f"{current_mode} mode")
                
                # HOLD = start script
                elif action == "hold" and process is None:
                    if current_mode == "online":
                        speak("Starting assistant")
                        try:
                            process = subprocess.Popen(
                                [INDOOR_ENV, INDOOR_SCRIPT],
                                preexec_fn=os.setsid
                            )
                        except Exception as e:
                            speak("Failed to start")
                            print(f"Error: {e}")
                            process = None
                    else:
                        speak("Starting detection")
                        try:
                            process = subprocess.Popen(
                                [YOLO_ENV, YOLO_SCRIPT],
                                preexec_fn=os.setsid
                            )
                        except Exception as e:
                            speak("Failed to start")
                            print(f"Error: {e}")
                            process = None
            
            # Check if process died
            if process is not None and process.poll() is not None:
                speak("Script stopped")
                process = None
                time.sleep(0.5)
                speak(f"{current_mode} mode")
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    
    finally:
        if process is not None:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except:
                pass
        GPIO.cleanup()

if __name__ == "__main__":
    main()
