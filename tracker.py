from datetime import datetime, timedelta

def add_job(service, spreadsheet_id, job_data, sheet_name='Sheet1'):
    """
    Append a new job application to the sheet.
    job_data = [Job Title, Company, Date Applied, Status]
    """
    try:
        datetime.strptime(job_data[2], "%Y-%m-%d")
    except ValueError:
        print("❌ Error: Please enter the date in YYYY-MM-DD format.")
        return

    body = {'values': [job_data]}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A:D',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"Added job application: {job_data[0]} at {job_data[1]}")


def view_jobs(service, spreadsheet_id, sheet_name='Sheet1'):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:D').execute()
    values = result.get('values', [])

    if not values or len(values) == 1:
        print("No job applications found.")
        return

    # Pad rows to make sure all columns are present
    for row in values:
        while len(row) < 4:
            row.append('')

    # Define column widths
    col_widths = [20, 20, 20, 20]  # Adjust as needed

    # Print header
    for i, col in enumerate(values[0]):
        print(col.ljust(col_widths[i]), end="")
    print()

    # Print each job application row
    for row in values[1:]:
        for i, col in enumerate(row):
            print(col.ljust(col_widths[i]), end="")
        print()



def update_job_status(service, spreadsheet_id, sheet_name='Sheet1'):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:D').execute()
    values = result.get('values', [])

    if not values or len(values) == 1:
        print("No job applications found.")
        return

    # Show job list with indexes
    print("Job Applications:")
    for i, row in enumerate(values[1:], start=1):
        if len(row) < 2:
            print(f"{i}: [Invalid Row]")
            continue
        
        status = row[3] if len(row) > 3 else "N/A"
        print(f"{i}. {row[0]} at {row[1]} - Status: {status}")

    choice = input("Enter the number of the jobs to update: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(values) - 1:
        print("Invalid choice.")
        return
    idx = int(choice)

    valid_statuses = ["Applied", "Interview", "Offer", "Rejected"]

    valid_statuses = ["Applied", "Interview", "Offer", "Rejected"]
    new_status = input("Enter new status: ").strip().capitalize()

    # Optionally validate
    if new_status not in valid_statuses:
        print("Invalid status. Please enter one of:", ", ".join(valid_statuses))
        return

    # Update the status cell (column D = 4th column, zero-index 3)
    update_range = f"{sheet_name}!D{idx + 1}"
    body = {'values': [[new_status]]}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=update_range,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    print(f"Updated job #{idx} status to {new_status}.")


def send_followup_reminders(service, spreadsheet_id, sheet_name='Sheet1', days_threshold=7):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:D').execute()
    values = result.get('values', [])

    if not values or len(values) == 1:
        print("No job applications found.")
        return

    today = datetime.now()
    reminders_sent = False

    for i, row in enumerate(values[1:], start=2):
        if len(row) < 3:
            continue
        try:
            date_applied = datetime.strptime(row[2], "%Y-%m-%d")
        except ValueError:
            print(f"Skipping row {i}: invalid date format '{row[2]}'")
            continue

        days_since_applied = (today - date_applied).days

        if days_since_applied >= days_threshold and row[3].strip().lower() == 'applied':
            print(f"Reminder: Follow up on {row[0]} at {row[1]}, applied {days_since_applied} days ago.")
            reminders_sent = True

    if not reminders_sent:
        print("No follow-up reminders to send today.")
