# Suppress SSL warnings using environment variable
import os
os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'

# Import Flask components and the main tracker logic
from flask import Flask, render_template, request
import main
from tracker import add_job, view_jobs, view_jobs_web, update_job_status, update_job_status_web, send_followup_reminders, send_followup_reminders_web

# Initialize Flask application
app = Flask(__name__)

# Route for the main page - displays the tracker interface
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle adding a new job application
@app.route('/add-job', methods=['POST'])
def add_jobs():
    try:
        # Get form data
        job_title = request.form.get('job_title', '').strip()
        company = request.form.get('company', '').strip()
        date_applied = request.form.get('date_applied', '').strip()
        status = request.form.get('status', '').strip()
        
        # Validate required fields
        if not all([job_title, company, date_applied, status]):
            return render_template('index.html', error="All fields are required", success=False)
        
        # Call the add_job function from tracker.py
        add_job(main.service, main.SPREADSHEET_ID, [job_title, company, date_applied, status])
        
        return render_template('index.html', result=f"Successfully added job application: {job_title} at {company}", success=True)
    except Exception as e:
        return render_template('index.html', error=str(e), success=False)

# Route to handle viewing all job applications
@app.route('/view-jobs', methods=['POST'])
def handle_view_jobs():
    try:
        # Call the web-friendly view_jobs_web function from tracker.py
        result = view_jobs_web(main.service, main.SPREADSHEET_ID)
        return render_template('index.html', result=result, success=True)
    except Exception as e:
        return render_template('index.html', error=str(e), success=False)

# Route to handle updating job status
@app.route('/update-status', methods=['POST'])
def update_status_web():
    try:
        # Get form data
        row_number = request.form.get('row_number', '').strip()
        new_status = request.form.get('new_status', '').strip()
        
        # Validate required fields
        if not all([row_number, new_status]):
            return render_template('index.html', error="Row number and new status are required", success=False)
        
        # Call the web-friendly update_job_status_web function from tracker.py
        result = update_job_status_web(main.service, main.SPREADSHEET_ID, row_number, new_status)
        
        # Check if the result contains an error message
        if result.startswith("Error:"):
            return render_template('index.html', error=result, success=False)
        else:
            return render_template('index.html', result=result, success=True)
    except Exception as e:
        return render_template('index.html', error=str(e), success=False)

# Route to handle sending follow-up reminders
@app.route('/send-reminders', methods=['POST'])
def send_reminders_web():
    try:
        # Call the web-friendly send_followup_reminders_web function from tracker.py
        result = send_followup_reminders_web(main.service, main.SPREADSHEET_ID)
        return render_template('index.html', result=result, success=True)
    except Exception as e:
        return render_template('index.html', error=str(e), success=False)

# Route to handle tracker execution when form is submitted (keeping for backward compatibility)
@app.route('/run-tracker', methods=['POST'])
def run_tracker():
    try:
        # Call the main tracker function from main.py
        result = main.main()  # main function
        # Render the same page with success results
        return render_template('index.html', result=result, success=True)
    except Exception as e:
        # If an error occurs, render the page with error message
        return render_template('index.html', error=str(e), success=False)

# Run the Flask app in debug mode when executed directly
if __name__ == '__main__':
    app.run(debug=True)
