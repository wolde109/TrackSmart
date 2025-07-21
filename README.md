# Job Application Tracker

A Python-based tool that helps you log, track, and follow up on job applications using Google Sheets.

## ✅ Features

- Log job applications with details like company, role, application date, and status
- Store all data in a Google Sheet via the Sheets API
- View your applications in a clean format
- Automatically send follow-up reminders 7 days after applying
- Update the status of applications as they progress

## 📦 Requirements

- Python 3.7+
- A Google Cloud service account with access to Google Sheets
- `gspread` and `google-auth` libraries (installed via `pip`)

## 🔧 Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/job-application-tracker.git
   cd job-application-tracker

## Optional (if local environment has trouble installing `gspread` and `google-auth` libraries):

python3 -m venv venv

source venv/bin/activate  # macOS/Linux

venv\Scripts\activate     # Windows


## Set up your Google service account:

1. Create credentials at Google Cloud Console

2. Enable the Google Sheets API

3. Download the secrets.json file and place it in your project directory

4. Share your Google Sheet with the service account email (found in the JSON)

5. Update main.py with the name of your Google Sheet (long string between /d/ and /edit in the URL bar) and desired range.


## Run:

python main.py


After running the program, you'll be prompted to:

1. Add a new job

2. View all jobs

3. Update application status

4. Send follow-up reminders

5. Exit


## File Structure
job-application-tracker/

main.py                   # Main script to interact with the tracker
reminder.py               # Helper functions (view, update, reminder logic)
secrets.json              # Google API credentials (do NOT commit this if repo is public)
README.md                 # This file


## Program Snippet:

<img width="428" height="142" alt="Image" src="https://github.com/user-attachments/assets/3b7dea6d-f059-4535-a668-8c275d664ebb" />

<img width="444" height="21" alt="Image" src="https://github.com/user-attachments/assets/42fa9a37-46fb-4468-9276-1f68ee3e38c2" />


# Notes:

1. Add secrets.json to your .gitignore file
2. If you choose to work in a virtual environment, please include 'venv/' in your .gitignore file too


