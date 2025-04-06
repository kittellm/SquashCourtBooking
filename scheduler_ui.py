# -*- coding: utf-8 -*-

#!/usr/bin/env python
# scheduler_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

CONFIG_FILE = "booking_config.json"
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---------------- Reference: Valid Timeslot Mappings ----------------
# These mappings convert a UI start time (from the ranking lists) into the full timeslot text.
# All bookings are 40 minutes long.

# For Courts 1-3 (7:00 AM to 8:20 PM)
COURT_GROUP_1 = {
    "7:00 AM": "7:00 AM - 7:40 AM",
    "7:40 AM": "7:40 AM - 8:20 AM",
    "8:20 AM": "8:20 AM - 9:00 AM",
    "9:00 AM": "9:00 AM - 9:40 AM",
    "9:40 AM": "9:40 AM - 10:20 AM",
    "10:20 AM": "10:20 AM - 11:00 AM",
    "11:00 AM": "11:00 AM - 11:40 AM",
    "11:40 AM": "11:40 AM - 12:20 PM",
    "12:20 PM": "12:20 PM - 1:00 PM",
    "1:00 PM": "1:00 PM - 1:40 PM",
    "1:40 PM": "1:40 PM - 2:20 PM",
    "2:20 PM": "2:20 PM - 3:00 PM",
    "3:00 PM": "3:00 PM - 3:40 PM",
    "3:40 PM": "3:40 PM - 4:20 PM",
    "4:20 PM": "4:20 PM - 5:00 PM",
    "5:00 PM": "5:00 PM - 5:40 PM",
    "5:40 PM": "5:40 PM - 6:20 PM",
    "6:20 PM": "6:20 PM - 7:00 PM",
    "7:00 PM": "7:00 PM - 7:40 PM",
    "7:40 PM": "7:40 PM - 8:20 PM",
    "8:20 PM": "8:20 PM - 9:00 PM"
}

# For Courts 4-7 (7:20 AM to 8:00 PM)
COURT_GROUP_2 = {
    "7:20 AM": "7:20 AM - 8:00 AM",
    "8:00 AM": "8:00 AM - 8:40 AM",
    "8:40 AM": "8:40 AM - 9:20 AM",
    "9:20 AM": "9:20 AM - 10:00 AM",
    "10:00 AM": "10:00 AM - 10:40 AM",
    "10:40 AM": "10:40 AM - 11:20 AM",
    "11:20 AM": "11:20 AM - 12:00 PM",
    "12:00 PM": "12:00 PM - 12:40 PM",
    "12:40 PM": "12:40 PM - 1:20 PM",
    "1:20 PM": "1:20 PM - 2:00 PM",
    "2:00 PM": "2:00 PM - 2:40 PM",
    "2:40 PM": "2:40 PM - 3:20 PM",
    "3:20 PM": "3:20 PM - 4:00 PM",
    "4:00 PM": "4:00 PM - 4:40 PM",
    "4:40 PM": "4:40 PM - 5:20 PM",
    "5:20 PM": "5:20 PM - 6:00 PM",
    "6:00 PM": "6:00 PM - 6:40 PM",
    "6:40 PM": "6:40 PM - 7:20 PM",
    "7:20 PM": "7:20 PM - 8:00 PM"
}

# ---------------- Helper Functions ----------------

def format_time(dt):
    """Format a datetime object to a time string without leading zeros."""
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    return f"{hour}:{dt.strftime('%M %p')}"

def generate_full_time_options():
    """Generate a full list of times in 20-minute increments from 7:00 AM to 8:20 PM."""
    times = []
    current = datetime.datetime.strptime("7:00 AM", "%I:%M %p")
    end = datetime.datetime.strptime("8:20 PM", "%I:%M %p")
    while current <= end:
        times.append(format_time(current))
        current += datetime.timedelta(minutes=20)
    return times

FULL_TIME_OPTIONS = generate_full_time_options()

def generate_time_slots(start_str, end_str):
    """
    Return a list of time slots (start times) in 20-minute intervals between start_str and end_str,
    inclusive of both endpoints.
    """
    try:
        # Parse the input times, handling both formats (with and without leading zeros)
        start_dt = datetime.datetime.strptime(start_str, "%I:%M %p")
        end_dt = datetime.datetime.strptime(end_str, "%I:%M %p")
    except Exception as e:
        messagebox.showerror("Error", "Time format error: " + str(e))
        return []
    if start_dt > end_dt:
        messagebox.showerror("Error", "Start time must be earlier than or equal to end time.")
        return []
    slots = []
    current = start_dt
    while current <= end_dt:
        # Format time without leading zeros
        hour = current.hour % 12
        if hour == 0:
            hour = 12
        time_str = f"{hour}:{current.strftime('%M %p')}"
        slots.append(time_str)
        current += datetime.timedelta(minutes=20)
    return slots

# ---------------- Config File Functions ----------------

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading config file: {e}")
            config = {}
        except Exception as e:
            print(f"Unexpected error loading config file: {e}")
            config = {}
    # Supply defaults if missing:
    if "active_days" not in config:
        # Default: Tuesdays, Thursdays, and Saturdays are active.
        config["active_days"] = {day: (day in ["Tuesday", "Thursday", "Saturday"]) for day in DAYS_OF_WEEK}
    if "weekday" not in config:
        default_weekday_start = "6:00 PM"
        default_weekday_end = "7:20 PM"
        config["weekday"] = {
            "start_time": default_weekday_start,
            "end_time": default_weekday_end,
            "time_ranking": generate_time_slots(default_weekday_start, default_weekday_end)
        }
    if "weekend" not in config:
        default_weekend_start = "9:00 AM"
        default_weekend_end = "11:00 AM"
        config["weekend"] = {
            "start_time": default_weekend_start,
            "end_time": default_weekend_end,
            "time_ranking": generate_time_slots(default_weekend_start, default_weekend_end)
        }
    if "court_ranking" not in config:
        config["court_ranking"] = [1, 2, 3, 4, 5, 6, 7]
    return config

def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise

# ---------------- UI Functions ----------------

def generate_weekday_slots():
    start = weekday_start_var.get()
    end = weekday_end_var.get()
    slots = generate_time_slots(start, end)
    weekday_listbox.delete(0, tk.END)
    for s in slots:
        weekday_listbox.insert(tk.END, s)

def generate_weekend_slots():
    start = weekend_start_var.get()
    end = weekend_end_var.get()
    slots = generate_time_slots(start, end)
    weekend_listbox.delete(0, tk.END)
    for s in slots:
        weekend_listbox.insert(tk.END, s)

def move_up_listbox(listbox):
    selection = listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    if idx == 0:
        return
    above_item = listbox.get(idx - 1)
    current_item = listbox.get(idx)
    listbox.delete(idx)
    listbox.delete(idx - 1)
    listbox.insert(idx - 1, current_item)
    listbox.insert(idx, above_item)
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(idx - 1)

def move_down_listbox(listbox):
    selection = listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    if idx >= listbox.size() - 1:
        return
    below_item = listbox.get(idx + 1)
    current_item = listbox.get(idx)
    listbox.delete(idx + 1)
    listbox.delete(idx)
    listbox.insert(idx, below_item)
    listbox.insert(idx + 1, current_item)
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(idx + 1)

def move_up_weekday():
    move_up_listbox(weekday_listbox)

def move_down_weekday():
    move_down_listbox(weekday_listbox)

def move_up_weekend():
    move_up_listbox(weekend_listbox)

def move_down_weekend():
    move_down_listbox(weekend_listbox)

def move_up_court():
    move_up_listbox(court_listbox)

def move_down_court():
    move_down_listbox(court_listbox)

def on_save():
    # First load existing config to preserve any data not in the UI
    config_data = load_config()
    
    # Update with current UI state
    # Save active days
    active_days = {day: var.get() for day, var in active_days_vars.items()}
    config_data["active_days"] = active_days

    # Save weekday settings
    weekday_slots = [weekday_listbox.get(i) for i in range(weekday_listbox.size())]
    config_data["weekday"] = {
        "start_time": weekday_start_var.get(),
        "end_time": weekday_end_var.get(),
        "time_ranking": weekday_slots
    }

    # Save weekend settings
    weekend_slots = [weekend_listbox.get(i) for i in range(weekend_listbox.size())]
    config_data["weekend"] = {
        "start_time": weekend_start_var.get(),
        "end_time": weekend_end_var.get(),
        "time_ranking": weekend_slots
    }

    # Save court ranking
    courts = []
    for i in range(court_listbox.size()):
        item_text = court_listbox.get(i)
        try:
            court_num = int(item_text.replace("Court", "").strip())
        except:
            continue
        courts.append(court_num)
    config_data["court_ranking"] = courts

    # Build final_schedule structure
    final_schedule = {}
    for day in DAYS_OF_WEEK:
        if not active_days.get(day, False):
            continue

        # Determine if day is weekend (Saturday/Sunday) or weekday.
        if day in ["Saturday", "Sunday"]:
            day_slots = weekend_slots
        else:
            day_slots = weekday_slots

        day_list = []
        for t in day_slots:
            for c in courts:
                if c <= 3:
                    mapping = COURT_GROUP_1
                else:
                    mapping = COURT_GROUP_2
                if t in mapping:
                    day_list.append({
                        "court": c,
                        "time_slot": mapping[t]
                    })
        final_schedule[day] = day_list

    config_data["final_schedule"] = final_schedule

    try:
        save_config(config_data)
        messagebox.showinfo("Saved", "Configuration saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def populate_ui_from_config(config_data):
    # Active days
    for day in DAYS_OF_WEEK:
        active_days_vars[day].set(config_data.get("active_days", {}).get(day, False))
    
    # Weekday settings
    weekday_start_var.set(config_data.get("weekday", {}).get("start_time", "6:00 PM"))
    weekday_end_var.set(config_data.get("weekday", {}).get("end_time", "7:20 PM"))
    generate_weekday_slots()
    weekday_ranking = config_data.get("weekday", {}).get("time_ranking", [])
    if weekday_ranking:
        weekday_listbox.delete(0, tk.END)
        for t in weekday_ranking:
            weekday_listbox.insert(tk.END, t)
    
    # Weekend settings
    weekend_start_var.set(config_data.get("weekend", {}).get("start_time", "9:00 AM"))
    weekend_end_var.set(config_data.get("weekend", {}).get("end_time", "11:00 AM"))
    generate_weekend_slots()
    weekend_ranking = config_data.get("weekend", {}).get("time_ranking", [])
    if weekend_ranking:
        weekend_listbox.delete(0, tk.END)
        for t in weekend_ranking:
            weekend_listbox.insert(tk.END, t)
    
    # Court ranking
    court_listbox.delete(0, tk.END)
    ranking = config_data.get("court_ranking", [1, 2, 3, 4, 5, 6, 7])
    for c in ranking:
        court_listbox.insert(tk.END, f"Court {c}")

# ---------------- Build the UI ----------------

root = tk.Tk()
root.title("Squash Booking Scheduler Configuration")

# ---- Active Days Frame ----
days_frame = ttk.LabelFrame(root, text="Active Days (Select the days you want bookings)")
days_frame.pack(padx=10, pady=5, fill="x")

active_days_vars = {}
for idx, day in enumerate(DAYS_OF_WEEK):
    var = tk.BooleanVar()
    active_days_vars[day] = var
    chk = ttk.Checkbutton(days_frame, text=day, variable=var)
    chk.grid(row=0, column=idx, padx=3, pady=3)

# ---- Weekday Time Settings Frame ----
weekday_frame = ttk.LabelFrame(root, text="Weekday Time Settings")
weekday_frame.pack(padx=10, pady=5, fill="x")

weekday_start_var = tk.StringVar()
weekday_end_var = tk.StringVar()

ttk.Label(weekday_frame, text="Start Time:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
weekday_start_cb = ttk.Combobox(weekday_frame, textvariable=weekday_start_var, state="readonly", width=10)
weekday_start_cb["values"] = FULL_TIME_OPTIONS
weekday_start_cb.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(weekday_frame, text="End Time:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
weekday_end_cb = ttk.Combobox(weekday_frame, textvariable=weekday_end_var, state="readonly", width=10)
weekday_end_cb["values"] = FULL_TIME_OPTIONS
weekday_end_cb.grid(row=0, column=3, padx=5, pady=5)

ttk.Button(weekday_frame, text="Generate Weekday Slots", command=generate_weekday_slots).grid(row=0, column=4, padx=5, pady=5)

ttk.Label(weekday_frame, text="Weekday Time Ranking:").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="e")
weekday_listbox = tk.Listbox(weekday_frame, height=5, exportselection=False)
weekday_listbox.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

weekday_button_frame = ttk.Frame(weekday_frame)
weekday_button_frame.grid(row=1, column=4, padx=5, pady=5)
ttk.Button(weekday_button_frame, text="Move Up", command=move_up_weekday).pack(fill="x", pady=2)
ttk.Button(weekday_button_frame, text="Move Down", command=move_down_weekday).pack(fill="x", pady=2)

# ---- Weekend Time Settings Frame ----
weekend_frame = ttk.LabelFrame(root, text="Weekend Time Settings")
weekend_frame.pack(padx=10, pady=5, fill="x")

weekend_start_var = tk.StringVar()
weekend_end_var = tk.StringVar()

ttk.Label(weekend_frame, text="Start Time:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
weekend_start_cb = ttk.Combobox(weekend_frame, textvariable=weekend_start_var, state="readonly", width=10)
weekend_start_cb["values"] = FULL_TIME_OPTIONS
weekend_start_cb.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(weekend_frame, text="End Time:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
weekend_end_cb = ttk.Combobox(weekend_frame, textvariable=weekend_end_var, state="readonly", width=10)
weekend_end_cb["values"] = FULL_TIME_OPTIONS
weekend_end_cb.grid(row=0, column=3, padx=5, pady=5)

ttk.Button(weekend_frame, text="Generate Weekend Slots", command=generate_weekend_slots).grid(row=0, column=4, padx=5, pady=5)

ttk.Label(weekend_frame, text="Weekend Time Ranking:").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="e")
weekend_listbox = tk.Listbox(weekend_frame, height=5, exportselection=False)
weekend_listbox.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

weekend_button_frame = ttk.Frame(weekend_frame)
weekend_button_frame.grid(row=1, column=4, padx=5, pady=5)
ttk.Button(weekend_button_frame, text="Move Up", command=move_up_weekend).pack(fill="x", pady=2)
ttk.Button(weekend_button_frame, text="Move Down", command=move_down_weekend).pack(fill="x", pady=2)

# ---- Court Ranking Section ----
court_frame = ttk.LabelFrame(root, text="Court Ranking (shared by all days)")
court_frame.pack(padx=10, pady=5, fill="x")

court_listbox = tk.Listbox(court_frame, height=7, exportselection=False)
court_listbox.pack(side="left", padx=5, pady=5)

court_button_frame = ttk.Frame(court_frame)
court_button_frame.pack(side="left", padx=5, pady=5)
ttk.Button(court_button_frame, text="Move Up", command=move_up_court).pack(fill="x", pady=2)
ttk.Button(court_button_frame, text="Move Down", command=move_down_court).pack(fill="x", pady=2)

# ---- Bottom Buttons ----
bottom_frame = ttk.Frame(root)
bottom_frame.pack(padx=10, pady=10, fill="x")
ttk.Button(bottom_frame, text="Save", command=on_save).pack(side="left", padx=5)
ttk.Button(bottom_frame, text="Quit", command=root.destroy).pack(side="left", padx=5)

# ---- Load configuration and populate UI ----
config = load_config()
populate_ui_from_config(config)

root.mainloop()
