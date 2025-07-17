from google.oauth2 import service_account
from googleapiclient.discovery import build
from tracker import add_job, view_jobs, update_job_status, send_followup_reminders

# Path to your downloaded secrets file
SERVICE_ACCOUNT_FILE = 'secrets.json'

# Google Sheet ID (from the URL)
SPREADSHEET_ID = '1TkbtTCeTOrK2LlJ8LGwdhgelCzxjZs-P5cQdbxRD_w8'

# Permission to view and edit Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

 # Authenticate with service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


# Range of cells you want to read (adjust as needed)
RANGE_NAME = 'Sheet1!A:D'

def main():
    while True:
        print("\n--- TrackSmart Menu ---")
        print("1. Add job application")
        print("2. View all applications")
        print("3. Update a job's status")
        print("4. Send follow-up reminders")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            job_title = input("Job Title: ").strip()
            company = input("Company: ").strip()
            date_applied = input("Date Applied (YYYY-MM-DD): ").strip()
            status = input("Status (e.g., Applied): ").strip()

            add_job(service, SPREADSHEET_ID, [job_title, company, date_applied, status])

        elif choice == "2":
            view_jobs(service, SPREADSHEET_ID)

        elif choice == "3":
            update_job_status(service, SPREADSHEET_ID)

        elif choice == "4":
            send_followup_reminders(service, SPREADSHEET_ID)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

if __name__ == '__main__':
    main()
