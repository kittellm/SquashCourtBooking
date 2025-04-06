import os
import time
import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
CLUBLOCKER_USERNAME = os.getenv("CLUBLOCKER_USERNAME")
CLUBLOCKER_PASSWORD = os.getenv("CLUBLOCKER_PASSWORD")

def format_line(text="", width=80, symbol="-"):
    """Format a line with centered text and padding"""
    if text:
        return f" {text} ".center(width, symbol)
    return symbol * width

class SquashBooking:
    def __init__(self, show_browser=False, test_mode=False, verbose=False):
        self.test_mode = test_mode
        self.verbose = verbose
        self.driver = None
        self.wait = None
        self.show_browser = show_browser
        
    def start_browser(self):
        """Initialize the browser with appropriate options"""
        chrome_options = Options()
        if not self.show_browser:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self):
        """Log in to the ClubLocker website"""
        print("\n=== Step 1: Login ===")
        login_url = "https://clublocker.com/login"
        print(f"Navigating to login page: {login_url}")
        self.driver.get(login_url)
        time.sleep(5)
        
        print("Entering credentials...")
        self.driver.find_element(By.ID, "login").send_keys(CLUBLOCKER_USERNAME)
        self.driver.find_element(By.ID, "loginpass").send_keys(CLUBLOCKER_PASSWORD)
        login_button = self.driver.find_element(By.XPATH, "//div[contains(@class, 'login-btn')]/button[@type='submit']")
        login_button.click()
        time.sleep(5)
        print("Login complete. Page title:", self.driver.title)
        
    def check_existing_bookings(self, target_date):
        """Check if there are any existing bookings on the target date"""
        print(f"\n=== Checking for existing bookings on {target_date} ===")
        
        # Click the "My Reservations" button to switch to reservations view
        try:
            reservations_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'My Reservations')]]"))
            )
            reservations_button.click()
            time.sleep(2)  # Wait for the view to switch
            
            # Check both upcoming and past reservations
            booking_elements = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'row')]//div[contains(@class, 'date-and-time')]"
            )
            
            for element in booking_elements:
                date_element = element.find_element(By.CLASS_NAME, "date")
                time_element = element.find_element(By.CLASS_NAME, "time")
                
                booking_date = date_element.text
                booking_time = time_element.text
                
                # Convert the date format from "Thu, Apr 10" to match our target date format
                try:
                    booking_date_obj = datetime.datetime.strptime(booking_date, "%a, %b %d")
                    # Set the year to match our target date
                    booking_date_obj = booking_date_obj.replace(year=datetime.datetime.strptime(target_date, "%Y-%m-%d").year)
                    
                    if booking_date_obj.strftime("%Y-%m-%d") == target_date:
                        print(f"Found existing booking: {booking_date} at {booking_time}")
                        return True
                except Exception as e:
                    print(f"Error parsing booking date: {e}")
                    continue
            
            print("No existing bookings found for this date")
            return False
            
        except Exception as e:
            print(f"Error checking existing bookings: {e}")
            return False
        finally:
            # Try to switch back to grid view using the "All Reservations" button
            try:
                all_reservations_button = self.driver.find_elements(
                    By.XPATH, 
                    "//button[.//span[contains(text(), 'All Reservations')]]"
                )
                if all_reservations_button:
                    self.driver.execute_script("arguments[0].click();", all_reservations_button[0])
                    time.sleep(2)  # Wait for the view to switch back
            except Exception as e:
                # This is not critical, so we just log it and continue
                print("Note: Could not switch back to grid view - continuing anyway")

    def navigate_to_date(self, booking_date, org_id):
        """Navigate to the booking page for the specified date"""
        print(f"\n=== Step 2: Navigating to booking date {booking_date} ===")
        booking_url = f"https://clublocker.com/organizations/{org_id}/reservations/{booking_date}/grid"
        print(f"Navigating to booking page: {booking_url}")
        self.driver.get(booking_url)
        time.sleep(5)
        
        # Check for existing bookings before proceeding
        if self.check_existing_bookings(booking_date):
            print("\n" + format_line("Found existing booking for this date!", symbol="!"))
            return False
        return True
        
    def check_slot_availability(self, court_number, time_slot):
        """Check if a specific slot is available for booking"""
        print(f"\n=== Step 3: Checking availability for Court {court_number} at {time_slot} ===")
        desired_start_time = time_slot.split(" - ")[0]
        
        # Get all slots for the desired court
        court_slots = self.driver.find_elements(
            By.XPATH,
            f"//div[contains(@class, 'courts-container-inner')]"
            f"/div[contains(@class, 'column slots')][{court_number}]"
            f"//usq-reservation-grid-slot//div[contains(@class, 'slot')]"
        )
        
        print(f"Found {len(court_slots)} total slots on court {court_number}")
        
        # Find the slot with matching start time
        for slot in court_slots:
            title = slot.get_attribute('title')
            classes = slot.get_attribute('class')
            
            # Split the title to get the time range
            title_lines = title.split('\n')
            if len(title_lines) > 0:
                slot_time_range = title_lines[0]
                slot_start_time = slot_time_range.split(" - ")[0]
                
                if slot_start_time == desired_start_time:
                    print(f"\nFound slot at {desired_start_time}:")
                    print(f"  Status: {'Available' if 'slot open' in classes else 'Not Available'}")
                    print(f"  Details: {slot_time_range}")
                    
                    if "slot open" in classes:
                        print("  [AVAILABLE] This slot is available for booking!")
                        return slot
                    else:
                        print("  [UNAVAILABLE] This slot is not available")
                        return None
        
        print(f"\n[NOT FOUND] No slot found for Court {court_number} at {time_slot}")
        return None
        
    def attempt_booking(self, slot):
        """Attempt to book the specified slot"""
        print(f"\n=== Step 4: Attempting to book slot ===")
        
        # Highlight the slot before clicking
        self.driver.execute_script("arguments[0].style.border='3px solid red'", slot)
        time.sleep(2)
        
        slot.click()
        time.sleep(3)

        if self.test_mode:
            print("TEST MODE: Would click on Save to confirm the booking.")
            return True
            
        try:
            xpath_save = "//button[.//span[contains(text(), 'Save')]]"
            if self.verbose:
                print("Locating Save button with XPath:", xpath_save)
            
            save_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_save)))
            print("Save button found and is clickable")
            save_button.click()
            print("[SUCCESS] Booking confirmed!")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"[ERROR] Error during booking: {str(e)}")
            return False
            
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Squash Booking Script")
    parser.add_argument("--advance_days", type=int, default=4, help="Days in advance to book")
    parser.add_argument("--desired_court_number", type=int, default=1, help="Desired court number")
    parser.add_argument("--desired_time_slot", type=str, help="Desired time slot text")
    parser.add_argument("--organization_id", type=str, default="10515", help="Organization ID")
    parser.add_argument("--booking_date", type=str, help="Override computed booking date (YYYY-MM-DD)")
    parser.add_argument("--test", action="store_true", help="Run in test (dry-run) mode")
    parser.add_argument("--verbose", action="store_true", help="Show verbose debugging output")
    parser.add_argument("--show_browser", action="store_true", help="Show browser window during booking")
    args = parser.parse_args()

    # Initialize the booking system
    booking = SquashBooking(
        show_browser=args.show_browser,
        test_mode=args.test,
        verbose=args.verbose
    )
    
    try:
        # Start browser and login
        booking.start_browser()
        booking.login()
        
        # Determine booking date
        if args.booking_date:
            booking_date = args.booking_date
        else:
            booking_date = (datetime.datetime.today() + datetime.timedelta(days=args.advance_days)).strftime('%Y-%m-%d')
            
        # Navigate to the booking page
        booking.navigate_to_date(booking_date, args.organization_id)
        
        # Check slot availability
        slot = booking.check_slot_availability(args.desired_court_number, args.desired_time_slot)
        if slot:
            # Attempt to book if available
            success = booking.attempt_booking(slot)
            if success:
                print("\nBooking successful! Press Enter to close the browser...")
                input()
        else:
            print("\nNo available slot found. Press Enter to close the browser...")
            input()
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
    finally:
        booking.close()

if __name__ == "__main__":
    main()
