# -*- coding: utf-8 -*-

#!/usr/bin/env python
# run_scheduled_bookings.py

import argparse
import json
import datetime
import os
from squash_booking import SquashBooking

CONFIG_FILE = "booking_config.json"
ORG_ID = "10515"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def parse_args():
    parser = argparse.ArgumentParser(description="Run scheduled bookings.")
    parser.add_argument("--test", action="store_true", help="Run in test (dry-run) mode.")
    parser.add_argument("--verbose", action="store_true", help="Output detailed debug information.")
    parser.add_argument("--current_date", type=str, default=None, help="Simulated current date (YYYY-MM-DD)")
    parser.add_argument("--show_browser", action="store_true", help="Show browser window during booking")
    return parser.parse_args()

def format_line(text="", width=80, symbol="-"):
    # Returns a line with the text centered, padded with the symbol.
    if text:
        return f" {text} ".center(width, symbol)
    return symbol * width

def main():
    args = parse_args()
    config = load_config()
    
    # Determine current date (from parameter or system)
    if args.current_date:
        try:
            current_dt = datetime.datetime.strptime(args.current_date, "%Y-%m-%d")
        except Exception as e:
            print("Error parsing --current_date:", e)
            return
    else:
        current_dt = datetime.datetime.now()

    # For testing, our target booking is 5 days from now.
    target_date = current_dt.date() + datetime.timedelta(days=5)
    target_day_name = target_date.strftime("%A")
    
    # Print header info with formatting
    print("\n" + format_line("Scheduled Booking Runner Test Mode" if args.test else "Scheduled Booking Runner"))
    print(f"Simulated current date/time: {current_dt}")
    print(f"Target booking date (current + 5 days): {target_date} which is a {target_day_name}")
    
    final_schedule = config.get("final_schedule", {})
    day_schedule = final_schedule.get(target_day_name, [])
    if not day_schedule:
        print("\nNo booking schedule found for", target_day_name, "\nExiting.")
        return

    print("\n" + format_line(f"Booking Attempts for {target_day_name}"))
    print(f"Found {len(day_schedule)} time slots to attempt")
    
    # Initialize the booking system
    booking = SquashBooking(
        show_browser=args.show_browser,
        test_mode=args.test,
        verbose=args.verbose
    )
    
    try:
        # Start browser and login once
        booking.start_browser()
        booking.login()
        
        # Navigate to the target date once and check for existing bookings
        if not booking.navigate_to_date(target_date.strftime("%Y-%m-%d"), ORG_ID):
            print("\n" + format_line("Cannot proceed with booking - existing booking found", symbol="!"))
            return
        
        # Try each court/time combination
        for idx, entry in enumerate(day_schedule, start=1):
            court = entry["court"]
            timeslot = entry["time_slot"]
            print(f"\n[{idx}] Attempting booking:")
            print(f"   Court: {court}")
            print(f"   Time Slot: {timeslot}")
            
            # Check if slot is available
            slot = booking.check_slot_availability(court, timeslot)
            if slot:
                # Attempt to book if available
                success = booking.attempt_booking(slot)
                if success:
                    print("\n" + format_line("Booking successful!", symbol="*"))
                    break
            else:
                print(f"   Slot not available, trying next option...")
        
        if not success:
            print("\n" + format_line("No available slots found", symbol="!"))
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
    finally:
        booking.close()

if __name__ == "__main__":
    main()
