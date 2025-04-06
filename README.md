# Squash Court Booking Automation

This project automates the booking of squash courts using Selenium WebDriver. It runs daily at noon to attempt bookings for the next available day.

## Setup

1. Create a GitHub repository and push this code to it
2. Add the following secrets to your GitHub repository:
   - `CLUBLOCKER_USERNAME`: Your ClubLocker username
   - `CLUBLOCKER_PASSWORD`: Your ClubLocker password
3. The workflow will run automatically at noon every day

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```
   CLUBLOCKER_USERNAME=your_username
   CLUBLOCKER_PASSWORD=your_password
   ```

4. Run the script:
   ```bash
   python run_scheduled_bookings.py --verbose
   ```

## Configuration

Edit `booking_config.json` to set your preferred courts and time slots. The script will attempt to book in the order specified.

## Testing

Use the `--test` flag to run in test mode (no actual bookings will be made):
```bash
python run_scheduled_bookings.py --test --verbose
``` 