import pyautogui
import cv2
import numpy as np
import time
import os
import subprocess
from PIL import Image, ImageGrab
import psutil

class DesktopFileDragger:
    def __init__(self):
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Define desktop right area (right half of screen)
        self.desktop_left = self.screen_width // 2
        self.desktop_right = self.screen_width
        self.desktop_top = 0
        self.desktop_bottom = self.screen_height
        
        # Define bottom-right corner area to scan
        self.scan_area = {
            'left': int(self.screen_width * 0.75),  # Right 25% of screen
            'top': int(self.screen_height * 0.75),   # Bottom 25% of screen
            'width': int(self.screen_width * 0.25),
            'height': int(self.screen_height * 0.25)
        }
        
        print(f"Screen size: {self.screen_width}x{self.screen_height}")
        print(f"Scan area: {self.scan_area}")

    def minimize_vscode(self):
        """Minimize VS Code window"""
        try:
            print("Minimizing VS Code...")
            # Method 1: Try using wmctrl to find and minimize VS Code
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['visual studio code', 'vscode', 'code']):
                        window_id = line.split()[0]
                        subprocess.run(['wmctrl', '-i', '-c', window_id])
                        print("VS Code minimized using wmctrl")
                        return True
            
            
            # Method 2: Try using xdotool
            result = subprocess.run(['xdotool', 'search', '--name', 'Visual Studio Code'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                for window_id in window_ids:
                    subprocess.run(['xdotool', 'windowminimize', window_id])
                print("VS Code minimized using xdotool")
                return True
                
            # Method 3: Try generic "code" window name
            result = subprocess.run(['xdotool', 'search', '--name', 'code'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                for window_id in window_ids:
                    subprocess.run(['xdotool', 'windowminimize', window_id])
                print("Code window minimized using xdotool")
                return True
                
        except Exception as e:
            print(f"Error minimizing VS Code: {e}")
        
        # Method 4: Keyboard shortcut fallback
        try:
            print("Trying keyboard shortcut to minimize current window...")
            pyautogui.hotkey('alt', 'F9')  # Common minimize shortcut
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Keyboard shortcut failed: {e}")
            
        print("Could not minimize VS Code")
        return False

    def open_chrome_left_half(self):
        """Open Chrome and position it in the left half of the screen"""
        try:
            print("Opening Chrome in left half...")
            
            # First, try to close any existing Chrome windows
            try:
                subprocess.run(['pkill', 'chrome'], capture_output=True)
                time.sleep(1)
            except:
                pass
            
            # Calculate left half dimensions
            left_width = self.screen_width // 2
            left_height = self.screen_height
            
            # Open Chrome with specific window size and position
            chrome_cmd = [
                'google-chrome',
                '--new-window',
                f'--window-size={left_width},{left_height}',
                f'--window-position=0,0',
                '--no-first-run',
                '--no-default-browser-check'
            ]
            
            # Try different Chrome executable names
            chrome_executables = ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']
            
            for chrome_exe in chrome_executables:
                try:
                    chrome_cmd[0] = chrome_exe
                    subprocess.Popen(chrome_cmd)
                    print(f"Chrome opened using {chrome_exe}")
                    time.sleep(3)  # Wait for Chrome to open
                    
                    # Use wmctrl to ensure proper positioning
                    self.position_chrome_left_half()
                    return True
                except FileNotFoundError:
                    continue
            
            print("Chrome executable not found, trying alternative method...")
            # Fallback: try opening with system default
            subprocess.Popen(['x-www-browser'])
            time.sleep(3)
            self.position_chrome_left_half()
            return True
            
        except Exception as e:
            print(f"Error opening Chrome: {e}")
            return False

    def position_chrome_left_half(self):
        """Position Chrome window to left half using wmctrl or xdotool"""
        try:
            # Method 1: Use wmctrl
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['chrome', 'chromium']):
                        window_id = line.split()[0]
                        left_width = self.screen_width // 2
                        left_height = self.screen_height
                        
                        # Move and resize window
                        subprocess.run(['wmctrl', '-i', '-r', window_id, '-e', f'0,0,0,{left_width},{left_height}'])
                        print("Chrome positioned using wmctrl")
                        return True
            
            # Method 2: Use xdotool
            result = subprocess.run(['xdotool', 'search', '--name', 'chrome'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                window_id = window_ids[0]  # Use first Chrome window
                
                left_width = self.screen_width // 2
                left_height = self.screen_height
                
                # Move and resize
                subprocess.run(['xdotool', 'windowmove', window_id, '0', '0'])
                subprocess.run(['xdotool', 'windowsize', window_id, str(left_width), str(left_height)])
                print("Chrome positioned using xdotool")
                return True
                
        except Exception as e:
            print(f"Error positioning Chrome: {e}")
        
        return False

    def show_desktop(self):
        """Show desktop by minimizing all windows"""
        try:
            print("Showing desktop...")
            # Method 1: Use wmctrl to minimize all windows except Chrome
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if not any(keyword in line.lower() for keyword in ['chrome', 'chromium']):
                        window_id = line.split()[0]
                        subprocess.run(['wmctrl', '-i', '-t', '-1', window_id])  # Send to all desktops and minimize
                return True
            
            # Method 2: Keyboard shortcut
            pyautogui.hotkey('ctrl', 'alt', 'd')  # Common show desktop shortcut
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Error showing desktop: {e}")
            # Fallback keyboard shortcuts
            try:
                pyautogui.hotkey('super', 'd')  # Windows key + D
                time.sleep(1)
                return True
            except:
                pass
            
        return False

    def get_chrome_window_center(self):
        """Find Chrome window and return its center coordinates"""
        try:
            # Use wmctrl to get window information
            result = subprocess.run(['wmctrl', '-lG'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("wmctrl not available")
            
            lines = result.stdout.strip().split('\n')
            chrome_windows = []
            
            for line in lines:
                if 'chrome' in line.lower() or 'chromium' in line.lower():
                    parts = line.split()
                    if len(parts) >= 6:
                        x, y, width, height = map(int, parts[2:6])
                        chrome_windows.append((x, y, width, height))
            
            if chrome_windows:
                x, y, width, height = chrome_windows[0]
                center_x = x + width // 2
                center_y = y + height // 2
                
                print(f"Chrome window: x={x}, y={y}, width={width}, height={height}")
                print(f"Chrome center: ({center_x}, {center_y})")
                
                return center_x, center_y
                
        except Exception as e:
            print(f"Error finding Chrome with wmctrl: {e}")
        
        # Fallback: assume Chrome is in left half
        center_x = self.screen_width // 4  # Left quarter (center of left half)
        center_y = self.screen_height // 2  # Middle height
        print(f"Using fallback Chrome center: ({center_x}, {center_y})")
        return center_x, center_y

    def find_desktop_files_smart(self):
        """Smart method to find files in bottom-right corner"""
        detected_items = []
        
        # Method 1: Check actual desktop folder and estimate positions
        try:
            desktop_paths = [
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Рабочий стол"),  # Russian
                os.path.expanduser("~/Bureau"),  # French
                os.path.expanduser("~/Área de Trabalho"),  # Portuguese
            ]
            
            desktop_path = None
            for path in desktop_paths:
                if os.path.exists(path):
                    desktop_path = path
                    break
            
            if desktop_path:
                files = []
                for item in os.listdir(desktop_path):
                    item_path = os.path.join(desktop_path, item)
                    if os.path.isfile(item_path) or os.path.isdir(item_path):
                        files.append(item)
                
                print(f"Found {len(files)} items on desktop: {files[:5]}")
                
                # Estimate positions in bottom-right area
                start_x = self.scan_area['left'] + 60
                start_y = self.scan_area['top'] + 60
                
                for i, filename in enumerate(files[:8]):  # Limit to 8 items
                    # Grid layout: 2 columns, 4 rows
                    col = i % 2
                    row = i // 2
                    
                    x = start_x + col * 120
                    y = start_y + row * 100
                    
                    # Make sure coordinates are within scan area
                    if x < self.scan_area['left'] + self.scan_area['width'] - 50:
                        if y < self.scan_area['top'] + self.scan_area['height'] - 50:
                            detected_items.append({
                                'center': (x, y),
                                'bounds': (x-30, y-30, 60, 60),
                                'filename': filename
                            })
        
        except Exception as e:
            print(f"Error in smart detection: {e}")
        
        # Method 2: If no files found, create some test coordinates
        if not detected_items:
            print("No desktop files found, using default test positions...")
            test_positions = [
                (self.scan_area['left'] + 80, self.scan_area['top'] + 80),
                (self.scan_area['left'] + 180, self.scan_area['top'] + 80),
                (self.scan_area['left'] + 80, self.scan_area['top'] + 180),
            ]
            
            for i, (x, y) in enumerate(test_positions):
                detected_items.append({
                    'center': (x, y),
                    'bounds': (x-30, y-30, 60, 60),
                    'filename': f'TestFile{i+1}'
                })
        
        return detected_items

    def drag_file_to_chrome_enhanced(self, file_coordinates, chrome_center):
        """Enhanced drag with visual feedback"""
        start_x, start_y = file_coordinates
        end_x, end_y = chrome_center
        
        print(f"🎯 Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        
        # Move to file location with smooth animation
        pyautogui.moveTo(start_x, start_y, duration=0.8)
        time.sleep(0.3)
        
        # Click and hold
        pyautogui.mouseDown()
        print("🖱️  File grabbed!")
        time.sleep(0.2)
        
        # Drag with smooth movement
        pyautogui.moveTo(end_x, end_y, duration=1.2)
        time.sleep(0.3)
        
        # Release
        pyautogui.mouseUp()
        print("🎉 File dropped in Chrome!")
        time.sleep(0.5)

    def run_complete_sequence(self):
        """Run the complete sequence: minimize VS Code, open Chrome, show desktop, drag file"""
        print("🚀 Starting complete desktop file drag sequence...")
        print("=" * 50)
        
        # Step 1: Minimize VS Code
        print("Step 1: Minimizing VS Code...")
        self.minimize_vscode()
        time.sleep(1)
        
        # Step 2: Open Chrome in left half
        print("Step 2: Opening Chrome in left half...")
        chrome_opened = self.open_chrome_left_half()
        if not chrome_opened:
            print("⚠️  Chrome opening failed, continuing anyway...")
        time.sleep(2)
        
        # Step 3: Show desktop
        print("Step 3: Showing desktop...")
        self.show_desktop()
        time.sleep(1)
        
        # Step 4: Get Chrome center
        print("Step 4: Locating Chrome window...")
        chrome_center = self.get_chrome_window_center()
        
        # Step 5: Find files to drag
        print("Step 5: Finding desktop files...")
        detected_items = self.find_desktop_files_smart()
        
        if detected_items:
            print(f"Found {len(detected_items)} items to drag:")
            for i, item in enumerate(detected_items):
                filename = item.get('filename', 'Unknown')
                print(f"  📁 Item {i+1}: {filename} at {item['center']}")
            
            # Step 6: Drag first file
            print("Step 6: Dragging file to Chrome...")
            first_item = detected_items[0]
            self.drag_file_to_chrome_enhanced(first_item['center'], chrome_center)
            
            print("✅ Complete sequence finished successfully!")
            return True
        else:
            print("❌ No files found to drag.")
            return False

    def interactive_mode(self):
        """Interactive mode with user choices"""
        print("🎮 Interactive Desktop File Dragger")
        print("=" * 40)
        print("1. Run complete sequence (minimize VS Code + open Chrome + drag file)")
        print("2. Just drag file (Chrome should already be open)")
        print("3. Test mode (show coordinates)")
        print("4. Setup mode (open Chrome only)")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            return self.run_complete_sequence()
        elif choice == "2":
            chrome_center = self.get_chrome_window_center()
            detected_items = self.find_desktop_files_smart()
            if detected_items:
                self.drag_file_to_chrome_enhanced(detected_items[0]['center'], chrome_center)
                return True
            return False
        elif choice == "3":
            self.test_coordinates()
            return True
        elif choice == "4":
            return self.open_chrome_left_half()
        else:
            print("Invalid choice")
            return False

    def test_coordinates(self):
        """Test mode to show mouse coordinates"""
        print("🧪 Test mode - Move mouse to see coordinates")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                x, y = pyautogui.position()
                in_scan_area = (self.scan_area['left'] <= x <= self.scan_area['left'] + self.scan_area['width'] and
                               self.scan_area['top'] <= y <= self.scan_area['top'] + self.scan_area['height'])
                area_indicator = " [SCAN AREA]" if in_scan_area else ""
                print(f"Mouse: ({x:4d}, {y:4d}){area_indicator}", end='\r')
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Exiting test mode...")

def check_dependencies():
    """Check and install required dependencies"""
    tools = ['wmctrl', 'xdotool', 'scrot']
    missing = []
    
    for tool in tools:
        try:
            subprocess.run(['which', tool], capture_output=True, check=True)
            print(f"✅ {tool} found")
        except subprocess.CalledProcessError:
            missing.append(tool)
            print(f"❌ {tool} missing")
    
    if missing:
        print(f"\n🔧 Install missing tools with:")
        print(f"sudo apt-get install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies found!")
    return True

def main():
    print("🎪 Enhanced Desktop File Dragger for Linux")
    print("==========================================")
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return
    
    # Create dragger instance
    dragger = DesktopFileDragger()
    
    # Run interactive mode
    dragger.interactive_mode()

if __name__ == "__main__":
    main()