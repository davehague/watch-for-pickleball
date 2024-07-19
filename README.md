# Pickleball Event Checker

This script checks a specific URL for new pickleball events and sends an email notification if new events are found. It runs daily and keeps track of previously found events to avoid duplicate notifications.

## Requirements

The following Python packages are required:
- `requests`
- `beautifulsoup4`
- `schedule`
- `python-dotenv`

You can install the required packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Configuration

### Gmail Setup

To use your Gmail account to send email notifications, follow these steps:

1. **Generate an App Password** (if you have 2-Step Verification enabled):
   - Go to the [App passwords page](https://myaccount.google.com/apppasswords).
   - Generate an app password and store it in `.env` under `PASSWORD`

### Environment Variables

Create a `.env` file in the root directory of your project with the following content:

```
EMAIL=your-email@gmail.com
PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient-email@example.com
URL=https://example.com/pickleball-events
```

Replace the placeholders with your actual information.

### Chrome WebDriver
Get the chrome webdriver from [this location](https://googlechromelabs.github.io/chrome-for-testing/), extract it,
and place it in the same folder as `main.py`

## Running the Script

### Manually

You can run the script manually by executing the following command:

```bash
python pickleball_event_checker.py
```

### Automatically Using Windows Task Scheduler

1. Open Task Scheduler.
2. Click on "Create Basic Task".
3. Name your task and provide a description.
4. Choose the trigger (e.g., daily) and set the time.
5. Choose "Start a program" as the action.
6. Browse to your Python executable (e.g., `python.exe`).
7. Add the path to your script in the "Add arguments" field (e.g., `C:\path\to\pickleball_event_checker.py`).
8. Finish and save the task.

The script will now run daily at the specified time and check for new pickleball events.

## Script Details

The script performs the following steps:

1. Fetches and parses the webpage content from the specified URL.
2. Checks for new events by comparing the fetched events with previously stored events.
3. Sends an email notification if new events are found.
4. Stores the new events in a JSON file to avoid duplicate notifications.

## Scheduling (Windows)
1. Set the environment variable `WATCH_PB_PROJECT_DIR` to the location of this project.
2. Create a new task in Task Scheduler. Set Actions -> Program/Script to the `.bat` file in the root of this project.