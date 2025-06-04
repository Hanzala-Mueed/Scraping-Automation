import pyautogui
import time
import os

# Configure pyautogui
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to stop
pyautogui.PAUSE = 0.1      # Small pause between actions

def drag_drop_file(source_x, source_y, dest_x, dest_y, drag_duration=1.0):
    """
    Drag and drop a file from source coordinates to destination coordinates
    
    Args:
        source_x, source_y: Starting position (file location)
        dest_x, dest_y: Ending position (drop location)
        drag_duration: How long the drag takes in seconds
    """
    print(f"Dragging from ({source_x}, {source_y}) to ({dest_x}, {dest_y})")
    
    # Move to source position
    pyautogui.moveTo(source_x, source_y, duration=0.5)
    time.sleep(0.3)
    
    # Click to select the file first
    pyautogui.click()
    time.sleep(0.2)
    
    # Press and hold mouse button
    pyautogui.mouseDown(button='left')
    time.sleep(0.3)  # Hold longer to ensure drag starts
    
    # Drag to destination with slower movement
    pyautogui.moveTo(dest_x, dest_y, duration=max(drag_duration, 1.5))
    time.sleep(0.2)
    
    # Release mouse button
    pyautogui.mouseUp(button='left')
    time.sleep(0.3)
    
    print("✓ Drag and drop completed")

def drag_drop_file_alternative(source_x, source_y, dest_x, dest_y, drag_duration=2.0):
    """
    Alternative drag and drop method using pyautogui.drag()
    
    Args:
        source_x, source_y: Starting position (file location)
        dest_x, dest_y: Ending position (drop location)
        drag_duration: How long the drag takes in seconds
    """
    print(f"Alternative drag from ({source_x}, {source_y}) to ({dest_x}, {dest_y})")
    
    # Move to source position and click to select
    pyautogui.moveTo(source_x, source_y, duration=0.5)
    time.sleep(0.3)
    pyautogui.click()
    time.sleep(0.5)  # Give time for file selection
    
    # Calculate relative movement
    dx = dest_x - source_x
    dy = dest_y - source_y
    
    # Use pyautogui.drag() which handles the mouse down/up automatically
    pyautogui.drag(dx, dy, duration=drag_duration, button='left')
    time.sleep(0.5)
    
    print("✓ Alternative drag and drop completed")

def drag_drop_file_macos(source_x, source_y, dest_x, dest_y, drag_duration=2.0):
    """
    macOS-optimized drag and drop method
    
    Args:
        source_x, source_y: Starting position (file location)
        dest_x, dest_y: Ending position (drop location)
        drag_duration: How long the drag takes in seconds
    """
    print(f"macOS drag from ({source_x}, {source_y}) to ({dest_x}, {dest_y})")
    
    # Move to source position
    pyautogui.moveTo(source_x, source_y, duration=0.5)
    time.sleep(0.5)
    
    # Single click to ensure file is selected
    pyautogui.click()
    time.sleep(0.3)
    
    # Move slightly to ensure we're on the file
    pyautogui.moveTo(source_x, source_y, duration=0.1)
    time.sleep(0.2)
    
    # Press and hold with longer initial delay
    pyautogui.mouseDown(button='left')
    time.sleep(0.5)  # Longer hold for macOS
    
    # Slow drag to destination
    pyautogui.moveTo(dest_x, dest_y, duration=max(drag_duration, 2.0))
    time.sleep(0.3)
    
    # Release
    pyautogui.mouseUp(button='left')
    time.sleep(0.5)
    
    print("✓ macOS drag and drop completed")

def drag_drop_file_macos_v2(source_x, source_y, dest_x, dest_y, drag_duration=2.0):
    """
    Alternative macOS drag method with drag threshold
    """
    print(f"macOS v2 drag from ({source_x}, {source_y}) to ({dest_x}, {dest_y})")
    
    # Move to source and select file
    pyautogui.moveTo(source_x, source_y, duration=0.5)
    time.sleep(0.3)
    pyautogui.click()
    time.sleep(0.5)
    
    # Start drag with mouse down
    pyautogui.mouseDown(button='left')
    time.sleep(0.2)
    
    # Move a small amount first to initiate drag (drag threshold)
    pyautogui.moveRel(5, 5, duration=0.2)
    time.sleep(0.3)
    
    # Now move to destination
    pyautogui.moveTo(dest_x, dest_y, duration=drag_duration)
    time.sleep(0.2)
    
    # Release
    pyautogui.mouseUp(button='left')
    time.sleep(0.5)
    
    print("✓ macOS v2 drag and drop completed")

def drag_drop_file_macos_v3(source_x, source_y, dest_x, dest_y, drag_duration=2.0):
    """
    macOS method using dragTo function
    """
    print(f"macOS v3 drag from ({source_x}, {source_y}) to ({dest_x}, {dest_y})")
    
    # Move to source and select file
    pyautogui.moveTo(source_x, source_y, duration=0.5)
    time.sleep(0.3)
    pyautogui.click()
    time.sleep(0.5)
    
    # Use dragTo which might work better on macOS
    pyautogui.dragTo(dest_x, dest_y, duration=drag_duration, button='left')
    time.sleep(0.5)
    
    print("✓ macOS v3 drag and drop completed")

def get_mouse_position():
    """Get current mouse position - useful for finding coordinates"""
    x, y = pyautogui.position()
    print(f"Current mouse position: ({x}, {y})")
    return x, y

def interactive_drag_drop():
    """Interactive mode - click to set source and destination"""
    print("=== Interactive Drag & Drop ===")
    print("Instructions:")
    print("1. Position your mouse over the FILE you want to drag")
    print("2. Press ENTER")
    print("3. Position your mouse over the DESTINATION")
    print("4. Press ENTER")
    print("5. Choose drag method")
    print("6. Watch the magic happen!")
    print("\nMove mouse to top-left corner to emergency stop")
    
    # Get source position
    input("\nPosition mouse over SOURCE file and press ENTER...")
    # 1320, 70
    source_x, source_y = get_mouse_position()
    
    # Get destination position
    input("Position mouse over DESTINATION and press ENTER...")
    dest_x, dest_y = get_mouse_position()
    
    # Choose method
    print("\nChoose drag method:")
    print("1. Standard method (improved)")
    print("2. Alternative method (pyautogui.drag)")
    print("3. macOS method")
    print("4. macOS v2 (with drag threshold)")
    print("5. macOS v3 (dragTo method)")
    method = input("Enter choice (1-5): ").strip()
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    # Perform drag and drop
    if method == "5":
        drag_drop_file_macos_v3(source_x, source_y, dest_x, dest_y)
    elif method == "4":
        drag_drop_file_macos_v2(source_x, source_y, dest_x, dest_y)
    elif method == "3":
        drag_drop_file_macos(source_x, source_y, dest_x, dest_y)
    elif method == "2":
        drag_drop_file_alternative(source_x, source_y, dest_x, dest_y)
    else:
        drag_drop_file(source_x, source_y, dest_x, dest_y)

def preset_drag_drop():
    """Use preset coordinates - modify these for your screen"""
    print("=== Preset Drag & Drop ===")
    
    # Example coordinates - CHANGE THESE FOR YOUR SCREEN
    file_positions = [
        (1320, 70),  # File 1 position
    ]
    
    destination = (834, 395)  # Folder or destination position
    
    print("Current preset positions:")
    print(f"Files: {file_positions}")
    print(f"Destination: {destination}")
    print("\nTo find coordinates, use interactive mode first!")
    
    choice = input("Use these presets? (y/n): ")
    if choice.lower() != 'y':
        return
    
    # Choose method
    print("\nChoose drag method:")
    print("1. Standard method")
    print("2. Alternative method")
    print("3. macOS method")
    print("4. macOS v2 (with drag threshold)")
    print("5. macOS v3 (dragTo method)")
    method = input("Enter choice (1-5): ").strip()
    
    # Drag each file
    for i, (x, y) in enumerate(file_positions):
        print(f"\nDragging file {i+1}...")
        
        if method == "5":
            drag_drop_file_macos_v3(x, y, destination[0], destination[1])
        elif method == "4":
            drag_drop_file_macos_v2(x, y, destination[0], destination[1])
        elif method == "3":
            drag_drop_file_macos(x, y, destination[0], destination[1])
        elif method == "2":
            drag_drop_file_alternative(x, y, destination[0], destination[1])
        else:
            drag_drop_file(x, y, destination[0], destination[1])
            
        time.sleep(1)  # Wait between files

def mouse_position_finder():
    """Helper to find coordinates on your screen"""
    print("=== Mouse Position Finder ===")
    print("Move your mouse around and press SPACE to get coordinates")
    print("Press ESC to exit")
    
    import keyboard
    
    try:
        while True:
            if keyboard.is_pressed('space'):
                x, y = pyautogui.position()
                print(f"Position: ({x}, {y})")
                time.sleep(0.5)  # Prevent spam
            elif keyboard.is_pressed('esc'):
                break
            time.sleep(0.1)
    except ImportError:
        print("Install keyboard library: pip install keyboard")
        print("Using basic mode...")
        
        for i in range(10):
            print(f"Position in {5-i//2} seconds...")
            time.sleep(0.5)
            x, y = pyautogui.position()
            print(f"Current position: ({x}, {y})")

def main():
    """Main menu"""
    print("🖱️  Mouse Cursor File Drag & Drop Script")
    print("=" * 40)
    
    try:
        while True:
            print("\nChoose an option:")
            print("1. Interactive drag & drop")
            print("2. Use preset coordinates")
            print("3. Find mouse positions")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                interactive_drag_drop()
            elif choice == '2':
                preset_drag_drop()
            elif choice == '3':
                mouse_position_finder()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
                
    except KeyboardInterrupt:
        print("\nScript stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if pyautogui is installed
    try:
        import pyautogui
        main()
    except ImportError:
        print("Please install required libraries:")
        print("pip install pyautogui")
        print("pip install keyboard  # Optional, for position finder")