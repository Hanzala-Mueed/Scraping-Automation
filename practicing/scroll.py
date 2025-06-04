#python cursor movements

import pyautogui
import time

# Wait for 2 seconds before moving the mouse
time.sleep(2)

# Move the mouse to position (100, 200)
pyautogui.moveTo(100, 50, duration=10)  # duration is optional (in seconds)


# from pynput.mouse import Controller
# import time

# mouse = Controller()

# # Wait before moving
# time.sleep(2)

# # Move the mouse to (300, 400)
# mouse.position = (300, 400)



