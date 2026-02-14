import RPi.GPIO as GPIO
import time

# Use BCM numbering (matches GPIO 17 and GPIO 27 labels)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define your pins
button_1 = 17
button_2 = 27

# Setup pins as INPUT with internal PULL-DOWN resistors
# This ensures the pin stays at 0V until the button connects it to 3.3V
GPIO.setup(button_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Testing buttons... Press Ctrl+C to stop.")

try:
    while True:
        # Check Button 1
        if GPIO.input(button_1) == GPIO.HIGH:
            print("Button on GPIO 17 was pushed!")
            time.sleep(0.2) # Simple debounce
            
        # Check Button 2
        if GPIO.input(button_2) == GPIO.HIGH:
            print("Button on GPIO 27 was pushed!")
            time.sleep(0.2) # Simple debounce
            
        time.sleep(0.01) # Small delay to save CPU power

except KeyboardInterrupt:
    print("\nCleaning up...")
    GPIO.cleanup()